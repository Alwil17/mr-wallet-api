from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.constants import Constants
from app.schemas.debt_dto import (
    DebtCreateDTO,
    DebtUpdateDTO,
    DebtResponse,
    DebtListResponse,
    DebtSummaryResponse,
    DebtFilterDTO,
    DebtMarkPaidDTO
)
from app.schemas.user_dto import UserResponse
from app.services.debt_service import DebtService
from app.core.security import get_current_user
from app.db.base import get_db

router = APIRouter(prefix="/debts", tags=["Debt Management"])

# Constants
DEBT_NOT_FOUND = "Debt not found"


@router.post("/", response_model=DebtResponse, status_code=201)
async def create_debt(
    debt_data: DebtCreateDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new debt record.

    Args:
        debt_data (DebtCreateDTO): The debt data
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        DebtResponse: The created debt

    Raises:
        HTTPException: If wallet not found or invalid data
    """
    debt_service = DebtService(db)
    try:
        debt = debt_service.create_debt(debt_data, current_user.id)
        return DebtResponse.model_validate(debt)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=DebtListResponse)
async def get_user_debts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    debt_type: Optional[str] = Query(None, pattern=Constants.TRANSACTION_TYPE_REGEX, description="Filter by debt type"),
    is_paid: Optional[bool] = Query(None, description="Filter by payment status"),
    borrower: Optional[str] = Query(None, description="Filter by borrower name"),
    overdue_only: Optional[bool] = Query(False, description="Show only overdue debts"),
    wallet_id: Optional[int] = Query(None, description="Filter by wallet ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all debts for the current user with optional filtering.

    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        debt_type (str): Filter by debt type
        is_paid (bool): Filter by payment status
        borrower (str): Filter by borrower name
        overdue_only (bool): Show only overdue debts
        wallet_id (int): Filter by wallet ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        DebtListResponse: List of debts with total count
    """
    debt_service = DebtService(db)
    
    # Create filter object
    filters = DebtFilterDTO(
        debt_type=debt_type,
        is_paid=is_paid,
        borrower=borrower,
        overdue_only=overdue_only,
        wallet_id=wallet_id
    )
    
    return debt_service.get_user_debts(current_user.id, filters, skip, limit)


@router.get("/summary", response_model=DebtSummaryResponse)
async def get_debt_summary(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get debt summary for the current user.

    Args:
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        DebtSummaryResponse: Summary of user's debts
    """
    debt_service = DebtService(db)
    return debt_service.get_debt_summary(current_user.id)


@router.get("/wallet/{wallet_id}")
async def get_wallet_debts(
    wallet_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all debts for a specific wallet.

    Args:
        wallet_id (int): The wallet ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        List[DebtResponse]: List of debts for the wallet

    Raises:
        HTTPException: If wallet not found or not owned by user
    """
    debt_service = DebtService(db)
    try:
        return debt_service.get_wallet_debts(wallet_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{debt_id}", response_model=DebtResponse)
async def get_debt(
    debt_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific debt by ID.

    Args:
        debt_id (int): The debt ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        DebtResponse: The debt data

    Raises:
        HTTPException: If debt not found or not owned by user
    """
    debt_service = DebtService(db)
    debt = debt_service.get_debt_by_id(debt_id, current_user.id)
    
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DEBT_NOT_FOUND
        )
    
    return DebtResponse.model_validate(debt)


@router.put("/{debt_id}", response_model=DebtResponse)
async def update_debt(
    debt_id: int,
    debt_data: DebtUpdateDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update debt information.

    Args:
        debt_id (int): The debt ID
        debt_data (DebtUpdateDTO): The update data
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        DebtResponse: The updated debt

    Raises:
        HTTPException: If debt not found or not owned by user
    """
    debt_service = DebtService(db)
    try:
        debt = debt_service.update_debt(debt_id, debt_data, current_user.id)
        return DebtResponse.model_validate(debt)
    except ValueError as e:
        if Constants.NOT_FOUND in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@router.patch("/{debt_id}/payment", response_model=DebtResponse)
async def mark_debt_payment(
    debt_id: int,
    payment_data: DebtMarkPaidDTO,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark debt as paid or unpaid.

    Args:
        debt_id (int): The debt ID
        payment_data (DebtMarkPaidDTO): Payment status data
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        DebtResponse: The updated debt

    Raises:
        HTTPException: If debt not found or not owned by user
    """
    debt_service = DebtService(db)
    try:
        debt = debt_service.mark_debt_as_paid(debt_id, payment_data, current_user.id)
        return DebtResponse.model_validate(debt)
    except ValueError as e:
        if Constants.NOT_FOUND in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@router.delete("/{debt_id}")
async def delete_debt(
    debt_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a debt record.

    Args:
        debt_id (int): The debt ID
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If debt not found or not owned by user
    """
    debt_service = DebtService(db)
    try:
        debt_service.delete_debt(debt_id, current_user.id)
        return {"message": "Debt deleted successfully"}
    except ValueError as e:
        if Constants.NOT_FOUND in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
