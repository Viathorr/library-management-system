import pytest
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.crud.order import OrderCRUD
from app.models.order import Order as OrderModel
from app.schemas.order import OrderBase
from app.exceptions.crud_exception import CRUDException
from unittest.mock import Mock
from datetime import datetime

# Fixture for mock database session
@pytest.fixture
def db_session():
    return Mock(spec=Session)

# Fixture for sample order data
@pytest.fixture
def order_data():
    return OrderBase(
        user_id=uuid4(),
        copy_id=uuid4(),
        order_type="borrow",
        order_date=datetime(2025, 5, 29),
        due_date=datetime(2025, 6, 5),
        return_date=None,
        status="active"
    )

# Fixture for sample Order model instance
@pytest.fixture
def order_instance():
    return OrderModel(
        order_id=uuid4(),
        user_id=uuid4(),
        copy_id=uuid4(),
        order_type="borrow",
        order_date=datetime(2025, 5, 29),
        due_date=datetime(2025, 6, 5),
        return_date=None,
        status="active"
    )

def test_create_order_success(db_session, order_data, order_instance):
    db_session.add = Mock()
    db_session.commit = Mock()
    db_session.refresh = Mock(return_value=order_instance)
    order_crud = OrderCRUD(db_session)
    
    result = order_crud.create_order(order_data)
    
    assert isinstance(result, OrderModel)
    assert result.order_type == order_data.order_type
    assert result.user_id == order_data.user_id
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()

def test_create_order_error(db_session, order_data):
    db_session.add = Mock()
    db_session.commit = Mock(side_effect=Exception("Database error"))
    db_session.rollback = Mock()
    order_crud = OrderCRUD(db_session)
    
    with pytest.raises(CRUDException) as exc:
        order_crud.create_order(order_data)
    assert exc.value.status_code == 500
    assert exc.value.message == "Internal server error"
    db_session.rollback.assert_called_once()

def test_get_all_active_orders_success(db_session):
    order_id = uuid4()
    copy_id = uuid4()
    mock_orders = [
        Mock(
            order_id=order_id,
            username="test_user",   
            copy_id=copy_id,
            order_type="borrow",
            order_date=datetime(2025, 5, 29),
            due_date=datetime(2025, 6, 5),
            return_date=None,
            status="active",
            book_title="Test Book",
        )
    ]

    query_mock = Mock()
    query_mock.outerjoin.return_value \
        .outerjoin.return_value \
        .outerjoin.return_value \
        .filter.return_value.order_by.return_value \
        .limit.return_value.offset.return_value.all.return_value = mock_orders

    query_mock.outerjoin.return_value \
        .outerjoin.return_value \
        .outerjoin.return_value \
        .filter.return_value.order_by.return_value \
        .limit.return_value.offset.return_value.first.return_value = None

    db_session.query.return_value = query_mock

    order_crud = OrderCRUD(db_session)

    result = order_crud.get_all_active_orders(limit=10, offset=0)

    assert isinstance(result, dict)
    assert "orders" in result
    assert len(result["orders"]) == 1
    assert result["orders"][0]["username"] == "test_user"  
    assert result["orders"][0]["book_title"] == "Test Book"
    assert result["page"] == 1
    assert result["has_next"] in [True, False]


def test_get_all_active_orders_empty(db_session):
    # Mock SQLAlchemy chained query
    query_mock = Mock()

    # Mock the main query returning an empty list
    query_mock.outerjoin.return_value \
        .outerjoin.return_value \
        .outerjoin.return_value \
        .filter.return_value.order_by.return_value \
        .limit.return_value.offset.return_value.all.return_value = []

    # Mock .first() for checking next page (should also be None)
    query_mock.outerjoin.return_value \
        .outerjoin.return_value \
        .outerjoin.return_value \
        .filter.return_value.order_by.return_value \
        .limit.return_value.offset.return_value.first.return_value = None

    db_session.query.return_value = query_mock

    order_crud = OrderCRUD(db_session)

    result = order_crud.get_all_active_orders(limit=10, offset=0)

    assert result["orders"] == []
    assert result["page"] == 1
    assert result["has_next"] is False


