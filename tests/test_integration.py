import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
import math

from tests.utils.data_seeder import DataSeeder


class TestIntegration:
    """Integration tests using DataSeeder utility"""

    def test_user_wallet_flow_with_seeder(self, client: TestClient, db: Session):
        """Test complete user-wallet flow using DataSeeder"""
        seeder = DataSeeder(db)
        
        # Create user with wallets using seeder
        user, _ = seeder.create_user_with_wallets(
            user_name="Integration Test User",
            user_email="integration@example.com",
            user_password="password123",
            wallets_data=[
                {"name": "Test Checking", "type": "checking", "balance": Decimal("1000.00")},
                {"name": "Test Savings", "type": "savings", "balance": Decimal("2000.00")},
            ]
        )
        
        # Login
        form_data = {
            "username": user.email,
            "password": "password123"
        }
        
        login_response = client.post("/auth/token", data=form_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Get user's wallets
        wallets_response = client.get("/wallets/", headers=headers)
        assert wallets_response.status_code == 200
        
        wallet_data = wallets_response.json()
        user_wallets = wallet_data["wallets"]  # Extract wallets from response
        assert len(user_wallets) == 2
        
        # Find checking account
        checking_wallet = next(w for w in user_wallets if w["type"] == "checking")
        wallet_id = checking_wallet["id"]
        
        # Test balance operations
        # Credit the account
        credit_response = client.post(
            f"/wallets/{wallet_id}/credit",
            json={"amount": 500.00},
            headers=headers
        )
        assert credit_response.status_code == 200
        assert math.isclose(float(credit_response.json()["balance"]), 1500.00, rel_tol=1e-9)

        # Debit the account
        debit_response = client.post(
            f"/wallets/{wallet_id}/debit",
            json={"amount": 300.00},
            headers=headers
        )
        assert debit_response.status_code == 200
        assert math.isclose(float(debit_response.json()["balance"]), 1200.00, rel_tol=1e-9)

        # Check balance
        balance_response = client.get(f"/wallets/{wallet_id}/balance", headers=headers)
        assert balance_response.status_code == 200
        assert math.isclose(float(balance_response.json()["balance"]), 1200.00, rel_tol=1e-9)

    def test_complete_scenario_with_seeder(self, client: TestClient, db: Session):
        """Test complete scenario with multiple users and wallets"""
        seeder = DataSeeder(db)
        
        # Create complete scenario
        scenario = seeder.create_complete_scenario()
        
        # Test regular user operations
        regular_user = scenario["regular_user"]
        form_data = {
            "username": regular_user.email,
            "password": "password123"
        }
        
        login_response = client.post("/auth/token", data=form_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Get user's wallets
        wallets_response = client.get("/wallets/", headers=headers)
        assert wallets_response.status_code == 200
        
        wallet_data = wallets_response.json()
        user_wallets = wallet_data["wallets"]  # Extract wallets from response  
        assert len(user_wallets) == 3
        
        # Test admin user operations
        admin_user = scenario["admin_user"]
        admin_form_data = {
            "username": admin_user.email,
            "password": "adminpassword123"
        }
        
        admin_login_response = client.post("/auth/token", data=admin_form_data)
        assert admin_login_response.status_code == 200
        
        admin_token_data = admin_login_response.json()
        admin_headers = {"Authorization": f"Bearer {admin_token_data['access_token']}"}
        
        # Get admin's wallets
        admin_wallets_response = client.get("/wallets/", headers=admin_headers)
        assert admin_wallets_response.status_code == 200
        
        admin_wallet_data = admin_wallets_response.json()
        admin_wallets = admin_wallet_data["wallets"]  # Extract wallets from response
        assert len(admin_wallets) == 1
        assert admin_wallets[0]["name"] == "Admin Account"

    def test_credit_wallet_operations(self, client: TestClient, db: Session):
        """Test credit wallet specific operations"""
        seeder = DataSeeder(db)
        
        user = seeder.create_user(
            name="Credit User",
            email="credit@example.com",
            password="password123"
        )
        
        # Create credit wallet with negative balance
        credit_wallet = seeder.create_wallet(
            user=user,
            name="Credit Card",
            wallet_type="credit",
            balance=Decimal("-500.00")
        )
        
        # Login
        form_data = {
            "username": user.email,
            "password": "password123"
        }
        
        login_response = client.post("/auth/token", data=form_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Test debit operation (should increase negative balance)
        debit_response = client.post(
            f"/wallets/{credit_wallet.id}/debit",
            json={"amount": 200.00},
            headers=headers
        )
        assert debit_response.status_code == 200
        assert float(debit_response.json()["balance"]) == -700.00
        
        # Test credit operation (should decrease negative balance)
        credit_response = client.post(
            f"/wallets/{credit_wallet.id}/credit",
            json={"amount": 300.00},
            headers=headers
        )
        assert credit_response.status_code == 200
        assert float(credit_response.json()["balance"]) == -400.00

    def test_wallet_deletion_scenarios(self, client: TestClient, db: Session):
        """Test wallet deletion in various scenarios"""
        seeder = DataSeeder(db)
        
        user = seeder.create_user(
            name="Delete Test User",
            email="delete@example.com",
            password="password123"
        )
        
        # Create wallets with different balances
        zero_balance_wallet = seeder.create_wallet(
            user=user,
            name="Zero Balance",
            wallet_type="checking",
            balance=Decimal("0.00")
        )
        
        positive_balance_wallet = seeder.create_wallet(
            user=user,
            name="Positive Balance",
            wallet_type="savings",
            balance=Decimal("100.00")
        )
        
        # Login
        form_data = {
            "username": user.email,
            "password": "password123"
        }
        
        login_response = client.post("/auth/token", data=form_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Should be able to delete zero balance wallet
        delete_response = client.delete(
            f"/wallets/{zero_balance_wallet.id}",
            headers=headers
        )
        assert delete_response.status_code == 200
        
        # Should NOT be able to delete wallet with balance
        delete_response = client.delete(
            f"/wallets/{positive_balance_wallet.id}",
            headers=headers
        )
        assert delete_response.status_code == 400
        assert "balance must be zero" in delete_response.json()["detail"].lower()

    def test_user_profile_and_gdpr_with_wallets(self, client: TestClient, db: Session):
        """Test user profile and GDPR data export with wallets"""
        seeder = DataSeeder(db)
        
        user, wallets = seeder.create_user_with_wallets(
            user_name="GDPR Test User",
            user_email="gdpr@example.com"
        )
        
        # Login
        form_data = {
            "username": user.email,
            "password": "testpassword123"
        }
        
        login_response = client.post("/auth/token", data=form_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Test profile
        profile_response = client.get("/auth/profile", headers=headers)
        assert profile_response.status_code == 200
        
        profile_data = profile_response.json()
        assert profile_data["email"] == user.email
        assert profile_data["name"] == user.name
        
        # Test GDPR data export
        gdpr_response = client.get("/auth/gdpr/data", headers=headers)
        assert gdpr_response.status_code == 200
        
        gdpr_data = gdpr_response.json()
        assert gdpr_data["user_info"]["email"] == user.email
        assert "wallets" in gdpr_data
        assert len(gdpr_data["wallets"]) == len(wallets)

    def test_account_deletion_with_wallets(self, client: TestClient, db: Session):
        """Test account deletion when user has wallets"""
        seeder = DataSeeder(db)
        
        user, _ = seeder.create_user_with_wallets(
            user_name="Delete Account User",
            user_email="deleteaccount@example.com"
        )
        
        # Login
        form_data = {
            "username": user.email,
            "password": "testpassword123"
        }
        
        login_response = client.post("/auth/token", data=form_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # Delete account (should cascade delete wallets)
        delete_response = client.delete("/auth/account", headers=headers)
        assert delete_response.status_code == 200
        
        # Verify account is deleted by trying to login again
        login_again_response = client.post("/auth/token", data=form_data)
        assert login_again_response.status_code == 401
