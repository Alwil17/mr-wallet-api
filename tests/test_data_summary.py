import pytest
from fastapi.testclient import TestClient


class TestDataSummary:
    """Test data summary endpoint"""

    def test_get_data_summary_success(self, client: TestClient, user_auth):
        """Test successful data summary retrieval"""
        response = client.get("/auth/data-summary", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()

        # Verify all expected fields are present
        assert "user_id" in data
        assert "email" in data
        assert "account_created" in data
        assert "wallets_count" in data
        assert "transactions_count" in data
        assert "debts_count" in data
        assert "transfers_count" in data
        assert "total_balance" in data
        assert "data_summary_generated_at" in data

        # Verify data types
        assert isinstance(data["user_id"], int)
        assert isinstance(data["email"], str)
        assert isinstance(data["wallets_count"], int)
        assert isinstance(data["transactions_count"], int)
        assert isinstance(data["debts_count"], int)
        assert isinstance(data["transfers_count"], int)

        # Verify counts are non-negative
        assert data["wallets_count"] >= 0
        assert data["transactions_count"] >= 0
        assert data["debts_count"] >= 0
        assert data["transfers_count"] >= 0

    def test_get_data_summary_with_data(self, client: TestClient, user_auth):
        """Test data summary with actual data"""
        # Create a wallet first
        wallet_data = {"name": "Test Wallet", "type": "checking", "balance": 1000.00}
        wallet_response = client.post(
            "/wallets/", json=wallet_data, headers=user_auth["headers"]
        )
        assert wallet_response.status_code == 201

        # Get data summary (should show at least 1 wallet)
        response = client.get("/auth/data-summary", headers=user_auth["headers"])

        assert response.status_code == 200
        data = response.json()

        # Verify counts reflect the created data
        assert data["wallets_count"] >= 1

    def test_get_data_summary_unauthorized(self, client: TestClient):
        """Test data summary without authentication"""
        response = client.get("/auth/data-summary")

        assert response.status_code == 401
