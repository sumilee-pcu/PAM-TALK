/**
 * Admin Login Page
 * 관리자 로그인 페이지
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminLoginPage.css';

function AdminLoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert('이메일과 비밀번호를 입력해주세요.');
      return;
    }

    setLoading(true);

    try {
      // 개발 모드: 간단한 인증
      // 실제 배포 시에는 백엔드 API 호출로 변경
      if (email === 'admin@esgdigital.org' && password === 'admin123') {
        // 로그인 성공
        const adminUser = {
          id: 1,
          email: 'admin@esgdigital.org',
          name: '관리자',
          role: 'admin',
        };

        // localStorage에 저장
        localStorage.setItem('pam_user', JSON.stringify(adminUser));
        localStorage.setItem('pam_token', 'dev_admin_token_' + Date.now());
        localStorage.setItem('adminToken', 'dev_admin_token_' + Date.now());

        alert('✅ 로그인 성공!');
        navigate('/admin/dashboard');
      } else {
        alert('❌ 로그인 실패\n\n이메일 또는 비밀번호가 올바르지 않습니다.');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('❌ 로그인 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 개발용 빠른 로그인
  const handleQuickLogin = () => {
    setEmail('admin@esgdigital.org');
    setPassword('admin123');
  };

  return (
    <div className="admin-login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>🛠️ 관리자 로그인</h1>
          <p>PAM ESG 시스템 관리자 페이지</p>
        </div>

        <form className="login-form" onSubmit={handleLogin}>
          <div className="form-group">
            <label>이메일</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@esgdigital.org"
              className="form-input"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label>비밀번호</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호 입력"
              className="form-input"
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="btn-login"
            disabled={loading}
          >
            {loading ? '로그인 중...' : '🔐 로그인'}
          </button>
        </form>

        <div className="login-footer">
          <div className="dev-info">
            <p>🔧 개발 모드</p>
            <button className="btn-quick-login" onClick={handleQuickLogin}>
              빠른 로그인 (자동 입력)
            </button>
            <div className="dev-credentials">
              <small>ID: admin@esgdigital.org</small>
              <small>PW: admin123</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminLoginPage;
