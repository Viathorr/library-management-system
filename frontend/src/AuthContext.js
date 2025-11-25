import { createContext, useContext, useState, useEffect } from 'react';
import api from './api/axios';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); 
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const decoded = jwtDecode(token); 
        setUser({ username: decoded.username, role: decoded.role });
      } catch (error) {
        localStorage.removeItem('access_token');
      }
    } 
    setLoading(false);
  }, []);

  const signup = async (username, email, role, password) => {
    const res = await api.post('/users/signup', { "username": username, "email": email, "role": role, "password_hash": password });
    localStorage.setItem('access_token', res.data.access_token);
    const decoded = jwtDecode(res.data.access_token);
    setUser({ username: decoded.username, role: decoded.role });
  }

  const login = async (username, password) => {
    const res = await api.post('/users/login', { "username": username, "password_hash": password });
    localStorage.setItem('access_token', res.data.access_token);
    const decoded = jwtDecode(res.data.access_token);
    setUser({ username: decoded.username, role: decoded.role });
  };

  const logout = async () => {
    await api.post('/users/logout');
    localStorage.removeItem('access_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);