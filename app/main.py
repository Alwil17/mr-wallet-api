from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.core.config import settings
from app.api.routes import (
    auth_routes,
    health_routes,
    wallet_routes,
    transaction_routes,
    debt_routes,
    transfer_routes,
)

# Define tags metadata for Swagger documentation
tags_metadata = [
    {
        "name": "Authentication",
        "description": "User authentication, registration, login, and account management endpoints.",
    },
    {
        "name": "Wallet Management",
        "description": "Endpoints for creating, updating, deleting, and retrieving user wallets.",
    },
    {
        "name": "Transactions Management",
        "description": "Endpoints for managing wallet transactions, including creation, listing, and summaries.",
    },
    {
        "name": "Debt Management",
        "description": "Endpoints for tracking debts, repayments, and debt summaries.",
    },
    {
        "name": "Transfer Management",
        "description": "Endpoints for transferring funds between wallets and viewing transfer history.",
    },
    {
        "name": "Health Check",
        "description": "System status and health monitoring endpoints.",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    **Mr Wallet API** is a personal finance management API that provides:

    * **Wallet Management**: Create and manage multiple wallets
    * **Transaction Tracking**: Record and categorize transactions
    * **Budgeting Tools**: Set and track budgets for different categories
    * **Reporting**: Generate reports on spending and savings
    * **GDPR Compliance**: Full data export and account deletion capabilities
    
    ## Authentication
    Most endpoints require JWT authentication. Get your token from `/auth/token`.
    
    ## Data Privacy
    This API is GDPR compliant and respects user privacy with explicit consent management.
    """,
    version=settings.APP_VERSION,
    contact={
        "name": "Mr Wallet API Support",
        "email": "willialfred24@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    debug=settings.APP_DEBUG,
    openapi_tags=tags_metadata,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_routes.router)
app.include_router(auth_routes.router)
app.include_router(wallet_routes.router)
app.include_router(transaction_routes.router)
app.include_router(debt_routes.router)
app.include_router(transfer_routes.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
