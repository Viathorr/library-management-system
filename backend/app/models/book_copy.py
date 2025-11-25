from sqlalchemy import Column, TIMESTAMP, ForeignKey, CheckConstraint, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from app.db.base_class import Base


class BookCopy(Base):
    """
    BookCopy model.
    """
    __tablename__ = "book_copies"

    copy_id = Column(UUID(), primary_key=True, server_default=text("uuid_generate_v4()"), nullable=False)
    book_id = Column(UUID(), ForeignKey("books.book_id"), nullable=False)
    status = Column(String(20), CheckConstraint("status IN ('available', 'borrowed', 'reserved')"), nullable=False) 
    added_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")) 