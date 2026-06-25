# models.py ka shuruat ka hissa check karein:
from database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func

# Class ka naam exact 'Account' hona chahiye (Singular aur Capital 'A')
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(50), unique=True, nullable=False)
    owner_name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

# Iske niche aapki LedgerEntry class hogi...