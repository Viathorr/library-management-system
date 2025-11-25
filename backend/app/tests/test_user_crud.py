import pytest
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.crud.user import UserCRUD
from app.models.user import User
from app.schemas.user import UserBase
from app.exceptions.crud_exception import CRUDException
from unittest.mock import Mock

# Fixture for mock database session
@pytest.fixture
def db_session():
    return Mock(spec=Session)

# Fixture for sample user data
@pytest.fixture
def user_data():
    return UserBase(
        username="testuser",
        email="test@example.com",
        role="reader",
        password_hash="testpass123"
    )

# Fixture for sample User model instance
@pytest.fixture
def user_instance():
    return User(
        user_id=uuid4(),
        username="testuser",
        email="test@example.com",
        role="reader",
        password_hash="hashed_password",
        created_at="2025-05-29T18:44:00"
    )

def test_create_user_success(db_session, user_data, user_instance):
    # Arrange
    db_session.add = Mock()
    db_session.commit = Mock()
    db_session.refresh = Mock()
    db_session.query.return_value.filter.return_value.first.return_value = None
    user_crud = UserCRUD(db_session)
    
    # Act
    result = user_crud.create_user(user_data)
    
    # Assert
    assert isinstance(result, User)
    assert result.username == user_data.username
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()

def test_create_user_duplicate_username(db_session, user_data):
    # Arrange
    db_session.add = Mock()
    db_session.commit = Mock(side_effect=IntegrityError("unique constraint", {}, BaseException("unique constraint")))
    db_session.rollback = Mock()
    user_crud = UserCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        user_crud.create_user(user_data)
    assert exc.value.status_code == 409
    assert "Username or email already exists" in exc.value.message
    db_session.rollback.assert_called_once()

def test_get_user_password_hash_success(db_session, user_instance):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = user_instance
    user_crud = UserCRUD(db_session)
    
    # Act
    result = user_crud.get_user_password_hash("testuser")
    
    # Assert
    assert result == "hashed_password"

def test_get_user_password_hash_not_found(db_session):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = None
    user_crud = UserCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        user_crud.get_user_password_hash("nonexistent")
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.message

def test_get_user_id_by_username_success(db_session, user_instance):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = user_instance
    user_crud = UserCRUD(db_session)
    
    # Act
    result = user_crud.get_user_id_by_username("testuser")
    
    # Assert
    assert isinstance(result, UUID)
    assert result == user_instance.user_id

def test_get_user_id_by_username_not_found(db_session):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = None
    user_crud = UserCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        user_crud.get_user_id_by_username("nonexistent")
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.message

def test_get_user_by_username_success(db_session, user_instance):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = user_instance
    user_crud = UserCRUD(db_session)
    
    # Act
    result = user_crud.get_user_by_username("testuser")
    
    # Assert
    assert isinstance(result, User)
    assert result.username == "testuser"

def test_get_user_by_username_not_found(db_session):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = None
    user_crud = UserCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        user_crud.get_user_by_username("nonexistent")
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.message

def test_get_user_by_id_success(db_session, user_instance):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = user_instance
    user_crud = UserCRUD(db_session)
    
    # Act
    result = user_crud.get_user_by_id(user_instance.user_id)
    
    # Assert
    assert isinstance(result, User)
    assert result.user_id == user_instance.user_id

def test_get_user_by_id_not_found(db_session):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = None
    user_crud = UserCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        user_crud.get_user_by_id(uuid4())
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.message

def test_delete_user_success(db_session, user_instance):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = user_instance
    db_session.delete = Mock()
    db_session.commit = Mock()
    user_crud = UserCRUD(db_session)
    
    # Act
    result = user_crud.delete_user(user_instance.username)
    
    # Assert
    assert result == {"message": "User deleted successfully"}
    db_session.delete.assert_called_once()
    db_session.commit.assert_called_once()

def test_delete_user_not_found(db_session):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = None
    user_crud = UserCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        user_crud.delete_user("nonexistent")
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.message