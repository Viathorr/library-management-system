from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from enum import Enum
from typing import Optional


class OrderType(str, Enum):
    borrow = "borrow"
    read_in_library = "read_in_library"
    
    
class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    overdue = "overdue"
    
    
class OrderBase(BaseModel):
    user_id: UUID
    copy_id: UUID
    order_type: OrderType
    due_date: Optional[datetime] = None
    
    
class Order(OrderBase):
    order_id: UUID
    order_date: datetime
    return_date: Optional[datetime] = None
    status: OrderStatus
    book_title: str = None
    
    class Config:
        from_attributes = True
        use_enum_values = True