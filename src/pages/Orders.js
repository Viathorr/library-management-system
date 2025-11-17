import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios.js";
import "./css/Orders.css";

const ActiveOrders = () => {
  const [orders, setOrders] = useState([]);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState(""); // ← NEW
  const limit = 10;

  const fetchOrders = async () => {
    try {
      let res;

      if (search.trim() !== "") {
        res = await api.get(
          `/orders/${search}?limit=${limit}&offset=${(page - 1) * limit}`
        );
      } else {
        res = await api.get(
          `/orders?limit=${limit}&offset=${(page - 1) * limit}`
        );
      }

      setOrders(res.data.orders);
      setHasNext(res.data.has_next);
      setError("");
    } catch (err) {
      setOrders([]);
      setHasNext(false);
      setError(err.response?.data?.detail || "Failed to load orders.");
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [page, search]); 

  const handleComplete = async (orderId) => {
    try {
      await api.put(`/orders/${orderId}?status=completed`);
      setOrders(orders.filter((order) => order.order_id !== orderId));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to complete order.");
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "—";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="orders-container">
      <div className="top-bar">
        <Link to="/home" className="home-button">Home</Link>
      </div>

      {error && <div className="error-message">{error}</div>}

      <h1>Active Orders</h1>
      
      <div className="search-wrapper">
        <input
          type="text"
          className="search-bar"
          placeholder="Search by username..."
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
        />
      </div>
      {orders.length > 0 ? (
        <>
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Username</th>
                <th>Book Title</th>
                <th>Order Type</th>
                <th>Order Date</th>
                <th>Due Date</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((entry) => (
                <tr key={entry.order_id}>
                  <td>{entry.order_id}</td>
                  <td>{entry.username}</td>
                  <td>{entry.book_title}</td>
                  <td>{entry.order_type}</td>
                  <td>{formatDate(entry.order_date)}</td>
                  <td>{formatDate(entry.due_date)}</td>
                  <td>{entry.status}</td>
                  <td>
                    {entry.status !== "completed" ? (
                      <button
                        className="btn-complete"
                        onClick={() => handleComplete(entry.order_id)}
                      >
                        Set Completed
                      </button>
                    ) : (
                      "Completed"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="pagination">
            {page > 1 && (
              <button onClick={() => setPage(page - 1)}>« Previous</button>
            )}
            <span>Page {page}</span>
            {hasNext && (
              <button onClick={() => setPage(page + 1)}>Next »</button>
            )}
          </div>
        </>
      ) : (
        <p>No active orders found.</p>
      )}
    </div>
  );
};

export default ActiveOrders;