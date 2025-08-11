#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual category seeder example.
This shows how to use the category seeder in your own scripts.
"""

from app.seeders.category_seeder import CategorySeeder, DEFAULT_CATEGORIES


def example_usage():
    """Example of how to use the category seeder"""

    print("🌱 Category Seeder Usage Example")
    print("=" * 40)

    print(f"\n📊 Available categories: {len(DEFAULT_CATEGORIES)}")

    print("\n💰 Income Categories:")
    income_categories = [
        cat
        for cat in DEFAULT_CATEGORIES
        if any(
            keyword in cat["name"].lower()
            for keyword in [
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

    for cat in income_categories[:5]:  # Show first 5
        print(f"   {cat['icon']} {cat['name']} ({cat['color']})")
    print(f"   ... and {len(income_categories) - 5} more")

    print("\n💸 Expense Categories:")
    expense_categories = [
        cat for cat in DEFAULT_CATEGORIES if cat not in income_categories
    ]

    for cat in expense_categories[:5]:  # Show first 5
        print(f"   {cat['icon']} {cat['name']} ({cat['color']})")
    print(f"   ... and {len(expense_categories) - 5} more")

    print("\n🔧 Usage in your code:")
    print(
        """
from sqlalchemy.orm import Session
from app.seeders.category_seeder import CategorySeeder

# Method 1: Use with database session
def seed_categories_for_user(db: Session, user_id: int):
    seeder = CategorySeeder(db)
    created_count = seeder.seed_for_user(user_id)
    seeder.commit()
    return created_count

# Method 2: Use with existing user
def seed_categories_by_email(db: Session, email: str):
    seeder = CategorySeeder(db)
    created_count = seeder.seed_for_user_by_email(email)
    if created_count is not None:
        seeder.commit()
        return created_count
    return 0

# Method 3: Seed for all users
def seed_categories_for_all(db: Session):
    seeder = CategorySeeder(db)
    result = seeder.seed_for_all_users()
    seeder.commit()
    return result
"""
    )

    print(
        "\n✅ Ready to use! Import CategorySeeder and use with your database session."
    )


if __name__ == "__main__":
    example_usage()
