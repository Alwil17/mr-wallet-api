from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, or_, desc
from app.db.models.transfer import Transfer
from app.db.models.wallet import Wallet
from app.schemas.transfer_dto import TransferCreateDTO, TransferFilterDTO


class TransferRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, transfer_data: TransferCreateDTO, user_id: int) -> Transfer:
        """
        Create a new transfer record and update wallet balances atomically

        Args:
            transfer_data (TransferCreateDTO): The transfer data
            user_id (int): The user ID (for wallet ownership verification)

        Returns:
            Transfer: The created transfer

        Raises:
            ValueError: If wallets not found, not owned by user, or insufficient funds
        """
        # Verify both wallets belong to the user
        source_wallet = (
            self.db.query(Wallet)
            .filter(
                and_(
                    Wallet.id == transfer_data.source_wallet_id,
                    Wallet.user_id == user_id,
                )
            )
            .first()
        )

        target_wallet = (
            self.db.query(Wallet)
            .filter(
                and_(
                    Wallet.id == transfer_data.target_wallet_id,
                    Wallet.user_id == user_id,
                )
            )
            .first()
        )

        if not source_wallet:
            raise ValueError("Source wallet not found or not owned by user")

        if not target_wallet:
            raise ValueError("Target wallet not found or not owned by user")

        # Check if source wallet has sufficient funds (except for credit wallets)
        if (
            source_wallet.type != "credit"
            and source_wallet.balance < transfer_data.amount
        ):
            raise ValueError("Insufficient funds in source wallet")

        # Create transfer record
        transfer = Transfer(
            amount=transfer_data.amount,
            source_wallet_id=transfer_data.source_wallet_id,
            target_wallet_id=transfer_data.target_wallet_id,
            description=transfer_data.description,
        )

        # Update wallet balances atomically
        source_wallet.balance -= transfer_data.amount
        target_wallet.balance += transfer_data.amount

        self.db.add(transfer)
        self.db.commit()
        self.db.refresh(transfer)
        return transfer

    def get_by_id(self, transfer_id: int) -> Optional[Transfer]:
        """Get transfer by ID with wallet information"""
        return (
            self.db.query(Transfer)
            .options(
                joinedload(Transfer.source_wallet), joinedload(Transfer.target_wallet)
            )
            .filter(Transfer.id == transfer_id)
            .first()
        )

    def get_by_id_and_user(self, transfer_id: int, user_id: int) -> Optional[Transfer]:
        """Get transfer by ID and user (through wallet ownership)"""
        return (
            self.db.query(Transfer)
            .join(
                Wallet,
                or_(
                    Transfer.source_wallet_id == Wallet.id,
                    Transfer.target_wallet_id == Wallet.id,
                ),
            )
            .options(
                joinedload(Transfer.source_wallet), joinedload(Transfer.target_wallet)
            )
            .filter(and_(Transfer.id == transfer_id, Wallet.user_id == user_id))
            .first()
        )

    def get_user_transfers(
        self,
        user_id: int,
        filters: Optional[TransferFilterDTO] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Transfer]:
        """
        Get all transfers for a user with optional filtering

        Args:
            user_id (int): The user ID
            filters (TransferFilterDTO): Optional filters
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            List[Transfer]: List of transfers
        """
        # Query transfers where user owns either source or target wallet
        query = (
            self.db.query(Transfer)
            .join(
                Wallet,
                or_(
                    Transfer.source_wallet_id == Wallet.id,
                    Transfer.target_wallet_id == Wallet.id,
                ),
            )
            .options(
                joinedload(Transfer.source_wallet), joinedload(Transfer.target_wallet)
            )
            .filter(Wallet.user_id == user_id)
        )

        if filters:
            if filters.source_wallet_id:
                query = query.filter(
                    Transfer.source_wallet_id == filters.source_wallet_id
                )

            if filters.target_wallet_id:
                query = query.filter(
                    Transfer.target_wallet_id == filters.target_wallet_id
                )

            if filters.wallet_id:
                query = query.filter(
                    or_(
                        Transfer.source_wallet_id == filters.wallet_id,
                        Transfer.target_wallet_id == filters.wallet_id,
                    )
                )

            if filters.min_amount:
                query = query.filter(Transfer.amount >= filters.min_amount)

            if filters.max_amount:
                query = query.filter(Transfer.amount <= filters.max_amount)

            if filters.date_from:
                query = query.filter(Transfer.created_at >= filters.date_from)

            if filters.date_to:
                query = query.filter(Transfer.created_at <= filters.date_to)

        return query.order_by(desc(Transfer.created_at)).offset(skip).limit(limit).all()

    def count_user_transfers(
        self, user_id: int, filters: Optional[TransferFilterDTO] = None
    ) -> int:
        """Count total transfers for a user with optional filtering"""
        query = (
            self.db.query(Transfer)
            .join(
                Wallet,
                or_(
                    Transfer.source_wallet_id == Wallet.id,
                    Transfer.target_wallet_id == Wallet.id,
                ),
            )
            .filter(Wallet.user_id == user_id)
        )

        if filters:
            if filters.source_wallet_id:
                query = query.filter(
                    Transfer.source_wallet_id == filters.source_wallet_id
                )

            if filters.target_wallet_id:
                query = query.filter(
                    Transfer.target_wallet_id == filters.target_wallet_id
                )

            if filters.wallet_id:
                query = query.filter(
                    or_(
                        Transfer.source_wallet_id == filters.wallet_id,
                        Transfer.target_wallet_id == filters.wallet_id,
                    )
                )

            if filters.min_amount:
                query = query.filter(Transfer.amount >= filters.min_amount)

            if filters.max_amount:
                query = query.filter(Transfer.amount <= filters.max_amount)

            if filters.date_from:
                query = query.filter(Transfer.created_at >= filters.date_from)

            if filters.date_to:
                query = query.filter(Transfer.created_at <= filters.date_to)

        return query.count()

    def get_wallet_transfers(self, wallet_id: int, user_id: int) -> List[Transfer]:
        """Get all transfers for a specific wallet (both sent and received)"""
        # Verify wallet ownership
        wallet = (
            self.db.query(Wallet)
            .filter(and_(Wallet.id == wallet_id, Wallet.user_id == user_id))
            .first()
        )

        if not wallet:
            raise ValueError("Wallet not found or not owned by user")

        return (
            self.db.query(Transfer)
            .options(
                joinedload(Transfer.source_wallet), joinedload(Transfer.target_wallet)
            )
            .filter(
                or_(
                    Transfer.source_wallet_id == wallet_id,
                    Transfer.target_wallet_id == wallet_id,
                )
            )
            .order_by(desc(Transfer.created_at))
            .all()
        )

    def delete(self, transfer_id: int, user_id: int) -> bool:
        """
        Delete a transfer and reverse the wallet balance changes

        Args:
            transfer_id (int): The transfer ID
            user_id (int): The user ID (for ownership verification)

        Returns:
            bool: True if deleted, False if not found

        Raises:
            ValueError: If transfer not found or not owned by user
        """
        transfer = self.get_by_id_and_user(transfer_id, user_id)
        if not transfer:
            raise ValueError("Transfer not found or not owned by user")

        # Reverse the wallet balance changes
        source_wallet = transfer.source_wallet
        target_wallet = transfer.target_wallet

        # Check if reversing would cause negative balance (except for credit wallets)
        if target_wallet.type != "credit" and target_wallet.balance < transfer.amount:
            raise ValueError(
                "Cannot reverse transfer: insufficient funds in target wallet"
            )

        # Reverse balances
        source_wallet.balance += transfer.amount
        target_wallet.balance -= transfer.amount

        self.db.delete(transfer)
        self.db.commit()
        return True

    def get_user_transfer_summary(self, user_id: int) -> dict:
        """
        Get transfer summary for a user

        Args:
            user_id (int): The user ID

        Returns:
            dict: Summary statistics
        """
        # Get all transfers for user
        transfers = self.get_user_transfers(user_id)

        total_transfers = len(transfers)
        total_amount_transferred = sum(transfer.amount for transfer in transfers)

        # Group by wallet
        transfers_by_wallet = {}
        user_wallets = self.db.query(Wallet).filter(Wallet.user_id == user_id).all()

        for wallet in user_wallets:
            sent_transfers = [t for t in transfers if t.source_wallet_id == wallet.id]
            received_transfers = [
                t for t in transfers if t.target_wallet_id == wallet.id
            ]

            total_sent = sum(t.amount for t in sent_transfers)
            total_received = sum(t.amount for t in received_transfers)

            transfers_by_wallet[wallet.name] = {
                "wallet_id": wallet.id,
                "total_sent": total_sent,
                "total_received": total_received,
                "net_amount": total_received - total_sent,
                "transfer_count": len(sent_transfers) + len(received_transfers),
            }

        # Get recent transfers (last 5)
        recent_transfers = transfers[:5] if transfers else []

        return {
            "total_transfers": total_transfers,
            "total_amount_transferred": total_amount_transferred,
            "transfers_by_wallet": transfers_by_wallet,
            "recent_transfers": recent_transfers,
        }
