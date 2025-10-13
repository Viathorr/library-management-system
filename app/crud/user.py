from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserBase
from app.config.logger import logger
from app.exceptions.crud_exception import CRUDException


class UserCRUD:
    def __init__(self, db: Session):
        self.db = db
        
    def create_user(self, user: UserBase):
        try:
            logger.info(f"Creating user with username: {user.username}")
            db_user = User(**user.model_dump())
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error while creating user: {str(e)}")
            if "unique constraint" in str(e.orig).lower():
                raise CRUDException(
                    message="Username or email already exists",
                    status_code=409  # Conflict
                )
            raise CRUDException(
                message="Database integrity error",
                status_code=400  # Bad Request
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error while creating user: {str(e)}")
            raise CRUDException(
                message=f"Unexpected database error: {str(e)}",
                status_code=500  # Internal Server Error
            )
            
    def get_user_password_hash(self, username: str):
        try:
            logger.info(f"Retrieving password hash for user: {username}")
            user = self.db.query(User).filter(User.username == username).first()
            if user is None:
                raise CRUDException(
                    message="User not found",
                    status_code=404  # Not Found
                )
            return user.password_hash
        except CRUDException as e:
            raise e
        except Exception as e:
            logger.error(f"Error retrieving password hash for user {username}: {str(e)}")
            raise CRUDException(
                message=f"Error retrieving password hash: {str(e)}",
                status_code=500  # Internal Server Error
            )
            
    def get_user_id_by_username(self, username: str):
        try:
            logger.info(f"Retrieving user ID for username: {username}")
            user = self.db.query(User).filter(User.username == username).first()
            if user is None:
                raise CRUDException(
                    message="User not found",
                    status_code=404  # Not Found
                )
            return user.user_id
        except CRUDException as e:
            raise e
        except Exception as e:
            logger.error(f"Error retrieving user ID for username {username}: {str(e)}")
            raise CRUDException(
                message=f"Error retrieving user ID: {str(e)}",
                status_code=500  # Internal Server Error
            )
            
    def get_user_by_username(self, username: str) -> User:
        try:
            logger.info(f"Retrieving user by username: {username}")
            user = self.db.query(User).filter(User.username == username).first()
            if user is None:
                raise CRUDException(
                    message="User not found",
                    status_code=404  # Not Found
                )
            return user
        except CRUDException as e:
            raise e
        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {str(e)}")
            raise CRUDException(
                message=f"Error retrieving user: {str(e)}",
                status_code=500  # Internal Server Error
            )
            
    def get_user_by_id(self, user_id: UUID) -> User:
        try:
            logger.info(f"Retrieving user by ID: {user_id}")
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if user is None:
                raise CRUDException(
                    message="User not found",
                    status_code=404  # Not Found
                )
            return user
        except CRUDException as e:
            raise e
        except Exception as e:
            logger.error(f"Error retrieving user by ID {user_id}: {str(e)}")
            raise CRUDException(
                message=f"Error retrieving user: {str(e)}",
                status_code=500  # Internal Server Error
            )
            
    def delete_user(self, username: UUID):
        try:
            logger.info(f"Deleting user with username: {username}")
            user = self.db.query(User).filter(User.username == username).first()
            if user is None:
                raise CRUDException(
                    message="User not found",
                    status_code=404  # Not Found
                )
            self.db.delete(user)
            self.db.commit()
            return {"message": "User deleted successfully"}
        except CRUDException as e:
            raise e
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user with username {username}: {str(e)}")
            raise CRUDException(
                message=f"Error deleting user: {str(e)}",
                status_code=500  # Internal Server Error
            )   