from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
from sqlalchemy.sql import func
# (Note: schemas name ki file hum aglay step mein use karenge, abhi aap raw dict ya fields soch sakte hain)

app = FastAPI(title="Quantum Idempotent Fintech Ledger")

#  Step 1: Tell SQLAlchemy to create tables when the app boots up
Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():
    return {"status": "active", "service": "ledger-engine"}

#  Endpoint 1: Create a New Financial Account Wallet
@app.post("/accounts")
def create_account(owner_name: str, account_number: str, db: Session = Depends(get_db)):
    # Step 1: Query the database to check if the account number is already registered
    existing_account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    
    # Step 2: Validate against duplicate entry. Raise 400 Bad Request if it exists.
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Account number already exists!"
        )
        
    # Step 3: Instantiate a new Account database entity mapping the input parameters
    new_account = models.Account(owner_name=owner_name, account_number=account_number)
    
    # Step 4: Stage the object into the database transaction session context
    db.add(new_account)
    
    # Step 5: Execute the network commit to finalize the INSERT transaction block securely
    db.commit()
    
    # Step 6: Refresh the instance to pull the auto-generated fields (like primary key ID) back from Postgres
    db.refresh(new_account)
    
    # Step 7: Return the synchronized database object wrapper back to the client wrapper
    return new_account

# Endpoint 2: The Core Idempotent Ledger Transaction System
@app.post("/transactions")
def create_transaction(
    idempotency_key: str, 
    account_number: str, 
    amount: float,  # Positive for credit, Negative for debit
    description: str,
    db: Session = Depends(get_db)
):
    # Step 1: Verify request idempotency to prevent double-charging or duplicate entries
    existing_entry = db.query(models.LedgerEntry).filter(models.LedgerEntry.idempotency_key == idempotency_key).first()

    if existing_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate transaction request! This idempotency key has already been used."
        )

    # Step 2: Retrieve account with a pessimistic lock (FOR UPDATE) to block concurrent balance alterations
    account = db.query(models.Account).filter(models.Account.account_number == account_number).with_for_update().first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target financial account does not exist!"
        )

    # Step 3: Compute the current net balance by aggregating all historical ledger rows for this account
    balance_result = db.query(func.sum(models.LedgerEntry.amount)).filter(models.LedgerEntry.account_id == account.id).scalar()
    
    # Fallback to 0.0 if no ledger entries exist yet (new account)
    current_balance = float(balance_result) if balance_result is not None else 0.0
    
    # Step 4: Overdraft protection validation check
    if current_balance + amount < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds! Your current balance is {current_balance}, cannot execute transaction."
        )

    # Step 5: Construct and append the new financial record into the ledger stream
    new_entry = models.LedgerEntry(
        idempotency_key=idempotency_key,
        account_id=account.id,
        amount=amount,
        description=description
    )
    
    # Stage the ledger row insertion inside the transaction context
    db.add(new_entry)
    
    # Commit the transaction block securely, releasing the database row lock
    db.commit()
    
    # Refresh the tracking object instance to synchronize with live database states
    db.refresh(new_entry)
    
    return {
        "status": "Transaction executed successfully",
        "transaction_id": new_entry.id,
        "new_balance": float(current_balance + amount)
    }


@app.get("/accounts/{account_number}/balance")
def get_balance(account_number: str, db: Session = Depends(get_db)):
    # 1. Fetch the account from the database using the account_number string
    account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    
    # 2. Add validation: If account does not exist, raise a 404 HTTPException
    if not account:
        # WRITE YOUR CODE HERE
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Not Found"
        )

    # 3. Aggregate the sum of all transaction amounts for this account ID
    balance_result = db.query(func.sum(models.LedgerEntry.amount)).filter(models.LedgerEntry.account_id == account.id).scalar()
    
    # 4. Handle fallback: Convert Decimal to float, and default to 0.0 if balance_result is None
    # WRITE YOUR CODE HERE
    current_balance = float(balance_result) if balance_result is  not None else 0.0
    
    # 5. Return the clean balance data
    return {
        "account_number": account_number,
        "owner_name": account.owner_name,
        "current_balance": current_balance
    }


@app.get("/accounts/{account_number}/statement")
def get_statement(account_number: str, db: Session = Depends(get_db)):
    # 1. Validate Account existence
    account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        
    # 2. Fetch history records sorted from newest to oldest
    history = db.query(models.LedgerEntry).filter(models.LedgerEntry.account_id == account.id).order_by(models.LedgerEntry.created_at.desc()).all()
    
    return {
        "account_number": account_number,
        "history": history
    }