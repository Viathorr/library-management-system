from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.book import Book as BookModel
from app.models.book_copy import BookCopy
from app.schemas.book import BookBase
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
    