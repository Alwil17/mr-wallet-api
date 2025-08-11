from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File as FileUpload,
    Form,
    Query,
)
from sqlalchemy.orm import Session

from app.constants import Constants
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
    FileResponse,
)

router = APIRouter(prefix="/transactions", tags=["Transactions Management"])


@router.post(
    "/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction_data: TransactionCreateDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new transaction
    """
    service = TransactionService(db)
    try:
        transaction = service.create_transaction(transaction_data, current_user.id)
        resp = TransactionResponse.model_validate(transaction)
        if getattr(transaction, "user_category", None):
            from app.schemas.category_dto import CategoryResponse
            resp.user_category = CategoryResponse.model_validate(transaction.user_category)
        return resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=TransactionListResponse)
def get_transactions(
    filters: TransactionFilterDTO = Depends(),
    category_id: Optional[int] = Query(None, description="User-defined category ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("date"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user's transactions with filtering and pagination
    """
    if category_id:
        filters.category_id = category_id
    service = TransactionService(db)
    return service.get_user_transactions(
        current_user.id, filters, skip, limit, sort_by, sort_order
    )


@router.get("/summary", response_model=TransactionSummaryResponse)
def get_transaction_summary(
    wallet_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
        filters.start_date = date_from
    if date_to:
        filters.end_date = date_to

    service = TransactionService(db)
    return service.get_transaction_summary(current_user.id, filters)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific transaction by ID
    """
    service = TransactionService(db)
    transaction = service.get_transaction_by_id(transaction_id, current_user.id)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Constants.TRANSACTION_NOT_FOUND,
        )

    resp = TransactionResponse.model_validate(transaction)
    if getattr(transaction, "user_category", None):
        from app.schemas.category_dto import CategoryResponse
        resp.user_category = CategoryResponse.model_validate(transaction.user_category)
    return resp


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdateDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a transaction
    """
    service = TransactionService(db)
    try:
        transaction = service.update_transaction(
            transaction_id, update_data, current_user.id
        )
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=Constants.TRANSACTION_NOT_FOUND,
            )
        resp = TransactionResponse.model_validate(transaction)
        if getattr(transaction, "user_category", None):
            from app.schemas.category_dto import CategoryResponse
            resp.user_category = CategoryResponse.model_validate(transaction.user_category)
        return resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
                detail=Constants.TRANSACTION_NOT_FOUND,
            )

        return {"message": "Transaction deleted successfully"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/bulk",
    response_model=List[TransactionResponse],
    status_code=status.HTTP_201_CREATED,
)
def bulk_create_transactions(
    bulk_data: BulkTransactionCreateDTO,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create multiple transactions in bulk
    """
    service = TransactionService(db)
    try:
        transactions = service.bulk_create_transactions(bulk_data, current_user.id)
        return [TransactionResponse.model_validate(t) for t in transactions]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{transaction_id}/files",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_transaction_file(
    transaction_id: int,
    file: UploadFile = FileUpload(...),
    file_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
            detail=f"Invalid file type. Must be one of: {[ft.value for ft in FileType]}",
        )

    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit",
        )

    service = TransactionService(db)

    # Check if transaction exists
    transaction = service.get_transaction_by_id(transaction_id, current_user.id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Constants.TRANSACTION_NOT_FOUND,
        )

    try:
        file_record = service.add_file_to_transaction(
            file, transaction_id, file_type_enum, current_user.id
        )
        return FileResponse.model_validate(file_record)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )


@router.get("/{transaction_id}/files", response_model=List[FileResponse])
def get_transaction_files(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
            detail=Constants.TRANSACTION_NOT_FOUND,
        )

    files = service.get_transaction_files(transaction_id, current_user.id)
    return [FileResponse.model_validate(f, from_attributes=True) for f in files]


@router.delete("/files/{file_id}")
def delete_transaction_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a file attachment
    """
    service = TransactionService(db)
    success = service.delete_file(file_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    return {"message": "File deleted successfully"}


@router.get("/wallet/{wallet_id}", response_model=List[TransactionResponse])
def get_wallet_transactions(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all transactions for a specific wallet
    """
    service = TransactionService(db)
    transactions = service.get_transactions_by_wallet(wallet_id, current_user.id)
    return [TransactionResponse.model_validate(t) for t in transactions]
