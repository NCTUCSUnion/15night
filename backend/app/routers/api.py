import os
import time
import glob
import jwt
import httpx
import uuid
import random
import secrets
import pytz
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from typing import Optional, List, Dict
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import desc
from fastapi import Depends, Cookie, Form, Request
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from app.dependencies import get_db
from app.models import User, Block, BackpackItem, Prize
from app.config import settings
from urllib.parse import unquote

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def get_user_from_db(student_id: str, db: Session):
    return db.query(User).filter(User.student_id == student_id).first()

def save_user_to_db(student_id: str, email: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.student_id == student_id).first()
    if (existing_user):
        return existing_user
    
    admin_ids = ["admin", "112550013", "112550024", "112550127", "111550085", "111550160"]
    
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
async def oauth_nycu_login(
    request: Request,
    redirect_to: Optional[str] = Query(None),
):
    csrf_token = secrets.token_urlsafe(32)
    request.session['csrf_token'] = csrf_token
    if redirect_to:
        decoded_redirect_to = unquote(redirect_to)
        print(f"Decoded redirect_to: {decoded_redirect_to}")
        request.session['after_login_redirect'] = decoded_redirect_to
    else:
        request.session['after_login_redirect'] = settings.FRONTEND_URL + settings.FRONTEND_REDIRECT_PATH

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

    redirect_to = request.session.pop('after_login_redirect', None)
    if not redirect_to:
        redirect_to = settings.FRONTEND_URL + settings.FRONTEND_REDIRECT_PATH

    url = f"{redirect_to}?token={our_jwt_token}"
    return RedirectResponse(url=url)

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

@router.get("/blocks")
async def get_all_blocks(db: Session = Depends(get_db)):
    """Get all blocks available in the game"""
    blocks = db.query(Block).all()
    result = []
    
    for block in blocks:
        result.append({
            "id": block.id,
            "name": block.name,
            "health": block.health,
            "enabled": block.enabled,
            "has_prizes": block.prize_chance > 0 and block.quantity > 0,
            "prize_chance": block.prize_chance,
            "garbage_chance": block.garbage_chance
        })
    
    return {
        "blocks": result,
        "total_blocks": len(result)
    }

