from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.wallet_repository import WalletRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.debt_repository import DebtRepository
from app.repositories.transfer_repository import TransferRepository
from app.repositories.file_repository import FileRepository
from app.schemas.user_dto import (
    UserCreateDTO,
    UserResponse,
    UserUpdateDTO,
    UserExportData,
    AccountDeletionRequest,
)
from app.schemas.wallet_dto import WalletResponse
from app.schemas.transaction_dto import TransactionResponse
from app.schemas.debt_dto import DebtResponse
from app.schemas.transfer_dto import TransferResponse
from datetime import datetime

USER_NOT_FOUND = "User not found"


class UserService:
    def __init__(self, db_session: Session):
        """
        Constructor for UserService

        Args:
            db_session (Session): The database session
        """
        self.repository = UserRepository(db_session)
        self.wallet_repository = WalletRepository(db_session)
        self.transaction_repository = TransactionRepository(db_session)
        self.debt_repository = DebtRepository(db_session)
        self.transfer_repository = TransferRepository(db_session)
        self.file_repository = FileRepository(db_session)
        self.db = db_session

    def create_user(self, user_data: UserCreateDTO) -> User:
        """
        Create a new user

        Args:
            user_data (UserCreateDTO): The user data

        Returns:
            User: The created user

        Raises:
            ValueError: If user with email already exists
        """
        # Check if the user already exists
        existing_user = self.repository.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("A user with this email already exists.")
        return self.repository.create(user_data)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email

        Args:
            email (str): The email address

        Returns:
            Optional[User]: The user if found
        """
        return self.repository.get_by_email(email)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password

        Args:
            email (str): The email address
            password (str): The password

        Returns:
            Optional[User]: The user if authenticated, None otherwise
        """
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID

        Args:
            user_id (int): The user ID

        Returns:
            Optional[User]: The user if found
        """
        return self.repository.get_by_id(user_id)

    def list_users(self) -> List[User]:
        """
        Get all users

        Returns:
            List[User]: List of all users
        """
        return self.repository.list()

    def update_user(self, user_id: int, user_data: UserUpdateDTO) -> Optional[User]:
        """
        Update a user

        Args:
            user_id (int): The user ID
            user_data (UserUpdateDTO): The update data

        Returns:
            Optional[User]: The updated user if found
        """
        return self.repository.update(user_id, user_data)

    def delete_user(self, user_id: int) -> bool:
        """
        Delete a user

        Args:
            user_id (int): The user ID

        Returns:
            bool: True if deleted, False if not found
        """
        return self.repository.delete(user_id)

    def export_user_data(self, user_id: int) -> UserExportData:
        """
        Export all user data for GDPR compliance

        Args:
            user_id (int): The user ID

        Returns:
            UserExportData: The exported user data

        Raises:
            ValueError: If user not found
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)

        # Get all user wallets
        wallets = self.wallet_repository.get_user_wallets(user_id, limit=1000)
        wallet_data = [WalletResponse.model_validate(wallet) for wallet in wallets]

        # Get all user transactions
        transaction_response = self.transaction_repository.get_user_transactions(
            user_id=user_id, filters=None, skip=0, limit=10000
        )
        transaction_data = transaction_response.transactions

        # Get all user debts
        debts = self.debt_repository.get_user_debts(user_id, limit=1000)
        debt_data = [DebtResponse.model_validate(debt) for debt in debts]

        # Get all user transfers
        transfers = self.transfer_repository.get_user_transfers(user_id, limit=1000)
        transfer_data = [
            TransferResponse.model_validate(transfer) for transfer in transfers
        ]

        return UserExportData(
            user_info=UserResponse.model_validate(user),
            wallets=wallet_data,
            transactions=transaction_data,
            debts=debt_data,
            transfers=transfer_data,
            export_timestamp=datetime.now(),
            data_retention_period="As per GDPR, data is retained for legitimate business purposes only",
        )

    def delete_user_account(
        self, user_id: int, deletion_request: AccountDeletionRequest
    ) -> dict:
        """
        Permanently delete user account and all associated data

        Args:
            user_id (int): The user ID
            deletion_request (AccountDeletionRequest): The deletion confirmation

        Returns:
            dict: Success message

        Raises:
            ValueError: If confirmation is invalid or user not found
        """
        # Validate confirmation
        if deletion_request.confirmation_text.upper() != "DELETE":
            raise ValueError(
                "Invalid confirmation. Please type 'DELETE' to confirm account deletion."
            )

        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)

        try:
            # Start transaction
            self.db.begin()

            # Since we have CASCADE constraints set up in the database,
            # deleting the user should automatically delete all related data
            # However, we need to handle files separately as they may have physical files on disk

            # Get all user transactions to clean up their files
            transaction_response = self.transaction_repository.get_user_transactions(
                user_id=user_id, filters=None, skip=0, limit=10000
            )

            # Delete all transaction files (both database records and physical files)
            for transaction in transaction_response.transactions:
                files = self.file_repository.get_transaction_files(
                    transaction.id, user_id
                )
                for file in files:
                    self.file_repository.delete(file.id, user_id)

            # Now delete the user account (CASCADE will handle all related data)
            success = self.repository.delete(user_id)

            if not success:
                raise ValueError("Failed to delete user account")

            # Commit transaction
            self.db.commit()

            return {
                "message": "User account and all associated data has been permanently deleted",
                "deleted_at": datetime.now().isoformat(),
                "user_email": user.email,
            }

        except Exception as e:
            # Rollback transaction
            self.db.rollback()
            raise ValueError(f"Failed to delete user account: {str(e)}")

    def change_password(self, user_id: int, new_password: str) -> bool:
        """
        Change user password

        Args:
            user_id (int): The user ID
            new_password (str): The new password

        Returns:
            bool: True if password was changed successfully

        Raises:
            ValueError: If user not found
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)

        return self.repository.update_password(user_id, new_password)

    def anonymize_user_data(self, user_id: int) -> dict:
        """
        Anonymize user data (GDPR right to anonymization)

        Args:
            user_id (int): The user ID

        Returns:
            dict: Success message

        Raises:
            ValueError: If user not found
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError(USER_NOT_FOUND)

        try:
            # Anonymize user data
            anonymous_email = f"anonymous_{user_id}@deleted.local"
            anonymous_name = f"Anonymous User {user_id}"

            # Update user with anonymized data
            update_data = UserUpdateDTO(name=anonymous_name, email=anonymous_email)

            updated_user = self.repository.update(user_id, update_data)
            if not updated_user:
                raise ValueError("Failed to anonymize user data")

            return {
                "message": "User data has been anonymized",
                "anonymized_at": datetime.now().isoformat(),
                "user_id": user_id,
            }

        except Exception as e:
            raise ValueError(f"Failed to anonymize user data: {str(e)}")
