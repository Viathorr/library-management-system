import os
import bcrypt
from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User

# Security utilities for hashing passwords and JWT token management
load_dotenv()

# Constants for JWT token management
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Creates a JWT access token with the given data and expiration time.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta | None): The expiration time for the token.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    """
    Verifies a JWT access token and returns the decoded data.

    Args:
        token (str): The JWT access token to verify.

    Returns:
        dict: The decoded data from the token if valid, otherwise raises an exception.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise JWTError("Could not validate credentials")
    
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Retrieves the current user from the given access token.

    Args:
        token (str): The JWT access token to verify.
        db (Session): The database session to use for the query.

    Returns:
        User: The current user if the token is valid and the user exists, otherwise raises an exception.
    """
    try:
        payload = verify_access_token(token)
    
        if not payload or not payload.get("username"):
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == payload["username"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(required_role: str):
    """
    Requires the given role for the route.

    Args:
        required_role (str): The required role.

    Returns:
        Callable[[User], User]: A function that checks if the current user has the required role.
    """
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail=f"Role {required_role} required")
        return user
    return role_checker

def hash_password(password: str) -> str:
    """
    Hashes a plain password using the default password hashing algorithm.

    Args:
        password (str): The plain password to hash.

    Returns:
        str: The hashed password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to verify against.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))