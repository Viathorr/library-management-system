import "./css/Signup.css"
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext.js";
import Footer from "../components/Footer.js";

const Signup = () => {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [role, setRole] = useState("");
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { signup, loading } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username || !password || !confirmPassword || !role) {
            setError('Username, password, confirm password, and role are required.');
            return;
        }
        if (username.length < 3) {
            setError('Username must be at least 3 characters long.');
            return;
        }
        if (password.length < 8) {
            setError('Password must be at least 8 characters long.');
            return;
        }
        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
        try {
            await signup(username, email ? email : null, role, password);
            navigate('/home');
        } catch (err) {
            setError(err.response?.data.detail[0].msg || err.response?.data?.detail || 'Signup failed.');
        }
    };

    return (
        <div className="signup-container">
            <header>
                <h1>Library Management System</h1>
            </header>
            <main>
                <section className="form-container">
                    <h2>Create Your Account</h2>
                    {error && <p className="error-message">{error}</p>}
                    <form onSubmit={handleSubmit}>
                        <label htmlFor="username">Username: <span className="required">*</span></label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                        <label htmlFor="email">Email:</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                        <label htmlFor="password">Password: <span className="required">*</span></label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <label htmlFor="confirm_password">Confirm Password: <span className="required">*</span></label>
                        <input
                            type="password"
                            id="confirm_password"
                            name="confirm_password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                        <label htmlFor="role">Role: <span className="required">*</span></label>
                        <select
                            id="role"
                            name="role"
                            value={role}
                            onChange={(e) => setRole(e.target.value)}
                            required
                        >
                            <option value="" disabled>Select role</option>
                            <option value="reader">Reader</option>
                            <option value="librarian">Librarian</option>
                        </select>
                        <button type="submit" disabled={loading}>{loading ? 'Signing Up...' : 'Sign Up'}</button>
                    </form>
                    <p className="login-link">Already have an account? <Link to="/login">Log In</Link></p>
                </section>
            </main>
            <Footer />
        </div>
    );
}

export default Signup;