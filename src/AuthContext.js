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
    
  }

  const login = async (username, password) => {
    
  };

  const logout = async () => {
    
  };

  return (
    <AuthContext.Provider value={{ user, loading, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);