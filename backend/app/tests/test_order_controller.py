import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.controllers.orders.order_controller import OrderController
from app.schemas.order import OrderBase
from app.crud.order import OrderCRUD
from app.crud.book_copy import BookCopyCRUD
from app.exceptions.crud_exception import CRUDException
from app.models.order import Order as OrderModel
from app.models.book_copy import BookCopy
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from freezegun import freeze_time

# Fixture for mock database session
@pytest.fixture
def db_session():
    return Mock(spec=Session)

# Fixture for sample order data
@pytest.fixture
def order_data():
    return {
        "book_id": uuid4(),
        "order_type": "borrow"
    }

# Fixture for sample BookCopy instance
@pytest.fixture
def book_copy_instance(order_data):  # Depend on order_data to use its book_id
    return BookCopy(
        copy_id=uuid4(),
        book_id=order_data["book_id"],  # Ensure book_id matches order_data
        status="available",
        added_at=datetime(2025, 5, 29, tzinfo=timezone.utc)
    )

# Fixture for sample Order model instance
@pytest.fixture
def order_instance(book_copy_instance):  # Depend on book_copy_instance for copy_id
    return OrderModel(
        order_id=uuid4(),
        user_id=uuid4(),
        copy_id=book_copy_instance.copy_id,  # Use same copy_id as book_copy_instance
        order_type="borrow",
        order_date=datetime(2025, 5, 29, tzinfo=timezone.utc),
        due_date=datetime(2025, 6, 5, tzinfo=timezone.utc),
        return_date=None,
        status="active"
    )

# Fixture for mocked OrderCRUD
@pytest.fixture
def mock_order_crud(order_instance):
    mock_crud = Mock(spec=OrderCRUD)
    mock_crud.create_order = Mock(return_value=order_instance)
    mock_crud.get_all_active_orders = Mock(return_value=[
        (
            order_instance.order_id,
            order_instance.user_id,
            order_instance.copy_id,
            order_instance.order_type,
            order_instance.order_date,
            order_instance.due_date,
            order_instance.return_date,
            order_instance.status,
            "Test Book"
        )
    ])
    mock_crud.get_orders_by_user = Mock(return_value=[
        (
            order_instance.order_id,
            order_instance.user_id,
            order_instance.copy_id,
            order_instance.order_type,
            order_instance.order_date,
            order_instance.due_date,
            order_instance.return_date,
            order_instance.status,
            "Test Book"
        )
    ])
    mock_crud.update_order_status = Mock(return_value=order_instance)
    return mock_crud

# Fixture for mocked BookCopyCRUD
@pytest.fixture
def mock_book_copy_crud(book_copy_instance):
    mock_crud = Mock(spec=BookCopyCRUD)
    mock_crud.get_available_copies = Mock(return_value=[book_copy_instance])
    mock_crud.update_book_copy_status = Mock()
    return mock_crud

def test_create_order_success_borrow(db_session, order_data, order_instance, mock_order_crud, mock_book_copy_crud):
    # Arrange
    user_id = uuid4()
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Freeze time for consistent datetime
    with freeze_time("2025-05-29 12:00:00", tz_offset=0):
        # Act
        result = order_controller.create_order(user_id, order_data)

    # Assert
    assert result == order_instance
    mock_book_copy_crud.get_available_copies.assert_called_once_with(order_data["book_id"])
    mock_book_copy_crud.update_book_copy_status.assert_called_once_with(
        order_instance.copy_id, "borrowed"
    )
    mock_order_crud.create_order.assert_called_once()
    called_order = mock_order_crud.create_order.call_args[0][0]
    assert isinstance(called_order, OrderBase)
    assert called_order.user_id == user_id
    assert called_order.copy_id == order_instance.copy_id
    assert called_order.order_type == "borrow"
    assert called_order.due_date == datetime(2025, 6, 5, 12, 0, tzinfo=timezone.utc)

def test_create_order_no_available_copies(db_session, order_data, mock_order_crud, mock_book_copy_crud):
    # Arrange
    user_id = uuid4()
    mock_book_copy_crud.get_available_copies = Mock(return_value=[])
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        order_controller.create_order(user_id, order_data)
    assert exc.value.status_code == 404
    assert exc.value.detail == "No available copies for this book"
    mock_book_copy_crud.get_available_copies.assert_called_once()
    mock_book_copy_crud.update_book_copy_status.assert_not_called()
    mock_order_crud.create_order.assert_not_called()

