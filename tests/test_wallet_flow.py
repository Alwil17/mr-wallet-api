#!/usr/bin/env python3
"""
Test script for wallet management functionality.
This tests wallet CRUD operations and balance management.
"""

import requests
import json
import random
import string
from typing import Dict, Any, Tuple

BASE_URL = "http://localhost:8000"


def generate_test_email() -> str:
    """Generate a random test email"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"wallet_test_{random_str}@example.com"


def authenticate_user() -> Tuple[str, Dict[str, Any]]:
    """Create a test user and get access token"""
    test_email = generate_test_email()
    test_password = "testpassword123"
    
    # Register user
    register_data = {
        "name": "Wallet Test User",
        "email": test_email,
        "password": test_password
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code != 201:
        raise Exception(f"Failed to register user: {response.text}")
    
    user_data = response.json()
    
    # Login to get token
    login_data = {
        "username": test_email,
        "password": test_password
    }
    
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if response.status_code != 200:
        raise Exception(f"Failed to login: {response.text}")
    
    tokens = response.json()
    access_token = tokens["access_token"]
    
    return access_token, user_data


def test_wallet_management():
    """Test the complete wallet management flow"""
    print("🧪 Testing Mr Wallet API - Wallet Management\n")
    
    try:
        # Authenticate
        print("🔑 Authenticating user...")
        access_token, user_data = authenticate_user()
        headers = {"Authorization": f"Bearer {access_token}"}
        print(f"✅ Authenticated as: {user_data['name']}")
        
        # 1. Create wallets
        print("\n1️⃣  Testing Wallet Creation...")
        
        # Create checking account
        checking_data = {
            "name": "Main Checking",
            "type": "checking", 
            "balance": "1500.00"
        }
        
        response = requests.post(f"{BASE_URL}/wallets/", json=checking_data, headers=headers)
        if response.status_code == 201:
            checking_wallet = response.json()
            print(f"✅ Created checking wallet: {checking_wallet['name']} (ID: {checking_wallet['id']})")
            print(f"   Balance: ${checking_wallet['balance']}")
        else:
            print(f"❌ Failed to create checking wallet: {response.status_code} - {response.text}")
            return False
        
        # Create savings account
        savings_data = {
            "name": "Emergency Fund",
            "type": "savings",
            "balance": "5000.00"
        }
        
        response = requests.post(f"{BASE_URL}/wallets/", json=savings_data, headers=headers)
        if response.status_code == 201:
            savings_wallet = response.json()
            print(f"✅ Created savings wallet: {savings_wallet['name']} (ID: {savings_wallet['id']})")
            print(f"   Balance: ${savings_wallet['balance']}")
        else:
            print(f"❌ Failed to create savings wallet: {response.status_code} - {response.text}")
            return False
        
        # Create cash wallet
        cash_data = {
            "name": "Cash on Hand",
            "type": "cash",
            "balance": "200.00"
        }
        
        response = requests.post(f"{BASE_URL}/wallets/", json=cash_data, headers=headers)
        if response.status_code == 201:
            cash_wallet = response.json()
            print(f"✅ Created cash wallet: {cash_wallet['name']} (ID: {cash_wallet['id']})")
            print(f"   Balance: ${cash_wallet['balance']}")
        else:
            print(f"❌ Failed to create cash wallet: {response.status_code} - {response.text}")
            return False
        
        # 2. Get all wallets
        print("\n2️⃣  Testing Get All Wallets...")
        response = requests.get(f"{BASE_URL}/wallets/", headers=headers)
        if response.status_code == 200:
            wallet_data = response.json()
            print(f"✅ Retrieved {wallet_data['total']} wallets")
            for wallet in wallet_data['wallets']:
                print(f"   - {wallet['name']} ({wallet['type']}): ${wallet['balance']}")
        else:
            print(f"❌ Failed to get wallets: {response.status_code} - {response.text}")
            return False
        
        # 3. Get wallet summary
        print("\n3️⃣  Testing Wallet Summary...")
        response = requests.get(f"{BASE_URL}/wallets/summary", headers=headers)
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Wallet Summary:")
            print(f"   Total wallets: {summary['total_wallets']}")
            print(f"   Total balance: ${summary['total_balance']}")
            print(f"   Wallets by type:")
            for wallet_type, data in summary['wallets_by_type'].items():
                print(f"     - {wallet_type}: {data['count']} wallets, ${data['total_balance']}")
        else:
            print(f"❌ Failed to get wallet summary: {response.status_code} - {response.text}")
            return False
        
        # 4. Get specific wallet
        print("\n4️⃣  Testing Get Specific Wallet...")
        response = requests.get(f"{BASE_URL}/wallets/{checking_wallet['id']}", headers=headers)
        if response.status_code == 200:
            wallet = response.json()
            print(f"✅ Retrieved wallet: {wallet['name']} - ${wallet['balance']}")
        else:
            print(f"❌ Failed to get specific wallet: {response.status_code} - {response.text}")
            return False
        
        # 5. Update wallet info
        print("\n5️⃣  Testing Wallet Update...")
        update_data = {
            "name": "Primary Checking Account"
        }
        
        response = requests.put(f"{BASE_URL}/wallets/{checking_wallet['id']}", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_wallet = response.json()
            print(f"✅ Updated wallet name: {updated_wallet['name']}")
        else:
            print(f"❌ Failed to update wallet: {response.status_code} - {response.text}")
            return False
        
        # 6. Test balance operations
        print("\n6️⃣  Testing Balance Operations...")
        
        # Add money
        add_balance = {
            "amount": "500.00",
            "operation": "add",
            "note": "Salary deposit"
        }
        
        response = requests.patch(f"{BASE_URL}/wallets/{checking_wallet['id']}/balance", json=add_balance, headers=headers)
        if response.status_code == 200:
            updated_wallet = response.json()
            print(f"✅ Added $500 to checking: New balance ${updated_wallet['balance']}")
        else:
            print(f"❌ Failed to add balance: {response.status_code} - {response.text}")
            return False
        
        # Subtract money
        subtract_balance = {
            "amount": "100.00",
            "operation": "subtract",
            "note": "ATM withdrawal"
        }
        
        response = requests.patch(f"{BASE_URL}/wallets/{checking_wallet['id']}/balance", json=subtract_balance, headers=headers)
        if response.status_code == 200:
            updated_wallet = response.json()
            print(f"✅ Subtracted $100 from checking: New balance ${updated_wallet['balance']}")
        else:
            print(f"❌ Failed to subtract balance: {response.status_code} - {response.text}")
            return False
        
        # Test insufficient balance
        overdraft_balance = {
            "amount": "10000.00",
            "operation": "subtract",
            "note": "Test overdraft protection"
        }
        
        response = requests.patch(f"{BASE_URL}/wallets/{checking_wallet['id']}/balance", json=overdraft_balance, headers=headers)
        if response.status_code == 400:
            print(f"✅ Overdraft protection working: {response.json()['detail']}")
        else:
            print(f"⚠️  Overdraft protection may not be working properly")
        
        # 7. Get wallets by type
        print("\n7️⃣  Testing Get Wallets by Type...")
        response = requests.get(f"{BASE_URL}/wallets/type/savings", headers=headers)
        if response.status_code == 200:
            savings_wallets = response.json()
            print(f"✅ Found {len(savings_wallets)} savings wallets")
            for wallet in savings_wallets:
                print(f"   - {wallet['name']}: ${wallet['balance']}")
        else:
            print(f"❌ Failed to get wallets by type: {response.status_code} - {response.text}")
            return False
        
        # 8. Delete a wallet
        print("\n8️⃣  Testing Wallet Deletion...")
        response = requests.delete(f"{BASE_URL}/wallets/{cash_wallet['id']}", headers=headers)
        if response.status_code == 204:
            print(f"✅ Deleted cash wallet successfully")
            
            # Verify it's gone
            response = requests.get(f"{BASE_URL}/wallets/{cash_wallet['id']}", headers=headers)
            if response.status_code == 404:
                print(f"✅ Wallet properly deleted - not found")
            else:
                print(f"⚠️  Wallet may not have been properly deleted")
        else:
            print(f"❌ Failed to delete wallet: {response.status_code} - {response.text}")
            return False
        
        # 9. Final summary
        print("\n9️⃣  Final Wallet Summary...")
        response = requests.get(f"{BASE_URL}/wallets/summary", headers=headers)
        if response.status_code == 200:
            final_summary = response.json()
            print(f"✅ Final Summary:")
            print(f"   Total wallets: {final_summary['total_wallets']}")
            print(f"   Total balance: ${final_summary['total_balance']}")
        else:
            print(f"❌ Failed to get final summary: {response.status_code} - {response.text}")
            return False
        
        print("\n🎉 All wallet management tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Make sure the API is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_wallet_management()
    exit(0 if success else 1)
