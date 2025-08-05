from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.constants import Constants
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.file_repository import FileRepository
from app.repositories.wallet_repository import WalletRepository
from app.db.models.transaction import Transaction
from app.db.models.file import File, FileType
from app.schemas.transaction_dto import (
    TransactionCreateDTO,
    TransactionUpdateDTO,
    TransactionFilterDTO,
    TransactionListResponse,
    TransactionSummaryResponse,
    BulkTransactionCreateDTO,
)


class TransactionService:
    def __init__(self, db_session: Session):
        """
        Constructor for TransactionService

        Args:
            db_session (Session): The database session
        """
        self.transaction_repository = TransactionRepository(db_session)
        self.file_repository = FileRepository(db_session)
        self.wallet_repository = WalletRepository(db_session)
        self.db = db_session

    def create_transaction(
        self, transaction_data: TransactionCreateDTO, user_id: int
    ) -> Transaction:
        """
        Create a new transaction and update wallet balance

        Args:
            transaction_data (TransactionCreateDTO): The transaction data
            user_id (int): The user ID

        Returns:
            Transaction: The created transaction

        Raises:
            ValueError: If wallet not found or insufficient funds
        """
        # Create the transaction
        transaction = self.transaction_repository.create(transaction_data, user_id)

        # Update wallet balance based on transaction type
        try:
            wallet = self.wallet_repository.get_by_id_and_user(
                transaction_data.wallet_id, user_id
            )
            if not wallet:
                raise ValueError(Constants.WALLET_NOT_FOUND)

            if transaction_data.type.value == "income":
                # Add to wallet balance for income
                new_balance = wallet.balance + transaction_data.amount
            else:
                # Subtract from wallet balance for expense
                new_balance = wallet.balance - transaction_data.amount

                # Check for sufficient funds (except for credit wallets)
                if wallet.type != "credit" and new_balance < 0:
                    # Rollback transaction creation
                    self.db.delete(transaction)
                    raise ValueError("Insufficient funds in wallet")

            # Update wallet balance
            wallet.balance = new_balance
            self.db.commit()

        except Exception as e:
            # Rollback transaction if wallet update fails
            self.db.rollback()
            raise e

        return transaction

    def get_transaction_by_id(
        self, transaction_id: int, user_id: int
    ) -> Optional[Transaction]:
        """
        Get a transaction by ID

        Args:
            transaction_id (int): The transaction ID
            user_id (int): The user ID

        Returns:
            Optional[Transaction]: The transaction or None if not found
        """
        return self.transaction_repository.get_by_id(transaction_id, user_id)

    def get_user_transactions(
        self,
        user_id: int,
        filters: TransactionFilterDTO = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "date",
        sort_order: str = "desc",
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
        return self.transaction_repository.get_user_transactions(
            user_id, filters, skip, limit, sort_by, sort_order
        )

    def update_transaction(
        self, transaction_id: int, update_data: TransactionUpdateDTO, user_id: int
    ) -> Optional[Transaction]:
        """
        Update a transaction and adjust wallet balance

        Args:
            transaction_id (int): The transaction ID
            update_data (TransactionUpdateDTO): The update data
            user_id (int): The user ID

        Returns:
            Optional[Transaction]: The updated transaction or None if not found

        Raises:
            ValueError: If insufficient funds after update
        """
        # Get the original transaction
        original_transaction = self.transaction_repository.get_by_id(
            transaction_id, user_id
        )
        if not original_transaction:
            return None

        # Get the wallet
        wallet = self.wallet_repository.get_by_id_and_user(
            original_transaction.wallet_id, user_id
        )
        if not wallet:
            raise ValueError("Wallet not found")

        try:
            # Calculate balance adjustment
            original_amount = original_transaction.amount
            original_type = original_transaction.type

            # Revert original transaction effect on wallet balance
            if original_type.value == "income":
                wallet.balance -= original_amount
            else:
                wallet.balance += original_amount

            # Update the transaction
            updated_transaction = self.transaction_repository.update(
                transaction_id, update_data, user_id
            )

            # Apply new transaction effect on wallet balance
            new_amount = updated_transaction.amount
            new_type = updated_transaction.type

            if new_type.value == "income":
                wallet.balance += new_amount
            else:
                wallet.balance -= new_amount

                # Check for sufficient funds (except for credit wallets)
                if wallet.type != "credit" and wallet.balance < 0:
                    raise ValueError("Insufficient funds in wallet after update")

            self.db.commit()
            return updated_transaction

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """
        Delete a transaction and adjust wallet balance

        Args:
            transaction_id (int): The transaction ID
            user_id (int): The user ID

        Returns:
            bool: True if deleted, False if not found
        """
        # Get the transaction
        transaction = self.transaction_repository.get_by_id(transaction_id, user_id)
        if not transaction:
            return False

        # Get the wallet
        wallet = self.wallet_repository.get_by_id_and_user(
            transaction.wallet_id, user_id
        )
        if not wallet:
            raise ValueError("Wallet not found")

        try:
            # Revert transaction effect on wallet balance
            if transaction.type.value == "income":
                wallet.balance -= transaction.amount
            else:
                wallet.balance += transaction.amount

            # Delete the transaction (files will be cascade deleted)
            success = self.transaction_repository.delete(transaction_id, user_id)

            if success:
                self.db.commit()
            else:
                self.db.rollback()

            return success

        except Exception as e:
            self.db.rollback()
            raise e

    def get_transaction_summary(
        self, user_id: int, filters: TransactionFilterDTO = None
    ) -> TransactionSummaryResponse:
        """
        Get transaction summary statistics

        Args:
            user_id (int): The user ID
            filters (TransactionFilterDTO): Optional filters

        Returns:
            TransactionSummaryResponse: Summary statistics
        """
        return self.transaction_repository.get_transaction_summary(user_id, filters)

    def bulk_create_transactions(
        self, bulk_data: BulkTransactionCreateDTO, user_id: int
    ) -> List[Transaction]:
        """
        Create multiple transactions in bulk

        Args:
            bulk_data (BulkTransactionCreateDTO): Bulk transaction data
            user_id (int): The user ID

        Returns:
            List[Transaction]: List of created transactions

        Raises:
            ValueError: If any validation fails
        """
        try:
            self._validate_bulk_transactions(bulk_data.transactions, user_id)
            created_transactions = self.transaction_repository.bulk_create(
                bulk_data.transactions, user_id
            )
            self._apply_bulk_wallet_balance_changes(created_transactions, user_id)
            self.db.commit()
            return created_transactions

        except Exception as e:
            self.db.rollback()
            raise e

    def _validate_bulk_transactions(self, transactions, user_id: int):
        """
        Validate wallets and balances for bulk transactions.
        """
        for transaction_data in transactions:
            wallet = self.wallet_repository.get_by_id_and_user(
                transaction_data.wallet_id, user_id
            )
            if not wallet:
                raise ValueError(f"Wallet {transaction_data.wallet_id} not found")
            if transaction_data.type.value == "expense":
                if wallet.type != "credit" and wallet.balance < transaction_data.amount:
                    raise ValueError(f"Insufficient funds in wallet {wallet.name}")

    def _apply_bulk_wallet_balance_changes(
        self, created_transactions: List[Transaction], user_id: int
    ):
        """
        Apply wallet balance changes for bulk created transactions.
        """
        wallet_balance_changes = {}
        for transaction in created_transactions:
            wallet_id = transaction.wallet_id
            if wallet_id not in wallet_balance_changes:
                wallet_balance_changes[wallet_id] = Decimal("0")
            if transaction.type.value == "income":
                wallet_balance_changes[wallet_id] += transaction.amount
            else:
                wallet_balance_changes[wallet_id] -= transaction.amount

        for wallet_id, balance_change in wallet_balance_changes.items():
            wallet = self.wallet_repository.get_by_id_and_user(wallet_id, user_id)
            wallet.balance += balance_change

    def add_file_to_transaction(
        self, file: UploadFile, transaction_id: int, file_type: FileType, user_id: int
    ) -> File:
        """
        Add a file attachment to a transaction

        Args:
            file (UploadFile): The uploaded file
            transaction_id (int): The transaction ID
            file_type (FileType): The file type
            user_id (int): The user ID

        Returns:
            File: The created file record
        """
        return self.file_repository.create(file, transaction_id, file_type, user_id)

    def get_transaction_files(self, transaction_id: int, user_id: int) -> List[File]:
        """
        Get all files for a transaction

        Args:
            transaction_id (int): The transaction ID
            user_id (int): The user ID

        Returns:
            List[File]: List of files
        """
        return self.file_repository.get_transaction_files(transaction_id, user_id)

    def delete_file(self, file_id: int, user_id: int) -> bool:
        """
        Delete a file attachment

        Args:
            file_id (int): The file ID
            user_id (int): The user ID

        Returns:
            bool: True if deleted, False if not found
        """
        return self.file_repository.delete(file_id, user_id)

    def get_transactions_by_wallet(
        self, wallet_id: int, user_id: int
    ) -> List[Transaction]:
        """
        Get all transactions for a specific wallet

        Args:
            wallet_id (int): The wallet ID
            user_id (int): The user ID

        Returns:
            List[Transaction]: List of transactions
        """
        return self.transaction_repository.get_transactions_by_wallet(
            wallet_id, user_id
        )
