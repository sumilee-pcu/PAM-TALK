/**
 * PAM-TALK 메인 라우터
 * 3-Portal 시스템 라우팅
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import UserRoutes from './UserRoutes';
import CommitteeRoutes from './CommitteeRoutes';
import AdminRoutes from './AdminRoutes';

function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ========== User Portal (Public + Protected) ========== */}
        <Route path="/*" element={<UserRoutes />} />

        {/* ========== Committee Portal (Protected) ========== */}
        <Route
          path="/committee/*"
          element={
            <ProtectedRoute requiredRole="committee">
              <CommitteeRoutes />
            </ProtectedRoute>
          }
        />

        {/* ========== Admin Dashboard (Protected) ========== */}
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute requiredRole="admin">
              <AdminRoutes />
            </ProtectedRoute>
          }
        />

        {/* ========== 404 Fallback ========== */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRouter;
