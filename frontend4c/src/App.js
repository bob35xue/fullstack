import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ChatbotPage from './pages/ChatbotPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
// eslint-disable-next-line no-unused-vars
// import { API } from './config';

function App() {
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    // Check if a user is already logged in
    const user = JSON.parse(localStorage.getItem('user'));
    if (user) {
      setCurrentUser(user);
    }
  }, []);

  const handleLogin = (user) => {
    setCurrentUser(user);
    localStorage.setItem('user', JSON.stringify(user));
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
        <Route 
          path="/chatbot" 
          element={
            currentUser ? <ChatbotPage /> : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/adminDashboard"
          element={
            currentUser && currentUser.is_superuser ? 
              <AdminDashboardPage /> : 
              <Navigate to="/login" />
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;