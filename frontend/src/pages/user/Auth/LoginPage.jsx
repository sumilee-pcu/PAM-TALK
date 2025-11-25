import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import '../../../styles/auth.css';

function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    role: 'user'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await login(formData.email, formData.password, formData.role);

      if (result.success) {
        // 역할에 따라 다른 페이지로 리다이렉트
        if (formData.role === 'admin') {
          navigate('/admin/dashboard');
        } else if (formData.role === 'committee') {
          navigate('/committee/dashboard');
        } else {
          navigate('/dashboard');
        }
      } else {
        setError(result.error || '로그인에 실패했습니다.');
      }
    } catch (err) {
      setError('로그인 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 데모 계정으로 빠른 로그인
  const handleDemoLogin = (role) => {
    setFormData({
      email: `demo_${role}@pam.com`,
      password: 'demo123',
      role: role
    });
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>PAM-TALK</h1>
          <p>블록체인 기반 탄소 감축 플랫폼</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">이메일</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="이메일을 입력하세요"
              required
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
            />
          </div>

          <div className="form-group">
            <label htmlFor="role">사용자 유형</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
            >
              <option value="user">일반 사용자</option>
              <option value="committee">MRV 위원회</option>
              <option value="admin">관리자</option>
            </select>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <div className="demo-accounts">
          <p className="demo-title">데모 계정으로 빠른 로그인:</p>
          <div className="demo-buttons">
            <button
              type="button"
              className="btn-demo"
              onClick={() => handleDemoLogin('user')}
            >
              일반 사용자
            </button>
            <button
              type="button"
              className="btn-demo"
              onClick={() => handleDemoLogin('committee')}
            >
              MRV 위원회
            </button>
            <button
              type="button"
              className="btn-demo"
              onClick={() => handleDemoLogin('admin')}
            >
              관리자
            </button>
          </div>
        </div>

        <div className="auth-footer">
          <p>
            계정이 없으신가요? <Link to="/signup">회원가입</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
