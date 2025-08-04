# 💰 Mr Wallet API - Personal Finance Management Backend

**Mr Wallet** is a comprehensive personal finance management application designed to help users track their expenses, incomes, debts, and transfers between multiple wallets.

## 📖 Project Overview

This is the backend API for Mr Wallet, built with **FastAPI** and **PostgreSQL**. The API provides secure endpoints for managing personal finances with a clean, modular architecture inspired by Clean/Hexagonal Architecture principles.

## 🎯 Core Features

- **👤 User Authentication** - JWT-based secure authentication system
- **💼 Multi-Wallet Management** - Create and manage multiple wallets (bank accounts, cash, credit cards)
- **💸 Transaction Tracking** - Record income and expenses with categories and notes
- **📎 File Attachments** - Upload receipts, invoices, and documents to transactions
- **🤝 Debt & Loan Management** - Track money owed and lent with due dates
- **🔄 Wallet Transfers** - Move money between different wallets
- **📊 Balance Tracking** - Real-time wallet balance calculations
- **🔒 GDPR Compliance** - Data export and deletion capabilities

## 🏗️ Technical Architecture

```
app/
├── api/routes/     # REST API endpoints (auth, wallets, transactions, debts, transfers)
├── core/           # Security (JWT, password hashing), configuration, logging
├── repositories/   # Business logic and database access layer
├── db/models/      # SQLAlchemy ORM models
├── schemas/        # Pydantic models for request/response validation
├── services/       # Business services and external integrations
└── tests/          # Comprehensive test suite with pytest
```

## 🛠️ Technology Stack

- **Python 3.10+** - Modern Python with type hints
- **FastAPI** - High-performance async web framework
- **PostgreSQL** - Reliable relational database
- **SQLAlchemy** - Powerful ORM with async support
- **Pydantic** - Data validation and serialization
- **Alembic** - Database migrations
- **Docker** - Containerization for easy deployment
- **GitHub Actions** - CI/CD pipeline
- **JWT** - Secure token-based authentication

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Alwil17/mr-wallet-api.git
   cd mr-wallet-api
   ```

2. **Setup environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and JWT secret
   ```

4. **Run with Docker (recommended)**
   ```bash
   docker-compose up -d
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## 📊 Database Schema

The application uses the following main entities:

- **User** - Application users with authentication
- **Wallet** - Financial accounts (bank, cash, credit cards)
- **Transaction** - Income and expense records
- **File** - Attachments linked to transactions
- **Debt** - Money owed or lent tracking
- **Transfer** - Money movement between wallets

See `assets/mr_wallet_diagram.svg` for the complete database schema.

## 🔧 Development Guidelines

- Use **async/await** for all database operations
- Implement proper **error handling** with FastAPI exceptions
- Follow **RESTful API** conventions
- Use **Pydantic** models for request/response validation
- Write **comprehensive tests** for all endpoints
- Follow **PEP8** coding standards
- Use **type hints** throughout the codebase

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## 📝 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to Mr Wallet API.

## 🔒 Security

For security concerns, please see our [Security Policy](SECURITY.md). Do not report security vulnerabilities through public GitHub issues.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for better personal finance management**
