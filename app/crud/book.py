from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.book import Book as BookModel
from app.models.book_copy import BookCopy
from app.models.order import Order
from app.config.logger import logger
from app.exceptions.crud_exception import CRUDException


class BookCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_book(self, book) -> BookModel:
        try:
            logger.info(f"Creating book with title: {book['title']}")
            db_book = BookModel(**book)
            self.db.add(db_book)
            self.db.commit()
            self.db.refresh(db_book)
            return db_book
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error while creating book: {e}")
            raise CRUDException(status_code=400, message="Book already exists")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error while creating book: {e}")
            raise CRUDException(status_code=500, message="Internal server error")
        
    def get_book(self, book_id: UUID):
        logger.info(f"Retrieving book with id: {book_id}")
        book = self.db.query(BookModel).filter(BookModel.book_id == book_id).first()
        available_copies = self.db.query(BookCopy).filter(BookCopy.book_id == book_id, BookCopy.status == "available").count()
        if not book:
            raise CRUDException(status_code=404, message="Book not found")
        return {
        "book_id": book.book_id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "publication_year": book.publication_year,
        "description": book.description,
        "available_copies": available_copies
    }
        
    def get_books(self, limit: int, offset: int):
        logger.info(f"Retrieving books with limit: {limit}, offset: {offset}")
        try:
            # Calculate page number
            page = (offset // limit) + 1 if limit > 0 else 1

            # Fetch books
            books = self.db.query(
                BookModel.book_id,
                BookModel.title,
                BookModel.author,
                BookModel.isbn,
                BookModel.publication_year,
                BookModel.description,
                func.count(BookCopy.copy_id).label("available_copies")
            ).outerjoin(BookCopy, (BookModel.book_id == BookCopy.book_id) & (BookCopy.status == "available")) \
            .group_by(BookModel.book_id) \
            .order_by(BookModel.title) \
            .limit(limit) \
            .offset(offset) \
            .all()
            
            books_list = [
                {
                    "book_id": book.book_id,
                    "title": book.title,
                    "author": book.author,
                    "isbn": book.isbn,
                    "publication_year": book.publication_year,
                    "description": book.description,
                    "available_copies": book.available_copies
                }
                for book in books
            ]

            # Check for next page
            has_next = False
            if books:
                next_books = self.db.query(BookModel.book_id) \
                    .outerjoin(BookCopy, (BookModel.book_id == BookCopy.book_id) & (BookCopy.status == "available")) \
                    .group_by(BookModel.book_id) \
                    .order_by(BookModel.title) \
                    .limit(1) \
                    .offset(offset + limit) \
                    .first()
                has_next = next_books is not None

            return {
                "books": books_list,
                "page": page,
                "has_next": has_next
            }
        except Exception as e:
            logger.error(f"Error while retrieving books: {e}")
            raise CRUDException(status_code=500, message="Internal server error")
        
    def get_most_popular_books_last_month(self, limit: int = 10):
        """
        Returns the most popular books based on orders within the last 30 days.
        """
        try:
            logger.info("Fetching most popular books (last month)")
            last_month_date = datetime.now(timezone.utc) - timedelta(days=30)

            results = (
                self.db.query(
                    BookModel.book_id,
                    BookModel.title,
                    BookModel.author,
                    func.count(Order.order_id).label("recent_orders")
                )
                .join(BookCopy, BookCopy.book_id == BookModel.book_id)
                .join(Order, and_(
                    Order.copy_id == BookCopy.copy_id,
                    Order.order_date >= last_month_date
                ))
                .group_by(BookModel.book_id)
                .order_by(desc("recent_orders"))
                .limit(limit)
                .all()
            )

            return [
                {
                    "book_id": r.book_id,
                    "title": r.title,
                    "author": r.author,
                    "recent_orders": r.recent_orders,
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error fetching most popular books (last month): {e}")
            raise CRUDException(status_code=500, message="Internal server error")
    