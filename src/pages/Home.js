import { Link } from "react-router-dom"
import "./css/Home.css"
import { useState } from "react";
import { useAuth } from "../AuthContext.js";
import Footer from "../components/Footer.js";

const Home = () => {
    const { user, logout } = useAuth();
    const [ logoutClicked, setLogoutClicked ] = useState(false);

    const handleLogout = async () => {
        await logout();
        setLogoutClicked(false);
    }

    return(
        <div className="home-container">
            <header>
                    <h1>Library Management System</h1>
            </header>
            <main>
            { !user? (
                <section className="auth-section">
                    <p>Please login or sign up to continue.</p>
                    <div className="nav-buttons">
                        <Link className="btn" to="/login" style={{fontSize: "16px"}}>
                        Login
                        </Link>
                        <Link className="btn" to="/signup" style={{fontSize: "16px"}}>
                        Sign Up
                        </Link>
                    </div>
                </section>
            ) : user.role === "librarian" ? (
                <section className="welcome-container">
                    <h2>Welcome, {user.username}!</h2>
                    <div className="nav-buttons">
                        <Link to="/books" className="btn">
                        Book Catalog
                        </Link>
                        <Link to="/books/add" className="btn">
                        Add Book
                        </Link>
                        <Link to="/orders" className="btn">
                        Orders
                        </Link>
                        <button className="btn logout" onClick={() => setLogoutClicked(true)}>Logout</button>
                    </div>
                </section>
            ) : (
                <section className="welcome-container">
                    <h2>Welcome, {user.username}!</h2>
                    <div className="nav-buttons">
                        <Link to="/books" className="btn">Book Catalog
                        </Link>
                        <Link to="/my_orders" className="btn">My Orders
                        </Link>
                        <button className="btn logout" onClick={() => setLogoutClicked(true)}>Logout</button>
                    </div>
                </section>
            )
            }
            </main>
            { logoutClicked && (
                <div id="logout-popup" class="popup">
                    <div class="popup-content">
                        <p>Are you sure you want to log out?</p>
                        <div class="popup-actions">
                            <button onClick={handleLogout}>Yes</button>
                            <button onClick={() => setLogoutClicked(false)}>No</button>
                        </div>
                    </div>
                </div>
            )}
            <Footer />
        </div>
    );
}

export default Home;