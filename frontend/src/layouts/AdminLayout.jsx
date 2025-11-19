import React from 'react';
import { Outlet } from 'react-router-dom';

function AdminLayout() {
  return (
    <div className="admin-layout">
      <header style={{ padding: '1rem 2rem', background: '#9C27B0', color: 'white' }}>
        <h2>관리자 대시보드</h2>
      </header>
      <main style={{ padding: '2rem' }}>
        <Outlet />
      </main>
    </div>
  );
}

export default AdminLayout;
