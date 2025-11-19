/**
 * 위원회 포털 라우트
 * Committee Portal Routes
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import CommitteeLayout from '../layouts/CommitteeLayout';

// Lazy load pages
const CommitteeLogin = React.lazy(() => import('../pages/committee/Login/CommitteeLoginPage'));
const CommitteeDashboard = React.lazy(() => import('../pages/committee/Dashboard/CommitteeDashboard'));
const VerificationPage = React.lazy(() => import('../pages/committee/Verification/VerificationPage'));
const CouponIssuancePage = React.lazy(() => import('../pages/committee/CouponIssuance/CouponIssuancePage'));
const ReportsPage = React.lazy(() => import('../pages/committee/Reports/ReportsPage'));
const MembersPage = React.lazy(() => import('../pages/committee/Members/MembersPage'));

function CommitteeRoutes() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        {/* Login (No Layout) */}
        <Route path="/login" element={<CommitteeLogin />} />

        {/* Routes with CommitteeLayout */}
        <Route element={<CommitteeLayout />}>
          {/* Redirect /committee to /committee/dashboard */}
          <Route index element={<Navigate to="/committee/dashboard" replace />} />

          <Route path="/dashboard" element={<CommitteeDashboard />} />

          {/* Verification */}
          <Route path="/verification/*" element={<VerificationPage />} />

          {/* Coupon Issuance */}
          <Route path="/coupon-issuance/*" element={<CouponIssuancePage />} />

          {/* Reports */}
          <Route path="/reports/*" element={<ReportsPage />} />

          {/* Members */}
          <Route path="/members/*" element={<MembersPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<Navigate to="/committee/dashboard" replace />} />
      </Routes>
    </React.Suspense>
  );
}

export default CommitteeRoutes;
