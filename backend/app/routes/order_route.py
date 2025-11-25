from fastapi import Depends, APIRouter
from app.schemas.order import Order
from app.controllers.orders.order_controller import OrderController, get_order_controller
from app.config.logger import logger
from app.utils.security import get_current_user, require_role


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", dependencies=[Depends(require_role("reader"))])
def create_order(
    order_data: dict,
    order_controller: OrderController = Depends(get_order_controller),
    current_user = Depends(get_current_user)
):
    logger.info(f"Creating order for user {current_user.username}")
    return order_controller.create_order(current_user.user_id, order_data)


@router.get("/my_orders", response_model=dict, dependencies=[Depends(require_role("reader"))])
def get_my_orders(
    limit: int = 10,
    offset: int = 0,
    order_controller: OrderController = Depends(get_order_controller),
    current_user = Depends(get_current_user)
):
    logger.info(f"Fetching orders for user {current_user.username}")
    return order_controller.get_orders_by_user(current_user.username, limit, offset)


@router.get("/{username}", response_model=dict, dependencies=[Depends(require_role("librarian"))])
def get_orders_by_user(
    username: str,
    limit: int = 10,
    offset: int = 0,
    order_controller: OrderController = Depends(get_order_controller)
):
    logger.info(f"Fetching orders for user {username}")
    return order_controller.get_orders_by_user(username, limit, offset)
 

@router.get("/", response_model=dict, dependencies=[Depends(require_role("librarian"))])
def get_all_orders(
    limit: int = 10,
    offset: int = 0,
    order_controller: OrderController = Depends(get_order_controller)
):
    logger.info("Fetching all orders")
    return order_controller.get_all_orders(limit, offset)


@router.put("/{order_id}", dependencies=[Depends(require_role("librarian"))])
def update_order_status(
    order_id: str,
    status: str,
    order_controller: OrderController = Depends(get_order_controller)
):
    logger.info(f"Updating status of order {order_id} to {status}")
    return order_controller.update_order_status(order_id, status)