def test_get_all_active_orders_error(db_session):
    db_session.query.side_effect = Exception("Database error")
    order_crud = OrderCRUD(db_session)
    
    with pytest.raises(CRUDException) as exc:
        order_crud.get_all_active_orders(limit=10, offset=0)
    assert exc.value.status_code == 500
    assert exc.value.message == "Internal server error"

def test_get_orders_by_user_success(db_session):
    username = "test_user"
    order_id = uuid4()
    copy_id = uuid4()

    mock_orders = [
        Mock(
            order_id=order_id,
            username=username,          
            copy_id=copy_id,
            order_type="borrow",
            order_date=datetime(2025, 5, 29),
            due_date=datetime(2025, 6, 5),
            return_date=None,
            status="active",
            book_title="Test Book",
        )
    ]

    query_mock = Mock()
    query_mock.outerjoin.return_value \
        .outerjoin.return_value \
        .outerjoin.return_value \
        .filter.return_value.order_by.return_value \
        .limit.return_value.offset.return_value.all.return_value = mock_orders

    db_session.query.return_value = query_mock
    order_crud = OrderCRUD(db_session)

    result = order_crud.get_orders_by_user(username=username, limit=10, offset=0)

    assert "orders" in result
    assert len(result["orders"]) == 1
    assert result["orders"][0]["book_title"] == "Test Book"
    assert result["orders"][0]["username"] == username     


def test_get_orders_by_user_empty(db_session):
    username = "test_user"

    query_mock = Mock()

    query_mock.outerjoin.return_value \
        .outerjoin.return_value \
        .outerjoin.return_value \
        .filter.return_value.order_by.return_value \
        .limit.return_value.offset.return_value.all.return_value = []

    db_session.query.return_value = query_mock
    order_crud = OrderCRUD(db_session)

    result = order_crud.get_orders_by_user(username=username, limit=10, offset=0)

    assert result["orders"] == []
    assert result["page"] == 1
    assert result["has_next"] is False


def test_get_orders_by_user_error(db_session):
    username = "test_user"
    db_session.query.side_effect = Exception("Database error")
    order_crud = OrderCRUD(db_session)
    
    with pytest.raises(CRUDException) as exc:
        order_crud.get_orders_by_user(username=username, limit=10, offset=0)

    assert exc.value.status_code == 500
    assert exc.value.message == "Internal server error"

def test_update_order_status_success(db_session, order_instance):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = order_instance
    db_session.commit = Mock()
    db_session.refresh = Mock()
    order_crud = OrderCRUD(db_session)
    
    # Act
    result = order_crud.update_order_status(order_instance.order_id, "completed")
    
    # Assert
    assert isinstance(result, OrderModel)
    assert result.status == "completed"
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()

def test_update_order_status_not_found(db_session):
    # Arrange
    order_id = uuid4()
    db_session.query.return_value.filter.return_value.first.return_value = None
    order_crud = OrderCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        order_crud.update_order_status(order_id, "completed")
    assert exc.value.status_code == 404
    assert exc.value.message == "Order not found"

def test_update_order_status_integrity_error(db_session, order_instance):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = order_instance
    db_session.commit = Mock(side_effect=IntegrityError("constraint violation", {}, None))
    db_session.rollback = Mock()
    order_crud = OrderCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        order_crud.update_order_status(order_instance.order_id, "invalid_status")
    assert exc.value.status_code == 400
    assert exc.value.message == "Invalid status update"
    db_session.rollback.assert_called_once()

def test_update_order_status_unexpected_error(db_session, order_instance):
    # Arrange
    db_session.query.return_value.filter.return_value.first.return_value = order_instance
    db_session.commit = Mock(side_effect=Exception("Unexpected error"))
    db_session.rollback = Mock()
    order_crud = OrderCRUD(db_session)
    
    # Act & Assert
    with pytest.raises(CRUDException) as exc:
        order_crud.update_order_status(order_instance.order_id, "completed")
    assert exc.value.status_code == 500
    assert exc.value.message == "Internal server error"
    db_session.rollback.assert_called_once()