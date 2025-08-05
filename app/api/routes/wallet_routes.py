from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.wallet_dto import (
    WalletCreateDTO,
    WalletUpdateDTO,
    WalletResponse,
    WalletListResponse,
    WalletBalanceUpdateDTO,
    WalletSummaryResponse,
    AmountDTO
)
from app.schemas.user_dto import UserResponse
from app.services.wallet_service import WalletService
from app.core.security import get_current_user
from app.db.base import get_db

router = APIRouter(prefix="/wallets", tags=["Wallet Management"])

# Constants
WALLET_NOT_FOUND = "Wallet not found"


@router.post("/", response_model=WalletResponse, status_code=201)
async def create_wallet(
    wallet_data: WalletCreateDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new wallet for the current user.

    Args:
        wallet_data (WalletCreateDTO): The wallet data
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        WalletResponse: The created wallet

    Raises:
        HTTPException: If creation fails
    """
    wallet_service = WalletService(db)
    try:
        wallet = wallet_service.create_wallet(wallet_data, current_user.id)
        return WalletResponse.model_validate(wallet)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=WalletListResponse)
async def get_user_wallets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all wallets for the current user.

    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        WalletListResponse: List of user's wallets with total count
    """
    wallet_service = WalletService(db)
    return wallet_service.get_user_wallets(current_user.id, skip, limit)


@router.get("/summary", response_model=WalletSummaryResponse)
async def get_wallet_summary(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get wallet summary for the current user.

    Args:
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        WalletSummaryResponse: Summary of user's wallets
    """
    wallet_service = WalletService(db)
    return wallet_service.get_wallet_summary(current_user.id)


@router.get("/type/{wallet_type}")
async def get_wallets_by_type(
    wallet_type: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all wallets of a specific type for the current user.

    Args:
        wallet_type (str): The wallet type to filter by
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        List[WalletResponse]: List of wallets of the specified type
    """
    wallet_service = WalletService(db)
    return wallet_service.get_wallets_by_type(current_user.id, wallet_type)


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific wallet by ID.

    Args:
        wallet_id (int): The wallet ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        WalletResponse: The wallet data

    Raises:
        HTTPException: If wallet not found or not owned by user
    """
    wallet_service = WalletService(db)
    wallet = wallet_service.get_wallet_by_id(wallet_id, current_user.id)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=WALLET_NOT_FOUND
        )
    
    return WalletResponse.model_validate(wallet)


@router.put("/{wallet_id}", response_model=WalletResponse)
async def update_wallet(
    wallet_id: int,
    wallet_data: WalletUpdateDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a wallet.

    Args:
        wallet_id (int): The wallet ID
        wallet_data (WalletUpdateDTO): The update data
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        WalletResponse: The updated wallet

    Raises:
        HTTPException: If wallet not found or not owned by user
    """
    wallet_service = WalletService(db)
    try:
        wallet = wallet_service.update_wallet(wallet_id, wallet_data, current_user.id)
        return WalletResponse.model_validate(wallet)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/{wallet_id}/balance", response_model=WalletResponse)
async def update_wallet_balance(
    wallet_id: int,
    balance_update: WalletBalanceUpdateDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update wallet balance.

    Args:
        wallet_id (int): The wallet ID
        balance_update (WalletBalanceUpdateDTO): The balance update data
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        WalletResponse: The updated wallet

    Raises:
        HTTPException: If wallet not found, not owned by user, or invalid operation
    """
    wallet_service = WalletService(db)
    try:
        wallet = wallet_service.update_wallet_balance(wallet_id, balance_update, current_user.id)
        return WalletResponse.model_validate(wallet)
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


@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a wallet.

    Args:
        wallet_id (int): The wallet ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If wallet not found or not owned by user
    """
    wallet_service = WalletService(db)
    try:
        wallet_service.delete_wallet(wallet_id, current_user.id)
        return {"message": "Wallet deleted successfully"}
    except ValueError as e:
        if "balance must be zero" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )


@router.post("/{wallet_id}/credit", response_model=WalletResponse)
async def credit_wallet(
    wallet_id: int,
    credit_data: AmountDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Credit amount to wallet.

    Args:
        wallet_id (int): The wallet ID
        credit_data (AmountDTO): The credit amount data
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        WalletResponse: The updated wallet

    Raises:
        HTTPException: If wallet not found or not owned by user
    """
    wallet_service = WalletService(db)
    try:
        # Create credit operation (positive amount)
        balance_update = WalletBalanceUpdateDTO(
            operation="add",
            amount=credit_data.amount
        )
        wallet = wallet_service.update_wallet_balance(wallet_id, balance_update, current_user.id)
        return WalletResponse.model_validate(wallet)
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


@router.post("/{wallet_id}/debit", response_model=WalletResponse)
async def debit_wallet(
    wallet_id: int,
    debit_data: AmountDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Debit amount from wallet.

    Args:
        wallet_id (int): The wallet ID
        debit_data (AmountDTO): The debit amount data
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        WalletResponse: The updated wallet

    Raises:
        HTTPException: If wallet not found, not owned by user, or insufficient funds
    """
    wallet_service = WalletService(db)
    try:
        # Create debit operation (negative amount)
        balance_update = WalletBalanceUpdateDTO(
            operation="subtract",
            amount=debit_data.amount
        )
        wallet = wallet_service.update_wallet_balance(wallet_id, balance_update, current_user.id)
        return WalletResponse.model_validate(wallet)
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


@router.get("/{wallet_id}/balance")
async def get_wallet_balance(
    wallet_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get wallet balance.

    Args:
        wallet_id (int): The wallet ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        dict: Wallet balance and name

    Raises:
        HTTPException: If wallet not found or not owned by user
    """
    wallet_service = WalletService(db)
    try:
        wallet = wallet_service.get_wallet_by_id(wallet_id, current_user.id)
        return {
            "balance": str(wallet.balance),
            "wallet_name": wallet.name
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
