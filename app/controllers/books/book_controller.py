from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.book import BookPost, BookBase
from app.schemas.book_copy import BookCopyBase, BookCopyStatus
from app.db.session import get_db
from app.crud.book import BookCRUD
from app.crud.book_copy import BookCopyCRUD
from app.exceptions.crud_exception import CRUDException


class BookController:
    def __init__(self, db: Session = Depends(get_db)):
        self.book_crud = BookCRUD(db)
        self.book_copy_crud = BookCopyCRUD(db)

    def add_book(self, book: BookPost):
        try:
            num_copies = book.num_copies
            book_info = book.model_dump(exclude={"num_copies"})
            created_book = self.book_crud.create_book(book_info)
            
            if num_copies > 0:
                # Create book copies
                for _ in range(num_copies):
                    book_copy = BookCopyBase(
                        book_id=created_book.book_id,
                        status=BookCopyStatus.available
                    )
                    self.book_copy_crud.create_book_copy(book_copy)
            return created_book
        except CRUDException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        
    def get_books(self, limit: int = 10, offset: int = 0):
        try:
            return self.book_crud.get_books(limit, offset)
        except CRUDException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        
        
def get_book_controller(db: Session = Depends(get_db)):
    return BookController(db)