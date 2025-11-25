/**
 * 보호된 라우트 컴포넌트
 * 인증 및 권한 확인
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  // 로딩 중
  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  // 인증되지 않음
  if (!isAuthenticated) {
    // 로그인 페이지로 리다이렉트 (원래 경로 저장)
    const loginPath = requiredRole === 'admin'
      ? '/admin/login'
      : requiredRole === 'committee'
      ? '/committee/login'
      : '/login';

    return <Navigate to={loginPath} state={{ from: location }} replace />;
  }

  // 권한 확인 (대소문자 무시)
  if (requiredRole && user.role.toUpperCase() !== requiredRole.toUpperCase()) {
    // 관리자가 아니면서 admin 페이지 접근 시도
    if (requiredRole.toLowerCase() === 'admin') {
      return (
        <div className="access-denied">
          <h1>403 - Access Denied</h1>
          <p>You don't have permission to access this page.</p>
          <a href="/">Go to Home</a>
        </div>
      );
    }

    // 위원회 위원이 아니면서 committee 페이지 접근 시도
    if (requiredRole.toLowerCase() === 'committee') {
      return (
        <div className="access-denied">
          <h1>403 - Access Denied</h1>
          <p>This page is only accessible to committee members.</p>
          <a href="/">Go to Home</a>
        </div>
      );
    }
  }

  // 권한 있음 - 자식 컴포넌트 렌더링
  return children;
}

export default ProtectedRoute;
