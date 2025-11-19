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

  const login = async (email, password, role = 'user') => {
    try {
      // TODO: API 호출로 대체
      // const response = await authApi.login(email, password);

      // 임시 구현
      const mockUser = {
        id: '123',
        email,
        role, // 'user', 'committee', 'admin'
        name: 'Test User',
      };

      const mockToken = 'mock_jwt_token_' + Date.now();

      localStorage.setItem('pam_user', JSON.stringify(mockUser));
      localStorage.setItem('pam_token', mockToken);

      setUser(mockUser);
      setIsAuthenticated(true);

      return { success: true, user: mockUser };
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('pam_user');
    localStorage.removeItem('pam_token');
    setUser(null);
    setIsAuthenticated(false);
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
