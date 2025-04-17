import os
import time
import glob
import jwt
import httpx
import uuid
import random
import secrets
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from typing import Optional, List, Dict
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi import Depends, Cookie, Form, Request
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from app.dependencies import get_db
from app.models import User, Block, BackpackItem, ItemType
from app.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def get_user_from_db(student_id: str, db: Session):
    return db.query(User).filter(User.student_id == student_id).first()

def save_user_to_db(student_id: str, email: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.student_id == student_id).first()
    if existing_user:
        return existing_user
    
    admin_ids = ["admin", "112550013"]
    
    new_user = User(
        student_id=student_id,
        shovel_level=1,
        money=0,
        is_admin=(student_id in admin_ids)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    if not settings.ALLOW_MOCK_LOGIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mock login is disabled in production environment"
        )

    user = get_user_from_db(form_data.username, db)
    if not user:
        admin_ids = ["admin", "112550013"]
        
        user = User(
            student_id=form_data.username,
            shovel_level=1,
            money=0,
            is_admin=(form_data.username in admin_ids)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    payload = {
        "sub": user.student_id,
        "exp": int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        "iat": int(time.time()),
        "iss": "15night",
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    # Return in the exact format OAuth2 expects
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/oauth/login")
async def oauth_nycu_login(request: Request):
    csrf_token = secrets.token_urlsafe(32)
    request.session['csrf_token'] = csrf_token
    
    scopes = "profile"
    auth_url = (
        f"{settings.NYCU_AUTHORIZE_URL}"
        f"?client_id={settings.NYCU_CLIENT_ID}"
        f"&response_type=code"
        f"&state={csrf_token}"
        f"&scope={scopes.replace(' ', '%20')}"
        f"&redirect_uri={settings.NYCU_REDIRECT_URI}"
    )
    return RedirectResponse(url=auth_url)

@router.get("/oauth/callback")
async def oauth_nycu_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    stored_csrf_token = request.session.get('csrf_token')
    if not stored_csrf_token or stored_csrf_token != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CSRF token"
        )
    
    request.session.pop('csrf_token', None)
    
    async with httpx.AsyncClient(verify=False) as client:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.NYCU_CLIENT_ID,
            "client_secret": settings.NYCU_CLIENT_SECRET,
            "redirect_uri": settings.NYCU_REDIRECT_URI,
        }
        token_resp = await client.post(settings.NYCU_TOKEN_URL, data=data)
    if token_resp.status_code != 200:
        raise HTTPException(status_code=token_resp.status_code, detail="Token exchange failed")
    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received from OAuth provider")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(verify=False) as client:
        profile_resp = await client.get(settings.NYCU_PROFILE_URL, headers=headers)
        
    if profile_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user information")
    profile_data = profile_resp.json()
    
    student_id = profile_data.get("username")
    user_email = profile_data.get("email")
    if not student_id or not user_email:
        raise HTTPException(status_code=400, detail="Incomplete user information")
    
    user_in_db = save_user_to_db(student_id, user_email, db)
    
    payload = {
        "sub": user_in_db.student_id,
        "exp": int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        "iat": int(time.time()),
        "iss": "15night",
        "jti": str(uuid.uuid4()), 
    }
    our_jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    front_end_redirect_url = f"{settings.FRONTEND_URL}{settings.FRONTEND_REDIRECT_PATH}?token={our_jwt_token}"
    return RedirectResponse(url=front_end_redirect_url)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        student_id = payload.get("sub")
        if student_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        user = get_user_from_db(student_id, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found in DB")

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token decode error")

@router.get("/leaderboard")
async def leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    """Get leaderboard - sorts first by shovel level, then by money"""
    users = db.query(User).order_by(
        User.shovel_level.desc(), 
        User.money.desc(),
        User.student_id.asc()
    ).limit(limit).all()
    
    result = []
    current_rank = 1
    prev_user = None
    
    for i, user in enumerate(users):
        if i == 0:
            rank = current_rank
        elif user.shovel_level == prev_user.shovel_level and user.money == prev_user.money:
            rank = result[-1]["rank"]
        else:
            current_rank = i + 1
            rank = current_rank

        result.append({
            "student_id": user.student_id,
            "shovel_level": user.shovel_level,
            "money": user.money,
            "rank": rank
        })
        
        prev_user = user
    
    return result

@router.get("/blocks/available")
async def get_available_blocks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get available blocks for mining"""
    blocks = db.query(Block).filter(Block.enabled == True).all()
    
    regular_blocks = [b for b in blocks if b.type == ItemType.REGULAR]
    prize_blocks = [b for b in blocks if b.type == ItemType.PRIZE]
    
    base_prize_chance = 10
    shovel_bonus = (current_user.shovel_level - 1) * 1
    prize_chance = min(base_prize_chance + shovel_bonus, 30)
    
    result = []
    for block in blocks:
        block_info = {
            "id": block.id,
            "name": block.name,
            "type": block.type.value
        }
        
        if block.type == ItemType.PRIZE:
            block_info["quantity"] = block.quantity
            block_info["available"] = block.quantity > 0
        
        result.append(block_info)

    return {
        "blocks": result,
        "stats": {
            "total_blocks": len(blocks),
            "regular_blocks": len(regular_blocks),
            "prize_blocks": len(prize_blocks),
            "prize_chance": prize_chance,
            "shovel_level": current_user.shovel_level
        }
    }

@router.post("/blocks/{block_id}/start")
async def start_mining(
    block_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start mining a block"""
    block = db.query(Block).filter(Block.id == block_id, Block.enabled == True).first()
    if not block:
        raise HTTPException(status_code=404, detail=f"Block with id {block_id} not found or not enabled")
    
    original_block = block
    is_special = False
    prize_chance = 0
    out_of_stock = False
    
    if block.type == ItemType.PRIZE:
        if block.quantity > 0:
            base_prize_chance = 10
            shovel_bonus = (current_user.shovel_level - 1) * 1
            block_bonus = block.prize_chance
            prize_chance = min(base_prize_chance + shovel_bonus + block_bonus, 30)
            
            is_special = random.randint(1, 100) <= prize_chance
            
            if is_special:
                block.quantity -= 1
                db.commit()
        else:
            out_of_stock = True
            is_special = False
        
        if not is_special:
            regular_blocks = db.query(Block).filter(
                Block.enabled == True, 
                Block.type == ItemType.REGULAR
            ).all()
            
            if not regular_blocks:
                raise HTTPException(status_code=404, detail="No regular blocks found")
            
            block = random.choice(regular_blocks)

    request.session[f"mining_{current_user.id}"] = {
        "block_id": block.id,
        "timestamp": time.time()
    }
    
    return {
        "block_id": block.id,
        "name": block.name,
        "type": block.type.value,
        "is_special": is_special or (block.type == ItemType.PRIZE and block.id == original_block.id),
        "original_request": {
            "block_id": original_block.id,
            "name": original_block.name,
            "type": original_block.type.value,
            "out_of_stock": out_of_stock
        } if block.id != original_block.id else None,
        "prize_info": {
            "prize_chance": prize_chance,
            "roll_succeeded": is_special,
            "remaining_quantity": original_block.quantity if original_block.type == ItemType.PRIZE else None
        } if original_block.type == ItemType.PRIZE else None
    }

@router.post("/blocks/{block_id}/complete")
async def complete_mining(
    block_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete mining and add block to backpack"""
    mining_data = request.session.get(f"mining_{current_user.id}")
    
    if not mining_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active mining session found"
        )
    
    started_block_id = mining_data.get("block_id")
    if started_block_id != block_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Block ID mismatch. You started mining block {started_block_id}, not {block_id}"
        )

    if time.time() - mining_data.get("timestamp", 0) > 300:
        request.session.pop(f"mining_{current_user.id}", None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mining session expired"
        )
    
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail=f"Block with id {block_id} not found")
    
    request.session.pop(f"mining_{current_user.id}", None)
    
    backpack_item = db.query(BackpackItem).filter(
        BackpackItem.user_id == current_user.id,
        BackpackItem.block_id == block.id
    ).first()
    
    if backpack_item:
        backpack_item.quantity += 1
    else:
        new_item = BackpackItem(
            user_id=current_user.id,
            block_id=block.id,
            quantity=1
        )
        db.add(new_item)
    
    base_money = random.randint(1, 5) * current_user.shovel_level
    
    if block.type == ItemType.PRIZE:
        money_earned = base_money * 2
    else:
        money_earned = base_money
    
    current_user.money += money_earned
    
    db.commit()
    
    return {
        "block_id": block.id,
        "name": block.name,
        "type": block.type.value,
        "money_earned": money_earned,
        "message": f"Mining completed! Added {block.name} to backpack and earned {money_earned} money."
    }

@router.get("/user/stats")
async def get_user_stats(current_user: User = Depends(get_current_user)):
    """Get user statistics"""
    return {
        "student_id": current_user.student_id,
        "shovel_level": current_user.shovel_level,
        "money": current_user.money,
        "is_admin": current_user.is_admin
    }

@router.post("/user/upgrade-shovel")
async def upgrade_shovel(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Upgrade user's shovel"""
    upgrade_cost = current_user.shovel_level * 100
    
    if current_user.money < upgrade_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough money. Need {upgrade_cost}, have {current_user.money}"
        )
    
    current_user.money -= upgrade_cost
    current_user.shovel_level += 1
    
    db.commit()
    
    return {
        "shovel_level": current_user.shovel_level,
        "money": current_user.money,
        "message": f"Shovel upgraded to level {current_user.shovel_level}"
    }

@router.get("/user/backpack")
async def get_user_backpack(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's backpack contents"""
    backpack_items = db.query(BackpackItem).filter(BackpackItem.user_id == current_user.id).all()
    
    total_items = 0
    result = []
    
    for item in backpack_items:
        block = db.query(Block).filter(Block.id == item.block_id).first()
        if block:
            total_items += item.quantity
            result.append({
                "block_id": block.id,
                "name": block.name,
                "type": block.type.value,
                "quantity": item.quantity
            })
    
    return {
        "items": result,
        "total_items": total_items,
        "unique_items": len(result)
    }
