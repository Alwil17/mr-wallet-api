from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.db.models.wallet import Wallet
from app.schemas.wallet_dto import WalletCreateDTO, WalletUpdateDTO


class WalletRepository:
    def __init__(self, db: Session):
        """
        Constructor for WalletRepository

        Args:
            db (Session): The database session
        """
        self.db = db

    def create(self, wallet_data: WalletCreateDTO, user_id: int) -> Wallet:
        """
        Create a new wallet

        Args:
            wallet_data (WalletCreateDTO): The wallet data
            user_id (int): The user ID who owns the wallet

        Returns:
            Wallet: The created wallet
        """
        wallet = Wallet(
            name=wallet_data.name,
            type=wallet_data.type,
            balance=wallet_data.balance or Decimal("0.00"),
            user_id=user_id
        )
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def get_by_id(self, wallet_id: int) -> Optional[Wallet]:
        """
        Get a wallet by ID

        Args:
            wallet_id (int): The wallet ID

        Returns:
            Optional[Wallet]: The wallet if found
        """
        return self.db.query(Wallet).filter(Wallet.id == wallet_id).first()

    def get_by_id_and_user(self, wallet_id: int, user_id: int) -> Optional[Wallet]:
        """
        Get a wallet by ID and user ID (for ownership verification)

        Args:
            wallet_id (int): The wallet ID
            user_id (int): The user ID

        Returns:
            Optional[Wallet]: The wallet if found and owned by user
        """
        return self.db.query(Wallet).filter(
            and_(Wallet.id == wallet_id, Wallet.user_id == user_id)
        ).first()

    def get_user_wallets(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Wallet]:
        """
        Get all wallets for a user

        Args:
            user_id (int): The user ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            List[Wallet]: List of user's wallets
        """
        return self.db.query(Wallet).filter(
            Wallet.user_id == user_id
        ).offset(skip).limit(limit).all()

    def count_user_wallets(self, user_id: int) -> int:
        """
        Count total wallets for a user

        Args:
            user_id (int): The user ID

        Returns:
            int: Total number of wallets
        """
        return self.db.query(Wallet).filter(Wallet.user_id == user_id).count()

    def update(self, wallet_id: int, wallet_data: WalletUpdateDTO) -> Optional[Wallet]:
        """
        Update a wallet

        Args:
            wallet_id (int): The wallet ID
            wallet_data (WalletUpdateDTO): The update data

        Returns:
            Optional[Wallet]: The updated wallet if found
        """
        wallet = self.get_by_id(wallet_id)
        if not wallet:
            return None

        # Update only provided fields
        if wallet_data.name is not None:
            wallet.name = wallet_data.name
        if wallet_data.type is not None:
            wallet.type = wallet_data.type

        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def update_balance(self, wallet_id: int, new_balance: Decimal) -> Optional[Wallet]:
        """
        Update wallet balance

        Args:
            wallet_id (int): The wallet ID
            new_balance (Decimal): The new balance

        Returns:
            Optional[Wallet]: The updated wallet if found
        """
        wallet = self.get_by_id(wallet_id)
        if not wallet:
            return None

        wallet.balance = new_balance
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def delete(self, wallet_id: int) -> bool:
        """
        Delete a wallet

        Args:
            wallet_id (int): The wallet ID

        Returns:
            bool: True if wallet was deleted, False if not found
        """
        wallet = self.get_by_id(wallet_id)
        if not wallet:
            return False

        self.db.delete(wallet)
        self.db.commit()
        return True

    def get_user_wallet_summary(self, user_id: int) -> dict:
        """
        Get wallet summary for a user

        Args:
            user_id (int): The user ID

        Returns:
            dict: Summary information about user's wallets
        """
        wallets = self.get_user_wallets(user_id)
        
        if not wallets:
            return {
                "total_wallets": 0,
                "total_balance": Decimal("0.00"),
                "wallets_by_type": {},
                "most_recent_wallet": None
            }

        total_balance = sum(wallet.balance for wallet in wallets)
        
        # Group by type
        wallets_by_type = {}
        for wallet in wallets:
            if wallet.type not in wallets_by_type:
                wallets_by_type[wallet.type] = {
                    "count": 0,
                    "total_balance": Decimal("0.00")
                }
            wallets_by_type[wallet.type]["count"] += 1
            wallets_by_type[wallet.type]["total_balance"] += wallet.balance

        # Most recent wallet
        most_recent = max(wallets, key=lambda w: w.created_at) if wallets else None

        return {
            "total_wallets": len(wallets),
            "total_balance": total_balance,
            "wallets_by_type": wallets_by_type,
            "most_recent_wallet": most_recent
        }
