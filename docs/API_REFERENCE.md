# 📚 Mr Wallet API Reference

*Personal Finance Management Backend - Complete API Documentation*

**Version:** 1.0.1  
**Base URL:** `http://localhost:8000` (Development) | `https://your-domain.com` (Production)  
**Authentication:** JWT Bearer Token  
**Content-Type:** `application/json`

---

## 🔐 Authentication

All endpoints except registration, login, and health check require JWT authentication via the `Authorization: Bearer <token>` header.

### 🎫 Token Management

#### `POST /auth/token`
**Description:** Authenticate user and get access/refresh tokens  
**Authentication:** None required  
**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
username=user@example.com&password=secretpassword
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials

---

#### `POST /auth/token/refresh`
**Description:** Refresh access token using refresh token  
**Authentication:** None required

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or expired refresh token

---

#### `POST /auth/logout`
**Description:** Logout user and revoke refresh token  
**Authentication:** None required

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

### 👤 User Management

#### `POST /auth/register`
**Description:** Register a new user account  
**Authentication:** None required

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": null
}
```

**Errors:**
- `400 Bad Request` - User already exists or validation error

---

#### `GET /auth/profile`
**Description:** Get current authenticated user information  
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": "2025-01-21T12:00:00Z"
}
```

---

#### `PUT /auth/profile`
**Description:** Update current user profile  
**Authentication:** Required

**Request Body:**
```json
{
  "name": "John Smith",
  "email": "johnsmith@example.com"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Smith",
  "email": "johnsmith@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": "2025-01-21T15:30:00Z"
}
```

---

#### `PUT /auth/password`
**Description:** Change user password  
**Authentication:** Required

**Request Body:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newPassword456"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password updated successfully"
}
```

**Errors:**
- `400 Bad Request` - Current password incorrect

---

### 🛡️ GDPR & Data Management

#### `GET /auth/gdpr/data`
**Description:** Export all user data (GDPR compliance)  
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "user_info": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-01-21T10:00:00Z",
    "updated_at": null
  },
  "wallets": [...],
  "transactions": [...],
  "debts": [...],
  "transfers": [...],
  "export_timestamp": "2025-01-21T15:45:00Z",
  "data_retention_period": "As per GDPR regulations"
}
```

---

#### `GET /auth/export-data/download`
**Description:** Download user data as JSON file  
**Authentication:** Required

**Response:** `200 OK`
- **Content-Type:** `application/json`
- **Headers:** `Content-Disposition: attachment; filename=user_data_1.json`

---

#### `DELETE /auth/delete-account`
**Description:** Permanently delete user account and all data  
**Authentication:** Required

**Request Body:**
```json
{
  "confirmation_text": "DELETE"
}
```

**Response:** `200 OK`
```json
{
  "message": "Account permanently deleted"
}
```

---

#### `POST /auth/anonymize-account`
**Description:** Anonymize user account data  
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "message": "Account data anonymized successfully"
}
```

---

#### `GET /auth/data-summary`
**Description:** Get summary of user's data counts and totals  
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "user_id": 1,
  "email": "john@example.com",
  "account_created": "2025-01-21T10:00:00Z",
  "wallets_count": 4,
  "transactions_count": 127,
  "debts_count": 3,
  "transfers_count": 15,
  "total_balance": 5432.10,
  "data_summary_generated_at": "2025-01-21T16:45:00Z"
}
```

---

## 💼 Wallet Management

### 💳 Wallet Operations

#### `POST /wallets/`
**Description:** Create a new wallet  
**Authentication:** Required

**Request Body:**
```json
{
  "name": "Main Checking",
  "type": "checking",
  "balance": 1000.50
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Main Checking",
  "type": "checking",
  "balance": 1000.50,
  "user_id": 1,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": null
}
```

**Wallet Types:** `checking`, `savings`, `cash`, `credit`, `investment`, `business`

---

#### `GET /wallets/`
**Description:** Get all user wallets with pagination  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100, max: 1000)

**Response:** `200 OK`
```json
{
  "wallets": [
    {
      "id": 1,
      "name": "Main Checking",
      "type": "checking",
      "balance": 1000.50,
      "user_id": 1,
      "created_at": "2025-01-21T10:00:00Z",
      "updated_at": null
    }
  ],
  "total": 1
}
```

---

