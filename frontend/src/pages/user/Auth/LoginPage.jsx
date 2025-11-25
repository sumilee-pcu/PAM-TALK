/**
 * User Login Page
 * 사용자 로그인 페이지
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import './LoginPage.css';

function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // 컴포넌트 마운트 시 에러 초기화
  useEffect(() => {
    setError('');
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(formData.email, formData.password);

      if (result.success) {
        // Redirect based on user role
        const role = result.user.role;
        switch (role) {
          case 'ADMIN':
            navigate('/admin/dashboard');
            break;
          case 'COMMITTEE':
            navigate('/committee/dashboard');
            break;
          case 'SUPPLIER':
            navigate('/user/marketplace');
            break;
          case 'COMPANY':
            navigate('/company/dashboard');
            break;
          default:
            navigate('/user/dashboard');
        }
      } else {
        setError(result.error || '로그인에 실패했습니다.');
      }
    } catch (err) {
      setError('로그인 중 오류가 발생했습니다.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Quick login buttons for demo
  const quickLogin = async (email, password, label) => {
    setFormData({ email, password });
    setLoading(true);
    try {
      const result = await login(email, password);
      if (result.success) {
        const role = result.user.role;
        switch (role) {
          case 'ADMIN':
            navigate('/admin/dashboard');
            break;
          case 'COMMITTEE':
            navigate('/committee/dashboard');
            break;
          case 'SUPPLIER':
            navigate('/user/marketplace');
            break;
          case 'COMPANY':
            navigate('/company/dashboard');
            break;
          default:
            navigate('/user/dashboard');
        }
      }
    } catch (err) {
      setError('로그인 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>PAM-TALK</h1>
          <p>블록체인 기반 탄소 감축 플랫폼</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <h2>로그인</h2>

          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="email">이메일</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="email@example.com"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="비밀번호를 입력하세요"
              required
              disabled={loading}
            />
          </div>

          <button type="submit" className="btn-login" disabled={loading}>
            {loading ? '로그인 중...' : '로그인'}
          </button>

          <div className="login-links">
            <Link to="/signup">회원가입</Link>
            <span>|</span>
            <Link to="/forgot-password">비밀번호 찾기</Link>
          </div>
        </form>

        {/* Quick Login for Demo */}
        <div className="quick-login">
          <h3>⚡ 빠른 시연 로그인 - 클릭 한 번으로 입장!</h3>
          <div className="quick-login-buttons">
            <button
              onClick={() => quickLogin('consumer@pamtalk.com', 'Consumer123!', '소비자')}
              disabled={loading}
              className="btn-quick user"
            >
              👤 소비자
            </button>
            <button
              onClick={() => quickLogin('supplier@pamtalk.com', 'Supplier123!', '공급자')}
              disabled={loading}
              className="btn-quick supplier"
            >
              🏭 공급자
            </button>
            <button
              onClick={() => quickLogin('company@pamtalk.com', 'Company123!', '기업담당자')}
              disabled={loading}
              className="btn-quick company"
            >
              🏢 기업담당자
            </button>
            <button
              onClick={() => quickLogin('committee@pamtalk.com', 'Committee123!', '위원회')}
              disabled={loading}
              className="btn-quick committee"
            >
              🎯 위원회
            </button>
            <button
              onClick={() => quickLogin('admin@pamtalk.com', 'Admin123!', '관리자')}
              disabled={loading}
              className="btn-quick admin"
            >
              ⚙️ 관리자
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
