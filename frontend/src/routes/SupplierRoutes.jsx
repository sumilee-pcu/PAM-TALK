/**
 * 공급자 포털 라우트
 * Supplier Portal Routes
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Lazy load pages
const SupplierDashboard = React.lazy(() => import('../pages/supplier/Dashboard/SupplierDashboard'));

function SupplierRoutes() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route index element={<SupplierDashboard />} />
        <Route path="*" element={<Navigate to="/supplier" replace />} />
      </Routes>
    </React.Suspense>
  );
}

export default SupplierRoutes;
