from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FileUpload, Form, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.base import get_db
from app.db.models.user import User
from app.db.models.file import FileType
from app.services.transaction_service import TransactionService
from app.schemas.transaction_dto import (
    TransactionCreateDTO,
    TransactionUpdateDTO,
    TransactionResponse,
    TransactionListResponse,
    TransactionSummaryResponse,
    TransactionFilterDTO,
    BulkTransactionCreateDTO,
    FileResponse
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: TransactionCreateDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new transaction
    """
    service = TransactionService(db)
    try:
        transaction = service.create_transaction(transaction_data, current_user.id)
        return TransactionResponse.from_orm(transaction)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=TransactionListResponse)
def get_transactions(
    wallet_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    amount_min: Optional[float] = Query(None),
    amount_max: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("date"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's transactions with filtering and pagination
    """
    # Build filters
    filters = TransactionFilterDTO()
    if wallet_id:
        filters.wallet_id = wallet_id
    if category:
        filters.category = category
    if transaction_type:
        filters.type = transaction_type
    if date_from:
        filters.date_from = date_from
    if date_to:
        filters.date_to = date_to
    if amount_min:
        filters.amount_min = amount_min
    if amount_max:
        filters.amount_max = amount_max
    if search:
        filters.search = search

    service = TransactionService(db)
    return service.get_user_transactions(
        current_user.id, 
        filters, 
        skip, 
        limit, 
        sort_by, 
        sort_order
    )


@router.get("/summary", response_model=TransactionSummaryResponse)
def get_transaction_summary(
    wallet_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transaction summary statistics
    """
    # Build filters
    filters = TransactionFilterDTO()
    if wallet_id:
        filters.wallet_id = wallet_id
    if category:
        filters.category = category
    if transaction_type:
        filters.type = transaction_type
    if date_from:
        filters.date_from = date_from
    if date_to:
        filters.date_to = date_to

    service = TransactionService(db)
    return service.get_transaction_summary(current_user.id, filters)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific transaction by ID
    """
    service = TransactionService(db)
    transaction = service.get_transaction_by_id(transaction_id, current_user.id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.from_orm(transaction)


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdateDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a transaction
    """
    service = TransactionService(db)
    try:
        transaction = service.update_transaction(transaction_id, update_data, current_user.id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return TransactionResponse.from_orm(transaction)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a transaction
    """
    service = TransactionService(db)
    try:
        success = service.delete_transaction(transaction_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return {"message": "Transaction deleted successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bulk", response_model=List[TransactionResponse], status_code=status.HTTP_201_CREATED)
def bulk_create_transactions(
    bulk_data: BulkTransactionCreateDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create multiple transactions in bulk
    """
    service = TransactionService(db)
    try:
        transactions = service.bulk_create_transactions(bulk_data, current_user.id)
        return [TransactionResponse.from_orm(t) for t in transactions]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{transaction_id}/files", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
def upload_transaction_file(
    transaction_id: int,
    file: UploadFile = FileUpload(...),
    file_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file attachment for a transaction
    """
    # Validate file type
    try:
        file_type_enum = FileType(file_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Must be one of: {[ft.value for ft in FileType]}"
        )

    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit"
        )

    service = TransactionService(db)
    
    # Check if transaction exists
    transaction = service.get_transaction_by_id(transaction_id, current_user.id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    try:
        file_record = service.add_file_to_transaction(file, transaction_id, file_type_enum, current_user.id)
        return FileResponse.from_orm(file_record)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/{transaction_id}/files", response_model=List[FileResponse])
def get_transaction_files(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all files for a transaction
    """
    service = TransactionService(db)
    
    # Check if transaction exists
    transaction = service.get_transaction_by_id(transaction_id, current_user.id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    files = service.get_transaction_files(transaction_id, current_user.id)
    return [FileResponse.from_orm(f) for f in files]


@router.delete("/files/{file_id}")
def delete_transaction_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file attachment
    """
    service = TransactionService(db)
    success = service.delete_file(file_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {"message": "File deleted successfully"}


@router.get("/wallet/{wallet_id}", response_model=List[TransactionResponse])
def get_wallet_transactions(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific wallet
    """
    service = TransactionService(db)
    transactions = service.get_transactions_by_wallet(wallet_id, current_user.id)
    return [TransactionResponse.from_orm(t) for t in transactions]
