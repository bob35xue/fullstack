import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log('Attempting login with:', { email, password });
      const response = await axios.post('http://localhost:8000/users/login', 
        { email, password },
        { 
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          withCredentials: true
        }
      );
      
      const user = response.data;
      console.log('Login successful, user data:', user);
      
      localStorage.setItem('user', JSON.stringify(user));
      
      if (onLogin) {
        console.log('Calling onLogin callback');
        onLogin(user);
      }

      if (!user.is_active) {
        console.log('User is not active, navigating to login');
        navigate('/login');
      } else if (user.is_superuser) {
        console.log('User is admin, navigating to admin dashboard');
        navigate('/adminDashboard');
      } else {
        console.log('User is regular user, navigating to chatbot');
        navigate('/chatbot');
      }
    } catch (error) {
      console.error('Login failed:', error);
      if (error.response) {
        console.error('Error response:', error.response.data);
      }
      if (error.response && error.response.data && error.response.data.detail) {
        setError(error.response.data.detail);
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      backgroundColor: '#f0f2f5'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        width: '300px'
      }}>
        <h1 style={{textAlign: 'center'}}>Login</h1>
        <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column'}}>
        <div> <label htmlFor="email">Email</label>
          <input
            type="email"
            id="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{
              margin: '10px 0',
              padding: '10px',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}
            required
          />
          </div>
          <div> <label htmlFor="password">Password</label>
          <input
            type="password"
            id="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              margin: '10px 0',
              padding: '10px',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}
            required
          />
          </div>
          {error && <p style={{color: 'red'}}>{error}</p>}
          <button 
            type="submit"
            style={{
              backgroundColor: '#4CAF50',
              color: 'white',
              padding: '10px',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '10px'
            }}
          >
            Log In
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;