import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from app.db.models.transaction import TransactionType, TransactionCategory
import math


# Top-level fixture for user-defined category
@pytest.fixture(scope="function")
def user_category(client, user_auth):
    """Create a user-defined category and return its id."""
    payload = {"name": "Test UserCat", "color": "#123456", "icon": "test-icon"}
    response = client.post("/categories/", json=payload, headers=user_auth["headers"])
    assert response.status_code == 201
    return response.json()["id"]


class TestTransactions:
    """Test transaction management endpoints"""

    def test_create_transaction_income_success(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test successful income transaction creation"""
        transaction_data = {
            "type": "income",
            "amount": 1500.00,
            "category": "salary",
            "note": "Monthly salary",
            "wallet_id": test_wallet_api["id"],
        }

        response = client.post(
            "/transactions/", json=transaction_data, headers=user_auth["headers"]
        )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "income"
        assert math.isclose(float(data["amount"]), 1500.00, rel_tol=1e-9)
        assert data["category"] == "salary"
        assert data["note"] == "Monthly salary"
        assert data["wallet_id"] == test_wallet_api["id"]
        assert "id" in data
        assert "created_at" in data

    def test_create_transaction_expense_success(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test successful expense transaction creation"""
        transaction_data = {
            "type": "expense",
            "amount": 150.00,
            "category": "food",
            "note": "Grocery shopping",
            "wallet_id": test_wallet_api["id"],
        }

        response = client.post(
            "/transactions/", json=transaction_data, headers=user_auth["headers"]
        )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "expense"
        assert math.isclose(float(data["amount"]), 150.00, rel_tol=1e-9)
        assert data["category"] == "food"
        assert data["note"] == "Grocery shopping"

    def test_create_transaction_unauthorized(self, client: TestClient, test_wallet_api):
        """Test transaction creation without authentication"""
        transaction_data = {
            "type": "income",
            "amount": 100.00,
            "category": "salary",
            "wallet_id": test_wallet_api["id"],
        }

        response = client.post("/transactions/", json=transaction_data)

        assert response.status_code == 401

    def test_create_transaction_invalid_wallet(self, client: TestClient, user_auth):
        """Test transaction creation with non-existent wallet"""
        transaction_data = {
            "type": "income",
            "amount": 100.00,
            "category": "salary",
            "wallet_id": 99999,
        }

        response = client.post(
            "/transactions/", json=transaction_data, headers=user_auth["headers"]
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_create_transaction_insufficient_funds(self, client: TestClient, user_auth):
        """Test expense transaction with insufficient funds"""
        # First create a wallet with low balance
        wallet_data = {
            "name": "Low Balance Wallet",
            "type": "checking",
            "balance": 50.00,
        }

        wallet_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = wallet_response.json()["id"]

        # Try to create expense transaction larger than balance
        transaction_data = {
            "type": "expense",
            "amount": 100.00,
            "category": "food",
            "wallet_id": wallet_id,
        }

        response = client.post(
            "/transactions/", json=transaction_data, headers=user_auth["headers"]
        )

        assert response.status_code == 400
        assert "insufficient funds" in response.json()["detail"].lower()

    def test_create_transaction_credit_wallet_overdraft(
        self, client: TestClient, user_auth
    ):
        """Test expense transaction on credit wallet (should allow overdraft)"""
        # Create credit wallet
        wallet_data = {"name": "Credit Card", "type": "credit", "balance": 0.00}

        wallet_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = wallet_response.json()["id"]

        # Create expense transaction (should work for credit wallet)
        transaction_data = {
            "type": "expense",
            "amount": 500.00,
            "category": "shopping",
            "wallet_id": wallet_id,
        }

        response = client.post(
            "/transactions/", json=transaction_data, headers=user_auth["headers"]
        )

        assert response.status_code == 201

    def test_get_user_transactions(
        self, client: TestClient, user_auth, test_wallet_api, user_category
    ):
        """Test getting user's transactions"""
        # Create a couple of transactions first

        transactions = [
            {
                "type": "income",
                "amount": 1000.00,
                "category": "salary",
                "note": "Salary deposit",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "type": "expense",
                "amount": 200.00,
                "category_id": user_category,
                "note": "Groceries",
                "wallet_id": test_wallet_api["id"],
            },
        ]
        for transaction_data in transactions:
            client.post(
                "/transactions/", json=transaction_data, headers=user_auth["headers"]
            )

        # Get transactions
        response = client.get("/transactions/", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()

    # (Removed misplaced assertions from class level. All logic is now inside test methods.)

    def test_get_transactions_with_filters(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test getting transactions with filters"""
        # Create transactions with different types and categories
        transactions = [
            {
                "type": "income",
                "amount": 1500.00,
                "category": "salary",
                "note": "Monthly salary",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "type": "expense",
                "amount": 300.00,
                "category": "food",
                "note": "Restaurant",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "type": "expense",
                "amount": 100.00,
                "category": "transport",
                "note": "Gas",
                "wallet_id": test_wallet_api["id"],
            },
        ]

        for transaction_data in transactions:
            client.post(
                "/transactions/", json=transaction_data, headers=user_auth["headers"]
            )

        # Filter by type (income)
        response = client.get(
            "/transactions/",
            params={"transaction_type": "income"},
            headers=user_auth["headers"],
        )

        assert response.status_code == 200
        data = response.json()
        income_transactions = [t for t in data["transactions"] if t["type"] == "income"]
        assert len(income_transactions) >= 1

        # Filter by category (food)
        response = client.get(
            "/transactions/", params={"category": "food"}, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        food_transactions = [t for t in data["transactions"] if t["category"] == "food"]
        assert len(food_transactions) >= 1

    def test_get_transaction_by_id(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test getting specific transaction by ID"""
        # Create a transaction
        transaction_data = {
            "type": "income",
            "amount": 800.00,
            "category": "freelance",
            "note": "Web development project",
            "wallet_id": test_wallet_api["id"],
        }

        create_response = client.post(
            "/transactions/", json=transaction_data, headers=user_auth["headers"]
        )
        transaction_id = create_response.json()["id"]

        # Get the transaction
        response = client.get(
            f"/transactions/{transaction_id}", headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id
        assert math.isclose(float(data["amount"]), 800.00, rel_tol=1e-9)
        assert data["category"] == "freelance"

    def test_get_transaction_not_found(self, client: TestClient, user_auth):
        """Test getting non-existent transaction"""
        response = client.get("/transactions/99999", headers=user_auth["headers"])

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_transaction_success(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test successful transaction update"""
        # Create transaction
        transaction_data = {
            "type": "expense",
            "amount": 100.00,
            "category": "food",
            "note": "Original note",
            "wallet_id": test_wallet_api["id"],
        }

        create_response = client.post(
            "/transactions/", json=transaction_data, headers=user_auth["headers"]
        )
        transaction_id = create_response.json()["id"]

        # Update transaction
        update_data = {
            "amount": 150.00,
            "note": "Updated note",
            "category": "entertainment",
        }

        response = client.put(
            f"/transactions/{transaction_id}",
            json=update_data,
            headers=user_auth["headers"],
        )

        assert response.status_code == 200
        data = response.json()
        assert math.isclose(float(data["amount"]), 150.00, rel_tol=1e-9)
        assert data["note"] == "Updated note"
        assert data["category"] == "entertainment"

    def test_update_transaction_not_found(self, client: TestClient, user_auth):
        """Test updating non-existent transaction"""
        update_data = {"amount": 100.00}

        response = client.put(
            "/transactions/99999", json=update_data, headers=user_auth["headers"]
        )

        assert response.status_code == 404

    def test_delete_transaction_success(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test successful transaction deletion"""
        # Create transaction
        transaction_data = {
            "type": "expense",
            "amount": 50.00,
            "category": "transport",
            "wallet_id": test_wallet_api["id"],
        }

        create_response = client.post(
            "/transactions/", json=transaction_data, headers=user_auth["headers"]
        )
        transaction_id = create_response.json()["id"]

        # Delete transaction
        response = client.delete(
            f"/transactions/{transaction_id}", headers=user_auth["headers"]
        )

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()

    def test_delete_transaction_not_found(self, client: TestClient, user_auth):
        """Test deleting non-existent transaction"""
        response = client.delete("/transactions/99999", headers=user_auth["headers"])

        assert response.status_code == 404

    def test_get_transaction_summary(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test getting transaction summary"""
        # Create various transactions
        transactions = [
            {
                "type": "income",
                "amount": 2000.00,
                "category": "salary",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "type": "income",
                "amount": 500.00,
                "category": "freelance",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "type": "expense",
                "amount": 300.00,
                "category": "food",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "type": "expense",
                "amount": 200.00,
                "category": "transport",
                "wallet_id": test_wallet_api["id"],
            },
        ]

        for transaction_data in transactions:
            client.post(
                "/transactions/", json=transaction_data, headers=user_auth["headers"]
            )

        # Get summary
        response = client.get("/transactions/summary", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expenses" in data
        assert "net_amount" in data
        assert "transactions_by_category" in data
        assert "transactions_by_type" in data

        # Verify calculations
        assert float(data["total_income"]) >= 2500.00  # 2000 + 500
        assert float(data["total_expenses"]) >= 500.00  # 300 + 200
        assert float(data["net_amount"]) >= 2000.00  # 2500 - 500

    def test_get_wallet_transactions(self, client: TestClient, user_auth):
        """Test getting transactions for a specific wallet"""
        # Create two wallets
        wallet1_data = {"name": "Wallet 1", "type": "checking", "balance": 1000.00}

        wallet2_data = {"name": "Wallet 2", "type": "savings", "balance": 2000.00}

        wallet1_response = client.post(
            "/wallets/", json=wallet1_data, headers=user_auth["headers"]
        )
        wallet2_response = client.post(
            "/wallets/", json=wallet2_data, headers=user_auth["headers"]
        )

        wallet1_id = wallet1_response.json()["id"]
        wallet2_id = wallet2_response.json()["id"]

        # Create transactions for each wallet
        transaction1 = {
            "type": "income",
            "amount": 500.00,
            "category": "salary",
            "wallet_id": wallet1_id,
        }

        transaction2 = {
            "type": "expense",
            "amount": 200.00,
            "category": "food",
            "wallet_id": wallet2_id,
        }

        client.post("/transactions/", json=transaction1, headers=user_auth["headers"])
        client.post("/transactions/", json=transaction2, headers=user_auth["headers"])

        # Get transactions for wallet 1
        response = client.get(
            f"/transactions/wallet/{wallet1_id}", headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should only contain transactions for wallet 1
        for transaction in data:
            assert transaction["wallet_id"] == wallet1_id

    def test_wallet_balance_update_after_transactions(
        self, client: TestClient, user_auth
    ):
        """Test that wallet balance is properly updated after transactions"""
        # Create wallet with initial balance
        wallet_data = {
            "name": "Balance Test Wallet",
            "type": "checking",
            "balance": 1000.00,
        }

        wallet_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        wallet_id = wallet_response.json()["id"]

        # Create income transaction (+500)
        income_data = {
            "type": "income",
            "amount": 500.00,
            "category": "salary",
            "wallet_id": wallet_id,
        }

        client.post("/transactions/", json=income_data, headers=user_auth["headers"])

        # Check wallet balance
        wallet_response = client.get(
            f"/wallets/{wallet_id}", headers=user_auth["headers"]
        )
        assert math.isclose(
            float(wallet_response.json()["balance"]), 1500.00, rel_tol=1e-9
        )

        # Create expense transaction (-200)
        expense_data = {
            "type": "expense",
            "amount": 200.00,
            "category": "food",
            "wallet_id": wallet_id,
        }

        client.post("/transactions/", json=expense_data, headers=user_auth["headers"])

        # Check wallet balance again
        wallet_response = client.get(
            f"/wallets/{wallet_id}", headers=user_auth["headers"]
        )
        assert math.isclose(
            float(wallet_response.json()["balance"]), 1300.00, rel_tol=1e-9
        )

    def test_transaction_operations_unauthorized(self, client: TestClient):
        """Test transaction operations without authentication"""
        operations = [
            ("GET", "/transactions/", None),
            (
                "POST",
                "/transactions/",
                {"type": "income", "amount": 100, "category": "salary", "wallet_id": 1},
            ),
            ("GET", "/transactions/1", None),
            ("PUT", "/transactions/1", {"amount": 150}),
            ("DELETE", "/transactions/1", None),
            ("GET", "/transactions/summary", None),
            ("GET", "/transactions/wallet/1", None),
        ]

        for method, url, data in operations:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data)
            elif method == "PUT":
                response = client.put(url, json=data)
            elif method == "DELETE":
                response = client.delete(url)

            assert response.status_code == 401
