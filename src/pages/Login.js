import "./css/Login.css"
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.js";
import Footer from "../components/Footer.js";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { login, loading } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username || !password) {
            setError('Username and password are required.');
            return;
        }
        if (password.length < 8) {
            setError('Password must be at least 8 characters long.');
            return;
        }
        if (username.length < 3) {
            setError('Username must be at least 3 characters long.');
            return;
        }
        try {
            await login(username, password);
            navigate('/home');
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed.');
        }
    };

    return (
        <div className="login-container">
            <header>
                <h1>Library Management System</h1>
            </header>
            <main>
                <section className="form-container">
                    <h2>Log In</h2>
                    {error && <p className="error-message">{error}</p>}
                    <form onSubmit={handleSubmit}>
                        <label htmlFor="username">Username: <span className="required">*</span></label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                        <label htmlFor="password">Password: <span className="required">*</span></label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <button type="submit" disabled={loading}>{loading ? 'Logging In...' : 'Log In'}</button>
                    </form>
                    <p className="signup-link">Need an account? <Link to="/signup">Sign Up</Link></p>
                </section>
            </main>
            <Footer />
        </div>
    );
}

export default Login;