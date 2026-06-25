# models.py ka shuruat ka hissa check karein:
from database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Numeric , ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# Class ka naam exact 'Account' hona chahiye (Singular aur Capital 'A')
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(50), unique=True, nullable=False)
    owner_name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

# Iske niche aapki LedgerEntry class hogi...

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    # 1. Primary Key: SERIAL in Postgres maps to Integer with primary_key=True
    id = Column(Integer, primary_key=True, index=True)

    # 2. Idempotency Key: Uses Postgres native UUID type and enforces uniqueness
    idempotency_key = Column(UUID(as_uuid=True), unique=True, nullable=False)

    # 3. Foreign Key: Maps to the 'id' column of the 'accounts' table
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)

    # 4. Financial Amount: High precision Numeric(15, 4) to eliminate rounding errors
    amount = Column(Numeric(15, 4), nullable=False)

    # 5. Description: Simple text field for tracking transaction details
    description = Column(String(255), nullable=True)

    # 6. Timestamp: Automatically sets the server time on row insertion
    created_at = Column(TIMESTAMP, server_default=func.now())