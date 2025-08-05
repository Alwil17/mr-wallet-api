from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.debt import Debt
from app.repositories.debt_repository import DebtRepository
from app.schemas.debt_dto import (
    DebtCreateDTO,
    DebtUpdateDTO,
    DebtResponse,
    DebtListResponse,
    DebtSummaryResponse,
    DebtFilterDTO,
    DebtMarkPaidDTO
)

DEBT_NOT_FOUND = "Debt not found"
WALLET_NOT_FOUND = "Wallet not found or not owned by user"


class DebtService:
    def __init__(self, db: Session):
        self.repository = DebtRepository(db)

    def create_debt(self, debt_data: DebtCreateDTO, user_id: int) -> Debt:
        """
        Create a new debt

        Args:
            debt_data (DebtCreateDTO): The debt data
            user_id (int): The user ID

        Returns:
            Debt: The created debt

        Raises:
            ValueError: If wallet not found or invalid data
        """
        try:
            return self.repository.create(debt_data, user_id)
        except ValueError as e:
            raise ValueError(str(e))

    def get_debt_by_id(self, debt_id: int, user_id: int) -> Optional[Debt]:
        """
        Get debt by ID

        Args:
            debt_id (int): The debt ID
            user_id (int): The user ID

        Returns:
            Optional[Debt]: The debt or None if not found/not owned
        """
        return self.repository.get_by_id_and_user(debt_id, user_id)

    def get_user_debts(self, user_id: int, filters: Optional[DebtFilterDTO] = None, 
                      skip: int = 0, limit: int = 100) -> DebtListResponse:
        """
        Get user's debts with optional filtering

        Args:
            user_id (int): The user ID
            filters (DebtFilterDTO): Optional filters
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            DebtListResponse: List of debts with total count
        """
        debts = self.repository.get_user_debts(user_id, filters, skip, limit)
        total = self.repository.count_user_debts(user_id, filters)
        
        debt_responses = [DebtResponse.model_validate(debt) for debt in debts]
        
        return DebtListResponse(
            debts=debt_responses,
            total=total
        )

    def get_wallet_debts(self, wallet_id: int, user_id: int) -> List[DebtResponse]:
        """
        Get all debts for a specific wallet

        Args:
            wallet_id (int): The wallet ID
            user_id (int): The user ID

        Returns:
            List[DebtResponse]: List of debts for the wallet

        Raises:
            ValueError: If wallet not found or not owned by user
        """
        try:
            debts = self.repository.get_wallet_debts(wallet_id, user_id)
            return [DebtResponse.model_validate(debt) for debt in debts]
        except ValueError as e:
            raise ValueError(str(e))

    def update_debt(self, debt_id: int, debt_data: DebtUpdateDTO, user_id: int) -> Optional[Debt]:
        """
        Update debt information

        Args:
            debt_id (int): The debt ID
            debt_data (DebtUpdateDTO): The update data
            user_id (int): The user ID

        Returns:
            Optional[Debt]: The updated debt

        Raises:
            ValueError: If debt not found or not owned by user
        """
        try:
            return self.repository.update(debt_id, debt_data, user_id)
        except ValueError as e:
            raise ValueError(str(e))

    def mark_debt_as_paid(self, debt_id: int, payment_data: DebtMarkPaidDTO, user_id: int) -> Optional[Debt]:
        """
        Mark debt as paid or unpaid

        Args:
            debt_id (int): The debt ID
            payment_data (DebtMarkPaidDTO): Payment status data
            user_id (int): The user ID

        Returns:
            Optional[Debt]: The updated debt

        Raises:
            ValueError: If debt not found or not owned by user
        """
        try:
            return self.repository.mark_as_paid(debt_id, payment_data.is_paid, user_id)
        except ValueError as e:
            raise ValueError(str(e))

    def delete_debt(self, debt_id: int, user_id: int) -> bool:
        """
        Delete a debt

        Args:
            debt_id (int): The debt ID
            user_id (int): The user ID

        Returns:
            bool: True if deleted successfully

        Raises:
            ValueError: If debt not found or not owned by user
        """
        try:
            return self.repository.delete(debt_id, user_id)
        except ValueError as e:
            raise ValueError(str(e))

    def get_debt_summary(self, user_id: int) -> DebtSummaryResponse:
        """
        Get debt summary for a user

        Args:
            user_id (int): The user ID

        Returns:
            DebtSummaryResponse: Summary of user's debts
        """
        summary_data = self.repository.get_user_debt_summary(user_id)
        
        return DebtSummaryResponse(
            total_debts=summary_data["total_debts"],
            total_amount_owed=summary_data["total_amount_owed"],
            total_amount_given=summary_data["total_amount_given"],
            net_position=summary_data["net_position"],
            paid_debts=summary_data["paid_debts"],
            unpaid_debts=summary_data["unpaid_debts"],
            overdue_debts=summary_data["overdue_debts"],
            debts_by_type=summary_data["debts_by_type"]
        )