#### `GET /wallets/summary`
**Description:** Get wallet summary statistics  
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "total_wallets": 4,
  "total_balance": 5432.10,
  "wallets_by_type": {
    "checking": 2,
    "savings": 1,
    "credit": 1
  }
}
```

---

#### `GET /wallets/type/{wallet_type}`
**Description:** Get wallets filtered by type  
**Authentication:** Required

**Path Parameters:**
- `wallet_type` (string): Type of wallet to filter by

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Main Checking",
    "type": "checking",
    "balance": 1000.50,
    "user_id": 1,
    "created_at": "2025-01-21T10:00:00Z",
    "updated_at": null
  }
]
```

---

#### `GET /wallets/{wallet_id}`
**Description:** Get specific wallet by ID  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Main Checking",
  "type": "checking",
  "balance": 1000.50,
  "user_id": 1,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": null
}
```

**Errors:**
- `404 Not Found` - Wallet not found or not owned by user

---

#### `PUT /wallets/{wallet_id}`
**Description:** Update wallet information  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Request Body:**
```json
{
  "name": "Updated Wallet Name",
  "type": "savings"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Updated Wallet Name",
  "type": "savings",
  "balance": 1000.50,
  "user_id": 1,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": "2025-01-21T15:30:00Z"
}
```

---

#### `PATCH /wallets/{wallet_id}/balance`
**Description:** Update wallet balance  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Request Body:**
```json
{
  "amount": 500.00,
  "operation": "add",
  "note": "Salary deposit"
}
```

**Operations:** `add`, `subtract`, `set`

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Main Checking",
  "type": "checking",
  "balance": 1500.50,
  "user_id": 1,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": "2025-01-21T15:30:00Z"
}
```

---

#### `DELETE /wallets/{wallet_id}`
**Description:** Delete a wallet  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Response:** `200 OK`
```json
{
  "message": "Wallet deleted successfully"
}
```

---

### 💰 Balance Operations

#### `POST /wallets/{wallet_id}/credit`
**Description:** Credit amount to wallet  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Request Body:**
```json
{
  "amount": 250.00
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Main Checking",
  "type": "checking",
  "balance": 1250.50,
  "user_id": 1,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": "2025-01-21T15:30:00Z"
}
```

---

#### `POST /wallets/{wallet_id}/debit`
**Description:** Debit amount from wallet  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Request Body:**
```json
{
  "amount": 100.00
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Main Checking",
  "type": "checking",
  "balance": 900.50,
  "user_id": 1,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": "2025-01-21T15:30:00Z"
}
```

---

#### `GET /wallets/{wallet_id}/balance`
**Description:** Get current wallet balance  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Response:** `200 OK`
```json
{
  "wallet_id": 1,
  "balance": 1000.50,
  "last_updated": "2025-01-21T15:30:00Z"
}
```

---

## 💸 Transaction Management

### 📊 Transaction Operations

#### `POST /transactions/`
**Description:** Create a new transaction  
**Authentication:** Required

**Request Body:**
```json
{
  "type": "expense",
  "amount": 25.50,
  "category": "food",
  "note": "Lunch at cafe",
  "date": "2025-01-21T12:30:00Z",
  "wallet_id": 1
}
```

**Transaction Types:** `income`, `expense`

**Categories:**
- **Income:** `salary`, `freelance`, `investment`, `gift`, `refund`, `other_income`
- **Expense:** `food`, `transport`, `housing`, `utilities`, `entertainment`, `healthcare`, `education`, `shopping`, `travel`, `insurance`, `taxes`, `debt_payment`, `other_expense`

**Response:** `201 Created`
```json
{
  "id": 1,
  "type": "expense",
  "amount": 25.50,
  "category": "food",
  "note": "Lunch at cafe",
  "date": "2025-01-21T12:30:00Z",
  "wallet_id": 1,
  "created_at": "2025-01-21T12:35:00Z",
  "updated_at": null,
  "files": []
}
```

---

#### `GET /transactions/`
**Description:** Get user transactions with filtering and pagination  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, optional): Records to skip (default: 0)
- `limit` (int, optional): Max records (default: 100, max: 1000)
- `sort_by` (string, optional): Sort field (default: "date")
- `sort_order` (string, optional): Sort order "asc" or "desc" (default: "desc")
- `wallet_id` (int, optional): Filter by wallet
- `type` (string, optional): Filter by transaction type
- `category` (string, optional): Filter by category
- `start_date` (string, optional): Filter from date (ISO format)
- `end_date` (string, optional): Filter to date (ISO format)
- `min_amount` (decimal, optional): Minimum amount
- `max_amount` (decimal, optional): Maximum amount

