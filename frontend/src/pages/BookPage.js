import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useAuth } from "../AuthContext.js";
import api from "../api/axios.js";
import "./css/BookPage.css";

const BookPage = () => {
  const { user } = useAuth();
  const { id } = useParams(); 
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchBook = async () => {
      try {
        const res = await api.get(`/books/${id}`);
        setBook(res.data);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load book details.");
      } finally {
        setLoading(false);
      }
    };
    fetchBook();
  }, [id]);

  if (loading) return <div className="loading">Loading book details...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!book) return <div>No book data available.</div>;

  return (
    <div className="bookpage-container">
      <div className="header">
        <h1>{book.title}</h1>
        <Link to="/books" className="back-button">Book Catalog</Link>
      </div>

      <div className="book-details">
        <p><strong>Author:</strong> {book.author}</p>
        <p><strong>ISBN:</strong> {book.isbn}</p>
        {book.publication_year && (
          <p><strong>Published:</strong> {book.publication_year}</p>
        )}
        {book.description && (
          <p className="description">
            <strong>Description:</strong> {book.description}
          </p>
        )}
        <p className="available">
          <strong>Available copies:</strong>{" "}
          {book.available_copies ?? "Unknown"}
        </p>

        {user?.role === "reader" && (
          book.available_copies > 0 ? (
            <Link
              to={`/orders/make_order?book_id=${book.book_id}`}
              className="order-button"
            >
              Order
            </Link>
          ) : (
            <button className="order-button disabled" disabled>
              Not Available
            </button>
          )
        )}
      </div>
    </div>
  );
};

export default BookPage;
