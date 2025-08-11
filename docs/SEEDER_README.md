# Category Seeder

This directory contains data seeders for the Mr Wallet API, specifically for creating default categories for users.

## Files

- `seed_categories.py` - Main standalone seeder script
- `app/seeders/category_seeder.py` - Modular seeder class for integration
- `test_category_seeder.py` - Test script for seeder functionality

## Default Categories

The seeder includes **39 comprehensive categories** organized by type:

### Income Categories (10)
- 💰 Salary
- 💻 Freelance
- 📈 Investment Returns
- 🏠 Rental Income
- 🏢 Business Income
- 🎁 Bonus
- 🚀 Side Hustle
- 🎀 Gifts Received
- ↩️ Refunds
- ➕ Other Income

### Expense Categories (29)

**Essential Expenses (8):**
- 🛒 Groceries
- 🏠 Rent/Mortgage
- ⚡ Utilities
- 📱 Internet & Phone
- 🛡️ Insurance
- 🏥 Healthcare
- 🚗 Transportation
- ⛽ Gas & Fuel

**Lifestyle Expenses (8):**
- 🍽️ Dining Out
- 🎬 Entertainment
- 🛍️ Shopping
- 👕 Clothing
- 💅 Personal Care
- 💪 Gym & Fitness
- 🎨 Hobbies
- 📚 Books & Learning

**Financial Categories (5):**
- 🏦 Savings
- 📊 Investments
- 💳 Debt Payment
- 🚨 Emergency Fund
- 👴 Retirement

**Occasional Expenses (8):**
- ✈️ Travel
- 🏖️ Vacation
- 🎁 Gifts Given
- ❤️ Charity
- 🎓 Education
- 🔨 Home Improvement
- 🐕 Pet Care
- 📱 Subscriptions
- 📊 Taxes
- ➖ Other Expenses

## Usage

### Option 1: Standalone Script

```bash
# List available categories
python seed_categories.py list

# Seed categories for all existing users
python seed_categories.py all

# Seed categories for a specific user
python seed_categories.py user test@example.com
```

### Option 2: Module Integration

```python
from sqlalchemy.orm import Session
from app.seeders.category_seeder import CategorySeeder

# Create seeder instance
seeder = CategorySeeder(db_session)

# Seed for a specific user
created_count = seeder.seed_for_user(user_id)
seeder.commit()

# Seed for all users
result = seeder.seed_for_all_users()
seeder.commit()
print(f"Processed {result['users_processed']} users")
print(f"Created {result['categories_created']} categories")

# Seed by email
created_count = seeder.seed_for_user_by_email("user@example.com")
if created_count is not None:
    seeder.commit()
    print(f"Created {created_count} categories")
else:
    print("User not found")
```

### Option 3: Test Script

```bash
# Run test with sample user
python test_category_seeder.py
```

## Features

- **Smart Duplicate Detection**: Won't create duplicate categories for the same user
- **Batch Processing**: Can seed categories for all users at once
- **Flexible Data**: Easy to customize category lists
- **Color-Coded**: Each category has a hex color for UI theming
- **Icon Support**: Emoji icons for visual representation
- **Transaction Safety**: Proper rollback on errors
- **Detailed Logging**: Clear feedback on operations

## Category Schema

Each category has the following structure:

```python
{
    "name": "Category Name",
    "color": "#hexcolor",  # Bootstrap/Material color
    "icon": "🏠"           # Emoji icon
}
```

## Integration with Transactions

These categories work with the dual category system:

- **Enum Categories**: Predefined in `TransactionCategory` enum
- **User Categories**: Custom categories created by seeder or users
- **Backward Compatibility**: Existing transactions continue to work

Transactions can use either:
- `category` field (enum value)
- `category_id` field (references user category)

## Environment Requirements

Make sure your database is properly configured and accessible via the `DATABASE_URL` setting in your environment configuration.

## Error Handling

The seeder includes comprehensive error handling:
- Database connection errors
- Missing users
- Duplicate categories (skipped by default)
- Transaction rollback on failures
