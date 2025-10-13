from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserBase
from app.db.session import get_db
from app.crud.user import UserCRUD
from app.exceptions.crud_exception import CRUDException
from app.utils.security import hash_password, verify_password, create_access_token


class AuthController:
    def __init__(self, db: Session = Depends(get_db)):
        self.user_crud = UserCRUD(db)
        
    def signup(self, user: UserBase):
        try:
            user.password_hash = hash_password(user.password_hash)
            user = self.user_crud.create_user(user) 
            
            access_token = create_access_token(data={"username": user.username, "role": user.role})
            print(f"Access Token: {access_token}")
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        except CRUDException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    def login(self, username: str, password: str):
        try:
            user = self.user_crud.get_user_by_username(username)
            
            if not verify_password(password, user.password_hash):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            access_token = create_access_token(data={"username": user.username, "role": user.role})
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        except CRUDException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def logout(self):
        return {"message": "Successfully logged out"}
    
    
def get_auth_controller(db: Session = Depends(get_db)) -> AuthController:
    return AuthController(db)