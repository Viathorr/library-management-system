import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.controllers.authentication.auth_controller import AuthController
from app.schemas.user import UserBase
from app.exceptions.crud_exception import CRUDException
from app.models.user import User

# Fixture for mock database session
@pytest.fixture
def db_session(mocker):
    return mocker.MagicMock(spec=Session)

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
        user_id="123e4567-e89b-12d3-a456-426614174000",
        username="testuser",
        email="test@example.com",
        role="reader",
        password_hash="hashed_password",
        created_at="2025-05-29T18:44:00"
    )

# def test_signup_success(mocker, db_session, user_data, user_instance):
#     # Arrange
#     mocker.patch("app.crud.user.UserCRUD.create_user", return_value=user_instance)
#     mocker.patch("app.utils.security.hash_password", return_value="hashed_password")
#     mocker.patch("app.utils.security.create_access_token", return_value="jwt_token")
#     auth_controller = AuthController(db=db_session)

#     # Act
#     result = auth_controller.signup(user_data)

#     # Assert
#     assert result == {"access_token": "jwt_token", "token_type": "bearer"}
#     assert user_data.password_hash == "hashed_password"
#     mocker.patch("app.crud.user.UserCRUD.create_user").assert_called_once()
#     mocker.patch("app.utils.security.create_access_token").assert_called_once_with(
#         data={"username": "testuser", "role": "reader"}
#     )

def test_signup_duplicate_user(mocker, db_session, user_data):
    # Arrange
    mocker.patch(
        "app.crud.user.UserCRUD.create_user",
        side_effect=CRUDException(message="Username or email already exists", status_code=409)
    )
    mocker.patch("app.utils.security.hash_password", return_value="hashed_password")
    auth_controller = AuthController(db=db_session)

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        auth_controller.signup(user_data)
    assert exc.value.status_code == 409
    assert exc.value.detail == "Username or email already exists"

def test_signup_unexpected_error(mocker, db_session, user_data):
    # Arrange
    mocker.patch("app.crud.user.UserCRUD.create_user", side_effect=Exception("Unexpected error"))
    mocker.patch("app.utils.security.hash_password", return_value="hashed_password")
    auth_controller = AuthController(db=db_session)

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        auth_controller.signup(user_data)
    assert exc.value.status_code == 500
    assert exc.value.detail == "Unexpected error"

# def test_login_success(mocker, db_session, user_instance):
#     # Arrange
#     mocker.patch("app.crud.user.UserCRUD.get_user_by_username", return_value=user_instance)
#     mocker.patch("app.utils.security.verify_password", return_value=True)
#     mocker.patch("app.utils.security.create_access_token", return_value="jwt_token")
#     auth_controller = AuthController(db=db_session)

#     # Act
#     result = auth_controller.login(username="testuser", password="testpass123")

#     # Assert
#     assert result == {"access_token": "jwt_token", "token_type": "bearer"}
#     mocker.patch("app.crud.user.UserCRUD.get_user_by_username").assert_called_once_with("testuser")
#     mocker.patch("app.utils.security.verify_password").assert_called_once_with("testpass123", "hashed_password")
#     mocker.patch("app.utils.security.create_access_token").assert_called_once_with(
#         data={"username": "testuser", "role": "reader"}
#     )

# def test_login_invalid_credentials(mocker, db_session, user_instance):
#     # Arrange
#     mocker.patch("app.crud.user.UserCRUD.get_user_by_username", return_value=user_instance)
#     mocker.patch("app.utils.security.verify_password", return_value=False)
#     auth_controller = AuthController(db=db_session)

#     # Act & Assert
#     with pytest.raises(HTTPException) as exc:
#         auth_controller.login(username="testuser", password="wrongpass")
#     assert exc.value.status_code == 401
#     assert exc.value.detail == "Invalid credentials"

def test_login_user_not_found(mocker, db_session):
    # Arrange
    mocker.patch(
        "app.crud.user.UserCRUD.get_user_by_username",
        side_effect=CRUDException(message="User not found", status_code=404)
    )
    auth_controller = AuthController(db=db_session)

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        auth_controller.login(username="nonexistent", password="testpass123")
    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"

def test_login_unexpected_error(mocker, db_session):
    # Arrange
    mocker.patch("app.crud.user.UserCRUD.get_user_by_username", side_effect=Exception("Unexpected error"))
    auth_controller = AuthController(db=db_session)

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        auth_controller.login(username="testuser", password="testpass123")
    assert exc.value.status_code == 500
    assert exc.value.detail == "Unexpected error"

def test_logout_success(mocker, db_session):
    # Arrange
    auth_controller = AuthController(db=db_session)

    # Act
    result = auth_controller.logout()

    # Assert
    assert result == {"message": "Successfully logged out"}