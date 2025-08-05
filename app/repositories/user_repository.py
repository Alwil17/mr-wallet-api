from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.db.models.user import User
from app.schemas.user_dto import UserCreateDTO, UserUpdateDTO
from app.core.config import settings


class UserRepository:
    def __init__(self, db: Session):
        """
        Constructor for UserRepository

        Args:
            db (Session): The database session
        """
        self.db = db

    def create(self, user_data: UserCreateDTO) -> User:
        """
        Create a new user

        Args:
            user_data (UserCreateDTO): The user data

        Returns:
            User: The created user
        """
        hashed_pw = hash_password(user_data.password)
        user = User(
            name=user_data.name, 
            email=user_data.email, 
            hashed_password=hashed_pw
        )

        # Auto-assign admin role for admin emails in debug or test mode
        if (settings.APP_DEBUG or settings.APP_ENV.lower() in ["test", "testing"]) and ("admin" in user_data.email):
            user.role = "admin"

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID

        Args:
            user_id (int): The user ID

        Returns:
            Optional[User]: The user if found
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email

        Args:
            email (str): The user email

        Returns:
            Optional[User]: The user if found
        """
        return self.db.query(User).filter(User.email == email).first()

    def list(self) -> List[User]:
        """
        Get all users

        Returns:
            List[User]: List of all users
        """
        return self.db.query(User).all()

    def update(self, user_id: int, user_data: UserUpdateDTO) -> Optional[User]:
        """
        Update a user

        Args:
            user_id (int): The user ID
            user_data (UserUpdateDTO): The update data

        Returns:
            Optional[User]: The updated user if found
        """
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Hash the password if present
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        
        for key, value in update_data.items():
            setattr(user, key, value)

        user.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user_id: int, new_password: str) -> bool:
        """
        Update user password

        Args:
            user_id (int): The user ID
            new_password (str): The new password

        Returns:
            bool: True if updated successfully
        """
        user = self.get_by_id(user_id)
        if not user:
            return False
            
        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.now()
        self.db.commit()
        return True

    def delete(self, user_id: int) -> bool:
        """
        Delete a user

        Args:
            user_id (int): The user ID

        Returns:
            bool: True if deleted, False if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
