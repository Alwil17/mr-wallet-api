from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from app.constants import Constants
from app.db.models.debt import Debt
from app.db.models.wallet import Wallet
from app.schemas.debt_dto import DebtCreateDTO, DebtUpdateDTO, DebtFilterDTO


class DebtRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, debt_data: DebtCreateDTO, user_id: int) -> Debt:
        """
        Create a new debt record

        Args:
            debt_data (DebtCreateDTO): The debt data
            user_id (int): The user ID (for wallet ownership verification)

        Returns:
            Debt: The created debt

        Raises:
            ValueError: If wallet not found or not owned by user
        """
        # Verify wallet ownership
        wallet = (
            self.db.query(Wallet)
            .filter(and_(Wallet.id == debt_data.wallet_id, Wallet.user_id == user_id))
            .first()
        )

        if not wallet:
            raise ValueError("Wallet not found or not owned by user")

        debt = Debt(
            amount=debt_data.amount,
            borrower=debt_data.borrower,
            type=debt_data.type,
            due_date=debt_data.due_date,
            description=debt_data.description,
            wallet_id=debt_data.wallet_id,
        )

        self.db.add(debt)
        self.db.commit()
        self.db.refresh(debt)
        return debt

    def get_by_id(self, debt_id: int) -> Optional[Debt]:
        """Get debt by ID"""
        return self.db.query(Debt).filter(Debt.id == debt_id).first()

    def get_by_id_and_user(self, debt_id: int, user_id: int) -> Optional[Debt]:
        """Get debt by ID and user (through wallet ownership)"""
        return (
            self.db.query(Debt)
            .join(Wallet)
            .filter(and_(Debt.id == debt_id, Wallet.user_id == user_id))
            .first()
        )

    def get_user_debts(
        self,
        user_id: int,
        filters: Optional[DebtFilterDTO] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Debt]:
        """
        Get all debts for a user with optional filtering

        Args:
            user_id (int): The user ID
            filters (DebtFilterDTO): Optional filters
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            List[Debt]: List of debts
        """
        query = self.db.query(Debt).join(Wallet).filter(Wallet.user_id == user_id)

        if filters:
            if filters.debt_type:
                query = query.filter(Debt.type == filters.debt_type)

            if filters.is_paid is not None:
                query = query.filter(Debt.is_paid == filters.is_paid)

            if filters.borrower:
                query = query.filter(Debt.borrower.ilike(f"%{filters.borrower}%"))

            if filters.overdue_only:
                query = query.filter(
                    and_(
                        Debt.due_date < datetime.now(timezone.utc),
                        Debt.is_paid == False,
                    )
                )

            if filters.wallet_id:
                query = query.filter(Debt.wallet_id == filters.wallet_id)

        return query.order_by(Debt.created_at.desc()).offset(skip).limit(limit).all()

    def count_user_debts(
        self, user_id: int, filters: Optional[DebtFilterDTO] = None
    ) -> int:
        """Count total debts for a user with optional filtering"""
        query = self.db.query(Debt).join(Wallet).filter(Wallet.user_id == user_id)

        if filters:
            if filters.debt_type:
                query = query.filter(Debt.type == filters.debt_type)

            if filters.is_paid is not None:
                query = query.filter(Debt.is_paid == filters.is_paid)

            if filters.borrower:
                query = query.filter(Debt.borrower.ilike(f"%{filters.borrower}%"))

            if filters.overdue_only:
                query = query.filter(
                    and_(
                        Debt.due_date < datetime.now(timezone.utc),
                        Debt.is_paid == False,
                    )
                )

            if filters.wallet_id:
                query = query.filter(Debt.wallet_id == filters.wallet_id)

        return query.count()

    def get_wallet_debts(self, wallet_id: int, user_id: int) -> List[Debt]:
        """Get all debts for a specific wallet"""
        # Verify wallet ownership
        wallet = (
            self.db.query(Wallet)
            .filter(and_(Wallet.id == wallet_id, Wallet.user_id == user_id))
            .first()
        )

        if not wallet:
            raise ValueError("Wallet not found or not owned by user")

        return (
            self.db.query(Debt)
            .filter(Debt.wallet_id == wallet_id)
            .order_by(Debt.created_at.desc())
            .all()
        )

    def update(
        self, debt_id: int, debt_data: DebtUpdateDTO, user_id: int
    ) -> Optional[Debt]:
        """
        Update debt information

        Args:
            debt_id (int): The debt ID
            debt_data (DebtUpdateDTO): The update data
            user_id (int): The user ID (for ownership verification)

        Returns:
            Optional[Debt]: The updated debt or None if not found

        Raises:
            ValueError: If debt not found or not owned by user
        """
        debt = self.get_by_id_and_user(debt_id, user_id)
        if not debt:
            raise ValueError(Constants.DEBT_NOT_FOUND)

        # Update fields that are provided
        update_data = debt_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(debt, field, value)

        self.db.commit()
        self.db.refresh(debt)
        return debt

    def mark_as_paid(self, debt_id: int, is_paid: bool, user_id: int) -> Optional[Debt]:
        """Mark debt as paid or unpaid"""
        debt = self.get_by_id_and_user(debt_id, user_id)
        if not debt:
            raise ValueError(Constants.DEBT_NOT_FOUND)

        debt.is_paid = is_paid
        self.db.commit()
        self.db.refresh(debt)
        return debt

    def delete(self, debt_id: int, user_id: int) -> bool:
        """
        Delete a debt

        Args:
            debt_id (int): The debt ID
            user_id (int): The user ID (for ownership verification)

        Returns:
            bool: True if deleted, False if not found

        Raises:
            ValueError: If debt not found or not owned by user
        """
        debt = self.get_by_id_and_user(debt_id, user_id)
        if not debt:
            raise ValueError(Constants.DEBT_NOT_FOUND)

        self.db.delete(debt)
        self.db.commit()
        return True

    def get_user_debt_summary(self, user_id: int) -> dict:
        """
        Get debt summary for a user

        Args:
            user_id (int): The user ID

        Returns:
            dict: Summary statistics
        """
        debts = self.db.query(Debt).join(Wallet).filter(Wallet.user_id == user_id).all()

        total_debts = len(debts)
        total_amount_owed = sum(debt.amount for debt in debts if debt.type == "owed")
        total_amount_given = sum(debt.amount for debt in debts if debt.type == "given")
        net_position = total_amount_owed - total_amount_given

        paid_debts = sum(1 for debt in debts if debt.is_paid)
        unpaid_debts = total_debts - paid_debts

        # Count overdue debts
        now = datetime.now(timezone.utc)
        overdue_debts = sum(
            1
            for debt in debts
            if debt.due_date and debt.due_date < now and not debt.is_paid
        )

        # Group by type
        debts_by_type = {
            "owed": sum(1 for debt in debts if debt.type == "owed"),
            "given": sum(1 for debt in debts if debt.type == "given"),
        }

        return {
            "total_debts": total_debts,
            "total_amount_owed": total_amount_owed,
            "total_amount_given": total_amount_given,
            "net_position": net_position,
            "paid_debts": paid_debts,
            "unpaid_debts": unpaid_debts,
            "overdue_debts": overdue_debts,
            "debts_by_type": debts_by_type,
        }
