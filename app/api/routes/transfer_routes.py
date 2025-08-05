from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.schemas.transfer_dto import (
    TransferCreateDTO,
    TransferResponse,
    TransferListResponse,
    TransferSummaryResponse,
    TransferFilterDTO,
    WalletTransferSummaryDTO
)
from app.schemas.user_dto import UserResponse
from app.services.transfer_service import TransferService
from app.core.security import get_current_user
from app.db.base import get_db

router = APIRouter(prefix="/transfers", tags=["Transfer Management"])

# Constants
TRANSFER_NOT_FOUND = "Transfer not found"


@router.post("/", response_model=TransferResponse, status_code=201)
async def create_transfer(
    transfer_data: TransferCreateDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new transfer between wallets.

    Args:
        transfer_data (TransferCreateDTO): The transfer data
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        TransferResponse: The created transfer

    Raises:
        HTTPException: If wallets not found, invalid data, or insufficient funds
    """
    transfer_service = TransferService(db)
    try:
        transfer = transfer_service.create_transfer(transfer_data, current_user.id)
        response = TransferResponse.model_validate(transfer)
        response.source_wallet_name = transfer.source_wallet.name if transfer.source_wallet else None
        response.target_wallet_name = transfer.target_wallet.name if transfer.target_wallet else None
        return response
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        elif "insufficient funds" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@router.get("/", response_model=TransferListResponse)
async def get_user_transfers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    source_wallet_id: Optional[int] = Query(None, description="Filter by source wallet ID"),
    target_wallet_id: Optional[int] = Query(None, description="Filter by target wallet ID"),
    wallet_id: Optional[int] = Query(None, description="Filter by transfers involving this wallet"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="Minimum transfer amount"),
    max_amount: Optional[Decimal] = Query(None, gt=0, description="Maximum transfer amount"),
    date_from: Optional[datetime] = Query(None, description="Filter transfers from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter transfers to this date"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all transfers for the current user with optional filtering.

    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        source_wallet_id (int): Filter by source wallet ID
        target_wallet_id (int): Filter by target wallet ID
        wallet_id (int): Filter by transfers involving this wallet
        min_amount (Decimal): Minimum transfer amount
        max_amount (Decimal): Maximum transfer amount
        date_from (datetime): Filter transfers from this date
        date_to (datetime): Filter transfers to this date
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        TransferListResponse: List of transfers with total count
    """
    transfer_service = TransferService(db)
    
    # Create filter object
    filters = TransferFilterDTO(
        source_wallet_id=source_wallet_id,
        target_wallet_id=target_wallet_id,
        wallet_id=wallet_id,
        min_amount=min_amount,
        max_amount=max_amount,
        date_from=date_from,
        date_to=date_to
    )
    
    return transfer_service.get_user_transfers(current_user.id, filters, skip, limit)


@router.get("/summary", response_model=TransferSummaryResponse)
async def get_transfer_summary(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transfer summary for the current user.

    Args:
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        TransferSummaryResponse: Summary of user's transfers
    """
    transfer_service = TransferService(db)
    return transfer_service.get_transfer_summary(current_user.id)


@router.get("/wallet/{wallet_id}")
async def get_wallet_transfers(
    wallet_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all transfers for a specific wallet.

    Args:
        wallet_id (int): The wallet ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        List[TransferResponse]: List of transfers for the wallet

    Raises:
        HTTPException: If wallet not found or not owned by user
    """
    transfer_service = TransferService(db)
    try:
        return transfer_service.get_wallet_transfers(wallet_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/wallet/{wallet_id}/summary", response_model=WalletTransferSummaryDTO)
async def get_wallet_transfer_summary(
    wallet_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transfer summary for a specific wallet.

    Args:
        wallet_id (int): The wallet ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        WalletTransferSummaryDTO: Transfer summary for the wallet

    Raises:
        HTTPException: If wallet not found or not owned by user
    """
    transfer_service = TransferService(db)
    try:
        return transfer_service.get_wallet_transfer_summary(wallet_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(
    transfer_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific transfer by ID.

    Args:
        transfer_id (int): The transfer ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        TransferResponse: The transfer data

    Raises:
        HTTPException: If transfer not found or not owned by user
    """
    transfer_service = TransferService(db)
    transfer = transfer_service.get_transfer_by_id(transfer_id, current_user.id)
    
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=TRANSFER_NOT_FOUND
        )
    
    response = TransferResponse.model_validate(transfer)
    response.source_wallet_name = transfer.source_wallet.name if transfer.source_wallet else None
    response.target_wallet_name = transfer.target_wallet.name if transfer.target_wallet else None
    return response


@router.delete("/{transfer_id}")
async def delete_transfer(
    transfer_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a transfer record and reverse the balance changes.

    Args:
        transfer_id (int): The transfer ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If transfer not found, not owned by user, or cannot be reversed
    """
    transfer_service = TransferService(db)
    try:
        transfer_service.delete_transfer(transfer_id, current_user.id)
        return {"message": "Transfer deleted successfully and wallet balances have been reversed"}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


# Alternative endpoint for creating transfers via wallets
@router.post("/wallets/{source_wallet_id}/transfer", response_model=TransferResponse, status_code=201)
async def create_wallet_transfer(
    source_wallet_id: int,
    target_wallet_id: int = Query(..., description="ID of the target wallet"),
    amount: Decimal = Query(..., gt=0, description="Transfer amount"),
    description: Optional[str] = Query(None, description="Optional description"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a transfer from a specific wallet (alternative endpoint).

    Args:
        source_wallet_id (int): The source wallet ID (from URL path)
        target_wallet_id (int): The target wallet ID (from query parameter)
        amount (Decimal): Transfer amount
        description (str): Optional description
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        TransferResponse: The created transfer

    Raises:
        HTTPException: If wallets not found, invalid data, or insufficient funds
    """
    transfer_data = TransferCreateDTO(
        amount=amount,
        source_wallet_id=source_wallet_id,
        target_wallet_id=target_wallet_id,
        description=description
    )
    
    transfer_service = TransferService(db)
    try:
        transfer = transfer_service.create_transfer(transfer_data, current_user.id)
        response = TransferResponse.model_validate(transfer)
        response.source_wallet_name = transfer.source_wallet.name if transfer.source_wallet else None
        response.target_wallet_name = transfer.target_wallet.name if transfer.target_wallet else None
        return response
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        elif "insufficient funds" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
