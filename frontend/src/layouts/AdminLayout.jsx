/**
 * Admin Layout with Navigation
 * 관리자 레이아웃 with 네비게이션
 */

import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import './AdminLayout.css';

function AdminLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems = [
    { path: '/admin/dashboard', icon: '📊', label: '대시보드' },
    { path: '/admin/esg-activities', icon: '🌱', label: 'ESG 활동 관리' },
    { path: '/admin/bulk-dc', icon: '💸', label: '대량 DC 전송' },
    { path: '/admin/coupon-system', icon: '🎟️', label: '쿠폰 발행' },
    { path: '/admin/users', icon: '👥', label: '사용자 관리' },
    { path: '/admin/committee-management', icon: '🏛️', label: '위원회 관리' },
    { path: '/admin/blockchain', icon: '⛓️', label: '블록체인' },
    { path: '/admin/analytics', icon: '📈', label: '분석' },
    { path: '/admin/system', icon: '⚙️', label: '시스템' },
    { path: '/admin/support', icon: '💬', label: '지원' },
  ];

  const handleLogout = () => {
    if (window.confirm('로그아웃 하시겠습니까?')) {
      // 로그아웃 처리 (예: localStorage 클리어, 세션 종료 등)
      localStorage.removeItem('adminToken');
      navigate('/admin/login');
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="admin-layout-container">
      {/* Sidebar */}
      <aside className={`admin-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>🛠️ Admin</h2>
          <button className="sidebar-toggle" onClick={toggleSidebar}>
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                {sidebarOpen && <span className="nav-label">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>
            <span className="nav-icon">🚪</span>
            {sidebarOpen && <span>로그아웃</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`admin-main ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <header className="admin-top-header">
          <div className="header-left">
            <button className="mobile-menu-toggle" onClick={toggleSidebar}>
              ☰
            </button>
            <h1>관리자 대시보드</h1>
          </div>
          <div className="header-right">
            <div className="admin-info">
              <span className="admin-avatar">👤</span>
              <span className="admin-name">관리자</span>
            </div>
          </div>
        </header>

        <main className="admin-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AdminLayout;
