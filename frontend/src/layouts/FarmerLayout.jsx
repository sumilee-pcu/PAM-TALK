/**
 * Farmer Layout with Navigation
 * 농부 레이아웃 with 네비게이션
 */

import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import './FarmerLayout.css';

function FarmerLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false); // 모바일 기본 닫힘

  const menuItems = [
    { path: '/farmer', icon: '📊', label: '대시보드' },
    { path: '/', icon: '🏠', label: '홈으로' },
  ];

  const handleLogout = () => {
    if (window.confirm('로그아웃 하시겠습니까?')) {
      localStorage.removeItem('token');
      navigate('/login');
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="farmer-layout-container">
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div className="mobile-overlay" onClick={toggleSidebar}></div>
      )}

      {/* Sidebar */}
      <aside className={`farmer-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2>🌾 농부</h2>
          <button className="sidebar-close" onClick={toggleSidebar}>
            ✕
          </button>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map((item) => {
            const isActive = item.path === '/farmer'
              ? location.pathname === '/farmer'
              : location.pathname.startsWith(item.path) && item.path !== '/';
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setSidebarOpen(false)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>
            <span className="nav-icon">🚪</span>
            <span>로그아웃</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="farmer-main">
        <header className="farmer-top-header">
          <div className="header-left">
            <button className="mobile-menu-toggle" onClick={toggleSidebar}>
              ☰
            </button>
            <h1>농부 대시보드</h1>
          </div>
          <div className="header-right">
            <button className="btn-home" onClick={() => navigate('/')}>
              🏠 홈
            </button>
            <div className="user-info">
              <span className="user-avatar">👤</span>
            </div>
          </div>
        </header>

        <main className="farmer-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default FarmerLayout;
