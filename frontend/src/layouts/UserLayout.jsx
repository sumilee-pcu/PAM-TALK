/**
 * User Portal Layout
 * 사용자 포털 메인 레이아웃
 */

import React from 'react';
import { Outlet } from 'react-router-dom';
import UserHeader from './UserHeader';
import UserFooter from './UserFooter';
import './UserLayout.css';

function UserLayout() {
  return (
    <div className="user-layout">
      <UserHeader />
      <main className="user-main">
        <Outlet />
      </main>
      <UserFooter />
    </div>
  );
}

export default UserLayout;
