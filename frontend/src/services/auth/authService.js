/**
 * Authentication Service
 * 인증 관련 API 서비스
 */

import apiClient from '../api/client';

const authService = {
  /**
   * 회원가입
   * @param {Object} userData - 사용자 정보 (name, email, password, phone, role)
   * @returns {Promise} 회원가입 결과
   */
  signup: async (userData) => {
    try {
      const response = await apiClient.post('/auth/signup', userData);

      // 토큰 저장
      if (response.data.tokens) {
        localStorage.setItem('pam_token', response.data.tokens.accessToken);
        localStorage.setItem('pam_refresh_token', response.data.tokens.refreshToken);
      }

      // 사용자 정보 저장
      if (response.data.user) {
        localStorage.setItem('pam_user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      // 개발 모드: 백엔드가 없을 때 임시 회원가입 처리
      console.warn('API 호출 실패, 개발 모드로 회원가입 처리:', error);

      const user = {
        id: Date.now(),
        name: userData.name,
        email: userData.email,
        phone: userData.phone || '',
        role: userData.role || 'CONSUMER',
        createdAt: new Date().toISOString()
      };

      // 임시 토큰 생성
      const token = 'dev_token_' + Date.now();
      localStorage.setItem('pam_token', token);
      localStorage.setItem('pam_refresh_token', 'dev_refresh_' + Date.now());
      localStorage.setItem('pam_user', JSON.stringify(user));

      return {
        user,
        tokens: {
          accessToken: token,
          refreshToken: 'dev_refresh_' + Date.now()
        }
      };
    }
  },

  /**
   * 로그인
   * @param {string} email - 이메일
   * @param {string} password - 비밀번호
   * @returns {Promise} 로그인 결과
   */
  login: async (email, password) => {
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password,
      });

      // 토큰 저장
      if (response.data.tokens) {
        localStorage.setItem('pam_token', response.data.tokens.accessToken);
        localStorage.setItem('pam_refresh_token', response.data.tokens.refreshToken);
      }

      // 사용자 정보 저장
      if (response.data.user) {
        localStorage.setItem('pam_user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      // 개발 모드: 백엔드가 없을 때 임시 인증 처리
      console.warn('API 호출 실패, 개발 모드로 로그인 처리:', error);
      console.log('로그인 시도:', email);

      // 데모 계정 정의
      const demoAccounts = {
        'consumer@pamtalk.com': {
          email: 'consumer@pamtalk.com',
          name: '소비자',
          role: 'CONSUMER',
          id: 1
        },
        'supplier@pamtalk.com': {
          email: 'supplier@pamtalk.com',
          name: '공급자',
          role: 'SUPPLIER',
          id: 2
        },
        'company@pamtalk.com': {
          email: 'company@pamtalk.com',
          name: '기업담당자',
          role: 'COMPANY',
          id: 3
        },
        'farmer@pamtalk.com': {
          email: 'farmer@pamtalk.com',
          name: '농부',
          role: 'FARMER',
          id: 4
        },
        'committee@pamtalk.com': {
          email: 'committee@pamtalk.com',
          name: '위원회',
          role: 'COMMITTEE',
          id: 5
        },
        'admin@pamtalk.com': {
          email: 'admin@pamtalk.com',
          name: '관리자',
          role: 'ADMIN',
          id: 6
        },
      };

      const user = demoAccounts[email];

      if (user) {
        // 임시 토큰 생성
        const token = 'dev_token_' + Date.now();
        localStorage.setItem('pam_token', token);
        localStorage.setItem('pam_refresh_token', 'dev_refresh_' + Date.now());
        localStorage.setItem('pam_user', JSON.stringify(user));

        console.log('✅ 개발 모드 로그인 성공:', user.name, user.role);

        return {
          user,
          tokens: {
            accessToken: token,
            refreshToken: 'dev_refresh_' + Date.now()
          }
        };
      } else {
        console.error('❌ 등록되지 않은 이메일:', email);
        console.log('사용 가능한 데모 계정:', Object.keys(demoAccounts));
        throw {
          error: '등록되지 않은 이메일입니다.',
          message: '데모 계정을 사용하거나 하단의 빠른 로그인 버튼을 클릭하세요.'
        };
      }
    }
  },

  /**
   * 로그아웃
   * @returns {Promise} 로그아웃 결과
   */
  logout: async () => {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      // 로컬 스토리지 정리
      localStorage.removeItem('pam_token');
      localStorage.removeItem('pam_refresh_token');
      localStorage.removeItem('pam_user');
    }
  },

  /**
   * 토큰 갱신
   * @returns {Promise} 새로운 토큰
   */
  refreshToken: async () => {
    try {
      const refreshToken = localStorage.getItem('pam_refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token found');
      }

      const response = await apiClient.post('/auth/refresh', {
        refreshToken,
      });

      // 새로운 토큰 저장
      if (response.data.tokens) {
        localStorage.setItem('pam_token', response.data.tokens.accessToken);
      }

      return response.data;
    } catch (error) {
      // Refresh 실패시 로그아웃
      localStorage.removeItem('pam_token');
      localStorage.removeItem('pam_refresh_token');
      localStorage.removeItem('pam_user');
      throw error.response?.data || error;
    }
  },

  /**
   * 내 정보 조회
   * @returns {Promise} 사용자 정보
   */
  getProfile: async () => {
    try {
      const response = await apiClient.get('/auth/me');

      // 사용자 정보 업데이트
      if (response.data.user) {
        localStorage.setItem('pam_user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 프로필 업데이트
   * @param {Object} updates - 업데이트할 정보
   * @returns {Promise} 업데이트 결과
   */
  updateProfile: async (updates) => {
    try {
      const response = await apiClient.put('/auth/profile', updates);

      // 사용자 정보 업데이트
      if (response.data.user) {
        localStorage.setItem('pam_user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 비밀번호 변경
   * @param {string} currentPassword - 현재 비밀번호
   * @param {string} newPassword - 새 비밀번호
   * @returns {Promise} 변경 결과
   */
  changePassword: async (currentPassword, newPassword) => {
    try {
      const response = await apiClient.put('/auth/password', {
        currentPassword,
        newPassword,
      });

      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 로컬 스토리지에서 사용자 정보 가져오기
   * @returns {Object|null} 사용자 정보
   */
  getCurrentUser: () => {
    try {
      const userStr = localStorage.getItem('pam_user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  },

  /**
   * 로컬 스토리지에서 토큰 가져오기
   * @returns {string|null} 액세스 토큰
   */
  getToken: () => {
    return localStorage.getItem('pam_token');
  },

  /**
   * 인증 여부 확인
   * @returns {boolean} 인증 여부
   */
  isAuthenticated: () => {
    const token = localStorage.getItem('pam_token');
    const user = localStorage.getItem('pam_user');
    return !!(token && user);
  },
};

export default authService;
