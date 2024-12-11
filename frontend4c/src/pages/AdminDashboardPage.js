import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AdminDashboardPage = () => {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get('http://localhost:8000/users');
        setUsers(response.data);
      } catch (error) {
        console.error('Failed to fetch users:', error);
        setError('Failed to load users');
      }
    };

    fetchUsers();
  }, []);

  return (
    <div>
      <h1>Admin Dashboard</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div>
        <h2>Users List</h2>
        {users.map(user => (
          <div key={user.id}>
            <p>Name: {user.full_name}</p>
            <p>Email: {user.email}</p>
            <p>Status: {user.is_active ? 'Active' : 'Inactive'}</p>
            <hr />
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdminDashboardPage;