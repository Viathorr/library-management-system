from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=13, max_length=13)
    publication_year: Optional[int] = None
    description: Optional[str] = None
    
    
class BookPost(BookBase):
    """
    Schema for creating a new book.
    """
    num_copies: int = Field(ge=0, description="Number of available copies of the book")
    
    
class Book(BookBase):
    book_id: UUID
    
    class Config:
        from_attributes = True
        
        
class BookGet(Book):
    available_copies: int = Field(ge=0, description="Number of available copies of the book")