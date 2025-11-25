from sqlalchemy import Column, String, TIMESTAMP, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from app.db.base_class import Base
    
    
class User(Base):
    """
    User model.
    """
    __tablename__ = "users"

    user_id = Column(UUID(), primary_key=True, server_default=text("uuid_generate_v4()"), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    role = Column(String(20), CheckConstraint("role IN ('reader', 'librarian')"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)