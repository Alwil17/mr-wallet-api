#!/usr/bin/env python3
"""
Simple test script to verify the authentication flow is working correctly.
This tests the core authentication endpoints: register, login, refresh, logout.
"""

import requests
import json
import random
import string
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def generate_test_email() -> str:
    """Generate a random test email"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_str}@example.com"


def test_auth_flow():
    """Test the complete authentication flow"""
    print("🧪 Testing Mr Wallet API Authentication Flow\n")
    
    # Test data
    test_email = generate_test_email()
    test_password = "testpassword123"
    
    print(f"📧 Using test email: {test_email}")
    
    # 1. Test Registration
    print("\n1️⃣  Testing User Registration...")
    register_data = {
        "name": "Test User",
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("✅ Registration successful")
            user_data = response.json()
            print(f"   User ID: {user_data['id']}")
            print(f"   Name: {user_data['name']}")
            print(f"   Email: {user_data['email']}")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Make sure the API is running on http://localhost:8000")
        return False
    
    # 2. Test Login
    print("\n2️⃣  Testing User Login...")
    login_data = {
        "username": test_email,  # OAuth2PasswordRequestForm uses 'username'
        "password": test_password
    }
    
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if response.status_code == 200:
        print("✅ Login successful")
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print(f"   Token type: {tokens['token_type']}")
        print(f"   Access token: {access_token[:50]}...")
        print(f"   Refresh token: {refresh_token[:50]}...")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False
    
    # 3. Test Protected Route
    print("\n3️⃣  Testing Protected Route (/auth/me)...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        print("✅ Protected route access successful")
        user_info = response.json()
        print(f"   User info: {user_info['name']} ({user_info['email']})")
    else:
        print(f"❌ Protected route failed: {response.status_code} - {response.text}")
        return False
    
    # 4. Test Token Refresh
    print("\n4️⃣  Testing Token Refresh...")
    refresh_data = {"refresh_token": refresh_token}
    
    response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
    if response.status_code == 200:
        print("✅ Token refresh successful")
        new_tokens = response.json()
        new_access_token = new_tokens["access_token"]
        new_refresh_token = new_tokens["refresh_token"]
        print(f"   New access token: {new_access_token[:50]}...")
        print(f"   New refresh token: {new_refresh_token[:50]}...")
        
        # Verify old refresh token no longer works
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        if response.status_code == 401:
            print("✅ Old refresh token correctly invalidated")
        else:
            print("⚠️  Old refresh token still works (potential security issue)")
        
        # Update tokens for logout test
        access_token = new_access_token
        refresh_token = new_refresh_token
        
    else:
        print(f"❌ Token refresh failed: {response.status_code} - {response.text}")
        return False
    
    # 5. Test Logout
    print("\n5️⃣  Testing Logout...")
    logout_data = {"refresh_token": refresh_token}
    
    response = requests.post(f"{BASE_URL}/auth/logout", json=logout_data)
    if response.status_code == 204:
        print("✅ Logout successful")
        
        # Verify refresh token no longer works
        response = requests.post(f"{BASE_URL}/auth/refresh", json=logout_data)
        if response.status_code == 401:
            print("✅ Refresh token correctly revoked after logout")
        else:
            print("⚠️  Refresh token still works after logout")
            
    else:
        print(f"❌ Logout failed: {response.status_code} - {response.text}")
        return False
    
    print("\n🎉 All authentication tests passed!")
    return True


if __name__ == "__main__":
    success = test_auth_flow()
    exit(0 if success else 1)
