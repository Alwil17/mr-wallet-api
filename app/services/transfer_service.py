from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.transfer import Transfer
from app.repositories.transfer_repository import TransferRepository
from app.schemas.transfer_dto import (
    TransferCreateDTO,
    TransferResponse,
    TransferListResponse,
    TransferSummaryResponse,
    TransferFilterDTO,
    WalletTransferSummaryDTO,
)

TRANSFER_NOT_FOUND = "Transfer not found"
WALLET_NOT_FOUND = "Wallet not found or not owned by user"
INSUFFICIENT_FUNDS = "Insufficient funds for transfer"


class TransferService:
    def __init__(self, db: Session):
        self.repository = TransferRepository(db)

    def create_transfer(
        self, transfer_data: TransferCreateDTO, user_id: int
    ) -> Transfer:
        """
        Create a new transfer between wallets

        Args:
            transfer_data (TransferCreateDTO): The transfer data
            user_id (int): The user ID

        Returns:
            Transfer: The created transfer

        Raises:
            ValueError: If wallets not found, invalid data, or insufficient funds
        """
        try:
            return self.repository.create(transfer_data, user_id)
        except ValueError as e:
            raise ValueError(str(e))

    def get_transfer_by_id(self, transfer_id: int, user_id: int) -> Optional[Transfer]:
        """
        Get transfer by ID

        Args:
            transfer_id (int): The transfer ID
            user_id (int): The user ID

        Returns:
            Optional[Transfer]: The transfer or None if not found/not owned
        """
        return self.repository.get_by_id_and_user(transfer_id, user_id)

    def get_user_transfers(
        self,
        user_id: int,
        filters: Optional[TransferFilterDTO] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> TransferListResponse:
        """
        Get user's transfers with optional filtering

        Args:
            user_id (int): The user ID
            filters (TransferFilterDTO): Optional filters
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            TransferListResponse: List of transfers with total count
        """
        transfers = self.repository.get_user_transfers(user_id, filters, skip, limit)
        total = self.repository.count_user_transfers(user_id, filters)

        # Enrich transfer responses with wallet names
        transfer_responses = []
        for transfer in transfers:
            response = TransferResponse.model_validate(transfer)
            response.source_wallet_name = (
                transfer.source_wallet.name if transfer.source_wallet else None
            )
            response.target_wallet_name = (
                transfer.target_wallet.name if transfer.target_wallet else None
            )
            transfer_responses.append(response)

        return TransferListResponse(transfers=transfer_responses, total=total)

    def get_wallet_transfers(
        self, wallet_id: int, user_id: int
    ) -> List[TransferResponse]:
        """
        Get all transfers for a specific wallet

        Args:
            wallet_id (int): The wallet ID
            user_id (int): The user ID

        Returns:
            List[TransferResponse]: List of transfers for the wallet

        Raises:
            ValueError: If wallet not found or not owned by user
        """
        try:
            transfers = self.repository.get_wallet_transfers(wallet_id, user_id)

            transfer_responses = []
            for transfer in transfers:
                response = TransferResponse.model_validate(transfer)
                response.source_wallet_name = (
                    transfer.source_wallet.name if transfer.source_wallet else None
                )
                response.target_wallet_name = (
                    transfer.target_wallet.name if transfer.target_wallet else None
                )
                transfer_responses.append(response)

            return transfer_responses
        except ValueError as e:
            raise ValueError(str(e))

    def delete_transfer(self, transfer_id: int, user_id: int) -> bool:
        """
        Delete a transfer and reverse the balance changes

        Args:
            transfer_id (int): The transfer ID
            user_id (int): The user ID

        Returns:
            bool: True if deleted successfully

        Raises:
            ValueError: If transfer not found or cannot be reversed
        """
        try:
            return self.repository.delete(transfer_id, user_id)
        except ValueError as e:
            raise ValueError(str(e))

    def get_transfer_summary(self, user_id: int) -> TransferSummaryResponse:
        """
        Get transfer summary for a user

        Args:
            user_id (int): The user ID

        Returns:
            TransferSummaryResponse: Summary of user's transfers
        """
        summary_data = self.repository.get_user_transfer_summary(user_id)

        # Convert recent transfers to response format
        recent_transfer_responses = []
        for transfer in summary_data["recent_transfers"]:
            response = TransferResponse.model_validate(transfer)
            response.source_wallet_name = (
                transfer.source_wallet.name if transfer.source_wallet else None
            )
            response.target_wallet_name = (
                transfer.target_wallet.name if transfer.target_wallet else None
            )
            recent_transfer_responses.append(response)

        return TransferSummaryResponse(
            total_transfers=summary_data["total_transfers"],
            total_amount_transferred=summary_data["total_amount_transferred"],
            transfers_by_wallet=summary_data["transfers_by_wallet"],
            recent_transfers=recent_transfer_responses,
        )

    def get_wallet_transfer_summary(
        self, wallet_id: int, user_id: int
    ) -> WalletTransferSummaryDTO:
        """
        Get transfer summary for a specific wallet

        Args:
            wallet_id (int): The wallet ID
            user_id (int): The user ID

        Returns:
            WalletTransferSummaryDTO: Transfer summary for the wallet

        Raises:
            ValueError: If wallet not found or not owned by user
        """
        try:
            transfers = self.repository.get_wallet_transfers(wallet_id, user_id)

            # Get wallet info
            wallet = (
                transfers[0].source_wallet
                if transfers and transfers[0].source_wallet_id == wallet_id
                else None
            )
            if not wallet and transfers:
                wallet = (
                    transfers[0].target_wallet
                    if transfers[0].target_wallet_id == wallet_id
                    else None
                )

            if not wallet:
                raise ValueError("Wallet not found")

            # Calculate summary
            total_sent = sum(
                t.amount for t in transfers if t.source_wallet_id == wallet_id
            )
            total_received = sum(
                t.amount for t in transfers if t.target_wallet_id == wallet_id
            )
            net_amount = total_received - total_sent
            transfer_count = len(transfers)

            return WalletTransferSummaryDTO(
                wallet_id=wallet_id,
                wallet_name=wallet.name,
                total_sent=total_sent,
                total_received=total_received,
                net_amount=net_amount,
                transfer_count=transfer_count,
            )

        except ValueError as e:
            raise ValueError(str(e))
