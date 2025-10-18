from fastapi import Depends, APIRouter
from app.schemas.book import Book, BookPost, BookGet
from app.controllers.books.book_controller import BookController, get_book_controller
from app.config.logger import logger
from app.utils.security import get_current_user, require_role


router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=Book, dependencies=[Depends(require_role("librarian"))])
def add_book(book: BookPost, book_controller: BookController = Depends(get_book_controller)):
    """
    Add a new book to the collection.
    """
    logger.info(f"POST request to add book: {book.title}")
    return book_controller.add_book(book)


@router.get("/", response_model=dict, dependencies=[Depends(get_current_user)])
def get_books(limit: int = 10, offset: int = 0, book_controller: BookController = Depends(get_book_controller)):
    """
    Retrieve a list of books with pagination.
    """
    logger.info(f"GET request to retrieve books with limit: {limit}, offset: {offset}")
    return book_controller.get_books(limit, offset)