/**
 * 기업 포털 라우트
 * Company Portal Routes
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import CompanyLayout from '../layouts/CompanyLayout';

// Lazy load pages
const CompanyDashboard = React.lazy(() => import('../pages/company/Dashboard/CompanyDashboard'));

function CompanyRoutes() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route element={<CompanyLayout />}>
          <Route index element={<CompanyDashboard />} />
        </Route>
        <Route path="*" element={<Navigate to="/company" replace />} />
      </Routes>
    </React.Suspense>
  );
}

export default CompanyRoutes;