@router.post("/blocks/{block_id}/start")
async def start_mining(
    block_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start mining a block"""
    if request.session.get(f"mining_{current_user.id}"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active mining session already exists. Please complete or cancel it first."
        )

    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail=f"Block with id {block_id} not found")
    
    got_garbage = False
    got_prize = False

    if random.randint(1, 100) <= block.garbage_chance:
        got_garbage = True
    else:
        if block.enabled:
            user_prize_count = db.query(Prize).filter(Prize.user_id == current_user.id).count()
            if user_prize_count < 3:
                prize_chance = block.prize_chance
                if random.randint(1, 10000) <= prize_chance and block.quantity > 0:
                    got_prize = True
                    block.quantity -= 1
                    db.commit()
    
    request.session[f"mining_{current_user.id}"] = {
        "block_id": block.id,
        "timestamp": time.time(),
        "got_prize": got_prize,
        "got_garbage": got_garbage
    }
    
    return {
        "block_id": block.id,
        "name": block.name,
        "health": block.health,
        "got_garbage": got_garbage,
        "got_prize": got_prize,
        "prize_info": {
            "prize_name": block.prize_name if got_prize else None,
            "remaining_quantity": block.quantity if got_prize else None
        } if got_prize else None
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
    
    # Extract information from session
    started_block_id = mining_data.get("block_id")
    got_prize = mining_data.get("got_prize", False)
    got_garbage = mining_data.get("got_garbage", False)
    start_timestamp = mining_data.get("timestamp", 0)
    
    if started_block_id != block_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Block ID mismatch. You started mining block {started_block_id}, not {block_id}"
        )

    elapsed_time = time.time() - start_timestamp
    if elapsed_time < 0.3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mining too fast! Please wait at least 0.3 seconds between start and complete (elapsed: {elapsed_time:.2f}s)"
        )

    if elapsed_time > 300:
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
    
    t = 45  # Expected time to upgrade (in seconds)
    base_money = 20 * block.health / t
    base_money *= random.uniform(0.8, 1.2)
    
    if got_garbage:
        money_earned = int(base_money * random.uniform(1.5, 2.0))
        message = "You found garbage! Bonus money earned."
    elif got_prize:
        money_earned = int(base_money)

        new_prize = Prize(
            user_id=current_user.id,
            block_id=block.id,
            prize_name=block.prize_name,
            claimed=False
        )
        db.add(new_prize)
        message = f"Mining completed! You earned a special prize that can be claimed later!"
    else:
        money_earned = int(base_money)
        message = f"Mining completed! Added {block.name} to backpack."
    
    current_user.money += money_earned
    db.commit()
    
    return {
        "block_id": block.id,
        "name": block.name,
        "money_earned": money_earned,
        "got_garbage": got_garbage,
        "got_prize": got_prize,
        "message": message + f" Earned {money_earned} money."
    }

@router.post("/blocks/status")
async def mining_status(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has an active mining session for the given block"""
    mining_data = request.session.get(f"mining_{current_user.id}")
    
    if not mining_data:
        return {
            "mining": False,
            "message": "No active mining session found"
        }
    
    if time.time() - mining_data.get("timestamp", 0) > 300:
        request.session.pop(f"mining_{current_user.id}", None)
        return {
            "mining": False,
            "message": "Mining session expired"
        }

    block_id = mining_data.get("block_id")
    
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        return {
            "mining": False,
            "message": f"Block with id {block_id} not found"
        }
    
    return {
        "mining": True,
        "block_id": block.id,
        "name": block.name,
        "health": block.health,
        "got_garbage": mining_data.get("got_garbage", False),
        "got_prize": mining_data.get("got_prize", False),
        "prize_info": {
            "prize_name": block.prize_name if mining_data.get("got_prize", False) else None,
            "remaining_quantity": block.quantity if mining_data.get("got_prize", False) else None
        } if mining_data.get("got_prize", False) else None,
        "start_time": mining_data.get("timestamp")
    }
    
@router.post("/blocks/{block_id}/cancel")
async def cancel_mining(
    block_id: int,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Cancel an active mining session"""
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
    
    # Clear the mining session
    request.session.pop(f"mining_{current_user.id}", None)
    
    return {
        "block_id": block_id,
        "message": "Mining session canceled successfully"
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
                "quantity": item.quantity
            })
    
    return {
        "items": result,
        "total_items": total_items,
        "unique_items": len(result)
    }

@router.get("/user/prizes")
async def get_user_prizes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's prizes"""
    prizes = db.query(Prize).filter(Prize.user_id == current_user.id).order_by(desc(Prize.created_at)).all()
    
    result = []
    for prize in prizes:
        block = db.query(Block).filter(Block.id == prize.block_id).first()
        if block:
            result.append({
                "id": prize.id,
                "block_id": block.id,
                "name": block.name,
                "prize_name": block.prize_name,
                "claimed": prize.claimed,
                "created_at": prize.created_at.isoformat(),
                "claimed_at": prize.claimed_at.isoformat() if prize.claimed_at else None
            })
    
    return {
        "prizes": result,
        "total_prizes": len(result),
        "claimed_prizes": sum(1 for p in result if p["claimed"])
    }

@router.put("/user/prizes/{prize_id}/claim")
async def claim_prize(
    prize_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Claim a prize"""
    prize = db.query(Prize).filter(
        Prize.id == prize_id,
        Prize.user_id == current_user.id,
        Prize.claimed == False
    ).first()
    
    if not prize:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prize not found or already claimed"
        )
    
    block = db.query(Block).filter(Block.id == prize.block_id).first()
    
    prize.claimed = True
    prize.claimed_at = datetime.utcnow()
    db.commit()
    
    return {
        "id": prize.id,
        "name": block.name if block else "Unknown",
        "claimed": prize.claimed,
        "claimed_at": prize.claimed_at.isoformat(),
        "message": f"Prize successfully claimed"
    }

@router.get("/admin/blocks")
async def get_all_block_templates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Admin: Get all blocks"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    blocks = db.query(Block).all()
    result = []
    
    for block in blocks:
        result.append({
            "id": block.id,
            "name": block.name,
            "enabled": block.enabled,
            "prize_chance": block.prize_chance,
            "garbage_chance": block.garbage_chance,
            "prize_name": block.prize_name,
            "quantity": block.quantity,
            "health": block.health
        })
    
    return result

@router.post("/admin/blocks")
async def create_block_template(
    name: str = Body(...), 
    enabled: bool = Body(False),
    prize_chance: int = Body(0),
    garbage_chance: int = Body(0),
    prize_name: str = Body(None),
    quantity: int = Body(0),
    health: int = Body(1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Create new block"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    if quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity cannot be negative"
        )
        
    if health < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Health must be at least 1"
        )
    
    new_block = Block(
        name=name,
        enabled=enabled,
        prize_chance=prize_chance,
        garbage_chance=garbage_chance,
        prize_name=prize_name,
        quantity=quantity,
        health=health
    )
    
    db.add(new_block)
    db.commit()
    db.refresh(new_block)
    
    return {
        "id": new_block.id,
        "name": new_block.name,
        "enabled": new_block.enabled,
        "prize_chance": new_block.prize_chance,
        "garbage_chance": new_block.garbage_chance,
        "prize_name": new_block.prize_name,
        "quantity": new_block.quantity,
        "health": new_block.health
    }

@router.put("/admin/blocks/{block_id}")
async def update_block(
    block_id: int,
    name: str = Body(None),
    enabled: bool = Body(None),
    prize_chance: int = Body(None),
    garbage_chance: int = Body(None),
    prize_name: str = Body(None),
    quantity: int = Body(None),
    health: int = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Update block properties"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with id {block_id} not found"
        )
    
    if name is not None:
        block.name = name
    
    if enabled is not None:
        block.enabled = enabled
        
    if prize_chance is not None:
        block.prize_chance = prize_chance
        
    if garbage_chance is not None:
        block.garbage_chance = garbage_chance
        
    if prize_name is not None:
        block.prize_name = prize_name
        
    if quantity is not None:
        if quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity cannot be negative"
            )
        block.quantity = quantity
        
    if health is not None:
        if health < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Health must be at least 1"
            )
        block.health = health
    
    db.commit()
    db.refresh(block)
    
    return {
        "id": block.id,
        "name": block.name,
        "enabled": block.enabled,
        "prize_chance": block.prize_chance,
        "garbage_chance": block.garbage_chance,
        "prize_name": block.prize_name,
        "quantity": block.quantity,
        "health": block.health
    }

@router.put("/admin/blocks/{block_id}/quantity")
async def update_block_quantity(
    block_id: int,
    quantity: int = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Update block quantity"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with id {block_id} not found"
        )
    
    if quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity cannot be negative"
        )
    
    block.quantity = quantity
    db.commit()
    
    return {
        "id": block.id,
        "name": block.name,
        "enabled": block.enabled,
        "quantity": block.quantity,
        "message": f"Quantity for block {block.name} updated to {quantity}"
    }

@router.put("/admin/blocks/type/toggle")
async def toggle_blocks_by_type(
    enabled: bool = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Toggle all blocks of a type"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    affected_rows = db.query(Block).update({Block.enabled: enabled})
    db.commit()
    
    return {
        "enabled": enabled,
        "affected_blocks": affected_rows,
        "message": f"All blocks have been {'enabled' if enabled else 'disabled'}"
    }

@router.get("/admin/users")
async def get_all_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Admin: Get all users"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    users = db.query(User).all()
    result = []
    
    for user in users:
        result.append({
            "id": user.id,
            "student_id": user.student_id,
            "shovel_level": user.shovel_level,
            "money": user.money,
            "is_admin": user.is_admin
        })
    
    return result

@router.put("/admin/users/{student_id}/set-admin")
async def set_admin_status(
    student_id: str,
    is_admin: bool = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Set admin status for a user"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    user = db.query(User).filter(User.student_id == student_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with student_id {student_id} not found"
        )
    
    user.is_admin = is_admin
    db.commit()
    
    return {
        "student_id": user.student_id,
        "is_admin": user.is_admin,
        "message": f"Admin status for {student_id} set to {is_admin}"
    }

@router.post("/admin/seed")
async def seed_blocks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Admin: Seed database with initial blocks"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    if db.query(Block).count() == 0:
        blocks = [
            {
                "name": "Dirt",
                "enabled": False,
                "prize_chance": 50,
                "garbage_chance": 20,
                "prize_name": "米庫早午食堂 折價券",
                "quantity": 10,
                "health": 60
            },
            {
                "name": "Stone",
                "enabled": False,
                "prize_chance": 50,
                "garbage_chance": 20,
                "prize_name": "lala kitchen 折價券",
                "quantity": 1,
                "health": 600
            },
            {
                "name": "Coal",
                "enabled": False,
                "prize_chance": 50,
                "garbage_chance": 20,
                "prize_name": "escapeholic 單人遊玩券",
                "quantity": 1,
                "health": 600
            },
            {
                "name": "Iron",
                "enabled": False,
                "prize_chance": 50,
                "garbage_chance": 20,
                "prize_name": "跳動格子單人免費券",
                "quantity": 1,
                "health": 600
            },
            {
                "name": "Gold",
                "enabled": False,
                "prize_chance": 50,
                "garbage_chance": 20,
                "prize_name": "金色三麥 啤酒招待券",
                "quantity": 2,
                "health": 300
            },
            {
                "name": "Diamond",
                "enabled": False,
                "prize_chance": 50,
                "garbage_chance": 20,
                "prize_name": "鉄燒餃子 百元折價券",
                "quantity": 10,
                "health": 60
            }
        ]
        
        for block_data in blocks:
            block = Block(**block_data)
            db.add(block)
        
        db.commit()
        return {"message": "Database seeded with initial blocks"}
    
    return {"message": "Database already has blocks, seeding skipped"}

@router.get("/admin/prizes")
async def get_all_prizes(
    claimed: bool = Query(None),
    student_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Get all prizes with optional filters"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    query = db.query(Prize).join(User)
    
    if claimed is not None:
        query = query.filter(Prize.claimed == claimed)
    
    if student_id is not None:
        query = query.filter(User.student_id == student_id)
    
    prizes = query.order_by(desc(Prize.created_at)).all()
    
    result = []
    for prize in prizes:
        user = db.query(User).filter(User.id == prize.user_id).first()
        block = db.query(Block).filter(Block.id == prize.block_id).first()
        
        result.append({
            "id": prize.id,
            "student_id": user.student_id if user else "Unknown",
            "block_id": prize.block_id,
            "block_name": block.name if block else "Unknown",
            "prize_name": block.prize_name if block else "Unknown",
            "claimed": prize.claimed,
            "created_at": prize.created_at.isoformat(),
            "claimed_at": prize.claimed_at.isoformat() if prize.claimed_at else None
        })
    
    return result

@router.put("/admin/prizes/{prize_id}/claim-status")
async def admin_update_claim_status(
    prize_id: int,
    claimed: bool = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin: Update prize claim status"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin endpoints"
        )
    
    prize = db.query(Prize).filter(Prize.id == prize_id).first()
    if not prize:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prize with id {prize_id} not found"
        )
    
    was_claimed = prize.claimed
    prize.claimed = claimed
    
    utc_8 = pytz.timezone("Asia/Taipei")
    now_utc8 = datetime.now(utc_8)
    
    if claimed and not was_claimed:
        prize.claimed_at = now_utc8
    elif not claimed:
        prize.claimed_at = None
    
    db.commit()
    
    user = db.query(User).filter(User.id == prize.user_id).first()
    block = db.query(Block).filter(Block.id == prize.block_id).first()
    
    return {
        "id": prize.id,
        "student_id": user.student_id if user else "Unknown",
        "block_name": block.name if block else "Unknown",
        "claimed": prize.claimed,
        "claimed_at": prize.claimed_at.isoformat() if prize.claimed_at else None,
        "message": f"Prize status updated to {'claimed' if claimed else 'unclaimed'}"
    }