**Response:** `200 OK`
```json
{
  "transactions": [
    {
      "id": 1,
      "type": "expense",
      "amount": 25.50,
      "category": "food",
      "note": "Lunch at cafe",
      "date": "2025-01-21T12:30:00Z",
      "wallet_id": 1,
      "created_at": "2025-01-21T12:35:00Z",
      "updated_at": null,
      "files": []
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

---

#### `GET /transactions/summary`
**Description:** Get transaction summary statistics  
**Authentication:** Required

**Query Parameters:**
- `wallet_id` (int, optional): Filter by wallet
- `category` (string, optional): Filter by category
- `transaction_type` (string, optional): Filter by type
- `date_from` (string, optional): From date
- `date_to` (string, optional): To date

**Response:** `200 OK`
```json
{
  "total_transactions": 45,
  "total_income": 3500.00,
  "total_expenses": 1250.75,
  "net_amount": 2249.25,
  "transactions_by_category": {
    "food": 15,
    "transport": 8,
    "salary": 2
  },
  "monthly_summary": {
    "2025-01": {
      "income": 3500.00,
      "expenses": 1250.75,
      "net": 2249.25
    }
  }
}
```

---

#### `GET /transactions/{transaction_id}`
**Description:** Get specific transaction by ID  
**Authentication:** Required

**Path Parameters:**
- `transaction_id` (int): Transaction ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "type": "expense",
  "amount": 25.50,
  "category": "food",
  "note": "Lunch at cafe",
  "date": "2025-01-21T12:30:00Z",
  "wallet_id": 1,
  "created_at": "2025-01-21T12:35:00Z",
  "updated_at": null,
  "files": []
}
```

---

#### `PUT /transactions/{transaction_id}`
**Description:** Update a transaction  
**Authentication:** Required

**Path Parameters:**
- `transaction_id` (int): Transaction ID

**Request Body:**
```json
{
  "amount": 30.00,
  "note": "Updated lunch amount",
  "category": "food"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "type": "expense",
  "amount": 30.00,
  "category": "food",
  "note": "Updated lunch amount",
  "date": "2025-01-21T12:30:00Z",
  "wallet_id": 1,
  "created_at": "2025-01-21T12:35:00Z",
  "updated_at": "2025-01-21T15:45:00Z",
  "files": []
}
```

---

#### `DELETE /transactions/{transaction_id}`
**Description:** Delete a transaction  
**Authentication:** Required

**Path Parameters:**
- `transaction_id` (int): Transaction ID

**Response:** `200 OK`
```json
{
  "message": "Transaction deleted successfully"
}
```

---

### 📎 File Attachments

#### `POST /transactions/{transaction_id}/files`
**Description:** Upload file attachment for transaction  
**Authentication:** Required  
**Content-Type:** `multipart/form-data`

**Path Parameters:**
- `transaction_id` (int): Transaction ID

**Form Data:**
- `file` (file): File to upload (max 10MB)
- `file_type` (string): File type enum

**File Types:** `receipt`, `invoice`, `document`, `image`, `pdf`, `other`

**Response:** `201 Created`
```json
{
  "id": 1,
  "filename": "receipt_20250121.jpg",
  "original_filename": "IMG_001.jpg",
  "url": "/uploads/transaction_files/receipt_20250121.jpg",
  "file_type": "receipt",
  "file_size": 125840,
  "mime_type": "image/jpeg",
  "uploaded_at": "2025-01-21T15:30:00Z"
}
```

**Errors:**
- `413 Request Entity Too Large` - File exceeds 10MB limit
- `400 Bad Request` - Invalid file type

---

#### `GET /transactions/{transaction_id}/files`
**Description:** Get all files for a transaction  
**Authentication:** Required

