from uuid import UUID
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.order import OrderBase
from app.db.session import get_db
from app.crud.order import OrderCRUD
from app.crud.book_copy import BookCopyCRUD
from app.exceptions.crud_exception import CRUDException


class OrderController:
    def __init__(self, db: Session):
        self.order_crud = OrderCRUD(db)
        self.book_copy_crud = BookCopyCRUD(db)

    def create_order(self, user_id, order_data):
        try:
            # order_data is a dict of book_id, order_type
            available_copies = self.book_copy_crud.get_available_copies(order_data['book_id'])
            if not available_copies:
                raise HTTPException(status_code=404, detail="No available copies for this book")
            
            if order_data['order_type'] == "borrow":
                order_date = datetime.now(timezone.utc)
                due_date = order_date + timedelta(days=7)
            else:
                due_date = None
            order = OrderBase(
                user_id=user_id,
                copy_id=available_copies[0].copy_id,  # Use the first available copy
                order_type=order_data['order_type'],
                due_date=due_date
            )
            
            self.book_copy_crud.update_book_copy_status(available_copies[0].copy_id, "borrowed")
            
            return self.order_crud.create_order(order)
        except HTTPException as e:
            raise e
        except CRUDException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")

    def get_all_orders(self, limit: int = 10, offset: int = 0):
        try: 
            return self.order_crud.get_all_active_orders(limit, offset)
        except CRUDException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
        
    def get_orders_by_user(self, username: str, limit: int = 10, offset: int = 0):
        try:
            return self.order_crud.get_orders_by_user(username, limit, offset)
        except CRUDException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")    
        
    def update_order_status(self, order_id: str, status: str):
        try:
            order = self.order_crud.update_order_status(order_id, status)
            
            if status == "completed":
                self.book_copy_crud.update_book_copy_status(order.copy_id, "available")
                
            return order
        except CRUDException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
        

def get_order_controller(db: Session = Depends(get_db)):
    return OrderController(db)