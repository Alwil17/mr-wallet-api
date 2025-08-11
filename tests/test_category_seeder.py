#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the category seeder using pytest fixtures.
This demonstrates the seeder working with the test database.
"""

import pytest
from sqlalchemy.orm import Session
from app.seeders.category_seeder import CategorySeeder
from app.db.models.user import User
from app.db.models.category import Category


def test_category_seeder_for_user(db: Session, test_user: User):
    """Test the category seeder with a test user"""

    # Initialize seeder
    seeder = CategorySeeder(db)

    # Get initial category count
    initial_count = seeder.get_user_category_count(test_user.id)
    assert initial_count == 0  # Should start with no categories

    # Seed categories for the test user
    created_count = seeder.seed_for_user(test_user.id)

    # Commit the transaction to persist changes
    seeder.commit()

    # Verify categories were created
    assert created_count > 0
    assert created_count == len(seeder.get_default_categories())

    # Check final count
    final_count = seeder.get_user_category_count(test_user.id)
    assert final_count == created_count

    # Verify some specific categories exist
    categories = db.query(Category).filter(Category.user_id == test_user.id).all()
    category_names = [cat.name for cat in categories]

    # Check for some expected categories
    assert "Salary" in category_names
    assert "Groceries" in category_names
    assert "Entertainment" in category_names
    assert "Savings" in category_names

    # Test that running seeder again doesn't create duplicates
    duplicate_count = seeder.seed_for_user(test_user.id)
    assert duplicate_count == 0  # Should skip existing categories

    # Final count should be the same
    final_count_after = seeder.get_user_category_count(test_user.id)
    assert final_count_after == final_count


def test_category_seeder_by_email(db: Session, test_user: User):
    """Test seeding categories using user email"""

    seeder = CategorySeeder(db)

    # Seed by email
    created_count = seeder.seed_for_user_by_email(test_user.email)

    # Commit the transaction
    seeder.commit()

    # Should have created default categories
    assert created_count > 0

    # Verify categories exist for the user
    final_count = seeder.get_user_category_count(test_user.id)
    assert final_count == created_count


def test_category_seeder_custom_categories(db: Session, test_user: User):
    """Test seeding custom categories"""

    seeder = CategorySeeder(db)

    # Define custom categories
    custom_categories = [
        {"name": "Custom Income", "color": "#FF0000", "icon": "custom"},
        {"name": "Custom Expense", "color": "#00FF00", "icon": "custom"},
    ]

    # Seed custom categories using the existing method
    created_count = seeder.seed_for_user(test_user.id, custom_categories)

    # Commit the transaction
    seeder.commit()

    # Verify custom categories were created
    assert created_count == 2

    # Check they exist in database
    categories = db.query(Category).filter(Category.user_id == test_user.id).all()
    category_names = [cat.name for cat in categories]

    assert "Custom Income" in category_names
    assert "Custom Expense" in category_names


def test_category_seeder_default_categories():
    """Test that default categories are properly defined"""

    seeder = CategorySeeder(None)  # Don't need DB for this test
    default_categories = seeder.get_default_categories()

    # Should have a good number of categories
    assert len(default_categories) > 30

    # Should have income and expense categories (based on names)
    income_names = ["Salary", "Freelance", "Investment Returns", "Bonus"]
    expense_names = ["Groceries", "Rent/Mortgage", "Entertainment", "Shopping"]

    category_names = [cat["name"] for cat in default_categories]

    # Check that we have income categories
    for income_name in income_names:
        assert income_name in category_names

    # Check that we have expense categories
    for expense_name in expense_names:
        assert expense_name in category_names

    # Each category should have required fields
    for category in default_categories:
        assert "name" in category
        assert "color" in category
        assert "icon" in category
        assert category["color"].startswith("#")
        assert len(category["color"]) == 7  # Should be hex color