**Path Parameters:**
- `transaction_id` (int): Transaction ID

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "filename": "receipt_20250121.jpg",
    "original_filename": "IMG_001.jpg",
    "url": "/uploads/transaction_files/receipt_20250121.jpg",
    "file_type": "receipt",
    "file_size": 125840,
    "mime_type": "image/jpeg",
    "uploaded_at": "2025-01-21T15:30:00Z"
  }
]
```

---

#### `DELETE /transactions/files/{file_id}`
**Description:** Delete a file attachment  
**Authentication:** Required

**Path Parameters:**
- `file_id` (int): File ID

**Response:** `200 OK`
```json
{
  "message": "File deleted successfully"
}
```

---

### 📊 Bulk Operations

#### `POST /transactions/bulk`
**Description:** Create multiple transactions in bulk  
**Authentication:** Required

**Request Body:**
```json
{
  "transactions": [
    {
      "type": "expense",
      "amount": 25.50,
      "category": "food",
      "note": "Lunch",
      "wallet_id": 1
    },
    {
      "type": "income",
      "amount": 3000.00,
      "category": "salary",
      "note": "Monthly salary",
      "wallet_id": 1
    }
  ]
}
```

**Response:** `201 Created`
```json
[
  {
    "id": 1,
    "type": "expense",
    "amount": 25.50,
    "category": "food",
    "note": "Lunch",
    "wallet_id": 1,
    "created_at": "2025-01-21T15:30:00Z"
  },
  {
    "id": 2,
    "type": "income",
    "amount": 3000.00,
    "category": "salary",
    "note": "Monthly salary",
    "wallet_id": 1,
    "created_at": "2025-01-21T15:30:00Z"
  }
]
```

---

#### `GET /transactions/wallet/{wallet_id}`
**Description:** Get all transactions for a specific wallet  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "type": "expense",
    "amount": 25.50,
    "category": "food",
    "note": "Lunch at cafe",
    "date": "2025-01-21T12:30:00Z",
    "wallet_id": 1,
    "created_at": "2025-01-21T12:35:00Z",
    "updated_at": null,
    "files": []
  }
]
```

---

## 🤝 Debt Management

### 💳 Debt Operations

#### `POST /debts/`
**Description:** Create a new debt record  
**Authentication:** Required

**Request Body:**
```json
{
  "amount": 500.00,
  "borrower": "John Smith",
  "type": "owed",
  "due_date": "2025-02-15T00:00:00Z",
  "description": "Loan for car repair",
  "wallet_id": 1
}
```

**Debt Types:**
- `owed` - Money you are owed by someone
- `given` - Money you owe to someone

**Response:** `201 Created`
```json
{
  "id": 1,
  "amount": 500.00,
  "borrower": "John Smith",
  "type": "owed",
  "is_paid": false,
  "due_date": "2025-02-15T00:00:00Z",
  "description": "Loan for car repair",
  "wallet_id": 1,
  "created_at": "2025-01-21T15:30:00Z",
  "updated_at": null
}
```

---

#### `GET /debts/`
**Description:** Get user debts with filtering and pagination  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, optional): Records to skip (default: 0)
- `limit` (int, optional): Max records (default: 100, max: 1000)
- `debt_type` (string, optional): Filter by debt type (`owed` or `given`)
- `is_paid` (boolean, optional): Filter by payment status
- `borrower` (string, optional): Filter by borrower name
- `overdue_only` (boolean, optional): Show only overdue debts (default: false)
- `wallet_id` (int, optional): Filter by wallet ID

**Response:** `200 OK`
```json
{
  "debts": [
    {
      "id": 1,
      "amount": 500.00,
      "borrower": "John Smith",
      "type": "owed",
      "is_paid": false,
      "due_date": "2025-02-15T00:00:00Z",
      "description": "Loan for car repair",
      "wallet_id": 1,
      "created_at": "2025-01-21T15:30:00Z",
      "updated_at": null
    }
  ],
  "total": 1
}
```

---

#### `GET /debts/summary`
**Description:** Get debt summary statistics  
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "total_debts": 5,
  "total_amount_owed": 1500.00,
  "total_amount_given": 800.00,
  "overdue_debts": 2,
  "paid_debts": 1,
  "unpaid_debts": 4,
  "debts_by_type": {
    "owed": 3,
    "given": 2
  }
}
```

---

#### `GET /debts/wallet/{wallet_id}`
**Description:** Get all debts for a specific wallet  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "amount": 500.00,
    "borrower": "John Smith",
    "type": "owed",
    "is_paid": false,
    "due_date": "2025-02-15T00:00:00Z",
    "description": "Loan for car repair",
    "wallet_id": 1,
    "created_at": "2025-01-21T15:30:00Z",
    "updated_at": null
  }
]
```

---

#### `GET /debts/{debt_id}`
**Description:** Get specific debt by ID  
**Authentication:** Required

