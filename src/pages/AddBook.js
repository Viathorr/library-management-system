import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios.js";
import "./css/AddBook.css";

const AddBook = () => {
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [isbn, setIsbn] = useState("");
  const [publicationYear, setPublicationYear] = useState(null);
  const [description, setDescription] = useState("");
  const [numCopies, setNumCopies] = useState(0);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !author || !isbn || !numCopies) {
      setError("Title, author, ISBN, and number of copies are required.");
      return;
    }
    try {
      await api.post("/books", {
        title,
        author,
        isbn,
        publication_year: publicationYear ? Number(publicationYear) : null,
        description,
        num_copies: Number(numCopies),
      });
      navigate("/home");
    } catch (err) {
      setError(err.response?.data.detail[0].msg || err.response?.data?.detail || "Failed to add book.");
    }
  };

  return (
    <div className="add-book-container">
        <div className="header">
            <h1>Add New Book</h1>
            <Link to="/home" className="home-button">
            Home
            </Link>
        </div>
        {error && <div className="error-message">{error}</div>}
        <form id="add-book-form" onSubmit={handleSubmit}>
            <label htmlFor="title">Title:</label>
            <input
                type="text"
                id="title"
                name="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
            />
            <label htmlFor="author">Author:</label>
            <input
                type="text"
                id="author"
                name="author"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                required
            />
            <label htmlFor="isbn">ISBN:</label>
            <input
                type="number"
                id="isbn"
                name="isbn"
                value={isbn}
                onChange={(e) => setIsbn(e.target.value)}
                required
            />
            <label htmlFor="publication_year">Publication Year:</label>
            <input
                type="number"
                id="publication_year"
                name="publication_year"
                value={publicationYear}
                onChange={(e) => setPublicationYear(e.target.value)}
                min="0"
                max="2100"
            />
            <label htmlFor="description">Description:</label>
            <textarea
                id="description"
                name="description"
                rows="4"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
            ></textarea>
            <label htmlFor="num_copies">Number of Copies:</label>
            <input
                type="number"
                id="num_copies"
                name="num_copies"
                value={numCopies}
                onChange={(e) => setNumCopies(e.target.value)}
                min="1"
                required
            />
            <button type="submit">Add Book</button>
        </form>
    </div>
  );
};

export default AddBook;