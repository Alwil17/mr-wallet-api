import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from app.db.models.debt import Debt
import math


class TestDebtManagement:
    """Test debt management endpoints"""

    def test_create_debt_owed_success(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test successful creation of debt (money owed to user)"""
        debt_data = {
            "amount": 500.00,
            "borrower": "John Doe",
            "type": "owed",
            "description": "Loan to John for car repair",
            "due_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "wallet_id": test_wallet_api["id"],
        }

        response = client.post("/debts/", json=debt_data, headers=user_auth["headers"])

        assert response.status_code == 201
        data = response.json()
        assert math.isclose(float(data["amount"]), 500.00, rel_tol=1e-9)
        assert data["borrower"] == "John Doe"
        assert data["type"] == "owed"
        assert data["description"] == "Loan to John for car repair"
        assert data["is_paid"] == False
        assert data["wallet_id"] == test_wallet_api["id"]
        assert "id" in data
        assert "created_at" in data

    def test_create_debt_given_success(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test successful creation of debt (money user owes)"""
        debt_data = {
            "amount": 300.00,
            "borrower": "Jane Smith",
            "type": "given",
            "description": "Money borrowed from Jane",
            "wallet_id": test_wallet_api["id"],
        }

        response = client.post("/debts/", json=debt_data, headers=user_auth["headers"])

        assert response.status_code == 201
        data = response.json()
        assert math.isclose(float(data["amount"]), 300.00, rel_tol=1e-9)
        assert data["borrower"] == "Jane Smith"
        assert data["type"] == "given"
        assert data["description"] == "Money borrowed from Jane"
        assert data["is_paid"] == False

    def test_create_debt_unauthorized(self, client: TestClient, test_wallet_api):
        """Test debt creation without authentication"""
        debt_data = {
            "amount": 100.00,
            "borrower": "Someone",
            "type": "owed",
            "wallet_id": test_wallet_api["id"],
        }

        response = client.post("/debts/", json=debt_data)

        assert response.status_code == 401

    def test_create_debt_invalid_wallet(self, client: TestClient, user_auth):
        """Test debt creation with non-existent wallet"""
        debt_data = {
            "amount": 100.00,
            "borrower": "Someone",
            "type": "owed",
            "wallet_id": 99999,
        }

        response = client.post("/debts/", json=debt_data, headers=user_auth["headers"])

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_create_debt_invalid_type(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test debt creation with invalid type"""
        debt_data = {
            "amount": 100.00,
            "borrower": "Someone",
            "type": "invalid_type",
            "wallet_id": test_wallet_api["id"],
        }

        response = client.post("/debts/", json=debt_data, headers=user_auth["headers"])

        assert response.status_code == 422  # Validation error

    def test_create_debt_negative_amount(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test debt creation with negative amount"""
        debt_data = {
            "amount": -100.00,
            "borrower": "Someone",
            "type": "owed",
            "wallet_id": test_wallet_api["id"],
        }

        response = client.post("/debts/", json=debt_data, headers=user_auth["headers"])

        assert response.status_code == 422  # Validation error

    def test_get_user_debts(self, client: TestClient, user_auth, test_wallet_api):
        """Test getting user's debts"""
        # Create a couple of debts first
        debts = [
            {
                "amount": 400.00,
                "borrower": "Alice",
                "type": "owed",
                "description": "Loan to Alice",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "amount": 200.00,
                "borrower": "Bob",
                "type": "given",
                "description": "Money borrowed from Bob",
                "wallet_id": test_wallet_api["id"],
            },
        ]

        for debt_data in debts:
            client.post("/debts/", json=debt_data, headers=user_auth["headers"])

        # Get debts
        response = client.get("/debts/", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()
        assert "debts" in data
        assert "total" in data
        assert data["total"] >= 2  # At least the 2 we created
        assert len(data["debts"]) >= 2

    def test_get_debts_with_filters(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test getting debts with filters"""
        # Create debts with different types
        debts = [
            {
                "amount": 500.00,
                "borrower": "Charlie",
                "type": "owed",
                "description": "Money owed by Charlie",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "amount": 300.00,
                "borrower": "Diana",
                "type": "given",
                "description": "Money owed to Diana",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "amount": 150.00,
                "borrower": "Eve",
                "type": "owed",
                "description": "Small loan to Eve",
                "wallet_id": test_wallet_api["id"],
            },
        ]

        for debt_data in debts:
            client.post("/debts/", json=debt_data, headers=user_auth["headers"])

        # Filter by type (owed)
        response = client.get(
            "/debts/", params={"debt_type": "owed"}, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        owed_debts = [d for d in data["debts"] if d["type"] == "owed"]
        assert len(owed_debts) >= 2

        # Filter by type (given)
        response = client.get(
            "/debts/", params={"debt_type": "given"}, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        given_debts = [d for d in data["debts"] if d["type"] == "given"]
        assert len(given_debts) >= 1

        # Filter by borrower
        response = client.get(
            "/debts/", params={"borrower": "Charlie"}, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        charlie_debts = [d for d in data["debts"] if "Charlie" in d["borrower"]]
        assert len(charlie_debts) >= 1

    def test_get_debt_by_id(self, client: TestClient, user_auth, test_wallet_api):
        """Test getting specific debt by ID"""
        # Create a debt
        debt_data = {
            "amount": 750.00,
            "borrower": "Frank",
            "type": "owed",
            "description": "Big loan to Frank",
            "wallet_id": test_wallet_api["id"],
        }

        create_response = client.post(
            "/debts/", json=debt_data, headers=user_auth["headers"]
        )
        debt_id = create_response.json()["id"]

        # Get the debt
        response = client.get(f"/debts/{debt_id}", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == debt_id
        assert math.isclose(float(data["amount"]), 750.00, rel_tol=1e-9)
        assert data["borrower"] == "Frank"

    def test_get_debt_not_found(self, client: TestClient, user_auth):
        """Test getting non-existent debt"""
        response = client.get("/debts/99999", headers=user_auth["headers"])

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_debt_success(self, client: TestClient, user_auth, test_wallet_api):
        """Test successful debt update"""
        # Create debt
        debt_data = {
            "amount": 400.00,
            "borrower": "Grace",
            "type": "owed",
            "description": "Original description",
            "wallet_id": test_wallet_api["id"],
        }

        create_response = client.post(
            "/debts/", json=debt_data, headers=user_auth["headers"]
        )
        debt_id = create_response.json()["id"]

        # Update debt
        update_data = {
            "amount": 600.00,
            "description": "Updated description",
            "due_date": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat(),
        }

        response = client.put(
            f"/debts/{debt_id}", json=update_data, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert math.isclose(float(data["amount"]), 600.00, rel_tol=1e-9)
        assert data["description"] == "Updated description"
        assert data["due_date"] is not None

    def test_update_debt_not_found(self, client: TestClient, user_auth):
        """Test updating non-existent debt"""
        update_data = {"amount": 100.00}

        response = client.put(
            "/debts/99999", json=update_data, headers=user_auth["headers"]
        )

        assert response.status_code == 404

    def test_mark_debt_as_paid(self, client: TestClient, user_auth, test_wallet_api):
        """Test marking debt as paid"""
        # Create debt
        debt_data = {
            "amount": 250.00,
            "borrower": "Henry",
            "type": "owed",
            "wallet_id": test_wallet_api["id"],
        }

        create_response = client.post(
            "/debts/", json=debt_data, headers=user_auth["headers"]
        )
        debt_id = create_response.json()["id"]

        # Mark as paid
        payment_data = {"is_paid": True, "payment_note": "Paid in full on time"}

        response = client.patch(
            f"/debts/{debt_id}/payment", json=payment_data, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_paid"] == True

    def test_mark_debt_as_unpaid(self, client: TestClient, user_auth, test_wallet_api):
        """Test marking debt as unpaid (reversing payment)"""
        # Create and mark debt as paid first
        debt_data = {
            "amount": 350.00,
            "borrower": "Ivy",
            "type": "given",
            "wallet_id": test_wallet_api["id"],
        }

        create_response = client.post(
            "/debts/", json=debt_data, headers=user_auth["headers"]
        )
        debt_id = create_response.json()["id"]

        # Mark as paid first
        client.patch(
            f"/debts/{debt_id}/payment",
            json={"is_paid": True},
            headers=user_auth["headers"],
        )

        # Mark as unpaid
        payment_data = {"is_paid": False}

        response = client.patch(
            f"/debts/{debt_id}/payment", json=payment_data, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_paid"] == False

    def test_delete_debt_success(self, client: TestClient, user_auth, test_wallet_api):
        """Test successful debt deletion"""
        # Create debt
        debt_data = {
            "amount": 150.00,
            "borrower": "Jack",
            "type": "owed",
            "wallet_id": test_wallet_api["id"],
        }

        create_response = client.post(
            "/debts/", json=debt_data, headers=user_auth["headers"]
        )
        debt_id = create_response.json()["id"]

        # Delete debt
        response = client.delete(f"/debts/{debt_id}", headers=user_auth["headers"])

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()

    def test_delete_debt_not_found(self, client: TestClient, user_auth):
        """Test deleting non-existent debt"""
        response = client.delete("/debts/99999", headers=user_auth["headers"])

        assert response.status_code == 404

    def test_get_debt_summary(self, client: TestClient, user_auth, test_wallet_api):
        """Test getting debt summary"""
        # Create various debts
        debts = [
            {
                "amount": 1000.00,
                "borrower": "Kelly",
                "type": "owed",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "amount": 500.00,
                "borrower": "Liam",
                "type": "owed",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "amount": 300.00,
                "borrower": "Mia",
                "type": "given",
                "wallet_id": test_wallet_api["id"],
            },
            {
                "amount": 200.00,
                "borrower": "Noah",
                "type": "given",
                "wallet_id": test_wallet_api["id"],
            },
        ]

        debt_ids = []
        for debt_data in debts:
            response = client.post(
                "/debts/", json=debt_data, headers=user_auth["headers"]
            )
            debt_ids.append(response.json()["id"])

        # Mark one debt as paid
        client.patch(
            f"/debts/{debt_ids[0]}/payment",
            json={"is_paid": True},
            headers=user_auth["headers"],
        )

        # Get summary
        response = client.get("/debts/summary", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()
        assert "total_debts" in data
        assert "total_amount_owed" in data
        assert "total_amount_given" in data
        assert "net_position" in data
        assert "paid_debts" in data
        assert "unpaid_debts" in data
        assert "overdue_debts" in data
        assert "debts_by_type" in data

        # Verify calculations
        assert data["total_debts"] >= 4
        assert float(data["total_amount_owed"]) >= 1500.00  # 1000 + 500
        assert float(data["total_amount_given"]) >= 500.00  # 300 + 200
        assert float(data["net_position"]) >= 1000.00  # 1500 - 500
        assert data["paid_debts"] >= 1
        assert data["unpaid_debts"] >= 3

    def test_get_wallet_debts(self, client: TestClient, user_auth):
        """Test getting debts for a specific wallet"""
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

        # Create debts for each wallet
        debt1 = {
            "amount": 500.00,
            "borrower": "Olivia",
            "type": "owed",
            "wallet_id": wallet1_id,
        }

        debt2 = {
            "amount": 300.00,
            "borrower": "Paul",
            "type": "given",
            "wallet_id": wallet2_id,
        }

        client.post("/debts/", json=debt1, headers=user_auth["headers"])
        client.post("/debts/", json=debt2, headers=user_auth["headers"])

        # Get debts for wallet 1
        response = client.get(
            f"/debts/wallet/{wallet1_id}", headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should only contain debts for wallet 1
        for debt in data:
            assert debt["wallet_id"] == wallet1_id

    def test_overdue_debts_filter(self, client: TestClient, user_auth, test_wallet_api):
        """Test filtering for overdue debts"""
        # Create an overdue debt (due date in the past)
        overdue_debt = {
            "amount": 400.00,
            "borrower": "Quinn",
            "type": "owed",
            "due_date": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
            "wallet_id": test_wallet_api["id"],
        }

        # Create a future debt
        future_debt = {
            "amount": 300.00,
            "borrower": "Rachel",
            "type": "owed",
            "due_date": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
            "wallet_id": test_wallet_api["id"],
        }

        client.post("/debts/", json=overdue_debt, headers=user_auth["headers"])
        client.post("/debts/", json=future_debt, headers=user_auth["headers"])

        # Filter for overdue debts only
        response = client.get(
            "/debts/", params={"overdue_only": True}, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        # Should contain at least the overdue debt we created
        overdue_debts = [d for d in data["debts"] if not d["is_paid"]]
        assert len(overdue_debts) >= 1

    def test_debt_operations_unauthorized(self, client: TestClient):
        """Test debt operations without authentication"""
        operations = [
            ("GET", "/debts/", None),
            (
                "POST",
                "/debts/",
                {"amount": 100, "borrower": "Someone", "type": "owed", "wallet_id": 1},
            ),
            ("GET", "/debts/1", None),
            ("PUT", "/debts/1", {"amount": 150}),
            ("PATCH", "/debts/1/payment", {"is_paid": True}),
            ("DELETE", "/debts/1", None),
            ("GET", "/debts/summary", None),
            ("GET", "/debts/wallet/1", None),
        ]

        for method, url, data in operations:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data)
            elif method == "PUT":
                response = client.put(url, json=data)
            elif method == "PATCH":
                response = client.patch(url, json=data)
            elif method == "DELETE":
                response = client.delete(url)

            assert response.status_code == 401
