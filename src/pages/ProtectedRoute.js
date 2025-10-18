import { Navigate } from 'react-router-dom';
import { useAuth } from '../AuthContext.js';

const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/home" replace />;
  }

  return children;
};

export default ProtectedRoute;