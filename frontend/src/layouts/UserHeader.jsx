/**
 * User Portal Header
 * 사용자 포털 헤더 네비게이션
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './UserHeader.css';

function UserHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <header className={`user-header ${scrolled ? 'scrolled' : ''}`}>
      <div className="header-container">
        {/* Logo */}
        <Link to="/" className="logo">
          <div className="logo-icon">🌱</div>
          <span className="logo-text">PAM-TALK</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="desktop-nav">
          <Link to="/activities" className="nav-link">활동하기</Link>
          <Link to="/esg" className="nav-link">ESG 인증</Link>
          <Link to="/marketplace" className="nav-link">마켓</Link>
          <Link to="/challenge" className="nav-link">챌린지</Link>
          <Link to="/community" className="nav-link">커뮤니티</Link>
        </nav>

        {/* Auth Buttons */}
        <div className="header-actions">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="btn-secondary">
                대시보드
              </Link>
              <div className="user-menu">
                <button className="user-avatar">
                  {user?.name?.charAt(0) || 'U'}
                </button>
                <div className="user-dropdown">
                  <Link to="/dashboard">대시보드</Link>
                  <Link to="/wallet">디지털 쿠폰함</Link>
                  <Link to="/profile">프로필</Link>
                  <Link to="/settings">설정</Link>
                  <button onClick={handleLogout}>로그아웃</button>
                </div>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary">로그인</Link>
              <Link to="/signup" className="btn-primary">시작하기</Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="mobile-nav">
          <Link to="/activities" onClick={() => setMobileMenuOpen(false)}>활동하기</Link>
          <Link to="/esg" onClick={() => setMobileMenuOpen(false)}>ESG 인증</Link>
          <Link to="/marketplace" onClick={() => setMobileMenuOpen(false)}>마켓</Link>
          <Link to="/challenge" onClick={() => setMobileMenuOpen(false)}>챌린지</Link>
          <Link to="/community" onClick={() => setMobileMenuOpen(false)}>커뮤니티</Link>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)}>대시보드</Link>
              <Link to="/wallet" onClick={() => setMobileMenuOpen(false)}>디지털 쿠폰함</Link>
              <Link to="/profile" onClick={() => setMobileMenuOpen(false)}>프로필</Link>
              <Link to="/settings" onClick={() => setMobileMenuOpen(false)}>설정</Link>
              <button onClick={handleLogout}>로그아웃</button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={() => setMobileMenuOpen(false)}>로그인</Link>
              <Link to="/signup" onClick={() => setMobileMenuOpen(false)}>시작하기</Link>
            </>
          )}
        </div>
      )}
    </header>
  );
}

export default UserHeader;