**Path Parameters:**
- `debt_id` (int): Debt ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "amount": 500.00,
  "borrower": "John Smith",
  "type": "owed",
  "is_paid": false,
  "due_date": "2025-02-15T00:00:00Z",
  "description": "Loan for car repair",
  "wallet_id": 1,
  "created_at": "2025-01-21T15:30:00Z",
  "updated_at": null
}
```

---

#### `PUT /debts/{debt_id}`
**Description:** Update debt information  
**Authentication:** Required

**Path Parameters:**
- `debt_id` (int): Debt ID

**Request Body:**
```json
{
  "amount": 600.00,
  "description": "Updated loan amount for car repair",
  "due_date": "2025-03-01T00:00:00Z"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "amount": 600.00,
  "borrower": "John Smith",
  "type": "owed",
  "is_paid": false,
  "due_date": "2025-03-01T00:00:00Z",
  "description": "Updated loan amount for car repair",
  "wallet_id": 1,
  "created_at": "2025-01-21T15:30:00Z",
  "updated_at": "2025-01-21T16:00:00Z"
}
```

---

#### `PATCH /debts/{debt_id}/payment`
**Description:** Mark debt as paid or update payment status  
**Authentication:** Required

**Path Parameters:**
- `debt_id` (int): Debt ID

**Request Body:**
```json
{
  "is_paid": true
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "amount": 500.00,
  "borrower": "John Smith",
  "type": "owed",
  "is_paid": true,
  "due_date": "2025-02-15T00:00:00Z",
  "description": "Loan for car repair",
  "wallet_id": 1,
  "created_at": "2025-01-21T15:30:00Z",
  "updated_at": "2025-01-21T16:15:00Z"
}
```

---

#### `DELETE /debts/{debt_id}`
**Description:** Delete a debt record  
**Authentication:** Required

**Path Parameters:**
- `debt_id` (int): Debt ID

**Response:** `200 OK`
```json
{
  "message": "Debt deleted successfully"
}
```

---

## 🔄 Transfer Management

### 💱 Transfer Operations

#### `POST /transfers/`
**Description:** Create a new transfer between wallets  
**Authentication:** Required

**Request Body:**
```json
{
  "amount": 250.00,
  "source_wallet_id": 1,
  "target_wallet_id": 2,
  "description": "Monthly savings transfer"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "amount": 250.00,
  "description": "Monthly savings transfer",
  "source_wallet_id": 1,
  "target_wallet_id": 2,
  "created_at": "2025-01-21T15:30:00Z",
  "source_wallet_name": "Main Checking",
  "target_wallet_name": "Savings Account"
}
```

**Errors:**
- `400 Bad Request` - Source and target wallets cannot be the same
- `400 Bad Request` - Insufficient funds in source wallet

---

#### `GET /transfers/`
**Description:** Get user transfers with filtering and pagination  
**Authentication:** Required

**Query Parameters:**
- `skip` (int, optional): Records to skip (default: 0)
- `limit` (int, optional): Max records (default: 100, max: 1000)
- `source_wallet_id` (int, optional): Filter by source wallet
- `target_wallet_id` (int, optional): Filter by target wallet
- `wallet_id` (int, optional): Filter by transfers involving this wallet
- `min_amount` (decimal, optional): Minimum transfer amount
- `max_amount` (decimal, optional): Maximum transfer amount
- `date_from` (string, optional): Filter from date (ISO format)
- `date_to` (string, optional): Filter to date (ISO format)

**Response:** `200 OK`
```json
{
  "transfers": [
    {
      "id": 1,
      "amount": 250.00,
      "description": "Monthly savings transfer",
      "source_wallet_id": 1,
      "target_wallet_id": 2,
      "created_at": "2025-01-21T15:30:00Z",
      "source_wallet_name": "Main Checking",
      "target_wallet_name": "Savings Account"
    }
  ],
  "total": 1
}
```

---

#### `GET /transfers/summary`
**Description:** Get transfer summary statistics  
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "total_transfers": 15,
  "total_amount_transferred": 3750.00,
  "transfers_by_wallet": {
    "1": {
      "outgoing": 5,
      "incoming": 3,
      "net_outgoing": 500.00
    },
    "2": {
      "outgoing": 2,
      "incoming": 7,
      "net_incoming": 1250.00
    }
  },
  "recent_transfers": [
    {
      "id": 1,
      "amount": 250.00,
      "description": "Monthly savings transfer",
      "source_wallet_id": 1,
      "target_wallet_id": 2,
      "created_at": "2025-01-21T15:30:00Z"
    }
  ]
}
```

---

