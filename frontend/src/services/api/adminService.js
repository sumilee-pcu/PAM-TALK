/**
 * Admin Service
 * 관리자 관련 API 서비스
 */

import apiClient from './client';

const adminService = {
  /**
   * 대시보드 통계 조회
   * @returns {Promise} 대시보드 통계
   */
  getDashboard: async () => {
    try {
      const response = await apiClient.get('/admin/dashboard');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 시스템 통계 조회
   * @param {string} period - 기간 (24h, 7d, 30d, 90d)
   * @returns {Promise} 시스템 통계
   */
  getSystemStats: async (period = '7d') => {
    try {
      const response = await apiClient.get('/admin/stats', {
        params: { period },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 사용자 목록 조회
   * @param {Object} params - 필터 옵션 (role, isActive, search, page, limit)
   * @returns {Promise} 사용자 목록
   */
  getUsers: async (params = {}) => {
    try {
      const response = await apiClient.get('/admin/users', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 사용자 상세 조회
   * @param {string} userId - 사용자 ID
   * @returns {Promise} 사용자 상세 정보
   */
  getUserById: async (userId) => {
    try {
      const response = await apiClient.get(`/admin/users/${userId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 사용자 정보 수정
   * @param {string} userId - 사용자 ID
   * @param {Object} updates - 수정할 정보 (role, isActive, name, phone, email)
   * @returns {Promise} 수정 결과
   */
  updateUser: async (userId, updates) => {
    try {
      const response = await apiClient.put(`/admin/users/${userId}`, updates);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 사용자 비활성화
   * @param {string} userId - 사용자 ID
   * @returns {Promise} 비활성화 결과
   */
  deactivateUser: async (userId) => {
    try {
      const response = await apiClient.delete(`/admin/users/${userId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 감사 로그 조회
   * @param {Object} params - 필터 옵션 (action, resourceType, userId, startDate, endDate, page, limit)
   * @returns {Promise} 감사 로그 목록
   */
  getAuditLogs: async (params = {}) => {
    try {
      const response = await apiClient.get('/admin/audit-logs', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * DC 요청 목록 조회
   * @param {Object} params - 필터 옵션 (status, page, limit)
   * @returns {Promise} DC 요청 목록
   */
  getDCRequests: async (params = {}) => {
    try {
      const response = await apiClient.get('/admin/dc/requests', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * DC 요청 처리
   * @param {string} requestId - 요청 ID
   * @param {string} status - 처리 상태 (APPROVED, REJECTED)
   * @param {string} reviewComment - 검토 코멘트
   * @returns {Promise} 처리 결과
   */
  processDCRequest: async (requestId, status, reviewComment) => {
    try {
      const response = await apiClient.post(`/admin/dc/requests/${requestId}/process`, {
        status,
        reviewComment,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 상품 관리 - 모든 상품 조회
   * @param {Object} params - 필터 옵션
   * @returns {Promise} 상품 목록
   */
  getAllProducts: async (params = {}) => {
    try {
      const response = await apiClient.get('/marketplace/products', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 주문 관리 - 모든 주문 조회
   * @param {Object} params - 필터 옵션
   * @returns {Promise} 주문 목록
   */
  getAllOrders: async (params = {}) => {
    try {
      const response = await apiClient.get('/marketplace/orders', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

export default adminService;
