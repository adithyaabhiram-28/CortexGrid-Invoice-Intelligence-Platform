import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('cortexgrid_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('cortexgrid_token');
    if (token) {
      authApi.getMe()
        .then((res) => {
          setUser(res.data.user);
          localStorage.setItem('cortexgrid_user', JSON.stringify(res.data.user));
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const response = await authApi.login({ email, password });
    const { token, user: userData } = response.data;
    localStorage.setItem('cortexgrid_token', token);
    localStorage.setItem('cortexgrid_user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  };

  const register = async (name, email, password, role) => {
    const response = await authApi.register({ name, email, password, role });
    const { token, user: userData } = response.data;
    localStorage.setItem('cortexgrid_token', token);
    localStorage.setItem('cortexgrid_user', JSON.stringify(userData));
    setUser(userData);
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('cortexgrid_token');
    localStorage.removeItem('cortexgrid_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