#### `GET /transfers/wallet/{wallet_id}`
**Description:** Get all transfers for a specific wallet  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "amount": 250.00,
    "description": "Monthly savings transfer",
    "source_wallet_id": 1,
    "target_wallet_id": 2,
    "created_at": "2025-01-21T15:30:00Z",
    "source_wallet_name": "Main Checking",
    "target_wallet_name": "Savings Account"
  }
]
```

---

#### `GET /transfers/wallet/{wallet_id}/summary`
**Description:** Get transfer summary for specific wallet  
**Authentication:** Required

**Path Parameters:**
- `wallet_id` (int): Wallet ID

**Response:** `200 OK`
```json
{
  "wallet_id": 1,
  "total_outgoing_transfers": 5,
  "total_incoming_transfers": 3,
  "total_outgoing_amount": 1250.00,
  "total_incoming_amount": 750.00,
  "net_transfer_amount": -500.00
}
```

---

#### `GET /transfers/{transfer_id}`
**Description:** Get specific transfer by ID  
**Authentication:** Required

**Path Parameters:**
- `transfer_id` (int): Transfer ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "amount": 250.00,
  "description": "Monthly savings transfer",
  "source_wallet_id": 1,
  "target_wallet_id": 2,
  "created_at": "2025-01-21T15:30:00Z",
  "source_wallet_name": "Main Checking",
  "target_wallet_name": "Savings Account"
}
```

---

#### `DELETE /transfers/{transfer_id}`
**Description:** Delete a transfer (reverses wallet balances)  
**Authentication:** Required

**Path Parameters:**
- `transfer_id` (int): Transfer ID

**Response:** `200 OK`
```json
{
  "message": "Transfer deleted successfully"
}
```

---

### 🔀 Alternative Transfer Endpoint

#### `POST /transfers/wallets/{source_wallet_id}/transfer`
**Description:** Create transfer using wallet-specific endpoint  
**Authentication:** Required

**Path Parameters:**
- `source_wallet_id` (int): Source wallet ID

**Query Parameters:**
- `target_wallet_id` (int, required): Target wallet ID
- `amount` (decimal, required): Transfer amount
- `description` (string, optional): Transfer description

**Response:** `201 Created`
```json
{
  "id": 1,
  "amount": 250.00,
  "description": "Monthly savings transfer",
  "source_wallet_id": 1,
  "target_wallet_id": 2,
  "created_at": "2025-01-21T15:30:00Z",
  "source_wallet_name": "Main Checking",
  "target_wallet_name": "Savings Account"
}
```

---

## 🏥 Health & System

### 📊 Health Check

#### `GET /health`
**Description:** Check API and database health  
**Authentication:** None required

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-01-21T15:30:00Z",
  "database": "healthy",
  "version": "1.0.1"
}
```

**Response when degraded:** `200 OK`
```json
{
  "status": "degraded",
  "timestamp": "2025-01-21T15:30:00Z",
  "database": "unhealthy: connection timeout",
  "version": "1.0.1"
}
```

---

#### `GET /`
**Description:** API root endpoint with basic information  
**Authentication:** None required

**Response:** `200 OK`
```json
{
  "message": "Welcome to Mr Wallet API - Personal Finance Management",
  "version": "1.0.1",
  "docs": "/docs or /redoc",
  "health": "/health"
}
```

---

## 📋 Data Models

### 🏗️ Core Data Structures

#### User Model
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": "2025-01-21T12:00:00Z"
}
```

#### Wallet Model
```json
{
  "id": 1,
  "name": "Main Checking",
  "type": "checking",
  "balance": 1000.50,
  "user_id": 1,
  "created_at": "2025-01-21T10:00:00Z",
  "updated_at": "2025-01-21T12:00:00Z"
}
```

#### Transaction Model
```json
{
  "id": 1,
  "type": "expense",
  "amount": 25.50,
  "category": "food",
  "note": "Lunch at cafe",
  "date": "2025-01-21T12:30:00Z",
  "wallet_id": 1,
  "created_at": "2025-01-21T12:35:00Z",
  "updated_at": null,
  "files": []
}
```

#### Debt Model
```json
{
  "id": 1,
  "amount": 500.00,
  "borrower": "John Smith",
  "type": "owed",
  "is_paid": false,
  "due_date": "2025-02-15T00:00:00Z",
  "description": "Loan for car repair",
  "wallet_id": 1,
  "created_at": "2025-01-21T15:30:00Z",
  "updated_at": null
}
```

