import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios.js";
import "./css/Books.css";

const Books = () => {
  const [books, setBooks] = useState([]);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [error, setError] = useState("");
  const limit = 9;

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const res = await api.get(`/books?limit=${limit}&offset=${(page - 1) * limit}`);
        setBooks(res.data.books);
        setHasNext(res.data.has_next);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load books.");
      }
    };
    fetchBooks();
  }, [page]);

  return (
    <div className="catalog-container">
      <div className="header">
        <h1>Library Catalog</h1>
        <Link to="/home" className="home-button">Home</Link>
      </div>
      {error && <div className="error-message">{error}</div>}
      <div className="catalog">
        {books.map((entry) => (
          <div key={entry.book_id} className="book-card">
            <h2>{entry.title}</h2>
            <p><strong>Author:</strong> {entry.author}</p>
            <p className="description">{entry.description ? entry.description.slice(0, 150) + "..." : "No description."}</p>
            <Link 
                to={`/books/${entry.book_id}`} 
                className="details-button"
            >
            View Details
            </Link>
          </div>
        ))}
      </div>
      <div className="pagination">
        {page > 1 && <button onClick={() => setPage(page - 1)}>« Prev</button>}
        <span>Page {page}</span>
        {hasNext && <button onClick={() => setPage(page + 1)}>Next »</button>}
      </div>
    </div>
  );
};

export default Books;
