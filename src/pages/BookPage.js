import { useLocation, Link } from "react-router-dom";
import { useAuth } from "../AuthContext.js";
import "./css/BookPage.css";

const BookPage = () => {
  const { user } = useAuth();
  const location = useLocation();
  const book = location.state?.book; 

  if (!book) return <div>No book data available.</div>;

  return (
    <div className="bookpage-container">
      <div className="header">
        <h1>{book.title}</h1>
        <Link to="/books" className="back-button">Back to Catalog</Link>
      </div>
      <div className="book-details">
        <p><strong>Author:</strong> {book.author}</p>
        <p><strong>ISBN:</strong> {book.isbn}</p>
        {book.publication_year && <p><strong>Published:</strong> {book.publication_year}</p>}
        {book.description && <p className="description"><strong>Description:</strong> {book.description}</p>}
        <p className="available"><strong>Available copies:</strong> {book.available_copies}</p>

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
