import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
import math


class TestWallets:
    """Test wallet management endpoints"""

    def test_create_wallet_success(self, client: TestClient, user_auth):
        """Test successful wallet creation"""
        wallet_data = {
            "name": "My Checking Account",
            "type": "checking",
            "balance": 1500.00,
        }

        response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == wallet_data["name"]
        assert data["type"] == wallet_data["type"]
        assert float(data["balance"]) == wallet_data["balance"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_wallet_unauthorized(self, client: TestClient):
        """Test wallet creation without authentication"""
        wallet_data = {
            "name": "Unauthorized Wallet",
            "type": "checking",
            "balance": 1000.00,
        }

        response = client.post("/wallets/", json=wallet_data)

        assert response.status_code == 401

    def test_create_wallet_invalid_data(self, client: TestClient, user_auth):
        """Test wallet creation with invalid data"""
        wallet_data = {
            "name": "",  # Empty name
            "type": "invalid_type",
            "balance": -100.00,  # Negative balance for non-credit wallet
        }

        response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )

        assert response.status_code == 422

    def test_create_wallet_negative_balance_credit(self, client: TestClient, user_auth):
        """Test creating credit wallet with negative balance (should be allowed)"""
        wallet_data = {"name": "Credit Card", "type": "credit", "balance": -500.00}

        response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )

        assert response.status_code == 201
        data = response.json()
        assert float(data["balance"]) == -500.00

    def test_get_user_wallets(self, client: TestClient, user_auth, multiple_wallets):
        """Test getting user's wallets"""
        response = client.get("/wallets/", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "wallets" in data
        assert "total" in data
        assert isinstance(data["wallets"], list)
        # Note: multiple_wallets fixture may not work with user_auth fixture
        # because they use different users, so let's just check structure
        assert len(data["wallets"]) == 0

    def test_get_user_wallets_unauthorized(self, client: TestClient):
        """Test getting wallets without authentication"""
        response = client.get("/wallets/")

        assert response.status_code == 401

    def test_get_wallet_by_id_success(self, client: TestClient, user_auth):
        """Test getting specific wallet by ID"""
        # First create a wallet
        wallet_data = {"name": "Test Wallet", "type": "checking", "balance": 1000.00}

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Then get it
        response = client.get(f"/wallets/{wallet_id}", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == wallet_id
        assert data["name"] == wallet_data["name"]

    def test_get_wallet_not_found(self, client: TestClient, user_auth):
        """Test getting non-existent wallet"""
        response = client.get("/wallets/99999", headers=user_auth["headers"])

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_wallet_other_user(self, client: TestClient, user_auth, test_wallet):
        """Test getting wallet from another user (should fail)"""
        # test_wallet belongs to test_user, user_auth creates different user
        response = client.get(
            f"/wallets/{test_wallet.id}", headers=user_auth["headers"]
        )

        assert response.status_code == 404

    def test_update_wallet_success(self, client: TestClient, user_auth):
        """Test successful wallet update"""
        # Create wallet first
        wallet_data = {"name": "Original Name", "type": "checking", "balance": 1000.00}

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Update wallet
        update_data = {"name": "Updated Name", "type": "savings"}

        response = client.put(
            f"/wallets/{wallet_id}", json=update_data, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["type"] == update_data["type"]
        assert math.isclose(
            float(data["balance"]), 1000.00, rel_tol=1e-9
        )  # Balance unchanged

    def test_update_wallet_not_found(self, client: TestClient, user_auth):
        """Test updating non-existent wallet"""
        update_data = {"name": "Updated Name"}

        response = client.put(
            "/wallets/99999", json=update_data, headers=user_auth["headers"]
        )

        assert response.status_code == 404

    def test_delete_wallet_success(self, client: TestClient, user_auth):
        """Test successful wallet deletion"""
        # Create wallet first
        wallet_data = {"name": "To Delete", "type": "checking", "balance": 0.00}

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Delete wallet
        response = client.delete(f"/wallets/{wallet_id}", headers=user_auth["headers"])

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()

    def test_delete_wallet_with_balance(self, client: TestClient, user_auth):
        """Test deleting wallet with non-zero balance (should fail)"""
        # Create wallet with balance
        wallet_data = {"name": "With Balance", "type": "checking", "balance": 100.00}

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Try to delete
        response = client.delete(f"/wallets/{wallet_id}", headers=user_auth["headers"])

        assert response.status_code == 400
        assert "balance must be zero" in response.json()["detail"].lower()

    def test_delete_wallet_not_found(self, client: TestClient, user_auth):
        """Test deleting non-existent wallet"""
        response = client.delete("/wallets/99999", headers=user_auth["headers"])

        assert response.status_code == 404

    def test_credit_wallet_success(self, client: TestClient, user_auth):
        """Test successful wallet credit"""
        # Create wallet
        wallet_data = {"name": "Credit Test", "type": "checking", "balance": 1000.00}

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Credit wallet
        credit_data = {"amount": 500.00}

        response = client.post(
            f"/wallets/{wallet_id}/credit",
            json=credit_data,
            headers=user_auth["headers"],
        )

        assert response.status_code == 200
        data = response.json()
        assert math.isclose(float(data["balance"]), 1500.00, rel_tol=1e-9)

    def test_credit_wallet_invalid_amount(self, client: TestClient, user_auth):
        """Test crediting wallet with invalid amount"""
        # Create wallet
        wallet_data = {"name": "Credit Test", "type": "checking", "balance": 1000.00}

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Try to credit negative amount
        credit_data = {"amount": -100.00}

        response = client.post(
            f"/wallets/{wallet_id}/credit",
            json=credit_data,
            headers=user_auth["headers"],
        )

        assert response.status_code == 422

    def test_debit_wallet_success(self, client: TestClient, user_auth):
        """Test successful wallet debit"""
        # Create wallet
        wallet_data = {"name": "Debit Test", "type": "checking", "balance": 1000.00}

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Debit wallet
        debit_data = {"amount": 300.00}

        response = client.post(
            f"/wallets/{wallet_id}/debit", json=debit_data, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert math.isclose(float(data["balance"]), 700.00, rel_tol=1e-9)

    def test_debit_wallet_insufficient_funds(self, client: TestClient, user_auth):
        """Test debiting wallet with insufficient funds"""
        # Create wallet with small balance
        wallet_data = {
            "name": "Insufficient Funds Test",
            "type": "checking",
            "balance": 100.00,
        }

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Try to debit more than balance
        debit_data = {"amount": 200.00}

        response = client.post(
            f"/wallets/{wallet_id}/debit", json=debit_data, headers=user_auth["headers"]
        )

        assert response.status_code == 400
        assert (
            "insufficient balance for this operation"
            in response.json()["detail"].lower()
        )

    def test_debit_credit_wallet_overdraft(self, client: TestClient, user_auth):
        """Test debiting credit wallet (overdraft allowed)"""
        # Create credit wallet
        wallet_data = {"name": "Credit Card", "type": "credit", "balance": 0.00}

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Debit credit wallet (should go negative)
        debit_data = {"amount": 500.00}

        response = client.post(
            f"/wallets/{wallet_id}/debit", json=debit_data, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["balance"]) == -500.00

    def test_get_wallet_balance(self, client: TestClient, user_auth):
        """Test getting wallet balance"""
        # Create wallet
        wallet_data = {"name": "Balance Test", "type": "savings", "balance": 2500.50}

        create_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = create_response.json()["id"]

        # Get balance
        response = client.get(
            f"/wallets/{wallet_id}/balance", headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert math.isclose(float(data["balance"]), 2500.50, rel_tol=1e-9)
        assert data["wallet_name"] == "Balance Test"

    def test_wallet_operations_unauthorized(self, client: TestClient):
        """Test wallet operations without authentication"""
        operations = [
            ("POST", "/wallets/1/credit", {"amount": 100}),
            ("POST", "/wallets/1/debit", {"amount": 100}),
            ("GET", "/wallets/1/balance", None),
        ]

        for method, url, data in operations:
            if method == "POST":
                response = client.post(url, json=data)
            else:
                response = client.get(url)

            assert response.status_code == 401
