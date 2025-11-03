import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.controllers.books.book_controller import BookController
from app.schemas.book import BookPost
from app.schemas.book_copy import BookCopyBase, BookCopyStatus
from app.crud.book import BookCRUD
from app.crud.book_copy import BookCopyCRUD
from app.exceptions.crud_exception import CRUDException
from app.models.book import Book as BookModel
from uuid import uuid4

# Fixture for mock database session
@pytest.fixture
def db_session():
    return Mock(spec=Session)

# Fixture for sample book data
@pytest.fixture
def book_post_data():
    return BookPost(
        title="Test Book",
        author="Test Author",
        isbn="1234567890123",
        publication_year=2020,
        description="A test book",
        num_copies=2
    )

# Fixture for sample Book model instance
@pytest.fixture
def book_instance():
    return BookModel(
        book_id=uuid4(),
        title="Test Book",
        author="Test Author",
        isbn="1234567890123",
        publication_year=2020,
        description="A test book"
    )

# Fixture for mocked BookCRUD
@pytest.fixture
def mock_book_crud(book_instance):
    mock_crud = Mock(spec=BookCRUD)
    mock_crud.create_book = Mock(return_value=book_instance)
    mock_crud.get_books = Mock(return_value=[
        (
            book_instance.book_id,
            book_instance.title,
            book_instance.author,
            book_instance.isbn,
            book_instance.publication_year,
            book_instance.description,
            2  # available_copies
        )
    ])
    return mock_crud

# Fixture for mocked BookCopyCRUD
@pytest.fixture
def mock_book_copy_crud():
    mock_crud = Mock(spec=BookCopyCRUD)
    mock_crud.create_book_copy = Mock()
    return mock_crud

def test_add_book_success_with_copies(db_session, book_post_data, book_instance, mock_book_crud, mock_book_copy_crud):
    # Arrange
    book_controller = BookController(db=db_session)
    book_controller.book_crud = mock_book_crud
    book_controller.book_copy_crud = mock_book_copy_crud

    # Act
    result = book_controller.add_book(book_post_data)

    # Assert
    assert result == book_instance
    mock_book_crud.create_book.assert_called_once_with({
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890123",
        "publication_year": 2020,
        "description": "A test book"
    })
    assert mock_book_copy_crud.create_book_copy.call_count == 2
    mock_book_copy_crud.create_book_copy.assert_called_with(
        BookCopyBase(book_id=book_instance.book_id, status=BookCopyStatus.available)
    )

def test_add_book_success_no_copies(db_session, book_instance, mock_book_crud, mock_book_copy_crud):
    # Arrange
    book_post_data = BookPost(
        title="Test Book",
        author="Test Author",
        isbn="1234567890123",
        publication_year=2020,
        description="A test book",
        num_copies=0
    )
    book_controller = BookController(db=db_session)
    book_controller.book_crud = mock_book_crud
    book_controller.book_copy_crud = mock_book_copy_crud

    # Act
    result = book_controller.add_book(book_post_data)

    # Assert
    assert result == book_instance
    mock_book_crud.create_book.assert_called_once()
    mock_book_copy_crud.create_book_copy.assert_not_called()

def test_add_book_duplicate_book(db_session, book_post_data, mock_book_crud, mock_book_copy_crud):
    # Arrange
    mock_book_crud.create_book = Mock(side_effect=CRUDException(
        message="Book already exists", status_code=400
    ))
    book_controller = BookController(db=db_session)
    book_controller.book_crud = mock_book_crud
    book_controller.book_copy_crud = mock_book_copy_crud

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        book_controller.add_book(book_post_data)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Book already exists"
    mock_book_copy_crud.create_book_copy.assert_not_called()

def test_get_books_success(db_session, mock_book_crud, mock_book_copy_crud):
    # Arrange
    book_controller = BookController(db=db_session)
    book_controller.book_crud = mock_book_crud
    book_controller.book_copy_crud = mock_book_copy_crud

    # Act
    result = book_controller.get_books(limit=10, offset=0)

    # Assert
    assert len(result) == 1
    assert result[0][1] == "Test Book"
    assert result[0][-1] == 2
    mock_book_crud.get_books.assert_called_once_with(10, 0)

def test_get_books_empty(db_session, mock_book_crud, mock_book_copy_crud):
    # Arrange
    mock_book_crud.get_books = Mock(return_value=[])
    book_controller = BookController(db=db_session)
    book_controller.book_crud = mock_book_crud
    book_controller.book_copy_crud = mock_book_copy_crud

    # Act
    result = book_controller.get_books(limit=10, offset=0)

    # Assert
    assert result == []
    mock_book_crud.get_books.assert_called_once_with(10, 0)

def test_get_books_error(db_session, mock_book_crud, mock_book_copy_crud):
    # Arrange
    mock_book_crud.get_books = Mock(side_effect=CRUDException(
        message="Internal server error", status_code=500
    ))
    book_controller = BookController(db=db_session)
    book_controller.book_crud = mock_book_crud
    book_controller.book_copy_crud = mock_book_copy_crud

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        book_controller.get_books(limit=10, offset=0)
    assert exc.value.status_code == 500
    assert exc.value.detail == "Internal server error"