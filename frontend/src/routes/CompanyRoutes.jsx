/**
 * 기업 포털 라우트
 * Company Portal Routes
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Lazy load pages
const CompanyDashboard = React.lazy(() => import('../pages/company/Dashboard/CompanyDashboard'));

function CompanyRoutes() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route index element={<CompanyDashboard />} />
        <Route path="*" element={<Navigate to="/company" replace />} />
      </Routes>
    </React.Suspense>
  );
}

export default CompanyRoutes;
