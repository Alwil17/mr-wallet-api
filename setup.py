#!/usr/bin/env python3
"""
Quick setup script for Mr Wallet API.
This script helps set up the development environment.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and return success status"""
    print(f"🔄 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def create_env_file():
    """Create a sample .env file if it doesn't exist"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating sample .env file...")
    env_content = """# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/mr_wallet_db

# Security
APP_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=Mr Wallet API
APP_VERSION=1.0.0
APP_DEBUG=true
APP_ENV=development

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Sample .env file created")
        print("⚠️  Please update the DATABASE_URL and APP_SECRET_KEY in .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ is required, but you have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} is compatible")
    return True

def install_requirements():
    """Install Python requirements"""
    if not Path("requirements.txt").exists():
        print("⚠️  requirements.txt not found, skipping dependency installation")
        return True
    
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def test_database_connection():
    """Test database connection"""
    print("🔄 Testing database connection...")
    try:
        # Try to import and test database connection
        from app.core.config import settings
        from sqlalchemy import create_engine, text
        
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure PostgreSQL is running and the DATABASE_URL in .env is correct")
        return False

def initialize_database():
    """Initialize database tables"""
    return run_command("python init_db.py", "Initializing database tables")

def run_tests():
    """Run test scripts"""
    print("\n🧪 Running Tests...")
    
    if not run_command("python test_auth_flow.py", "Testing authentication flow"):
        return False
    
    if not run_command("python tests/test_wallet_flow.py", "Testing wallet management"):
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Mr Wallet API Setup Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        print("❌ Setup failed at database connection")
        print("💡 Please configure your database and update .env file")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("❌ Setup failed at database initialization")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review and update the .env file with your actual database credentials")
    print("2. Start the API server: uvicorn app.main:app --reload")
    print("3. Visit http://localhost:8000/docs for API documentation")
    print("4. Run tests: python test_auth_flow.py && python tests/test_wallet_flow.py")
    
    # Ask if user wants to run tests
    if input("\n🧪 Would you like to run the test suite now? (y/N): ").lower().startswith('y'):
        if run_tests():
            print("\n🎉 All tests passed! Your API is ready to use.")
        else:
            print("\n⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
