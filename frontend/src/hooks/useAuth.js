/**
 * useAuth Hook
 * 인증 상태 관리 훅
 */

import { useState, useEffect, createContext, useContext } from 'react';

// Auth Context 생성
const AuthContext = createContext(null);

// Auth Provider Component
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // 로컬 스토리지에서 사용자 정보 로드
    const loadUser = () => {
      try {
        const savedUser = localStorage.getItem('pam_user');
        const savedToken = localStorage.getItem('pam_token');

        if (savedUser && savedToken) {
          const userData = JSON.parse(savedUser);
          setUser(userData);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Failed to load user:', error);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = async (email, password) => {
    try {
      // 실제 API 호출
      const authService = require('../services/auth/authService').default;
      const response = await authService.login(email, password);

      setUser(response.user);
      setIsAuthenticated(true);

      return { success: true, user: response.user };
    } catch (error) {
      console.error('Login failed:', error);
      return {
        success: false,
        error: error.error || error.message || 'Login failed'
      };
    }
  };

  const logout = async () => {
    try {
      const authService = require('../services/auth/authService').default;
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const updateUser = (updates) => {
    const updatedUser = { ...user, ...updates };
    localStorage.setItem('pam_user', JSON.stringify(updatedUser));
    setUser(updatedUser);
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// useAuth Hook
export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
}

export default useAuth;
