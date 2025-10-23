import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext.js";
import api from "../api/axios.js";
import "./css/Orders.css";

const MyOrders = () => {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [error, setError] = useState("");
  const limit = 10;

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const res = await api.get(`/orders/my_orders?limit=${limit}&offset=${(page - 1) * limit}`);
        setOrders(res.data.orders);
        setHasNext(res.data.has_next);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load orders.");
      }
    };
    if (user) fetchOrders();
  }, [page, user]);

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
        <Link to="/home" className="home-button">
          Home
        </Link>
      </div>
      {error && <div className="error-message">{error}</div>}
      <h1>My Active Orders</h1>
      {orders.length > 0 ? (
        <>
          <table>
            <thead>
              <tr>
                <th>Book Title</th>
                <th>Order Type</th>
                <th>Order Date</th>
                <th>Due Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((entry) => (
                <tr key={entry.order_id}>
                  <td>{entry.book_title}</td>
                  <td>{entry.order_type}</td>
                  <td>{formatDate(entry.order_date)}</td>
                  <td>{formatDate(entry.due_date)}</td>
                  <td>{entry.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="pagination">
            {page > 1 && (
              <button onClick={() => setPage(page - 1)}>Previous</button>
            )}
            <span>Page {page}</span>
            {hasNext && (
              <button onClick={() => setPage(page + 1)}>Next</button>
            )}
          </div>
        </>
      ) : (
        <p>No active orders found.</p>
      )}
    </div>
  );
};

export default MyOrders;