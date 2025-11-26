/**
 * 농부 포털 라우트
 * Farmer Portal Routes
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Lazy load pages
const FarmerDashboard = React.lazy(() => import('../pages/farmer/Dashboard/FarmerDashboard'));

function FarmerRoutes() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route index element={<FarmerDashboard />} />
        <Route path="*" element={<Navigate to="/farmer" replace />} />
      </Routes>
    </React.Suspense>
  );
}

export default FarmerRoutes;
