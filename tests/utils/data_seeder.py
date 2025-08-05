"""
Test data seeder utility for creating test data in the database.
Similar to auralys_api DataSeeder pattern.
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Optional

from app.db.models.user import User
from app.db.models.wallet import Wallet
from app.db.models.refresh_token import RefreshToken
from app.core.security import hash_password


class DataSeeder:
    """Utility class for seeding test data"""

    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        name: str = "Test User",
        email: str = "test@example.com",
        password: str = "testpassword123",
        role: str = "user",
    ) -> User:
        """Create a test user"""
        user = User(
            name=name, email=email, hashed_password=hash_password(password), role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_admin(
        self,
        name: str = "Admin User",
        email: str = "admin@example.com",
        password: str = "adminpassword123",
    ) -> User:
        """Create a test admin user"""
        return self.create_user(name=name, email=email, password=password, role="admin")

    def create_wallet(
        self,
        user: User,
        name: str = "Test Wallet",
        wallet_type: str = "checking",
        balance: Decimal = Decimal("1000.00"),
    ) -> Wallet:
        """Create a test wallet for a user"""
        wallet = Wallet(name=name, type=wallet_type, balance=balance, user_id=user.id)
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def create_multiple_wallets(
        self, user: User, wallets_data: Optional[List[dict]] = None
    ) -> List[Wallet]:
        """Create multiple wallets for a user"""
        if wallets_data is None:
            wallets_data = [
                {
                    "name": "Checking Account",
                    "type": "checking",
                    "balance": Decimal("1500.00"),
                },
                {
                    "name": "Savings Account",
                    "type": "savings",
                    "balance": Decimal("5000.00"),
                },
                {"name": "Cash Wallet", "type": "cash", "balance": Decimal("200.00")},
                {"name": "Credit Card", "type": "credit", "balance": Decimal("0.00")},
            ]

        wallets = []
        for wallet_data in wallets_data:
            wallet = self.create_wallet(
                user=user,
                name=wallet_data["name"],
                wallet_type=wallet_data["type"],
                balance=wallet_data["balance"],
            )
            wallets.append(wallet)

        return wallets

    def create_user_with_wallets(
        self,
        user_name: str = "Test User",
        user_email: str = "test@example.com",
        user_password: str = "testpassword123",
        wallets_data: Optional[List[dict]] = None,
    ) -> tuple[User, List[Wallet]]:
        """Create a user with multiple wallets"""
        user = self.create_user(
            name=user_name, email=user_email, password=user_password
        )
        wallets = self.create_multiple_wallets(user, wallets_data)
        return user, wallets

    def create_complete_scenario(self) -> dict:
        """Create a complete test scenario with multiple users and wallets"""
        # Create regular user with wallets
        regular_user = self.create_user(
            name="John Doe", email="john@example.com", password="password123"
        )

        regular_wallets = self.create_multiple_wallets(
            regular_user,
            [
                {
                    "name": "Main Checking",
                    "type": "checking",
                    "balance": Decimal("2500.00"),
                },
                {
                    "name": "Emergency Savings",
                    "type": "savings",
                    "balance": Decimal("10000.00"),
                },
                {"name": "Petty Cash", "type": "cash", "balance": Decimal("150.00")},
            ],
        )

        # Create admin user
        admin_user = self.create_admin(name="Admin Smith", email="admin@example.com")

        admin_wallets = self.create_multiple_wallets(
            admin_user,
            [
                {
                    "name": "Admin Account",
                    "type": "checking",
                    "balance": Decimal("5000.00"),
                },
            ],
        )

        # Create user with credit wallet
        credit_user = self.create_user(
            name="Jane Credit", email="jane@example.com", password="password123"
        )

        credit_wallets = self.create_multiple_wallets(
            credit_user,
            [
                {
                    "name": "Credit Card",
                    "type": "credit",
                    "balance": Decimal("-500.00"),
                },
                {
                    "name": "Debit Account",
                    "type": "checking",
                    "balance": Decimal("800.00"),
                },
            ],
        )

        return {
            "regular_user": regular_user,
            "regular_wallets": regular_wallets,
            "admin_user": admin_user,
            "admin_wallets": admin_wallets,
            "credit_user": credit_user,
            "credit_wallets": credit_wallets,
        }

    def cleanup_all(self):
        """Clean up all test data"""
        self.db.query(RefreshToken).delete()
        self.db.query(Wallet).delete()
        self.db.query(User).delete()
        self.db.commit()
