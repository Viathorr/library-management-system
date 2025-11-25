from fastapi import APIRouter, Depends
from app.schemas.user import UserBase
from app.controllers.authentication.auth_controller import AuthController, get_auth_controller
from app.utils.security import get_current_user
from app.config.logger import logger


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup")
def signup(user: UserBase, auth_controller: AuthController = Depends(get_auth_controller)):
    """
    Create a new user.
    """
    logger.info(f"Signup request for user: {user.username}")
    return auth_controller.signup(user)    


@router.post("/login")
def login(data: dict, auth_controller: AuthController = Depends(get_auth_controller)):
    """
    Login a user and return user details.
    """
    logger.info(f"Login request for user: {data.get('username')}")
    return auth_controller.login(data.get("username"), data.get("password_hash"))


@router.post("/logout", dependencies=[Depends(get_current_user)])
def logout(auth_controller: AuthController = Depends(get_auth_controller)):
    """
    Logout a user.
    """
    logger.info("Logout request")
    return auth_controller.logout()