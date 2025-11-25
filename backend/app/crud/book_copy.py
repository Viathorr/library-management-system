from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.book_copy import BookCopy as BookCopyModel
from app.schemas.book_copy import BookCopy, BookCopyBase
from app.config.logger import logger
from app.exceptions.crud_exception import CRUDException


class BookCopyCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_book_copy(self, book_copy: BookCopyBase) -> BookCopyModel:
        try:
            logger.info(f"Creating book copy for book_id: {book_copy.book_id}")
            db_book_copy = BookCopyModel(**book_copy.model_dump())
            self.db.add(db_book_copy)
            self.db.commit()
            self.db.refresh(db_book_copy)
            return db_book_copy
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error while creating book copy: {e}")
            raise CRUDException(status_code=500, message="Internal server error")
        
    def get_available_copies(self, book_id: UUID) -> list[BookCopyModel]:
        try:
            logger.info(f"Fetching available copies for book_id: {book_id}")
            copies = self.db.query(BookCopyModel).filter(
                BookCopyModel.book_id == book_id,
                BookCopyModel.status == "available"
            ).all()
            return copies
        except Exception as e:
            logger.error(f"Error while fetching available copies: {e}")
            raise CRUDException(status_code=500, message="Internal server error")
        
    def update_book_copy_status(self, copy_id: UUID, status: str) -> BookCopyModel:
        try:
            logger.info(f"Updating status of book copy {copy_id} to {status}")
            book_copy = self.db.query(BookCopyModel).filter(BookCopyModel.copy_id == copy_id).first()
            if not book_copy:
                raise CRUDException(status_code=404, message="Book copy not found")
            book_copy.status = status
            self.db.commit()
            self.db.refresh(book_copy)
            return book_copy
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error while updating book copy status: {e}")
            raise CRUDException(status_code=400, message="Invalid status update")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error while updating book copy status: {e}")
            raise CRUDException(status_code=500, message="Internal server error")