def test_create_order_crud_exception(db_session, order_data, mock_order_crud, mock_book_copy_crud):
    # Arrange
    user_id = uuid4()
    mock_order_crud.create_order = Mock(side_effect=CRUDException(
        message="Order creation failed", status_code=400
    ))
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        order_controller.create_order(user_id, order_data)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Order creation failed"
    mock_book_copy_crud.update_book_copy_status.assert_called_once()
    mock_order_crud.create_order.assert_called_once()

def test_create_order_unexpected_error(db_session, order_data, mock_order_crud, mock_book_copy_crud):
    # Arrange
    user_id = uuid4()
    mock_order_crud.create_order = Mock(side_effect=Exception("Unexpected error"))
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        order_controller.create_order(user_id, order_data)
    assert exc.value.status_code == 500
    assert exc.value.detail == "Internal server error"
    mock_book_copy_crud.update_book_copy_status.assert_called_once()
    mock_order_crud.create_order.assert_called_once()

def test_get_all_orders_success(db_session, mock_order_crud, mock_book_copy_crud):
    # Arrange
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act
    result = order_controller.get_all_orders(limit=10, offset=0)

    # Assert
    assert len(result) == 1
    assert result[0][-1] == "Test Book"
    mock_order_crud.get_all_active_orders.assert_called_once_with(10, 0)

def test_get_all_orders_empty(db_session, mock_order_crud, mock_book_copy_crud):
    # Arrange
    mock_order_crud.get_all_active_orders = Mock(return_value=[])
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act
    result = order_controller.get_all_orders(limit=10, offset=0)

    # Assert
    assert result == []
    mock_order_crud.get_all_active_orders.assert_called_once_with(10, 0)

def test_get_all_orders_error(db_session, mock_order_crud, mock_book_copy_crud):
    # Arrange
    mock_order_crud.get_all_active_orders = Mock(side_effect=CRUDException(
        message="Internal server error", status_code=500
    ))
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        order_controller.get_all_orders(limit=10, offset=0)
    assert exc.value.status_code == 500
    assert exc.value.detail == "Internal server error"

def test_get_orders_by_user_success(db_session, mock_order_crud, mock_book_copy_crud):
    # Arrange
    user_id = uuid4()
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act
    result = order_controller.get_orders_by_user(user_id, limit=10, offset=0)

    # Assert
    assert len(result) == 1
    mock_order_crud.get_orders_by_user.assert_called_once_with(user_id, 10, 0)

def test_get_orders_by_user_empty(db_session, mock_order_crud, mock_book_copy_crud):
    # Arrange
    user_id = uuid4()
    mock_order_crud.get_orders_by_user = Mock(return_value=[])
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act
    result = order_controller.get_orders_by_user(user_id, limit=10, offset=0)

    # Assert
    assert result == []
    mock_order_crud.get_orders_by_user.assert_called_once_with(user_id, 10, 0)

def test_get_orders_by_user_error(db_session, mock_order_crud, mock_book_copy_crud):
    # Arrange
    user_id = uuid4()
    mock_order_crud.get_orders_by_user = Mock(side_effect=CRUDException(
        message="Internal server error", status_code=500
    ))
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        order_controller.get_orders_by_user(user_id, limit=10, offset=0)
    assert exc.value.status_code == 500
    assert exc.value.detail == "Internal server error"

def test_update_order_status_success(db_session, order_instance, mock_order_crud, mock_book_copy_crud):
    # Arrange
    order_id = str(uuid4())
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act
    result = order_controller.update_order_status(order_id, "completed")

    # Assert
    assert result == order_instance
    mock_order_crud.update_order_status.assert_called_once_with(order_id, "completed")

def test_update_order_status_error(db_session, mock_order_crud, mock_book_copy_crud):
    # Arrange
    order_id = str(uuid4())
    mock_order_crud.update_order_status = Mock(side_effect=CRUDException(
        message="Order not found", status_code=404
    ))
    order_controller = OrderController(db=db_session)
    order_controller.order_crud = mock_order_crud
    order_controller.book_copy_crud = mock_book_copy_crud

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        order_controller.update_order_status(order_id, "completed")
    assert exc.value.status_code == 404
    assert exc.value.detail == "Order not found"