from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.models.base import Base
import enum


class FileType(str, enum.Enum):
    """File type enumeration"""

    RECEIPT = "receipt"
    INVOICE = "invoice"
    DOCUMENT = "document"
    IMAGE = "image"
    PDF = "pdf"
    OTHER = "other"


class File(Base):
    """File model for transaction attachments"""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String(100), nullable=True)

    # Foreign keys
    transaction_id = Column(
        Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transaction = relationship("Transaction", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.id}, filename={self.filename}, type={self.file_type})>"
