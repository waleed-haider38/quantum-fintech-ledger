from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
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
    #  APNI LOGIC IDHAR LIKHEIN:
    # 1. Check idempotency: Kya yeh key already ledger_entries mein exist karti hai?
    if create_transaction[idempotency_key]:
        return 
    # 2. Find Account: Account number se database se account ki ID nikaalein.
    # 3. Calculate Balance: Is ID ki saari ledger entries ka SUM nikaalein.
    # 4. Safety Check: Agar balance + amount < 0 ho raha hai, toh transaction block karein (Insufficient funds).
    # 5. Insert: Sab sahi hai toh models.LedgerEntry insert karein aur db.commit() karein.
    pass