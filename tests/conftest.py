import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Force use of test settings
os.environ["APP_ENV"] = "test"

# Import necessary modules
from app.db.base import Base, get_db
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.db.models.wallet import Wallet

# Create in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Database session fixture"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a db session
    db_session = TestingSessionLocal()
    
    # Override get_db dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


@pytest.fixture(scope="function") 
def client(db):
    """Test client fixture"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user"""
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db: Session) -> User:
    """Create a test admin user"""
    admin = User(
        name="Admin User", 
        email="admin@example.com",
        hashed_password=hash_password("adminpassword123"),
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(test_user: User):
    """Generate auth headers for test user"""
    token = create_access_token(
        data={"sub": test_user.email, "role": test_user.role, "user_id": test_user.id}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_admin: User):
    """Generate auth headers for admin user"""
    token = create_access_token(
        data={"sub": test_admin.email, "role": test_admin.role, "user_id": test_admin.id}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_auth(client):
    """
    Returns user auth data when needed.
    Creates a new user and returns authentication data.
    """
    import random
    import string
    
    # Generate unique email
    random_str = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email = f"test_{random_str}@example.com"
    
    user_payload = {
        "name": "Test User",
        "email": email,
        "password": "testpassword123",
    }
    
    # Register user
    response = client.post("/auth/register", json=user_payload)
    assert response.status_code == 201, response.text
    user_data = response.json()

    # Login to get tokens
    form_data = {
        "username": user_payload["email"],
        "password": user_payload["password"],
    }
    response = client.post("/auth/token", data=form_data)
    assert response.status_code == 200, response.text
    token_data = response.json()
    
    return {
        "user": user_data,
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"},
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "email": email,
        "password": "testpassword123"
    }


@pytest.fixture
def test_wallet(db: Session, test_user: User) -> Wallet:
    """Create a test wallet"""
    from decimal import Decimal
    
    wallet = Wallet(
        name="Test Wallet",
        type="checking",
        balance=Decimal("1000.00"),
        user_id=test_user.id
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


@pytest.fixture
def multiple_wallets(db: Session, test_user: User) -> list[Wallet]:
    """Create multiple test wallets"""
    from decimal import Decimal
    
    wallets_data = [
        {"name": "Checking Account", "type": "checking", "balance": Decimal("1500.00")},
        {"name": "Savings Account", "type": "savings", "balance": Decimal("5000.00")}, 
        {"name": "Cash Wallet", "type": "cash", "balance": Decimal("200.00")},
        {"name": "Credit Card", "type": "credit", "balance": Decimal("0.00")},
    ]
    
    wallets = []
    for wallet_data in wallets_data:
        wallet = Wallet(
            name=wallet_data["name"],
            type=wallet_data["type"],
            balance=wallet_data["balance"],
            user_id=test_user.id
        )
        db.add(wallet)
        wallets.append(wallet)
    
    db.commit()
    for wallet in wallets:
        db.refresh(wallet)
    
    return wallets


@pytest.fixture
def test_wallet_api(client, user_auth):
    """Create a test wallet using the API"""
    wallet_data = {
        "name": "Test Wallet",
        "type": "checking",
        "balance": 1000.00
    }
    
    response = client.post("/wallets/", json=wallet_data, headers=user_auth["headers"])
    assert response.status_code == 201
    return response.json()
