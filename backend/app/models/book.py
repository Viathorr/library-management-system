from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from app.db.base_class import Base


class Book(Base):
    """
    Book model.
    """
    __tablename__ = "books"

    book_id = Column(UUID(), primary_key=True, server_default=text("uuid_generate_v4()"), nullable=False)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(13), unique=True, nullable=False)
    publication_year = Column(Integer, nullable=True)
    description = Column(Text(), nullable=True)