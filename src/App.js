import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import PublicRoute from './pages/PublicRoute.js';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Missing from './pages/Missing';


function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Home />} />
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