from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.order import Order as OrderModel
from app.models.book_copy import BookCopy
from app.models.book import Book as BookModel
from app.models.user import User as UserModel
from app.schemas.order import Order, OrderBase
from app.config.logger import logger
from app.exceptions.crud_exception import CRUDException


class OrderCRUD:
    def __init__(self, db: Session):
        self.db = db
        
    def create_order(self, order: OrderBase) -> OrderModel:
        try:
            logger.info(f"Creating order")
            db_order = OrderModel(**order.model_dump())
            self.db.add(db_order)
            self.db.commit()
            self.db.refresh(db_order)
            return db_order
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error while creating order: {e}")
            raise CRUDException(status_code=500, message="Internal server error")
        
    def get_all_active_orders(self, limit: int, offset: int):
        try:
            logger.info(f"Fetching active orders with limit {limit} and offset {offset}")
            
            page = (offset // limit) + 1 if limit > 0 else 1

            orders = self.db.query(
                OrderModel.order_id,
                UserModel.username.label("username"),  
                OrderModel.copy_id,
                OrderModel.order_type,
                OrderModel.order_date,
                OrderModel.due_date,
                OrderModel.return_date,
                OrderModel.status,
                BookModel.title.label("book_title"),
            ).outerjoin(
                BookCopy, OrderModel.copy_id == BookCopy.copy_id
            ).outerjoin(
                BookModel, BookCopy.book_id == BookModel.book_id
            ).outerjoin(
                UserModel, OrderModel.user_id == UserModel.user_id  
            ).filter(
                OrderModel.status != "completed"
            ).order_by(
                OrderModel.order_date.desc()
            ).limit(limit).offset(offset).all()

            orders_list = [
                {
                    "order_id": order.order_id,
                    "username": order.username,  
                    "copy_id": order.copy_id,
                    "order_type": order.order_type,
                    "order_date": order.order_date.isoformat() if order.order_date else None,
                    "due_date": order.due_date.isoformat() if order.due_date else None,
                    "return_date": order.return_date.isoformat() if order.return_date else None,
                    "status": order.status,
                    "book_title": order.book_title
                }
                for order in orders
            ]

            has_next = False
            if orders:
                next_order = self.db.query(OrderModel.order_id) \
                    .outerjoin(BookCopy, OrderModel.copy_id == BookCopy.copy_id) \
                    .outerjoin(BookModel, BookCopy.book_id == BookModel.book_id) \
                    .outerjoin(UserModel, OrderModel.user_id == UserModel.user_id) \
                    .filter(
                        OrderModel.status != "completed"
                    ).order_by(
                        OrderModel.order_date.desc()
                    ).limit(1).offset(offset + limit).first()

                has_next = next_order is not None

            return {
                "orders": orders_list,
                "page": page,
                "has_next": has_next
            }
            
        except Exception as e:
            logger.error(f"Error while fetching active orders: {e}")
            raise CRUDException(status_code=500, message="Internal server error")
        
    def get_orders_by_user(self, username: str, limit: int, offset: int):
        try:
            logger.info(f"Fetching orders for username {username} with limit {limit} and offset {offset}")

            # Calculate page number
            page = (offset // limit) + 1 if limit > 0 else 1

            # Fetch orders (now joining UserModel and filtering by username)
            orders = self.db.query(
                OrderModel.order_id,
                UserModel.username.label("username"),
                OrderModel.copy_id,
                OrderModel.order_type,
                OrderModel.order_date,
                OrderModel.due_date,
                OrderModel.return_date,
                OrderModel.status,
                BookModel.title.label("book_title"),
            ).outerjoin(
                UserModel, OrderModel.user_id == UserModel.user_id
            ).outerjoin(
                BookCopy, OrderModel.copy_id == BookCopy.copy_id
            ).outerjoin(
                BookModel, BookCopy.book_id == BookModel.book_id
            ).filter(
                UserModel.username == username,
                OrderModel.status != "completed"
            ).order_by(
                OrderModel.order_date.desc()
            ).limit(limit).offset(offset).all()

            orders_list = [
                {
                    "order_id": order.order_id,
                    "username": order.username,
                    "copy_id": order.copy_id,
                    "order_type": order.order_type,
                    "order_date": order.order_date.isoformat() if order.order_date else None,
                    "due_date": order.due_date.isoformat() if order.due_date else None,
                    "return_date": order.return_date.isoformat() if order.return_date else None,
                    "status": order.status,
                    "book_title": order.book_title
                }
                for order in orders
            ]

            # Check for next page
            has_next = False
            if orders:
                next_order = self.db.query(OrderModel.order_id) \
                    .outerjoin(UserModel, OrderModel.user_id == UserModel.user_id) \
                    .outerjoin(BookCopy, OrderModel.copy_id == BookCopy.copy_id) \
                    .outerjoin(BookModel, BookCopy.book_id == BookModel.book_id) \
                    .filter(
                        UserModel.username == username,
                        OrderModel.status != "completed"
                    ).order_by(
                        OrderModel.order_date.desc()
                    ).limit(1).offset(offset + limit).first()

                has_next = next_order is not None

            return {
                "orders": orders_list,
                "page": page,
                "has_next": has_next
            }

        except Exception as e:
            logger.error(f"Error while fetching orders for username {username}: {e}")
            raise CRUDException(status_code=500, message="Internal server error")

        
    def update_order_status(self, order_id: UUID, status: str) -> OrderModel:
        try:
            logger.info(f"Updating order status for order_id {order_id} to {status}")
            order = self.db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
            if not order:
                raise CRUDException(status_code=404, message="Order not found")
            
            order.status = status
            self.db.commit()
            self.db.refresh(order)
            return order
        except CRUDException as e:
            raise e
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error while updating order status: {e}")
            raise CRUDException(status_code=400, message="Invalid status update")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error while updating order status: {e}")
            raise CRUDException(status_code=500, message="Internal server error")