from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(32), unique=True, nullable=False)
    shovel_level = Column(Integer, default=1)
    money = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)

    backpack_items = relationship("BackpackItem", back_populates="user")
    prizes = relationship("Prize", back_populates="user")

class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=False)
    prize_chance = Column(Integer, default=0)
    garbage_chance = Column(Integer, default=0)
    prize_name = Column(String(255), nullable=True)
    quantity = Column(Integer, default=0)
    health = Column(Integer, default=1)

class BackpackItem(Base):
    __tablename__ = "backpack_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    quantity = Column(Integer, default=0)

    user = relationship("User", back_populates="backpack_items")
    block = relationship("Block")

class Prize(Base):
    __tablename__ = "prizes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    block_id = Column(Integer, ForeignKey("blocks.id"))
    prize_name = Column(String(255), nullable=True)
    claimed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    claimed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="prizes")
    block = relationship("Block")