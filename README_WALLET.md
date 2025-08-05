# Mr Wallet API - Wallet Management System

A comprehensive FastAPI-based personal finance management system with secure wallet operations.

## 🚀 Features

### Authentication System
- JWT-based authentication with refresh tokens
- User registration and login
- Role-based access control (user/admin)
- GDPR-compliant data export and deletion
- Secure password hashing with bcrypt

### Wallet Management
- Create, read, update, and delete wallets
- Multiple wallet types (checking, savings, cash, credit, etc.)
- Balance management with overdraft protection
- Wallet summaries and analytics
- Filter wallets by type

## 📋 API Endpoints

### Authentication Endpoints
```
POST   /auth/register          - Register new user
POST   /auth/token             - Login (get access token)
POST   /auth/refresh           - Refresh access token
POST   /auth/logout            - Logout (revoke tokens)
GET    /auth/me                - Get current user info
PUT    /auth/edit              - Update user profile
DELETE /auth/remove            - Delete user account
GET    /auth/export-data       - Export user data (GDPR)
GET    /auth/export-data/download - Download user data
DELETE /auth/delete-account    - GDPR compliant account deletion
POST   /auth/anonymize-account - Anonymize user data
GET    /auth/data-summary      - Get user data summary
```

### Wallet Management Endpoints
```
POST   /wallets/               - Create new wallet
GET    /wallets/               - Get all user wallets
GET    /wallets/summary        - Get wallet summary
GET    /wallets/type/{type}    - Get wallets by type
GET    /wallets/{id}           - Get specific wallet
PUT    /wallets/{id}           - Update wallet info
PATCH  /wallets/{id}/balance   - Update wallet balance
DELETE /wallets/{id}           - Delete wallet
```

## 🏗️ Architecture

The project follows Clean Architecture principles with clear separation of concerns:

```
app/
├── api/routes/          # FastAPI route handlers
│   ├── auth_routes.py   # Authentication endpoints
│   └── wallet_routes.py # Wallet management endpoints
├── core/                # Core configuration and security
│   ├── config.py        # Application settings
│   └── security.py      # JWT handling, password hashing
├── db/                  # Database layer
│   ├── base.py          # Database connection
│   └── models/          # SQLAlchemy models
│       ├── user.py      # User model
│       ├── refresh_token.py # Refresh token model
│       └── wallet.py    # Wallet model
├── repositories/        # Data access layer
│   ├── user_repository.py
│   ├── refresh_token_repository.py
│   └── wallet_repository.py
├── schemas/             # Pydantic schemas (DTOs)
│   ├── user_dto.py      # User request/response schemas
│   ├── auth_dto.py      # Authentication schemas
│   └── wallet_dto.py    # Wallet schemas
├── services/            # Business logic layer
│   ├── user_service.py  # User business logic
│   └── wallet_service.py # Wallet business logic
└── main.py             # FastAPI application entry point
```

## 🗄️ Database Schema

### User Table
```sql
users (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Wallet Table
```sql
wallets (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    balance DECIMAL(10,2) DEFAULT 0.00,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Refresh Token Table
```sql
refresh_tokens (
    id INTEGER PRIMARY KEY,
    token VARCHAR UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT false,
    created_at TIMESTAMP
)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL database
- pip or poetry for dependency management

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd mr-wallet-api
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@localhost/mr_wallet_db
APP_SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_ENV=development
```

4. **Initialize the database**
```bash
python init_db.py
```

5. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

### Authentication Flow Test
```bash
python test_auth_flow.py
```

### Wallet Management Test
```bash
python tests/test_wallet_flow.py
```

### Manual Testing with curl

1. **Register a user**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

2. **Login to get token**
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=securepassword123"
```

3. **Create a wallet**
```bash
curl -X POST "http://localhost:8000/wallets/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Main Checking",
    "type": "checking",
    "balance": "1500.00"
  }'
```

4. **Get wallets**
```bash
curl -X GET "http://localhost:8000/wallets/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 Wallet Management Features

### Wallet Types
- **Checking**: Day-to-day spending accounts
- **Savings**: Long-term savings accounts  
- **Cash**: Physical cash tracking
- **Credit**: Credit card accounts
- **Investment**: Investment accounts
- **Other**: Custom wallet types

### Balance Operations
- **Add**: Increase wallet balance (deposits, income)
- **Subtract**: Decrease wallet balance (withdrawals, expenses)
- **Set**: Set absolute balance value

### Security Features
- **Ownership Verification**: Users can only access their own wallets
- **Overdraft Protection**: Prevents negative balances for most operations
- **Audit Trail**: All balance changes can be logged (future feature)

## 🔒 Security

- JWT tokens with configurable expiration
- Refresh token rotation for enhanced security
- Password hashing using bcrypt
- Role-based access control
- CORS protection
- Input validation using Pydantic
- SQL injection protection via SQLAlchemy ORM

## 🌐 Environment Configuration

### Development
```env
APP_ENV=development
APP_DEBUG=true
DATABASE_URL=postgresql://user:password@localhost/mr_wallet_dev
```

### Production
```env
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=postgresql://user:password@prod-server/mr_wallet
APP_SECRET_KEY=extremely-secure-production-key
```

### Testing
```env
APP_ENV=testing
DATABASE_URL=postgresql://user:password@localhost/mr_wallet_test
```

## 📈 Future Enhancements

### Planned Features
- Transaction tracking with categories
- Debt and loan management
- Inter-wallet transfers
- File attachments for transactions
- Budgeting and goal setting
- Analytics and reporting
- Mobile app integration
- Bank account synchronization
- Multi-currency support

### Database Extensions
Following the class diagram, these models will be added:

```python
# Transaction model
class Transaction:
    id, type, amount, category, note, date, wallet_id, created_at

# File model  
class File:
    id, filename, url, file_type, transaction_id, uploaded_at

# Debt model
class Debt:
    id, amount, borrower, type, is_paid, due_date, wallet_id, created_at

# Transfer model
class Transfer:
    id, amount, source_wallet_id, target_wallet_id, created_at
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, please open an issue on the GitHub repository or contact the development team.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and PostgreSQL**
