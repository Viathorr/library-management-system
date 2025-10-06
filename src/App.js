import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import Home from './pages/Home';
import Login from './pages/Login';
import Missing from './pages/Missing';


function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/home" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Missing />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;