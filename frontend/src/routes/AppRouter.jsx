/**
 * PAM-TALK 메인 라우터
 * 6-Portal 시스템 라우팅
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import UserRoutes from './UserRoutes';
import CommitteeRoutes from './CommitteeRoutes';
import AdminRoutes from './AdminRoutes';
import SupplierRoutes from './SupplierRoutes';
import CompanyRoutes from './CompanyRoutes';
import FarmerRoutes from './FarmerRoutes';

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
            <ProtectedRoute requiredRole="COMMITTEE">
              <CommitteeRoutes />
            </ProtectedRoute>
          }
        />

        {/* ========== Admin Dashboard (Protected) ========== */}
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminRoutes />
            </ProtectedRoute>
          }
        />

        {/* ========== Supplier Portal (Protected) ========== */}
        <Route
          path="/supplier/*"
          element={
            <ProtectedRoute requiredRole="SUPPLIER">
              <SupplierRoutes />
            </ProtectedRoute>
          }
        />

        {/* ========== Company Portal (Protected) ========== */}
        <Route
          path="/company/*"
          element={
            <ProtectedRoute requiredRole="COMPANY">
              <CompanyRoutes />
            </ProtectedRoute>
          }
        />

        {/* ========== Farmer Portal (Protected) ========== */}
        <Route
          path="/farmer/*"
          element={
            <ProtectedRoute requiredRole="FARMER">
              <FarmerRoutes />
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
