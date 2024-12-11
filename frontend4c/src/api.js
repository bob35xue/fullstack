import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Replace with your backend URL

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// User-related API calls
export const loginUser = async (email, password) => {
  try {
    const response = await api.post('/users/login', { email, password });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createUser = async (userData) => {
  try {
    const response = await api.post('/users/', userData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getUsers = async () => {
  try {
    const response = await api.get('/users/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Issue-related API calls
export const createIssue = async (query, userId) => {
  try {
    const response = await api.post('/issues/', { query }, {
      headers: {
        'x-user-id': userId,
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getIssuesByUser = async (userId) => {
  try {
    const response = await api.get(`/issues/user/${userId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};