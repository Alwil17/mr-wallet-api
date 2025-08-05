#!/usr/bin/env python3
"""
Database initialization script.
Creates all database tables based on the SQLAlchemy models.
"""

from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base import Base
from app.db.models import User, RefreshToken, Wallet


def create_tables():
    """Create all database tables"""
    engine = create_engine(settings.DATABASE_URL)

    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")

        # Print table information
        print("\n📋 Created tables:")
        for table in Base.metadata.tables.keys():
            print(f"   - {table}")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

    return True


if __name__ == "__main__":
    success = create_tables()
    exit(0 if success else 1)
