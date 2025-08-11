#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Category seeder script.
Seeds the database with default categories for all users.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models.user import User
from app.db.models.category import Category


# Default categories with their metadata
DEFAULT_CATEGORIES = [
    # Income Categories
    {"name": "Salary", "color": "#28a745", "icon": "money"},
    {"name": "Freelance", "color": "#17a2b8", "icon": "laptop"},
    {"name": "Investment Returns", "color": "#6f42c1", "icon": "trending-up"},
    {"name": "Rental Income", "color": "#fd7e14", "icon": "home"},
    {"name": "Business Income", "color": "#20c997", "icon": "briefcase"},
    {"name": "Bonus", "color": "#ffc107", "icon": "gift"},
    {"name": "Side Hustle", "color": "#e83e8c", "icon": "rocket"},
    {"name": "Gifts Received", "color": "#6610f2", "icon": "gift-box"},
    {"name": "Refunds", "color": "#198754", "icon": "return"},
    {"name": "Other Income", "color": "#6c757d", "icon": "plus"},
    # Expense Categories - Essential
    {"name": "Groceries", "color": "#dc3545", "icon": "shopping-cart"},
    {"name": "Rent/Mortgage", "color": "#fd7e14", "icon": "home"},
    {"name": "Utilities", "color": "#20c997", "icon": "lightning"},
    {"name": "Internet & Phone", "color": "#0dcaf0", "icon": "phone"},
    {"name": "Insurance", "color": "#6610f2", "icon": "shield"},
    {"name": "Healthcare", "color": "#dc3545", "icon": "medical"},
    {"name": "Transportation", "color": "#198754", "icon": "car"},
    {"name": "Gas & Fuel", "color": "#ffc107", "icon": "fuel"},
    # Expense Categories - Lifestyle
    {"name": "Dining Out", "color": "#e83e8c", "icon": "restaurant"},
    {"name": "Entertainment", "color": "#6f42c1", "icon": "movie"},
    {"name": "Shopping", "color": "#fd7e14", "icon": "shopping-bag"},
    {"name": "Clothing", "color": "#20c997", "icon": "shirt"},
    {"name": "Personal Care", "color": "#0dcaf0", "icon": "spa"},
    {"name": "Gym & Fitness", "color": "#198754", "icon": "fitness"},
    {"name": "Hobbies", "color": "#6610f2", "icon": "palette"},
    {"name": "Books & Learning", "color": "#17a2b8", "icon": "book"},
    # Expense Categories - Financial
    {"name": "Savings", "color": "#28a745", "icon": "piggy-bank"},
    {"name": "Investments", "color": "#6f42c1", "icon": "chart"},
    {"name": "Debt Payment", "color": "#dc3545", "icon": "credit-card"},
    {"name": "Emergency Fund", "color": "#ffc107", "icon": "alert"},
    {"name": "Retirement", "color": "#6c757d", "icon": "retirement"},
    # Expense Categories - Occasional
    {"name": "Travel", "color": "#17a2b8", "icon": "plane"},
    {"name": "Vacation", "color": "#20c997", "icon": "beach"},
    {"name": "Gifts Given", "color": "#e83e8c", "icon": "gift"},
    {"name": "Charity", "color": "#28a745", "icon": "heart"},
    {"name": "Education", "color": "#6610f2", "icon": "graduation"},
    {"name": "Home Improvement", "color": "#fd7e14", "icon": "hammer"},
    {"name": "Pet Care", "color": "#ffc107", "icon": "pet"},
    {"name": "Subscriptions", "color": "#6c757d", "icon": "subscription"},
    {"name": "Taxes", "color": "#dc3545", "icon": "receipt"},
    {"name": "Other Expenses", "color": "#6c757d", "icon": "minus"},
]


