import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import PublicRoute from './pages/PublicRoute.js';
import ProtectedRoute from './pages/ProtectedRoute.js'; 
import Home from './pages/Home';
import Books from './pages/Books.js';
import AddBook from './pages/AddBook.js';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Missing from './pages/Missing';
import BookPage from './pages/BookPage.js';
import MyOrders from './pages/MyOrders.js';
import Orders from './pages/Orders.js';
import MakeOrder from './pages/MakeOrder.js';


function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Home />} />
          <Route
            path="/books"
            element={
              <ProtectedRoute>
                <Books />
              </ProtectedRoute>   
            }
          />
          <Route
            path="/books/:id"
            element={
              <ProtectedRoute>
                <BookPage />
              </ProtectedRoute>   
            }
          />
          <Route
            path="/books/add"
            element={
              <ProtectedRoute requiredRole="librarian">
                <AddBook />
              </ProtectedRoute>
            }
          />
          <Route
            path='/my_orders'
            element={
              <ProtectedRoute requiredRole="reader">
                <MyOrders />
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders"
            element={
              <ProtectedRoute requiredRole="librarian">
                <Orders />
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders/make_order"
            element={
              <ProtectedRoute requiredRole="reader">
                <MakeOrder />
              </ProtectedRoute>
            }
          />
          <Route
            path='/login' 
            element={<PublicRoute><Login /></PublicRoute>} 
           />
          <Route 
            path='/signup' 
            element={<PublicRoute><Signup /></PublicRoute>} 
          />
          <Route path="*" element={<Missing />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;