from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.db.models.wallet import Wallet
from app.repositories.wallet_repository import WalletRepository
from app.schemas.wallet_dto import (
    WalletCreateDTO,
    WalletUpdateDTO,
    WalletResponse,
    WalletListResponse,
    WalletBalanceUpdateDTO,
    WalletSummaryResponse
)

WALLET_NOT_FOUND = "Wallet not found"
INSUFFICIENT_BALANCE = "Insufficient balance for this operation"
INVALID_OPERATION = "Invalid balance operation"


class WalletService:
    def __init__(self, db_session: Session):
        """
        Constructor for WalletService

        Args:
            db_session (Session): The database session
        """
        self.repository = WalletRepository(db_session)

    def create_wallet(self, wallet_data: WalletCreateDTO, user_id: int) -> Wallet:
        """
        Create a new wallet for a user

        Args:
            wallet_data (WalletCreateDTO): The wallet data
            user_id (int): The user ID

        Returns:
            Wallet: The created wallet
        """
        return self.repository.create(wallet_data, user_id)

    def get_wallet_by_id(self, wallet_id: int, user_id: int) -> Optional[Wallet]:
        """
        Get a wallet by ID (with user ownership verification)

        Args:
            wallet_id (int): The wallet ID
            user_id (int): The user ID

        Returns:
            Optional[Wallet]: The wallet if found and owned by user
        """
        return self.repository.get_by_id_and_user(wallet_id, user_id)

    def get_user_wallets(self, user_id: int, skip: int = 0, limit: int = 100) -> WalletListResponse:
        """
        Get all wallets for a user

        Args:
            user_id (int): The user ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            WalletListResponse: List of wallets with total count
        """
        wallets = self.repository.get_user_wallets(user_id, skip, limit)
        total = self.repository.count_user_wallets(user_id)
        
        wallet_responses = [WalletResponse.model_validate(wallet) for wallet in wallets]
        
        return WalletListResponse(
            wallets=wallet_responses,
            total=total
        )

    def update_wallet(self, wallet_id: int, wallet_data: WalletUpdateDTO, user_id: int) -> Optional[Wallet]:
        """
        Update a wallet (with user ownership verification)

        Args:
            wallet_id (int): The wallet ID
            wallet_data (WalletUpdateDTO): The update data
            user_id (int): The user ID

        Returns:
            Optional[Wallet]: The updated wallet if found and owned by user

        Raises:
            ValueError: If wallet not found or not owned by user
        """
        # Verify ownership
        wallet = self.repository.get_by_id_and_user(wallet_id, user_id)
        if not wallet:
            raise ValueError(WALLET_NOT_FOUND)

        return self.repository.update(wallet_id, wallet_data)

    def update_wallet_balance(self, wallet_id: int, balance_update: WalletBalanceUpdateDTO, user_id: int) -> Optional[Wallet]:
        """
        Update wallet balance

        Args:
            wallet_id (int): The wallet ID
            balance_update (WalletBalanceUpdateDTO): The balance update data
            user_id (int): The user ID

        Returns:
            Optional[Wallet]: The updated wallet

        Raises:
            ValueError: If wallet not found, not owned by user, or invalid operation
        """
        # Verify ownership
        wallet = self.repository.get_by_id_and_user(wallet_id, user_id)
        if not wallet:
            raise ValueError(WALLET_NOT_FOUND)

        current_balance = wallet.balance

        # Calculate new balance based on operation
        if balance_update.operation == "add":
            new_balance = current_balance + balance_update.amount
        elif balance_update.operation == "subtract":
            new_balance = current_balance - balance_update.amount
            if new_balance < 0:
                raise ValueError(INSUFFICIENT_BALANCE)
        elif balance_update.operation == "set":
            new_balance = balance_update.amount
            if new_balance < 0:
                raise ValueError("Balance cannot be negative")
        else:
            raise ValueError(INVALID_OPERATION)

        return self.repository.update_balance(wallet_id, new_balance)

    def delete_wallet(self, wallet_id: int, user_id: int) -> bool:
        """
        Delete a wallet (with user ownership verification)

        Args:
            wallet_id (int): The wallet ID
            user_id (int): The user ID

        Returns:
            bool: True if wallet was deleted

        Raises:
            ValueError: If wallet not found or not owned by user
        """
        # Verify ownership
        wallet = self.repository.get_by_id_and_user(wallet_id, user_id)
        if not wallet:
            raise ValueError(WALLET_NOT_FOUND)

        return self.repository.delete(wallet_id)

    def get_wallet_summary(self, user_id: int) -> WalletSummaryResponse:
        """
        Get wallet summary for a user

        Args:
            user_id (int): The user ID

        Returns:
            WalletSummaryResponse: Summary of user's wallets
        """
        summary_data = self.repository.get_user_wallet_summary(user_id)
        
        most_recent_wallet = None
        if summary_data["most_recent_wallet"]:
            most_recent_wallet = WalletResponse.model_validate(summary_data["most_recent_wallet"])

        return WalletSummaryResponse(
            total_wallets=summary_data["total_wallets"],
            total_balance=summary_data["total_balance"],
            wallets_by_type=summary_data["wallets_by_type"],
            most_recent_wallet=most_recent_wallet
        )

    def get_wallets_by_type(self, user_id: int, wallet_type: str) -> List[WalletResponse]:
        """
        Get all wallets of a specific type for a user

        Args:
            user_id (int): The user ID
            wallet_type (str): The wallet type to filter by

        Returns:
            List[WalletResponse]: List of wallets of the specified type
        """
        all_wallets = self.repository.get_user_wallets(user_id)
        filtered_wallets = [wallet for wallet in all_wallets if wallet.type == wallet_type]
        
        return [WalletResponse.model_validate(wallet) for wallet in filtered_wallets]
