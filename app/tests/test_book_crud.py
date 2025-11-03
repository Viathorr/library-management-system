import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.crud.book import BookCRUD
from app.models.book import Book as BookModel
from app.exceptions.crud_exception import CRUDException
from unittest.mock import Mock

# Fixture for mock database session
@pytest.fixture
def db_session():
    return Mock(spec=Session)

# Fixture for sample book data
@pytest.fixture
def book_data():
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890123",
        "publication_year": 2020,
        "description": "A test book"
    }

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

def test_create_book_success(db_session, book_data, book_instance):
    # Arrange
    db_session.add = Mock()
    db_session.commit = Mock()
    db_session.refresh = Mock(return_value=book_instance)
    book_crud = BookCRUD(db_session)
    
    # Act
    result = book_crud.create_book(book_data)
    
    # Assert
    assert isinstance(result, BookModel)
    assert result.title == book_data["title"]
    assert result.isbn == book_data["isbn"]
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()

def test_create_book_duplicate_isbn(db_session, book_data):
    # Arrange
    db_session.add = Mock()
    db_session.commit = Mock(side_effect=IntegrityError("unique constraint", {}, None))
    db_session.rollback = Mock()
    book_crud = BookCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        book_crud.create_book(book_data)
    assert exc.value.status_code == 400
    assert exc.value.message == "Book already exists"
    db_session.rollback.assert_called_once()

def test_create_book_unexpected_error(db_session, book_data):
    # Arrange
    db_session.add = Mock()
    db_session.commit = Mock(side_effect=Exception("Unexpected error"))
    db_session.rollback = Mock()
    book_crud = BookCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        book_crud.create_book(book_data)
    assert exc.value.status_code == 500
    assert exc.value.message == "Internal server error"
    db_session.rollback.assert_called_once()

def test_get_books_success(db_session, book_instance):
    # Arrange
    mock_book_data = [
        Mock(
            book_id=book_instance.book_id,
            title=book_instance.title,
            author=book_instance.author,
            isbn=book_instance.isbn,
            publication_year=book_instance.publication_year,
            description=book_instance.description,
            available_copies=2
        )
    ]

    query_mock = Mock()
    (
        query_mock.outerjoin.return_value
        .group_by.return_value
        .order_by.return_value
        .limit.return_value
        .offset.return_value
        .all.return_value
    ) = mock_book_data

    db_session.query.return_value = query_mock
    book_crud = BookCRUD(db_session)

    # Act
    result = book_crud.get_books(limit=10, offset=0)

    # Assert
    assert isinstance(result, dict)
    assert "books" in result
    assert len(result["books"]) == 1
    assert result["books"][0]["book_id"] == book_instance.book_id
    assert result["books"][0]["title"] == book_instance.title
    assert result["books"][0]["available_copies"] == 2
    assert result["page"] == 1
    assert result["has_next"] in [True, False]
    db_session.query.assert_called()

def test_get_books_empty_result(db_session):
    # Arrange
    query_mock = Mock()
    (
        query_mock.outerjoin.return_value
        .group_by.return_value
        .order_by.return_value
        .limit.return_value
        .offset.return_value
        .all.return_value
    ) = []

    db_session.query.return_value = query_mock
    book_crud = BookCRUD(db_session)

    # Act
    result = book_crud.get_books(limit=10, offset=0)

    # Assert
    assert isinstance(result, dict)
    assert result["books"] == []
    assert result["page"] == 1
    assert result["has_next"] is False
    db_session.query.assert_called()

def test_get_books_unexpected_error(db_session):
    # Arrange
    db_session.query.side_effect = Exception("Database error")
    book_crud = BookCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        book_crud.get_books(limit=10, offset=0)
    assert exc.value.status_code == 500
    assert exc.value.message == "Internal server error"