import os
from dotenv import load_dotenv
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from app.utils.security import (
    create_access_token,
    verify_access_token,
    hash_password,
    verify_password,
    get_current_user,
    require_role,
)
from app.models.user import User

# Test constants
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
USERNAME = "testuser"
ROLE = "reader"

@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    user = User(username=USERNAME, role=ROLE, password_hash=hash_password("testpass"))
    db.query().filter().first.return_value = user
    return db

def test_create_access_token():
    data = {"username": USERNAME, "role": ROLE}
    token = create_access_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["username"] == USERNAME
    assert payload["role"] == ROLE
    assert "exp" in payload
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()

def test_verify_access_token_valid():
    data = {"username": USERNAME, "role": ROLE}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    payload = verify_access_token(token)
    assert payload["username"] == USERNAME
    assert payload["role"] == ROLE

def test_verify_access_token_invalid():
    with pytest.raises(JWTError):
        verify_access_token("invalid.token.here")

def test_hash_password():
    password = "testpass"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)

def test_verify_password_valid():
    password = "testpass"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True

def test_verify_password_invalid():
    password = "testpass"
    hashed = hash_password("wrongpass")
    assert verify_password(password, hashed) is False

def test_get_current_user_valid(mock_db):
    data = {"username": USERNAME, "role": ROLE}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    user = get_current_user(token, mock_db)
    assert user.username == USERNAME
    assert user.role == ROLE

def test_get_current_user_invalid_token(mock_db):
    with pytest.raises(HTTPException) as exc:
        get_current_user("invalid.token.here", mock_db)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"

def test_get_current_user_user_not_found(mock_db):
    data = {"username": "nonexistent", "role": ROLE}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    mock_db.query().filter().first.return_value = None
    with pytest.raises(HTTPException) as exc:
        get_current_user(token, mock_db)
    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"

def test_require_role_valid(mock_db):
    user = User(username=USERNAME, role="reader")
    role_checker = require_role("reader")
    result = role_checker(user)
    assert result == user

def test_require_role_invalid(mock_db):
    user = User(username=USERNAME, role="reader")
    role_checker = require_role("librarian")
    with pytest.raises(HTTPException) as exc:
        role_checker(user)
    assert exc.value.status_code == 403
    assert exc.value.detail == f"Role librarian required"