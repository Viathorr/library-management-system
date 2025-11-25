import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios.js";
import "./css/Books.css"; // reuse your styles

const PopularBooks = () => {
  const [books, setBooks] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchMostBorrowedBooks = async () => {
      try {
        const res = await api.get("/books/most-borrowed");
        setBooks(res.data);
        setError("");
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load popular books.");
      }
    };

    fetchMostBorrowedBooks();
  }, []);

  return (
    <div className="catalog-container">
      <div className="header">
        <h1>Most Borrowed Books (Last 30 Days)</h1>
        <Link to="/home" className="home-button">Home</Link>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="catalog">
        {books.length > 0 ? (
          books.map((book, index) => (
            <div
              key={book.book_id}
              className={`book-card popular ${
                index === 0
                  ? "gold"
                  : index === 1
                  ? "silver"
                  : index === 2
                  ? "bronze"
                  : ""
              }`}
            >
              <div
                className={`popular-rank ${
                  index === 0
                    ? "gold"
                    : index === 1
                    ? "silver"
                    : index === 2
                    ? "bronze"
                    : ""
                }`}
              >
                {index === 0
                  ? "🥇"
                  : index === 1
                  ? "🥈"
                  : index === 2
                  ? "🥉"
                  : `#${index + 1}`}
              </div>
              <h2>{book.title}</h2>
              <p><strong>Author:</strong> {book.author}</p>
              <p><strong>Orders Last Month:</strong> {book.recent_orders}</p>
              <Link
                to={`/books/${book.book_id}`}
                className="details-button"
              >
                View Details
              </Link>
            </div>
          ))
        ) : (
          <p className="no-books">No popular books found this month.</p>
        )}
      </div>
    </div>
  );
};

export default PopularBooks;
