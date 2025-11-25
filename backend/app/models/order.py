from sqlalchemy import Column, ForeignKey, TIMESTAMP, CheckConstraint, String
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from app.db.base_class import Base


class Order(Base):
    """
    Order model.
    """
    __tablename__ = "orders"

    order_id = Column(UUID(), primary_key=True, server_default=text("uuid_generate_v4()"), nullable=False)
    user_id = Column(UUID(), ForeignKey("users.user_id"), nullable=False)
    copy_id = Column(UUID(), ForeignKey("book_copies.copy_id"), nullable=False)
    order_type = Column(String(20), CheckConstraint("order_type IN ('borrow', 'read_in_library')"), nullable=False)  
    order_date = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    due_date = Column(TIMESTAMP, nullable=True)  
    return_date = Column(TIMESTAMP, nullable=True)  
    status = Column(String(20), CheckConstraint("status IN ('pending', 'completed', 'overdue')"), server_default="pending", nullable=False)