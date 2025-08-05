from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from decimal import Decimal

from app.db.models.transaction import Transaction, TransactionType, TransactionCategory
from app.db.models.wallet import Wallet
from app.schemas.transaction_dto import (
    TransactionCreateDTO, 
    TransactionUpdateDTO, 
    TransactionFilterDTO,
    TransactionListResponse,
    TransactionSummaryResponse,
    TransactionStatsResponse
)


class TransactionRepository:
    def __init__(self, db: Session):
        """
        Constructor for TransactionRepository

        Args:
            db (Session): The database session
        """
        self.db = db

    def create(self, transaction_data: TransactionCreateDTO, user_id: int) -> Transaction:
        """
        Create a new transaction

        Args:
            transaction_data (TransactionCreateDTO): The transaction data
            user_id (int): The user ID (for ownership verification)

        Returns:
            Transaction: The created transaction
            
        Raises:
            ValueError: If wallet not found or not owned by user
        """
        # Verify wallet ownership
        wallet = self.db.query(Wallet).filter(
            and_(Wallet.id == transaction_data.wallet_id, Wallet.user_id == user_id)
        ).first()
        
        if not wallet:
            raise ValueError("Wallet not found or not owned by user")

        transaction = Transaction(
            type=transaction_data.type,
            amount=transaction_data.amount,
            category=transaction_data.category,
            note=transaction_data.note,
            date=transaction_data.date or datetime.now(),
            wallet_id=transaction_data.wallet_id
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_by_id(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """
        Get a transaction by ID with user ownership verification

        Args:
            transaction_id (int): The transaction ID
            user_id (int): The user ID

        Returns:
            Optional[Transaction]: The transaction or None if not found
        """
        return self.db.query(Transaction).join(Wallet).filter(
            and_(
                Transaction.id == transaction_id,
                Wallet.user_id == user_id
            )
        ).options(joinedload(Transaction.files)).first()

    def get_user_transactions(
        self, 
        user_id: int, 
        filters: TransactionFilterDTO = None,
        skip: int = 0, 
        limit: int = 100,
        sort_by: str = "date",
        sort_order: str = "desc"
    ) -> TransactionListResponse:
        """
        Get user's transactions with filtering and pagination

        Args:
            user_id (int): The user ID
            filters (TransactionFilterDTO): Filtering options
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            sort_by (str): Field to sort by
            sort_order (str): Sort order (asc/desc)

        Returns:
            TransactionListResponse: Paginated transactions
        """
        query = self.db.query(Transaction).join(Wallet).filter(Wallet.user_id == user_id)

        # Apply filters
        if filters:
            if filters.wallet_id:
                query = query.filter(Transaction.wallet_id == filters.wallet_id)
            if filters.type:
                query = query.filter(Transaction.type == filters.type)
            if filters.category:
                query = query.filter(Transaction.category == filters.category)
            if filters.start_date:
                query = query.filter(Transaction.date >= filters.start_date)
            if filters.end_date:
                query = query.filter(Transaction.date <= filters.end_date)
            if filters.min_amount:
                query = query.filter(Transaction.amount >= filters.min_amount)
            if filters.max_amount:
                query = query.filter(Transaction.amount <= filters.max_amount)
            if filters.search:
                query = query.filter(Transaction.note.ilike(f"%{filters.search}%"))

        # Apply sorting
        if sort_order.lower() == "desc":
            query = query.order_by(desc(getattr(Transaction, sort_by)))
        else:
            query = query.order_by(asc(getattr(Transaction, sort_by)))

        # Get total count
        total = query.count()

        # Apply pagination
        transactions = query.options(joinedload(Transaction.files)).offset(skip).limit(limit).all()

        # Calculate pagination info
        total_pages = (total + limit - 1) // limit
        current_page = (skip // limit) + 1

        return TransactionListResponse(
            transactions=transactions,
            total=total,
            page=current_page,
            size=limit,
            total_pages=total_pages
        )

    def update(self, transaction_id: int, update_data: TransactionUpdateDTO, user_id: int) -> Optional[Transaction]:
        """
        Update a transaction

        Args:
            transaction_id (int): The transaction ID
            update_data (TransactionUpdateDTO): The update data
            user_id (int): The user ID

        Returns:
            Optional[Transaction]: The updated transaction or None if not found
        """
        transaction = self.get_by_id(transaction_id, user_id)
        if not transaction:
            return None

        # Update fields that are provided
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(transaction, key, value)

        transaction.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete(self, transaction_id: int, user_id: int) -> bool:
        """
        Delete a transaction

        Args:
            transaction_id (int): The transaction ID
            user_id (int): The user ID

        Returns:
            bool: True if deleted, False if not found
        """
        transaction = self.get_by_id(transaction_id, user_id)
        if not transaction:
            return False

        self.db.delete(transaction)
        self.db.commit()
        return True

    def get_transaction_summary(self, user_id: int, filters: TransactionFilterDTO = None) -> TransactionSummaryResponse:
        """
        Get transaction summary statistics

        Args:
            user_id (int): The user ID
            filters (TransactionFilterDTO): Optional filters

        Returns:
            TransactionSummaryResponse: Summary statistics
        """
        query = self.db.query(Transaction).join(Wallet).filter(Wallet.user_id == user_id)

        # Apply filters
        if filters:
            if filters.wallet_id:
                query = query.filter(Transaction.wallet_id == filters.wallet_id)
            if filters.start_date:
                query = query.filter(Transaction.date >= filters.start_date)
            if filters.end_date:
                query = query.filter(Transaction.date <= filters.end_date)

        transactions = query.all()

        # Calculate summary
        total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        net_amount = total_income - total_expenses

        # Group by category
        category_stats = {}
        for transaction in transactions:
            category = transaction.category.value
            if category not in category_stats:
                category_stats[category] = {"count": 0, "total": Decimal("0")}
            category_stats[category]["count"] += 1
            category_stats[category]["total"] += transaction.amount

        # Group by type
        type_stats = {
            TransactionType.INCOME.value: {
                "count": len([t for t in transactions if t.type == TransactionType.INCOME]),
                "total": total_income
            },
            TransactionType.EXPENSE.value: {
                "count": len([t for t in transactions if t.type == TransactionType.EXPENSE]),
                "total": total_expenses
            }
        }

        return TransactionSummaryResponse(
            total_transactions=len(transactions),
            total_income=total_income,
            total_expenses=total_expenses,
            net_amount=net_amount,
            transactions_by_category=category_stats,
            transactions_by_type=type_stats
        )

    def bulk_create(self, transactions_data: List[TransactionCreateDTO], user_id: int) -> List[Transaction]:
        """
        Create multiple transactions in bulk

        Args:
            transactions_data (List[TransactionCreateDTO]): List of transaction data
            user_id (int): The user ID

        Returns:
            List[Transaction]: List of created transactions
            
        Raises:
            ValueError: If any wallet not found or not owned by user
        """
        # Verify all wallets exist and are owned by user
        wallet_ids = [t.wallet_id for t in transactions_data]
        wallets = self.db.query(Wallet).filter(
            and_(Wallet.id.in_(wallet_ids), Wallet.user_id == user_id)
        ).all()
        
        wallet_id_set = {w.id for w in wallets}
        for transaction_data in transactions_data:
            if transaction_data.wallet_id not in wallet_id_set:
                raise ValueError(f"Wallet {transaction_data.wallet_id} not found or not owned by user")

        # Create transactions
        transactions = []
        for transaction_data in transactions_data:
            transaction = Transaction(
                type=transaction_data.type,
                amount=transaction_data.amount,
                category=transaction_data.category,
                note=transaction_data.note,
                date=transaction_data.date or datetime.now(),
                wallet_id=transaction_data.wallet_id
            )
            transactions.append(transaction)
            self.db.add(transaction)

        self.db.commit()
        for transaction in transactions:
            self.db.refresh(transaction)
        
        return transactions

    def get_transactions_by_wallet(self, wallet_id: int, user_id: int) -> List[Transaction]:
        """
        Get all transactions for a specific wallet

        Args:
            wallet_id (int): The wallet ID
            user_id (int): The user ID

        Returns:
            List[Transaction]: List of transactions
        """
        return self.db.query(Transaction).join(Wallet).filter(
            and_(
                Transaction.wallet_id == wallet_id,
                Wallet.user_id == user_id
            )
        ).options(joinedload(Transaction.files)).order_by(desc(Transaction.date)).all()