#### Transfer Model
```json
{
  "id": 1,
  "amount": 250.00,
  "description": "Monthly savings transfer",
  "source_wallet_id": 1,
  "target_wallet_id": 2,
  "created_at": "2025-01-21T15:30:00Z",
  "source_wallet_name": "Main Checking",
  "target_wallet_name": "Savings Account"
}
```

#### File Model
```json
{
  "id": 1,
  "filename": "receipt_20250121.jpg",
  "original_filename": "IMG_001.jpg",
  "url": "/uploads/transaction_files/receipt_20250121.jpg",
  "file_type": "receipt",
  "file_size": 125840,
  "mime_type": "image/jpeg",
  "uploaded_at": "2025-01-21T15:30:00Z"
}
```

---

## 🔧 Error Handling

### 📊 HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| `200 OK` | Request successful |
| `201 Created` | Resource created successfully |
| `400 Bad Request` | Invalid request data or validation error |
| `401 Unauthorized` | Authentication required or invalid token |
| `403 Forbidden` | Access denied (insufficient permissions) |
| `404 Not Found` | Resource not found |
| `413 Request Entity Too Large` | File upload exceeds size limit |
| `422 Unprocessable Entity` | Validation error |
| `500 Internal Server Error` | Server error |

### 🚨 Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Validation Error Example:**
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

---

## 🔐 Authentication & Security

### 🎫 JWT Token Format

**Access Token (15 minutes expiry):**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwicm9sZSI6InVzZXIiLCJ1c2VyX2lkIjoxLCJleHAiOjE2NDI3ODk4MDB9.signature
```

**Refresh Token (30 days expiry):**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwicm9sZSI6InVzZXIiLCJ1c2VyX2lkIjoxLCJleHAiOjE2NDI3ODk4MDB9.signature"
}
```

### 🛡️ Security Features

- **Password Hashing:** bcrypt with salt
- **JWT Tokens:** HS256 algorithm
- **CORS Protection:** Configurable origins
- **Request Validation:** Pydantic models
- **File Upload Security:** Type and size validation
- **Rate Limiting:** Built-in protection
- **SQL Injection Protection:** SQLAlchemy ORM

---

## 🚀 Next.js Integration Examples

### 🔧 API Client Setup

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiOptions {
  token?: string;
  method?: string;
  body?: any;
}

export async function apiCall(endpoint: string, options: ApiOptions = {}) {
  const { token, method = 'GET', body } = options;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  const config: RequestInit = {
    method,
    headers,
  };
  
  if (body && method !== 'GET') {
    config.body = JSON.stringify(body);
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }
  
  return response.json();
}
```

### 🎫 Authentication Hook

```typescript
// hooks/useAuth.ts
import { useState, useEffect } from 'react';
import { apiCall } from '@/lib/api';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    loading: true,
  });

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUser(token);
    } else {
      setAuthState(prev => ({ ...prev, loading: false }));
    }
  }, []);

  const loadUser = async (token: string) => {
    try {
      const user = await apiCall('/auth/profile', { token });
      setAuthState({ user, token, loading: false });
    } catch (error) {
      console.error('Failed to load user:', error);
      logout();
    }
  };

  const login = async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const { access_token, refresh_token } = await response.json();
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    await loadUser(access_token);
    return access_token;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setAuthState({ user: null, token: null, loading: false });
  };

  return { ...authState, login, logout };
}
```

### 💼 Wallet Management Hook

```typescript
// hooks/useWallets.ts
import { useState, useEffect } from 'react';
import { apiCall } from '@/lib/api';
import { useAuth } from './useAuth';

interface Wallet {
  id: number;
  name: string;
  type: string;
  balance: number;
  user_id: number;
  created_at: string;
  updated_at: string | null;
}

