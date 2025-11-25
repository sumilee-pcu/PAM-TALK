/**
 * User Signup Page
 * 사용자 회원가입 페이지
 */

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../../../services/auth/authService';
import './SignupPage.css';

function SignupPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    role: 'USER', // USER, SUPPLIER, COMPANY
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: ''
  });

  // 한글 체크 함수
  const hasKorean = (text) => {
    const koreanRegex = /[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/;
    return koreanRegex.test(text);
  };

  // 이메일 유효성 검사
  const validateEmail = (email) => {
    if (!email) return '';

    if (hasKorean(email)) {
      return '한글은 입력할 수 없습니다';
    }

    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
      return '올바른 이메일 형식이 아닙니다';
    }

    return '';
  };

  // 전화번호 유효성 검사
  const validatePhone = (phone) => {
    if (!phone) return '';

    // 한글 체크
    if (hasKorean(phone)) {
      return '한글은 입력할 수 없습니다';
    }

    // 숫자와 하이픈만 허용
    const phoneRegex = /^[0-9-]+$/;
    if (!phoneRegex.test(phone)) {
      return '숫자와 하이픈(-)만 입력 가능합니다';
    }

    // 전화번호 형식 체크 (010-xxxx-xxxx 또는 01012345678)
    const formattedRegex = /^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$/;
    if (phone.length >= 10 && !formattedRegex.test(phone)) {
      return '올바른 전화번호 형식이 아닙니다 (예: 010-1234-5678)';
    }

    return '';
  };

  // 이름 유효성 검사
  const validateName = (name) => {
    if (!name) return '';

    if (name.trim().length < 2) {
      return '이름은 2자 이상 입력해주세요';
    }

    // 특수문자 체크 (한글, 영문, 공백만 허용)
    const nameRegex = /^[가-힣a-zA-Z\s]+$/;
    if (!nameRegex.test(name)) {
      return '이름은 한글 또는 영문만 입력 가능합니다';
    }

    return '';
  };

  // 비밀번호 유효성 검사
  const validatePassword = (password) => {
    if (!password) return '';

    if (password.length < 8) {
      return '비밀번호는 8자 이상이어야 합니다';
    }

    // 영문, 숫자, 특수문자 중 2가지 이상 포함 권장
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

    const criteriaCount = [hasLetter, hasNumber, hasSpecial].filter(Boolean).length;

    if (criteriaCount < 2) {
      return '영문, 숫자, 특수문자 중 2가지 이상 조합하세요';
    }

    return '';
  };

  // 비밀번호 확인 검사
  const validateConfirmPassword = (confirmPassword, password) => {
    if (!confirmPassword) return '';

    if (confirmPassword !== password) {
      return '비밀번호가 일치하지 않습니다';
    }

    return '';
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError('');

    // 실시간 유효성 검사
    let fieldError = '';

    switch(name) {
      case 'email':
        fieldError = validateEmail(value);
        break;
      case 'phone':
        fieldError = validatePhone(value);
        break;
      case 'name':
        fieldError = validateName(value);
        break;
      case 'password':
        fieldError = validatePassword(value);
        // 비밀번호 확인도 다시 체크
        if (formData.confirmPassword) {
          setFieldErrors(prev => ({
            ...prev,
            confirmPassword: validateConfirmPassword(formData.confirmPassword, value)
          }));
        }
        break;
      case 'confirmPassword':
        fieldError = validateConfirmPassword(value, formData.password);
        break;
      default:
        break;
    }

    setFieldErrors(prev => ({
      ...prev,
      [name]: fieldError
    }));
  };

  const validateForm = () => {
    const errors = {
      name: validateName(formData.name),
      email: validateEmail(formData.email),
      phone: validatePhone(formData.phone),
      password: validatePassword(formData.password),
      confirmPassword: validateConfirmPassword(formData.confirmPassword, formData.password)
    };

    setFieldErrors(errors);

    // 에러가 하나라도 있으면 false
    const hasError = Object.values(errors).some(error => error !== '');

    if (hasError) {
      const firstError = Object.values(errors).find(error => error !== '');
      setError(firstError);
      return false;
    }

    if (!formData.name.trim()) {
      setError('이름을 입력하세요.');
      return false;
    }

    if (!formData.email.trim()) {
      setError('이메일을 입력하세요.');
      return false;
    }

    if (!formData.password) {
      setError('비밀번호를 입력하세요.');
      return false;
    }

    if (!formData.phone.trim()) {
      setError('전화번호를 입력하세요.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const { confirmPassword, ...signupData } = formData;
      const result = await authService.signup(signupData);

      if (result.user) {
        // Signup successful, redirect based on role
        alert('회원가입이 완료되었습니다!');
        const role = result.user.role;
        switch (role) {
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
      if (err.error) {
        setError(err.error);
      } else {
        setError('회원가입 중 오류가 발생했습니다.');
      }
      console.error('Signup error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-page">
      <div className="signup-container">
        <div className="signup-header">
          <h1>PAM-TALK</h1>
          <p>탄소 감축 커뮤니티 플랫폼</p>
        </div>

        <form className="signup-form" onSubmit={handleSubmit}>
          <h2>회원가입</h2>

          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="name">
              이름 <span className="required">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="홍길동"
              required
              disabled={loading}
              className={fieldErrors.name ? 'input-error' : ''}
            />
            {fieldErrors.name && (
              <small className="error-text">{fieldErrors.name}</small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="email">
              이메일 <span className="required">*</span>
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="email@example.com"
              required
              disabled={loading}
              className={fieldErrors.email ? 'input-error' : ''}
            />
            {fieldErrors.email && (
              <small className="error-text">{fieldErrors.email}</small>
            )}
            {!fieldErrors.email && formData.email && (
              <small className="success-text">✓ 사용 가능한 이메일 형식입니다</small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="phone">
              전화번호 <span className="required">*</span>
            </label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="010-1234-5678"
              required
              disabled={loading}
              className={fieldErrors.phone ? 'input-error' : ''}
            />
            {fieldErrors.phone && (
              <small className="error-text">{fieldErrors.phone}</small>
            )}
            {!fieldErrors.phone && formData.phone && formData.phone.length >= 10 && (
              <small className="success-text">✓ 올바른 전화번호 형식입니다</small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="role">
              역할 <span className="required">*</span>
            </label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
              disabled={loading}
            >
              <option value="USER">소비자</option>
              <option value="SUPPLIER">공급자</option>
              <option value="COMPANY">기업담당자</option>
            </select>
            <small className="help-text">
              {formData.role === 'USER'
                ? '친환경 제품을 구매하고 ESG 활동을 합니다.'
                : formData.role === 'SUPPLIER'
                ? '농산물/상품을 공급하고 탄소 감축 활동을 합니다.'
                : '기업에서 소비자에게 ESG 활동을 인증하고 관리합니다.'}
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="password">
              비밀번호 <span className="required">*</span>
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="8자 이상 입력하세요"
              required
              disabled={loading}
              minLength={8}
              className={fieldErrors.password ? 'input-error' : ''}
            />
            {fieldErrors.password && (
              <small className="error-text">{fieldErrors.password}</small>
            )}
            {!fieldErrors.password && formData.password && formData.password.length >= 8 && (
              <small className="success-text">✓ 안전한 비밀번호입니다</small>
            )}
            {!fieldErrors.password && !formData.password && (
              <small className="help-text">8자 이상, 영문/숫자/특수문자 중 2가지 이상 조합</small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">
              비밀번호 확인 <span className="required">*</span>
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="비밀번호를 다시 입력하세요"
              required
              disabled={loading}
              className={fieldErrors.confirmPassword ? 'input-error' : ''}
            />
            {fieldErrors.confirmPassword && (
              <small className="error-text">{fieldErrors.confirmPassword}</small>
            )}
            {!fieldErrors.confirmPassword && formData.confirmPassword && formData.password === formData.confirmPassword && (
              <small className="success-text">✓ 비밀번호가 일치합니다</small>
            )}
          </div>

          <button type="submit" className="btn-signup" disabled={loading}>
            {loading ? '회원가입 중...' : '회원가입'}
          </button>

          <div className="signup-links">
            <span>이미 계정이 있으신가요?</span>
            <Link to="/login">로그인</Link>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SignupPage;
