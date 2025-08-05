#!/usr/bin/env python3
"""
Comprehensive test suite for Mr Wallet API.
This script tests the complete functionality including auth and wallet management.
"""

import requests
import json
import random
import string
import time
from typing import Dict, Any, Tuple, Optional

BASE_URL = "http://localhost:8000"


class APITestSuite:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token: Optional[str] = None
        self.user_data: Optional[Dict[str, Any]] = None
        self.created_wallets = []
        
    def generate_test_email(self) -> str:
        """Generate a random test email"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"comprehensive_test_{random_str}@example.com"
    
    def print_step(self, step_num: int, description: str):
        """Print a formatted test step"""
        print(f"\n{step_num}️⃣  Testing {description}...")
    
    def print_success(self, message: str):
        """Print a success message"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print an error message"""
        print(f"❌ {message}")
    
    def test_health_check(self) -> bool:
        """Test API health check"""
        self.print_step(1, "API Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.print_success("API is healthy and responding")
                return True
            else:
                self.print_error(f"Health check failed: {response.status_code}")
                return False
        except requests.ConnectionError:
            self.print_error("Cannot connect to API. Make sure it's running on http://localhost:8000")
            return False
        except Exception as e:
            self.print_error(f"Health check error: {e}")
            return False
    
    def test_user_registration(self) -> bool:
        """Test user registration"""
        self.print_step(2, "User Registration")
        
        test_email = self.generate_test_email()
        register_data = {
            "name": "Comprehensive Test User",
            "email": test_email,
            "password": "testpassword123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=register_data)
            if response.status_code == 201:
                self.user_data = response.json()
                self.print_success(f"User registered: {self.user_data['name']} ({self.user_data['email']})")
                return True
            else:
                self.print_error(f"Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Registration error: {e}")
            return False
    
    def test_user_login(self) -> bool:
        """Test user login"""
        self.print_step(3, "User Login")
        
        if not self.user_data:
            self.print_error("No user data available for login")
            return False
        
        login_data = {
            "username": self.user_data["email"],
            "password": "testpassword123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/token", data=login_data)
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens["access_token"]
                self.print_success("Login successful, access token obtained")
                return True
            else:
                self.print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Login error: {e}")
            return False
    
    def test_protected_route(self) -> bool:
        """Test accessing protected route"""
        self.print_step(4, "Protected Route Access")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/auth/me", headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                self.print_success(f"Protected route access successful: {user_info['name']}")
                return True
            else:
                self.print_error(f"Protected route failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Protected route error: {e}")
            return False
    
    def test_wallet_creation(self) -> bool:
        """Test wallet creation"""
        self.print_step(5, "Wallet Creation")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Create multiple wallets
        wallets_to_create = [
            {"name": "Primary Checking", "type": "checking", "balance": "2500.00"},
            {"name": "Emergency Savings", "type": "savings", "balance": "10000.00"},
            {"name": "Cash Wallet", "type": "cash", "balance": "300.00"},
            {"name": "Credit Card", "type": "credit", "balance": "0.00"}
        ]
        
        for wallet_data in wallets_to_create:
            try:
                response = requests.post(f"{self.base_url}/wallets/", json=wallet_data, headers=headers)
                if response.status_code == 201:
                    wallet = response.json()
                    self.created_wallets.append(wallet)
                    self.print_success(f"Created {wallet['name']}: ${wallet['balance']}")
                else:
                    self.print_error(f"Failed to create {wallet_data['name']}: {response.status_code} - {response.text}")
                    return False
            except Exception as e:
                self.print_error(f"Wallet creation error: {e}")
                return False
        
        return True
    
    def test_wallet_listing(self) -> bool:
        """Test wallet listing"""
        self.print_step(6, "Wallet Listing")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/wallets/", headers=headers)
            if response.status_code == 200:
                wallet_data = response.json()
                self.print_success(f"Retrieved {wallet_data['total']} wallets")
                for wallet in wallet_data['wallets']:
                    print(f"   - {wallet['name']} ({wallet['type']}): ${wallet['balance']}")
                return True
            else:
                self.print_error(f"Wallet listing failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Wallet listing error: {e}")
            return False
    
    def test_wallet_summary(self) -> bool:
        """Test wallet summary"""
        self.print_step(7, "Wallet Summary")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/wallets/summary", headers=headers)
            if response.status_code == 200:
                summary = response.json()
                self.print_success("Wallet summary retrieved:")
                print(f"   Total wallets: {summary['total_wallets']}")
                print(f"   Total balance: ${summary['total_balance']}")
                print(f"   Wallets by type:")
                for wallet_type, data in summary['wallets_by_type'].items():
                    print(f"     - {wallet_type}: {data['count']} wallets, ${data['total_balance']}")
                return True
            else:
                self.print_error(f"Wallet summary failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Wallet summary error: {e}")
            return False
    
    def test_balance_operations(self) -> bool:
        """Test wallet balance operations"""
        self.print_step(8, "Balance Operations")
        
        if not self.access_token or not self.created_wallets:
            self.print_error("No access token or wallets available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        test_wallet = self.created_wallets[0]  # Use first wallet for testing
        
        # Test adding money
        try:
            add_balance = {
                "amount": "500.00",
                "operation": "add",
                "note": "Test deposit"
            }
            
            response = requests.patch(
                f"{self.base_url}/wallets/{test_wallet['id']}/balance",
                json=add_balance,
                headers=headers
            )
            
            if response.status_code == 200:
                updated_wallet = response.json()
                expected_balance = float(test_wallet['balance']) + 500.00
                if float(updated_wallet['balance']) == expected_balance:
                    self.print_success(f"Added $500 to {test_wallet['name']}: ${updated_wallet['balance']}")
                else:
                    self.print_error(f"Balance calculation error: expected ${expected_balance}, got ${updated_wallet['balance']}")
                    return False
            else:
                self.print_error(f"Add balance failed: {response.status_code} - {response.text}")
                return False
            
            # Test subtracting money
            subtract_balance = {
                "amount": "200.00", 
                "operation": "subtract",
                "note": "Test withdrawal"
            }
            
            response = requests.patch(
                f"{self.base_url}/wallets/{test_wallet['id']}/balance",
                json=subtract_balance,
                headers=headers
            )
            
            if response.status_code == 200:
                updated_wallet = response.json()
                self.print_success(f"Subtracted $200 from {test_wallet['name']}: ${updated_wallet['balance']}")
            else:
                self.print_error(f"Subtract balance failed: {response.status_code} - {response.text}")
                return False
            
            # Test overdraft protection
            overdraft = {
                "amount": "99999.00",
                "operation": "subtract", 
                "note": "Test overdraft protection"
            }
            
            response = requests.patch(
                f"{self.base_url}/wallets/{test_wallet['id']}/balance",
                json=overdraft,
                headers=headers
            )
            
            if response.status_code == 400:
                self.print_success("Overdraft protection working correctly")
            else:
                self.print_error("Overdraft protection may not be working")
                
            return True
            
        except Exception as e:
            self.print_error(f"Balance operations error: {e}")
            return False
    
    def test_wallet_types_filter(self) -> bool:
        """Test filtering wallets by type"""
        self.print_step(9, "Wallet Type Filtering")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/wallets/type/savings", headers=headers)
            if response.status_code == 200:
                savings_wallets = response.json()
                self.print_success(f"Found {len(savings_wallets)} savings wallets")
                for wallet in savings_wallets:
                    print(f"   - {wallet['name']}: ${wallet['balance']}")
                return True
            else:
                self.print_error(f"Wallet type filtering failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Wallet type filtering error: {e}")
            return False
    
    def test_user_data_summary(self) -> bool:
        """Test user data summary"""
        self.print_step(10, "User Data Summary")
        
        if not self.access_token:
            self.print_error("No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/auth/data-summary", headers=headers)
            if response.status_code == 200:
                summary = response.json()
                self.print_success("User data summary retrieved:")
                print(f"   User ID: {summary['user_id']}")
                print(f"   Email: {summary['email']}")
                print(f"   Wallets: {summary['wallets_count']}")
                print(f"   Total Balance: ${summary['total_balance']}")
                return True
            else:
                self.print_error(f"Data summary failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Data summary error: {e}")
            return False
    
    def test_token_refresh(self) -> bool:
        """Test token refresh functionality"""
        self.print_step(11, "Token Refresh")
        
        # First, get a refresh token
        if not self.user_data:
            self.print_error("No user data available")
            return False
        
        login_data = {
            "username": self.user_data["email"],
            "password": "testpassword123"
        }
        
        try:
            # Get fresh tokens
            response = requests.post(f"{self.base_url}/auth/token", data=login_data)
            if response.status_code != 200:
                self.print_error("Could not get tokens for refresh test")
                return False
            
            tokens = response.json()
            refresh_token = tokens["refresh_token"]
            
            # Test refresh
            refresh_data = {"refresh_token": refresh_token}
            response = requests.post(f"{self.base_url}/auth/refresh", json=refresh_data)
            
            if response.status_code == 200:
                new_tokens = response.json()
                self.access_token = new_tokens["access_token"]  # Update for further tests
                self.print_success("Token refresh successful")
                return True
            else:
                self.print_error(f"Token refresh failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_error(f"Token refresh error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests in sequence"""
        print("🧪 Comprehensive API Test Suite")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_user_login,
            self.test_protected_route,
            self.test_wallet_creation,
            self.test_wallet_listing,
            self.test_wallet_summary,
            self.test_balance_operations,
            self.test_wallet_types_filter,
            self.test_user_data_summary,
            self.test_token_refresh,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
                    # Continue with other tests even if one fails
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print(f"\n📊 Test Results:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 All tests passed! Your API is working perfectly!")
            return True
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the error messages above.")
            return False


if __name__ == "__main__":
    test_suite = APITestSuite()
    success = test_suite.run_all_tests()
    exit(0 if success else 1)
