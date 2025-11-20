/**
 * 사용자 포털 라우트
 * User Portal Routes
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import UserLayout from '../layouts/UserLayout';

// Lazy load pages for better performance
const HomePage = React.lazy(() => import('../pages/user/Home/HomePage'));
const LoginPage = React.lazy(() => import('../pages/user/Auth/LoginPage'));
const SignupPage = React.lazy(() => import('../pages/user/Auth/SignupPage'));
const DashboardPage = React.lazy(() => import('../pages/user/Dashboard/UserDashboard'));
const WalletPage = React.lazy(() => import('../pages/user/Wallet/WalletPage'));
const FeedPage = React.lazy(() => import('../pages/user/Feed/FeedPage'));
const MarketplacePage = React.lazy(() => import('../pages/user/Marketplace/MarketplacePage'));
const ChallengePage = React.lazy(() => import('../pages/user/Challenge/ChallengePage'));
const ActivitiesPage = React.lazy(() => import('../pages/user/Activities/ActivitiesPage'));
const CouponsPage = React.lazy(() => import('../pages/user/Coupons/CouponsPage'));
const CommunityPage = React.lazy(() => import('../pages/user/Community/CommunityPage'));
const ProfilePage = React.lazy(() => import('../pages/user/Profile/ProfilePage'));
const SettingsPage = React.lazy(() => import('../pages/user/Settings/SettingsPage'));
const ESGRouter = React.lazy(() => import('../pages/user/ESG'));

function UserRoutes() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        {/* Public Routes (No Layout) */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Routes with UserLayout */}
        <Route element={<UserLayout />}>
          <Route index element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />

          {/* Feed */}
          <Route path="/feed/*" element={<FeedPage />} />

          {/* Marketplace */}
          <Route path="/marketplace/*" element={<MarketplacePage />} />

          {/* Challenge */}
          <Route path="/challenge" element={<ChallengePage />} />

          {/* Wallet */}
          <Route path="/wallet/*" element={<WalletPage />} />

          {/* Activities */}
          <Route path="/activities/*" element={<ActivitiesPage />} />

          {/* Coupons */}
          <Route path="/coupons/*" element={<CouponsPage />} />

          {/* Community */}
          <Route path="/community/*" element={<CommunityPage />} />

          {/* Profile */}
          <Route path="/profile/*" element={<ProfilePage />} />

          {/* Settings */}
          <Route path="/settings/*" element={<SettingsPage />} />

          {/* ESG Activity Certification */}
          <Route path="/esg/*" element={<ESGRouter />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </React.Suspense>
  );
}

export default UserRoutes;
