import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, timedelta
from app.db.models.transfer import Transfer
import math


class TestTransferManagement:
    """Test transfer management endpoints"""

    def test_create_transfer_success(self, client: TestClient, user_auth):
        """Test successful transfer creation"""
        # Create source and target wallets
        source_wallet_data = {
            "name": "Source Wallet",
            "type": "checking",
            "balance": 1000.00,
        }

        target_wallet_data = {
            "name": "Target Wallet",
            "type": "savings",
            "balance": 500.00,
        }

        source_response = client.post(
            "/wallets/", json=source_wallet_data, headers=user_auth["headers"]
        )
        target_response = client.post(
            "/wallets/", json=target_wallet_data, headers=user_auth["headers"]
        )

        source_wallet_id = source_response.json()["id"]
        target_wallet_id = target_response.json()["id"]

        # Create transfer
        transfer_data = {
            "amount": 300.00,
            "source_wallet_id": source_wallet_id,
            "target_wallet_id": target_wallet_id,
            "description": "Monthly savings transfer",
        }

        response = client.post(
            "/transfers/", json=transfer_data, headers=user_auth["headers"]
        )

        assert response.status_code == 201
        data = response.json()
        assert math.isclose(float(data["amount"]), 300.00, rel_tol=1e-9)
        assert data["source_wallet_id"] == source_wallet_id
        assert data["target_wallet_id"] == target_wallet_id
        assert data["description"] == "Monthly savings transfer"
        assert data["source_wallet_name"] == "Source Wallet"
        assert data["target_wallet_name"] == "Target Wallet"
        assert "id" in data
        assert "created_at" in data

    def test_create_transfer_updates_balances(self, client: TestClient, user_auth):
        """Test that transfer creation updates wallet balances correctly"""
        # Create wallets with specific balances
        source_wallet_data = {
            "name": "Balance Test Source",
            "type": "checking",
            "balance": 1500.00,
        }

        target_wallet_data = {
            "name": "Balance Test Target",
            "type": "savings",
            "balance": 2000.00,
        }

        source_response = client.post(
            "/wallets/", json=source_wallet_data, headers=user_auth["headers"]
        )
        target_response = client.post(
            "/wallets/", json=target_wallet_data, headers=user_auth["headers"]
        )

        source_wallet_id = source_response.json()["id"]
        target_wallet_id = target_response.json()["id"]

        # Create transfer
        transfer_data = {
            "amount": 400.00,
            "source_wallet_id": source_wallet_id,
            "target_wallet_id": target_wallet_id,
            "description": "Balance test transfer",
        }

        client.post("/transfers/", json=transfer_data, headers=user_auth["headers"])

        # Check updated balances
        source_balance_response = client.get(
            f"/wallets/{source_wallet_id}", headers=user_auth["headers"]
        )
        target_balance_response = client.get(
            f"/wallets/{target_wallet_id}", headers=user_auth["headers"]
        )

        assert math.isclose(
            float(source_balance_response.json()["balance"]), 1100.00, rel_tol=1e-9
        )  # 1500 - 400
        assert math.isclose(
            float(target_balance_response.json()["balance"]), 2400.00, rel_tol=1e-9
        )  # 2000 + 400

    def test_create_transfer_same_wallet_error(
        self, client: TestClient, user_auth, test_wallet_api
    ):
        """Test transfer creation with same source and target wallet"""
        transfer_data = {
            "amount": 100.00,
            "source_wallet_id": test_wallet_api["id"],
            "target_wallet_id": test_wallet_api["id"],
            "description": "Invalid same wallet transfer",
        }

        response = client.post(
            "/transfers/", json=transfer_data, headers=user_auth["headers"]
        )

        assert response.status_code == 422  # Validation error

    def test_create_transfer_insufficient_funds(self, client: TestClient, user_auth):
        """Test transfer creation with insufficient funds"""
        # Create wallets with low balance
        source_wallet_data = {
            "name": "Low Balance Wallet",
            "type": "checking",
            "balance": 50.00,
        }

        target_wallet_data = {
            "name": "Target Wallet",
            "type": "savings",
            "balance": 100.00,
        }

        source_response = client.post(
            "/wallets/", json=source_wallet_data, headers=user_auth["headers"]
        )
        target_response = client.post(
            "/wallets/", json=target_wallet_data, headers=user_auth["headers"]
        )

        source_wallet_id = source_response.json()["id"]
        target_wallet_id = target_response.json()["id"]

        # Try to transfer more than available
        transfer_data = {
            "amount": 100.00,
            "source_wallet_id": source_wallet_id,
            "target_wallet_id": target_wallet_id,
            "description": "Insufficient funds test",
        }

        response = client.post(
            "/transfers/", json=transfer_data, headers=user_auth["headers"]
        )

        assert response.status_code == 400
        assert "insufficient funds" in response.json()["detail"].lower()

    def test_create_transfer_credit_wallet_overdraft(
        self, client: TestClient, user_auth
    ):
        """Test transfer from credit wallet (should allow overdraft)"""
        # Create credit wallet and target wallet
        source_wallet_data = {"name": "Credit Card", "type": "credit", "balance": 0.00}

        target_wallet_data = {
            "name": "Checking Account",
            "type": "checking",
            "balance": 100.00,
        }

        source_response = client.post(
            "/wallets/", json=source_wallet_data, headers=user_auth["headers"]
        )
        target_response = client.post(
            "/wallets/", json=target_wallet_data, headers=user_auth["headers"]
        )

        source_wallet_id = source_response.json()["id"]
        target_wallet_id = target_response.json()["id"]

        # Transfer from credit wallet (should work)
        transfer_data = {
            "amount": 500.00,
            "source_wallet_id": source_wallet_id,
            "target_wallet_id": target_wallet_id,
            "description": "Credit advance",
        }

        response = client.post(
            "/transfers/", json=transfer_data, headers=user_auth["headers"]
        )

        assert response.status_code == 201

    def test_create_transfer_unauthorized(self, client: TestClient):
        """Test transfer creation without authentication"""
        transfer_data = {
            "amount": 100.00,
            "source_wallet_id": 1,
            "target_wallet_id": 2,
            "description": "Unauthorized transfer",
        }

        response = client.post("/transfers/", json=transfer_data)

        assert response.status_code == 401

    def test_create_transfer_invalid_wallet(self, client: TestClient, user_auth):
        """Test transfer creation with non-existent wallet"""
        transfer_data = {
            "amount": 100.00,
            "source_wallet_id": 99999,
            "target_wallet_id": 99998,
            "description": "Invalid wallet transfer",
        }

        response = client.post(
            "/transfers/", json=transfer_data, headers=user_auth["headers"]
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_get_user_transfers(self, client: TestClient, user_auth):
        """Test getting user's transfers"""
        # Create wallets and transfers
        wallet1_data = {"name": "Wallet 1", "type": "checking", "balance": 1000.00}
        wallet2_data = {"name": "Wallet 2", "type": "savings", "balance": 500.00}

        wallet1_response = client.post(
            "/wallets/", json=wallet1_data, headers=user_auth["headers"]
        )
        wallet2_response = client.post(
            "/wallets/", json=wallet2_data, headers=user_auth["headers"]
        )

        wallet1_id = wallet1_response.json()["id"]
        wallet2_id = wallet2_response.json()["id"]

        # Create a couple of transfers
        transfers = [
            {
                "amount": 200.00,
                "source_wallet_id": wallet1_id,
                "target_wallet_id": wallet2_id,
                "description": "Transfer 1",
            },
            {
                "amount": 150.00,
                "source_wallet_id": wallet2_id,
                "target_wallet_id": wallet1_id,
                "description": "Transfer 2",
            },
        ]

        for transfer_data in transfers:
            client.post("/transfers/", json=transfer_data, headers=user_auth["headers"])

        # Get transfers
        response = client.get("/transfers/", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()
        assert "transfers" in data
        assert "total" in data
        assert data["total"] >= 2
        assert len(data["transfers"]) >= 2

    def test_get_transfers_with_filters(self, client: TestClient, user_auth):
        """Test getting transfers with filters"""
        # Create wallets
        wallet1_data = {
            "name": "Filter Wallet 1",
            "type": "checking",
            "balance": 2000.00,
        }
        wallet2_data = {
            "name": "Filter Wallet 2",
            "type": "savings",
            "balance": 1000.00,
        }
        wallet3_data = {"name": "Filter Wallet 3", "type": "cash", "balance": 500.00}

        wallet1_response = client.post(
            "/wallets/", json=wallet1_data, headers=user_auth["headers"]
        )
        wallet2_response = client.post(
            "/wallets/", json=wallet2_data, headers=user_auth["headers"]
        )
        wallet3_response = client.post(
            "/wallets/", json=wallet3_data, headers=user_auth["headers"]
        )

        wallet1_id = wallet1_response.json()["id"]
        wallet2_id = wallet2_response.json()["id"]
        wallet3_id = wallet3_response.json()["id"]

        # Create transfers with different amounts
        transfers = [
            {
                "amount": 100.00,
                "source_wallet_id": wallet1_id,
                "target_wallet_id": wallet2_id,
                "description": "Small transfer",
            },
            {
                "amount": 500.00,
                "source_wallet_id": wallet1_id,
                "target_wallet_id": wallet3_id,
                "description": "Large transfer",
            },
            {
                "amount": 250.00,
                "source_wallet_id": wallet2_id,
                "target_wallet_id": wallet3_id,
                "description": "Medium transfer",
            },
        ]

        for transfer_data in transfers:
            client.post("/transfers/", json=transfer_data, headers=user_auth["headers"])

        # Filter by source wallet
        response = client.get(
            "/transfers/",
            params={"source_wallet_id": wallet1_id},
            headers=user_auth["headers"],
        )

        assert response.status_code == 200
        data = response.json()
        wallet1_transfers = [
            t for t in data["transfers"] if t["source_wallet_id"] == wallet1_id
        ]
        assert len(wallet1_transfers) >= 2

        # Filter by minimum amount
        response = client.get(
            "/transfers/", params={"min_amount": 200.00}, headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        large_transfers = [t for t in data["transfers"] if float(t["amount"]) >= 200.00]
        assert len(large_transfers) >= 2

    def test_get_transfer_by_id(self, client: TestClient, user_auth):
        """Test getting specific transfer by ID"""
        # Create wallets and transfer
        wallet1_data = {
            "name": "ID Test Wallet 1",
            "type": "checking",
            "balance": 800.00,
        }
        wallet2_data = {
            "name": "ID Test Wallet 2",
            "type": "savings",
            "balance": 200.00,
        }

        wallet1_response = client.post(
            "/wallets/", json=wallet1_data, headers=user_auth["headers"]
        )
        wallet2_response = client.post(
            "/wallets/", json=wallet2_data, headers=user_auth["headers"]
        )

        wallet1_id = wallet1_response.json()["id"]
        wallet2_id = wallet2_response.json()["id"]

        transfer_data = {
            "amount": 300.00,
            "source_wallet_id": wallet1_id,
            "target_wallet_id": wallet2_id,
            "description": "ID test transfer",
        }

        create_response = client.post(
            "/transfers/", json=transfer_data, headers=user_auth["headers"]
        )
        transfer_id = create_response.json()["id"]

        # Get the transfer
        response = client.get(f"/transfers/{transfer_id}", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transfer_id
        assert math.isclose(float(data["amount"]), 300.00, rel_tol=1e-9)
        assert data["description"] == "ID test transfer"

    def test_get_transfer_not_found(self, client: TestClient, user_auth):
        """Test getting non-existent transfer"""
        response = client.get("/transfers/99999", headers=user_auth["headers"])

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_wallet_transfers(self, client: TestClient, user_auth):
        """Test getting transfers for a specific wallet"""
        # Create wallets
        wallet1_data = {
            "name": "Wallet Transfer Test 1",
            "type": "checking",
            "balance": 1500.00,
        }
        wallet2_data = {
            "name": "Wallet Transfer Test 2",
            "type": "savings",
            "balance": 1000.00,
        }
        wallet3_data = {
            "name": "Wallet Transfer Test 3",
            "type": "cash",
            "balance": 500.00,
        }

        wallet1_response = client.post(
            "/wallets/", json=wallet1_data, headers=user_auth["headers"]
        )
        wallet2_response = client.post(
            "/wallets/", json=wallet2_data, headers=user_auth["headers"]
        )
        wallet3_response = client.post(
            "/wallets/", json=wallet3_data, headers=user_auth["headers"]
        )

        wallet1_id = wallet1_response.json()["id"]
        wallet2_id = wallet2_response.json()["id"]
        wallet3_id = wallet3_response.json()["id"]

        # Create transfers involving wallet1
        transfers = [
            {
                "amount": 200.00,
                "source_wallet_id": wallet1_id,
                "target_wallet_id": wallet2_id,
                "description": "From wallet1 to wallet2",
            },
            {
                "amount": 100.00,
                "source_wallet_id": wallet2_id,
                "target_wallet_id": wallet1_id,
                "description": "From wallet2 to wallet1",
            },
            {
                "amount": 50.00,
                "source_wallet_id": wallet3_id,
                "target_wallet_id": wallet2_id,
                "description": "Not involving wallet1",
            },
        ]

        for transfer_data in transfers:
            client.post("/transfers/", json=transfer_data, headers=user_auth["headers"])

        # Get transfers for wallet1
        response = client.get(
            f"/transfers/wallet/{wallet1_id}", headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should contain transfers where wallet1 is either source or target
        wallet1_transfers = [
            t
            for t in data
            if t["source_wallet_id"] == wallet1_id
            or t["target_wallet_id"] == wallet1_id
        ]
        assert len(wallet1_transfers) >= 2

    def test_get_transfer_summary(self, client: TestClient, user_auth):
        """Test getting transfer summary"""
        # Create wallets
        wallet1_data = {
            "name": "Summary Wallet 1",
            "type": "checking",
            "balance": 2000.00,
        }
        wallet2_data = {
            "name": "Summary Wallet 2",
            "type": "savings",
            "balance": 1000.00,
        }

        wallet1_response = client.post(
            "/wallets/", json=wallet1_data, headers=user_auth["headers"]
        )
        wallet2_response = client.post(
            "/wallets/", json=wallet2_data, headers=user_auth["headers"]
        )

        wallet1_id = wallet1_response.json()["id"]
        wallet2_id = wallet2_response.json()["id"]

        # Create various transfers
        transfers = [
            {
                "amount": 300.00,
                "source_wallet_id": wallet1_id,
                "target_wallet_id": wallet2_id,
                "description": "Transfer 1",
            },
            {
                "amount": 150.00,
                "source_wallet_id": wallet2_id,
                "target_wallet_id": wallet1_id,
                "description": "Transfer 2",
            },
            {
                "amount": 200.00,
                "source_wallet_id": wallet1_id,
                "target_wallet_id": wallet2_id,
                "description": "Transfer 3",
            },
        ]

        for transfer_data in transfers:
            client.post("/transfers/", json=transfer_data, headers=user_auth["headers"])

        # Get summary
        response = client.get("/transfers/summary", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()
        assert "total_transfers" in data
        assert "total_amount_transferred" in data
        assert "transfers_by_wallet" in data
        assert "recent_transfers" in data

        # Verify calculations
        assert data["total_transfers"] >= 3
        assert float(data["total_amount_transferred"]) >= 650.00  # 300 + 150 + 200

    def test_get_wallet_transfer_summary(self, client: TestClient, user_auth):
        """Test getting transfer summary for a specific wallet"""
        # Create wallets
        wallet1_data = {
            "name": "Wallet Summary Test 1",
            "type": "checking",
            "balance": 2000.00,
        }
        wallet2_data = {
            "name": "Wallet Summary Test 2",
            "type": "savings",
            "balance": 1000.00,
        }

        wallet1_response = client.post(
            "/wallets/", json=wallet1_data, headers=user_auth["headers"]
        )
        wallet2_response = client.post(
            "/wallets/", json=wallet2_data, headers=user_auth["headers"]
        )

        wallet1_id = wallet1_response.json()["id"]
        wallet2_id = wallet2_response.json()["id"]

        # Create transfers where wallet1 sends and receives money
        transfers = [
            {
                "amount": 400.00,
                "source_wallet_id": wallet1_id,
                "target_wallet_id": wallet2_id,
                "description": "Sent from wallet1",
            },
            {
                "amount": 100.00,
                "source_wallet_id": wallet2_id,
                "target_wallet_id": wallet1_id,
                "description": "Received by wallet1",
            },
            {
                "amount": 200.00,
                "source_wallet_id": wallet1_id,
                "target_wallet_id": wallet2_id,
                "description": "Sent from wallet1 again",
            },
        ]

        for transfer_data in transfers:
            client.post("/transfers/", json=transfer_data, headers=user_auth["headers"])

        # Get wallet1 summary
        response = client.get(
            f"/transfers/wallet/{wallet1_id}/summary", headers=user_auth["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        assert data["wallet_id"] == wallet1_id
        assert data["wallet_name"] == "Wallet Summary Test 1"
        assert math.isclose(
            float(data["total_sent"]), 600.00, rel_tol=1e-9
        )  # 400 + 200
        assert math.isclose(float(data["total_received"]), 100.00, rel_tol=1e-9)
        assert math.isclose(
            float(data["net_amount"]), -500.00, rel_tol=1e-9
        )  # 100 - 600
        assert data["transfer_count"] == 3

    def test_delete_transfer_success(self, client: TestClient, user_auth):
        """Test successful transfer deletion with balance reversal"""
        # Create wallets with specific balances
        wallet1_data = {
            "name": "Delete Test Wallet 1",
            "type": "checking",
            "balance": 1000.00,
        }
        wallet2_data = {
            "name": "Delete Test Wallet 2",
            "type": "savings",
            "balance": 500.00,
        }

        wallet1_response = client.post(
            "/wallets/", json=wallet1_data, headers=user_auth["headers"]
        )
        wallet2_response = client.post(
            "/wallets/", json=wallet2_data, headers=user_auth["headers"]
        )

        wallet1_id = wallet1_response.json()["id"]
        wallet2_id = wallet2_response.json()["id"]

        # Create transfer
        transfer_data = {
            "amount": 300.00,
            "source_wallet_id": wallet1_id,
            "target_wallet_id": wallet2_id,
            "description": "Delete test transfer",
        }

        create_response = client.post(
            "/transfers/", json=transfer_data, headers=user_auth["headers"]
        )
        transfer_id = create_response.json()["id"]

        # Verify balances after transfer
        wallet1_response = client.get(
            f"/wallets/{wallet1_id}", headers=user_auth["headers"]
        )
        wallet2_response = client.get(
            f"/wallets/{wallet2_id}", headers=user_auth["headers"]
        )

        assert math.isclose(
            float(wallet1_response.json()["balance"]), 700.00, rel_tol=1e-9
        )  # 1000 - 300
        assert math.isclose(
            float(wallet2_response.json()["balance"]), 800.00, rel_tol=1e-9
        )  # 500 + 300

        # Delete transfer
        response = client.delete(
            f"/transfers/{transfer_id}", headers=user_auth["headers"]
        )

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        assert "reversed" in response.json()["message"].lower()

        # Verify balances are reversed
        wallet1_response = client.get(
            f"/wallets/{wallet1_id}", headers=user_auth["headers"]
        )
        wallet2_response = client.get(
            f"/wallets/{wallet2_id}", headers=user_auth["headers"]
        )

        assert math.isclose(
            float(wallet1_response.json()["balance"]), 1000.00, rel_tol=1e-9
        )  # Original balance
        assert math.isclose(
            float(wallet2_response.json()["balance"]), 500.00, rel_tol=1e-9
        )  # Original balance

    def test_delete_transfer_not_found(self, client: TestClient, user_auth):
        """Test deleting non-existent transfer"""
        response = client.delete("/transfers/99999", headers=user_auth["headers"])

        assert response.status_code == 404

    def test_alternative_transfer_endpoint(self, client: TestClient, user_auth):
        """Test alternative transfer creation endpoint via wallets"""
        # Create wallets
        wallet1_data = {
            "name": "Alt Endpoint Wallet 1",
            "type": "checking",
            "balance": 1200.00,
        }
        wallet2_data = {
            "name": "Alt Endpoint Wallet 2",
            "type": "savings",
            "balance": 800.00,
        }

        wallet1_response = client.post(
            "/wallets/", json=wallet1_data, headers=user_auth["headers"]
        )
        wallet2_response = client.post(
            "/wallets/", json=wallet2_data, headers=user_auth["headers"]
        )

        wallet1_id = wallet1_response.json()["id"]
        wallet2_id = wallet2_response.json()["id"]

        # Create transfer using alternative endpoint
        response = client.post(
            f"/transfers/wallets/{wallet1_id}/transfer",
            params={
                "target_wallet_id": wallet2_id,
                "amount": 250.00,
                "description": "Alternative endpoint test",
            },
            headers=user_auth["headers"],
        )

        assert response.status_code == 201
        data = response.json()
        assert math.isclose(float(data["amount"]), 250.00, rel_tol=1e-9)
        assert data["source_wallet_id"] == wallet1_id
        assert data["target_wallet_id"] == wallet2_id
        assert data["description"] == "Alternative endpoint test"

    def test_transfer_operations_unauthorized(self, client: TestClient):
        """Test transfer operations without authentication"""
        operations = [
            ("GET", "/transfers/", None),
            (
                "POST",
                "/transfers/",
                {"amount": 100, "source_wallet_id": 1, "target_wallet_id": 2},
            ),
            ("GET", "/transfers/1", None),
            ("DELETE", "/transfers/1", None),
            ("GET", "/transfers/summary", None),
            ("GET", "/transfers/wallet/1", None),
            ("GET", "/transfers/wallet/1/summary", None),
        ]

        for method, url, data in operations:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data)
            elif method == "DELETE":
                response = client.delete(url)

            assert response.status_code == 401
