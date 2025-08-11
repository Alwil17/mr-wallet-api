# -*- coding: utf-8 -*-
"""
Category seeder module for creating default categories.
"""

from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.category import Category
from typing import List, Dict, Optional


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


class CategorySeeder:
    """Category seeder class for managing default categories"""

    def __init__(self, db: Session):
        self.db = db

    def seed_for_user(
        self,
        user_id: int,
        categories_data: Optional[List[Dict]] = None,
        skip_existing: bool = True,
    ) -> int:
        """
        Seed categories for a specific user

        Args:
            user_id: User ID to create categories for
            categories_data: List of category data dictionaries (defaults to DEFAULT_CATEGORIES)
            skip_existing: Whether to skip categories that already exist for the user

        Returns:
            Number of categories created
        """
        if categories_data is None:
            categories_data = DEFAULT_CATEGORIES

        created_count = 0

        for cat_data in categories_data:
            if skip_existing:
                # Check if category already exists for this user
                existing = (
                    self.db.query(Category)
                    .filter(
                        Category.user_id == user_id, Category.name == cat_data["name"]
                    )
                    .first()
                )

                if existing:
                    continue

            category = Category(
                name=cat_data["name"],
                color=cat_data.get("color"),
                icon=cat_data.get("icon"),
                user_id=user_id,
            )
            self.db.add(category)
            created_count += 1

        return created_count

    def seed_for_all_users(
        self, categories_data: Optional[List[Dict]] = None, skip_existing: bool = True
    ) -> Dict[str, int]:
        """
        Seed categories for all existing users

        Args:
            categories_data: List of category data dictionaries (defaults to DEFAULT_CATEGORIES)
            skip_existing: Whether to skip categories that already exist for users

        Returns:
            Dictionary with 'users_processed' and 'categories_created' counts
        """
        if categories_data is None:
            categories_data = DEFAULT_CATEGORIES

        users = self.db.query(User).all()

        if not users:
            return {"users_processed": 0, "categories_created": 0}

        total_created = 0

        for user in users:
            created_count = self.seed_for_user(user.id, categories_data, skip_existing)
            total_created += created_count

        return {"users_processed": len(users), "categories_created": total_created}

    def seed_for_user_by_email(
        self,
        email: str,
        categories_data: Optional[List[Dict]] = None,
        skip_existing: bool = True,
    ) -> Optional[int]:
        """
        Seed categories for a user by email

        Args:
            email: User email
            categories_data: List of category data dictionaries (defaults to DEFAULT_CATEGORIES)
            skip_existing: Whether to skip categories that already exist for the user

        Returns:
            Number of categories created, or None if user not found
        """
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            return None

        return self.seed_for_user(user.id, categories_data, skip_existing)

    def get_user_category_count(self, user_id: int) -> int:
        """Get the number of categories for a user"""
        return self.db.query(Category).filter(Category.user_id == user_id).count()

    def get_default_categories(self) -> List[Dict]:
        """Get the list of default categories"""
        return DEFAULT_CATEGORIES.copy()

    def commit(self):
        """Commit the database transaction"""
        self.db.commit()

    def rollback(self):
        """Rollback the database transaction"""
        self.db.rollback()


def seed_categories_for_user(db: Session, user_id: int) -> int:
    """
    Convenience function to seed default categories for a user

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Number of categories created
    """
    seeder = CategorySeeder(db)
    return seeder.seed_for_user(user_id)


def seed_categories_for_all_users(db: Session) -> Dict[str, int]:
    """
    Convenience function to seed default categories for all users

    Args:
        db: Database session

    Returns:
        Dictionary with processing results
    """
    seeder = CategorySeeder(db)
    return seeder.seed_for_all_users()
