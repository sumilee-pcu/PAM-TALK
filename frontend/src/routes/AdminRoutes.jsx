/**
 * 관리자 대시보드 라우트
 * Admin Dashboard Routes
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from '../layouts/AdminLayout';

// Lazy load pages
const AdminLogin = React.lazy(() => import('../pages/admin/Login/AdminLoginPage'));
const AdminDashboard = React.lazy(() => import('../pages/admin/Dashboard/AdminDashboard'));
const BlockchainPage = React.lazy(() => import('../pages/admin/Blockchain/BlockchainPage'));
const UsersPage = React.lazy(() => import('../pages/admin/Users/UsersPage'));
const CommitteeManagement = React.lazy(() => import('../pages/admin/Committee/CommitteeManagement'));
const CouponSystemPage = React.lazy(() => import('../pages/admin/CouponSystem/CouponSystemPage'));
const AnalyticsPage = React.lazy(() => import('../pages/admin/Analytics/AnalyticsPage'));
const SystemPage = React.lazy(() => import('../pages/admin/System/SystemPage'));
const SupportPage = React.lazy(() => import('../pages/admin/Support/SupportPage'));
const ESGActivitiesPage = React.lazy(() => import('../pages/admin/ESGActivities/ESGActivitiesPage'));
const BulkDCPage = React.lazy(() => import('../pages/admin/BulkDC/BulkDCPage'));
const ProductManagementPage = React.lazy(() => import('../pages/admin/Products/ProductManagementPage'));
const OrderManagementPage = React.lazy(() => import('../pages/admin/Orders/OrderManagementPage'));

function AdminRoutes() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        {/* Login (No Layout) */}
        <Route path="/login" element={<AdminLogin />} />

        {/* Routes with AdminLayout */}
        <Route element={<AdminLayout />}>
          {/* Redirect /admin to /admin/dashboard */}
          <Route index element={<Navigate to="/admin/dashboard" replace />} />

          <Route path="/dashboard" element={<AdminDashboard />} />

          {/* Blockchain Management */}
          <Route path="/blockchain/*" element={<BlockchainPage />} />

          {/* Users Management */}
          <Route path="/users/*" element={<UsersPage />} />

          {/* Committee Management */}
          <Route path="/committee-management/*" element={<CommitteeManagement />} />

          {/* Coupon System */}
          <Route path="/coupon-system/*" element={<CouponSystemPage />} />

          {/* Analytics */}
          <Route path="/analytics/*" element={<AnalyticsPage />} />

          {/* System */}
          <Route path="/system/*" element={<SystemPage />} />

          {/* Support */}
          <Route path="/support/*" element={<SupportPage />} />

          {/* ESG Activities */}
          <Route path="/esg-activities/*" element={<ESGActivitiesPage />} />

          {/* Bulk DC Distribution */}
          <Route path="/bulk-dc/*" element={<BulkDCPage />} />

          {/* Product Management */}
          <Route path="/products" element={<ProductManagementPage />} />

          {/* Order Management */}
          <Route path="/orders" element={<OrderManagementPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
      </Routes>
    </React.Suspense>
  );
}

export default AdminRoutes;