export function useWallets() {
  const { token } = useAuth();
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchWallets();
    }
  }, [token]);

  const fetchWallets = async () => {
    try {
      const data = await apiCall('/wallets/', { token });
      setWallets(data.wallets);
    } catch (error) {
      console.error('Failed to fetch wallets:', error);
    } finally {
      setLoading(false);
    }
  };

  const createWallet = async (walletData: {
    name: string;
    type: string;
    balance?: number;
  }) => {
    const wallet = await apiCall('/wallets/', {
      token,
      method: 'POST',
      body: walletData,
    });
    setWallets(prev => [...prev, wallet]);
    return wallet;
  };

  const updateWallet = async (id: number, updates: Partial<Wallet>) => {
    const wallet = await apiCall(`/wallets/${id}`, {
      token,
      method: 'PUT',
      body: updates,
    });
    setWallets(prev => prev.map(w => w.id === id ? wallet : w));
    return wallet;
  };

  const deleteWallet = async (id: number) => {
    await apiCall(`/wallets/${id}`, {
      token,
      method: 'DELETE',
    });
    setWallets(prev => prev.filter(w => w.id !== id));
  };

  return {
    wallets,
    loading,
    createWallet,
    updateWallet,
    deleteWallet,
    refetch: fetchWallets,
  };
}
```

### 💸 Transaction Management Hook

```typescript
// hooks/useTransactions.ts
import { useState, useEffect } from 'react';
import { apiCall } from '@/lib/api';
import { useAuth } from './useAuth';

interface Transaction {
  id: number;
  type: 'income' | 'expense';
  amount: number;
  category: string;
  note: string | null;
  date: string;
  wallet_id: number;
  created_at: string;
  updated_at: string | null;
  files: any[];
}

interface TransactionFilters {
  wallet_id?: number;
  type?: string;
  category?: string;
  start_date?: string;
  end_date?: string;
  min_amount?: number;
  max_amount?: number;
}

export function useTransactions(filters: TransactionFilters = {}) {
  const { token } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchTransactions();
    }
  }, [token, filters]);

  const fetchTransactions = async () => {
    try {
      const queryParams = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });

      const data = await apiCall(`/transactions/?${queryParams}`, { token });
      setTransactions(data.transactions);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTransaction = async (transactionData: {
    type: 'income' | 'expense';
    amount: number;
    category: string;
    note?: string;
    date?: string;
    wallet_id: number;
  }) => {
    const transaction = await apiCall('/transactions/', {
      token,
      method: 'POST',
      body: transactionData,
    });
    setTransactions(prev => [transaction, ...prev]);
    return transaction;
  };

  const updateTransaction = async (id: number, updates: Partial<Transaction>) => {
    const transaction = await apiCall(`/transactions/${id}`, {
      token,
      method: 'PUT',
      body: updates,
    });
    setTransactions(prev => prev.map(t => t.id === id ? transaction : t));
    return transaction;
  };

  const deleteTransaction = async (id: number) => {
    await apiCall(`/transactions/${id}`, {
      token,
      method: 'DELETE',
    });
    setTransactions(prev => prev.filter(t => t.id !== id));
  };

  return {
    transactions,
    total,
    loading,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    refetch: fetchTransactions,
  };
}
```

---

## 📖 Usage Examples

### 🔥 Common API Workflows

#### 1. User Registration & Authentication
```typescript
// Register new user
const user = await apiCall('/auth/register', {
  method: 'POST',
  body: {
    name: 'John Doe',
    email: 'john@example.com',
    password: 'securePassword123'
  }
});

// Login
const tokens = await apiCall('/auth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=john@example.com&password=securePassword123'
});
```

#### 2. Create Wallet & Add Transaction
```typescript
// Create wallet
const wallet = await apiCall('/wallets/', {
  token,
  method: 'POST',
  body: {
    name: 'Main Checking',
    type: 'checking',
    balance: 1000.00
  }
});

// Add transaction
const transaction = await apiCall('/transactions/', {
  token,
  method: 'POST',
  body: {
    type: 'expense',
    amount: 25.50,
    category: 'food',
    note: 'Lunch',
    wallet_id: wallet.id
  }
});
```

#### 3. Transfer Between Wallets
```typescript
// Create transfer
const transfer = await apiCall('/transfers/', {
  token,
  method: 'POST',
  body: {
    amount: 500.00,
    source_wallet_id: 1,
    target_wallet_id: 2,
    description: 'Monthly savings'
  }
});
```

---

## 🎯 Rate Limits & Quotas

- **Authentication Endpoints:** 10 requests per minute
- **Data Modification:** 100 requests per hour
- **Data Retrieval:** 1000 requests per hour
- **File Uploads:** 50 uploads per hour, 10MB max per file

---

## 🔍 OpenAPI Documentation

**Interactive Documentation Available At:**
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## 📞 Support & Resources

- **Repository:** [GitHub](https://github.com/your-username/mr-wallet-api)
- **Issues:** [GitHub Issues](https://github.com/your-username/mr-wallet-api/issues)
- **Email:** willialfred24@gmail.com
- **License:** MIT License

---

*Last Updated: January 21, 2025*  
*API Version: 1.0.1*
