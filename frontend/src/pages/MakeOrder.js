import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api from "../api/axios.js";
import "./css/MakeOrder.css";

const MakeOrder = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const bookId = queryParams.get("book_id");
  const [orderType, setOrderType] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!bookId || !orderType) {
      setError("Book ID and order type are required.");
      return;
    }
    try {
      await api.post("/orders", {
        book_id: bookId,
        order_type: orderType,
      });
      navigate("/my_orders");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to submit order.");
    }
  };

  return (
    <div className="make-order-container">
      <div className="header">
        <h1>Place an Order</h1>
        <Link to="/home" className="home-button">
          Home
        </Link>
      </div>
      <div className="form-container">
        <form id="orderForm" onSubmit={handleSubmit}>
          <input type="hidden" name="book_id" value={bookId} />
          {error ? (
            <div id="error-message" className="error-message">
              {error}
            </div>
          ) : (
            <div
              id="error-message"
              className="error-message"
              style={{ display: "none" }}
            ></div>
          )}
          <label htmlFor="order_type">Order Type:</label>
          <select
            id="order_type"
            name="order_type"
            value={orderType}
            onChange={(e) => setOrderType(e.target.value)}
            required
          >
            <option value="">Select...</option>
            <option value="borrow">Borrow</option>
            <option value="read_in_library">Read in Library</option>
          </select>
          <div className="info-message" id="borrow-info">
            If you borrow a book, you can keep it for up to <strong>7 days</strong>.
            Please return it by the due date.
          </div>
          <button type="submit">Submit Order</button>
        </form>
      </div>
    </div>
  );
};

export default MakeOrder;