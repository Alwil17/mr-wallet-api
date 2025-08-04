from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        """
        Constructor for RefreshTokenRepository

        Args:
            db (Session): The database session
        """
        self.db = db

    def create(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        """
        Create a new refresh token

        Args:
            user_id (int): The user ID
            token (str): The token string
            expires_at (datetime): When the token expires

        Returns:
            RefreshToken: The created refresh token
        """
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token

    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """
        Get a refresh token by token string

        Args:
            token (str): The token string

        Returns:
            Optional[RefreshToken]: The refresh token if found
        """
        return self.db.query(RefreshToken).filter(RefreshToken.token == token).first()

    def revoke(self, token: str) -> bool:
        """
        Revoke a refresh token by setting its revoked flag to True.

        Args:
            token (str): The token string to be revoked.

        Returns:
            bool: True if the token was found and revoked, False otherwise.
        """
        refresh_token = self.get_by_token(token)

        if not refresh_token:
            return False

        refresh_token.revoked = True
        self.db.commit()

        return True

    def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        Revoke all refresh tokens for a user

        Args:
            user_id (int): The user ID

        Returns:
            int: Number of tokens revoked
        """
        count = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).update({"revoked": True})
        self.db.commit()
        return count
