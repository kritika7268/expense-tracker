import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('expensely_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle errors & 401 redirect
api.interceptors.response.use(
  (response) => {
    // If backend wrapped in { success, data }, return response.data
    return response.data;
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      const errorMessage = data?.message || error.message || 'An unexpected error occurred';

      if (status === 401) {
        // Clear local storage and redirect if not already on auth page
        localStorage.removeItem('expensely_token');
        localStorage.removeItem('expensely_user');
        if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register')) {
          window.location.href = '/login?expired=1';
        }
      }
      
      return Promise.reject({
        status,
        message: errorMessage,
        data,
      });
    } else if (error.request) {
      return Promise.reject({
        status: 0,
        message: 'Cannot connect to server. Please ensure backend is running.',
      });
    } else {
      return Promise.reject({
        status: -1,
        message: error.message,
      });
    }
  }
);

export default api;
