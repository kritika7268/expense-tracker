import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('expensely_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('expensely_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyToken = async () => {
      const storedToken = localStorage.getItem('expensely_token');
      if (storedToken) {
        try {
          const res = await api.get('/auth/me');
          if (res?.data) {
            setUser(res.data);
            localStorage.setItem('expensely_user', JSON.stringify(res.data));
          }
        } catch (err) {
          console.error('Session verification failed:', err);
          logout();
        }
      }
      setLoading(false);
    };

    verifyToken();
  }, []);

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    if (res?.data) {
      const { access_token, user: userData } = res.data;
      localStorage.setItem('expensely_token', access_token);
      localStorage.setItem('expensely_user', JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      return userData;
    }
  };

  const register = async (name, email, password, confirm_password, currency = 'INR') => {
    const res = await api.post('/auth/register', {
      name,
      email,
      password,
      confirm_password,
      currency,
    });
    if (res?.data) {
      const { access_token, user: userData } = res.data;
      localStorage.setItem('expensely_token', access_token);
      localStorage.setItem('expensely_user', JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      return userData;
    }
  };

  const logout = () => {
    localStorage.removeItem('expensely_token');
    localStorage.removeItem('expensely_user');
    setToken(null);
    setUser(null);
  };

  const updateUser = (updatedData) => {
    setUser((prev) => {
      const merged = { ...prev, ...updatedData };
      localStorage.setItem('expensely_user', JSON.stringify(merged));
      return merged;
    });
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!token,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