def get_db_session():
    """Create database session"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def seed_categories_for_user(db, user_id: int, categories_data: list) -> int:
    """
    Seed categories for a specific user

    Args:
        db: Database session
        user_id: User ID to create categories for
        categories_data: List of category data dictionaries

    Returns:
        Number of categories created
    """
    created_count = 0

    for cat_data in categories_data:
        # Check if category already exists for this user
        existing = (
            db.query(Category)
            .filter(Category.user_id == user_id, Category.name == cat_data["name"])
            .first()
        )

        if not existing:
            category = Category(
                name=cat_data["name"],
                color=cat_data["color"],
                icon=cat_data["icon"],
                user_id=user_id,
            )
            db.add(category)
            created_count += 1

    return created_count


def seed_categories_for_all_users():
    """Seed categories for all existing users"""
    db = get_db_session()

    try:
        # Get all users
        users = db.query(User).all()

        if not users:
            print("No users found in the database. Please create users first.")
            return False

        print(f"Found {len(users)} users in the database")

        total_created = 0

        for user in users:
            print(f"\nSeeding categories for user: {user.name} ({user.email})")

            created_count = seed_categories_for_user(db, user.id, DEFAULT_CATEGORIES)
            total_created += created_count

            print(f"   Created {created_count} categories")

        # Commit all changes
        db.commit()

        print(
            f"\nSuccessfully created {total_created} total categories across all users!"
        )
        print(f"Default categories available: {len(DEFAULT_CATEGORIES)}")

        return True

    except Exception as e:
        print(f"Error seeding categories: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def seed_categories_for_specific_user(user_email: str):
    """Seed categories for a specific user by email"""
    db = get_db_session()

    try:
        # Find the user
        user = db.query(User).filter(User.email == user_email).first()

        if not user:
            print(f"User with email '{user_email}' not found.")
            return False

        print(f"Seeding categories for user: {user.name} ({user.email})")

        created_count = seed_categories_for_user(db, user.id, DEFAULT_CATEGORIES)

        # Commit changes
        db.commit()

        print(f"Created {created_count} categories for {user.name}")
        print(f"Default categories available: {len(DEFAULT_CATEGORIES)}")

        return True

    except Exception as e:
        print(f"Error seeding categories: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def list_available_categories():
    """List all available default categories"""
    print("Available Default Categories:")
    print("=" * 50)

    income_cats = [
        cat
        for cat in DEFAULT_CATEGORIES
        if any(
            word in cat["name"].lower()
            for word in [
                "salary",
                "freelance",
                "investment",
                "rental",
                "business",
                "bonus",
                "side",
                "gift",
                "refund",
                "income",
            ]
        )
    ]

    print("\nIncome Categories:")
    for cat in income_cats:
        print(f"   {cat['icon']} {cat['name']} ({cat['color']})")

    expense_cats = [cat for cat in DEFAULT_CATEGORIES if cat not in income_cats]

    print("\nExpense Categories:")
    for cat in expense_cats:
        print(f"   {cat['icon']} {cat['name']} ({cat['color']})")

    print(f"\nTotal Categories: {len(DEFAULT_CATEGORIES)}")


def main():
    """Main seeder function with command line interface"""
    if len(sys.argv) < 2:
        print("Category Seeder")
        print("=" * 30)
        print("\nUsage:")
        print("  python seed_categories.py all              # Seed for all users")
        print("  python seed_categories.py user <email>     # Seed for specific user")
        print(
            "  python seed_categories.py list             # List available categories"
        )
        print("\nExamples:")
        print("  python seed_categories.py all")
        print("  python seed_categories.py user test@example.com")
        print("  python seed_categories.py list")
        return

    command = sys.argv[1].lower()

    if command == "list":
        list_available_categories()

    elif command == "all":
        print("Starting category seeding for all users...")
        success = seed_categories_for_all_users()
        exit(0 if success else 1)

    elif command == "user":
        if len(sys.argv) < 3:
            print("Please provide user email: python seed_categories.py user <email>")
            exit(1)

        user_email = sys.argv[2]
        print(f"Starting category seeding for user: {user_email}")
        success = seed_categories_for_specific_user(user_email)
        exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        print("   Use 'all', 'user <email>', or 'list'")
        exit(1)


if __name__ == "__main__":
    main()
