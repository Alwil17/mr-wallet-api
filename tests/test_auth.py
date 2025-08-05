import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAuth:
    """Test authentication endpoints"""

    def test_register_user_success(self, client: TestClient):
        """Test successful user registration"""
        user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert data["role"] == "user"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_user_duplicate_email(self, client: TestClient, test_user):
        """Test registration with existing email"""
        user_data = {
            "name": "Duplicate User",
            "email": test_user.email,
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()

    def test_register_user_invalid_data(self, client: TestClient):
        """Test registration with invalid data"""
        user_data = {
            "name": "",
            "email": "invalid-email",
            "password": "123"  # Too short
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, test_user):
        """Test successful login"""
        form_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/auth/token", data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, test_user):
        """Test login with invalid credentials"""
        form_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/token", data=form_data)
        
        assert response.status_code == 401
        assert "incorrect email or password" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        form_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/token", data=form_data)
        
        assert response.status_code == 401

    def test_refresh_token_success(self, client: TestClient, user_auth):
        """Test successful token refresh"""
        response = client.post(
            "/auth/token/refresh",
            json={"refresh_token": user_auth["refresh_token"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # New tokens should be different
        assert data["access_token"] != user_auth["access_token"]
        assert data["refresh_token"] != user_auth["refresh_token"]

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token"""
        response = client.post(
            "/auth/token/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )
        
        assert response.status_code == 401
        assert "invalid refresh token" in response.json()["detail"].lower()

    def test_logout_success(self, client: TestClient, user_auth):
        """Test successful logout"""
        response = client.post(
            "/auth/logout",
            json={"refresh_token": user_auth["refresh_token"]},
            headers=user_auth["headers"]
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

    def test_logout_invalid_token(self, client: TestClient, auth_headers):
        """Test logout with invalid refresh token"""
        response = client.post(
            "/auth/logout",
            json={"refresh_token": "invalid_token"},
            headers=auth_headers
        )
        
        assert response.status_code == 401
        assert "invalid refresh token" in response.json()["detail"].lower()

    def test_get_profile(self, client: TestClient, test_user, auth_headers):
        """Test getting user profile"""
        response = client.get("/auth/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["id"] == test_user.id
        assert "hashed_password" not in data

    def test_get_profile_unauthorized(self, client: TestClient):
        """Test getting profile without authentication"""
        response = client.get("/auth/profile")
        
        assert response.status_code == 401

    def test_update_profile(self, client: TestClient, auth_headers):
        """Test updating user profile"""
        update_data = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        
        response = client.put("/auth/profile", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["email"] == update_data["email"]

    def test_change_password(self, client: TestClient, auth_headers):
        """Test changing password"""
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        
        response = client.put("/auth/password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Password updated successfully"

    def test_change_password_wrong_current(self, client: TestClient, auth_headers):
        """Test changing password with wrong current password"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        
        response = client.put("/auth/password", json=password_data, headers=auth_headers)
        
        assert response.status_code == 400
        assert "current password is incorrect" in response.json()["detail"].lower()

    def test_delete_account_success(self, client: TestClient, user_auth):
        """Test successful account deletion"""
        response = client.delete(
            "/auth/account",
            headers=user_auth["headers"]
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Account deleted successfully"

    def test_delete_account_unauthorized(self, client: TestClient):
        """Test account deletion without authentication"""
        response = client.delete("/auth/account")
        
        assert response.status_code == 401

    def test_get_gdpr_data(self, client: TestClient, test_user, auth_headers):
        """Test getting GDPR data export"""
        response = client.get("/auth/gdpr/data", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_info"]["email"] == test_user.email
        assert data["user_info"]["name"] == test_user.name
        assert "wallets" in data
        assert "transactions" in data
        assert "debts" in data
        assert "transfers" in data
        assert "export_timestamp" in data

    def test_protected_route_with_valid_token(self, client: TestClient, auth_headers):
        """Test accessing protected route with valid token"""
        response = client.get("/auth/profile", headers=auth_headers)
        
        assert response.status_code == 200

    def test_protected_route_with_invalid_token(self, client: TestClient):
        """Test accessing protected route with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/profile", headers=headers)
        
        assert response.status_code == 401

    def test_protected_route_without_token(self, client: TestClient):
        """Test accessing protected route without token"""
        response = client.get("/auth/profile")
        
        assert response.status_code == 401
