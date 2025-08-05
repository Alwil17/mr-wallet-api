import os
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import UploadFile

from app.db.models.file import File, FileType
from app.db.models.transaction import Transaction
from app.db.models.wallet import Wallet
from app.core.config import settings


class FileRepository:
    def __init__(self, db: Session):
        """
        Constructor for FileRepository

        Args:
            db (Session): The database session
        """
        self.db = db
        # Create upload directory if it doesn't exist
        self.upload_dir = "uploads/transaction_files"
        os.makedirs(self.upload_dir, exist_ok=True)

    def create(
        self, file: UploadFile, transaction_id: int, file_type: FileType, user_id: int
    ) -> File:
        """
        Upload and create a file record

        Args:
            file (UploadFile): The uploaded file
            transaction_id (int): The transaction ID
            file_type (FileType): The file type
            user_id (int): The user ID (for ownership verification)

        Returns:
            File: The created file record

        Raises:
            ValueError: If transaction not found or not owned by user
        """
        # Verify transaction ownership
        transaction = (
            self.db.query(Transaction)
            .join(Wallet)
            .filter(and_(Transaction.id == transaction_id, Wallet.user_id == user_id))
            .first()
        )

        if not transaction:
            raise ValueError("Transaction not found or not owned by user")

        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        # Create file record
        file_record = File(
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            url=f"/files/{unique_filename}",
            file_type=file_type,
            file_size=len(content),
            mime_type=file.content_type,
            transaction_id=transaction_id,
        )

        self.db.add(file_record)
        self.db.commit()
        self.db.refresh(file_record)
        return file_record

    def get_by_id(self, file_id: int, user_id: int) -> Optional[File]:
        """
        Get a file by ID with user ownership verification

        Args:
            file_id (int): The file ID
            user_id (int): The user ID

        Returns:
            Optional[File]: The file or None if not found
        """
        return (
            self.db.query(File)
            .join(Transaction)
            .join(Wallet)
            .filter(and_(File.id == file_id, Wallet.user_id == user_id))
            .first()
        )

    def get_transaction_files(self, transaction_id: int, user_id: int) -> List[File]:
        """
        Get all files for a transaction

        Args:
            transaction_id (int): The transaction ID
            user_id (int): The user ID

        Returns:
            List[File]: List of files
        """
        return (
            self.db.query(File)
            .join(Transaction)
            .join(Wallet)
            .filter(
                and_(File.transaction_id == transaction_id, Wallet.user_id == user_id)
            )
            .all()
        )

    def delete(self, file_id: int, user_id: int) -> bool:
        """
        Delete a file

        Args:
            file_id (int): The file ID
            user_id (int): The user ID

        Returns:
            bool: True if deleted, False if not found
        """
        file_record = self.get_by_id(file_id, user_id)
        if not file_record:
            return False

        # Delete file from disk
        file_path = os.path.join(self.upload_dir, file_record.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete database record
        self.db.delete(file_record)
        self.db.commit()
        return True

    def get_file_path(self, filename: str) -> str:
        """
        Get the full path to a file

        Args:
            filename (str): The filename

        Returns:
            str: The full file path
        """
        return os.path.join(self.upload_dir, filename)

    def cleanup_orphaned_files(self) -> int:
        """
        Clean up files that exist on disk but not in database

        Returns:
            int: Number of files cleaned up
        """
        if not os.path.exists(self.upload_dir):
            return 0

        # Get all filenames from database
        db_filenames = {f.filename for f in self.db.query(File.filename).all()}

        # Get all files on disk
        disk_files = os.listdir(self.upload_dir)

        # Remove orphaned files
        cleaned_count = 0
        for disk_file in disk_files:
            if disk_file not in db_filenames:
                file_path = os.path.join(self.upload_dir, disk_file)
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                except OSError:
                    pass  # File might be in use or permission issue

        return cleaned_count
