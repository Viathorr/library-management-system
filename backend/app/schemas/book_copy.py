from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class BookCopyStatus(str, Enum):
    available = "available"
    borrowed = "borrowed"
    reserved = "reserved"
    
    
class BookCopyBase(BaseModel):
    book_id: UUID
    status: BookCopyStatus
    
    
class BookCopy(BookCopyBase):
    copy_id: UUID
    added_at: datetime  
    
    class Config:
        from_attributes = True
        use_enum_values = True