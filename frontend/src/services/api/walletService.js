/**
 * Wallet Service
 * 지갑 관련 API 서비스
 */

import apiClient from './client';

const walletService = {
  /**
   * 지갑 잔액 조회
   * @returns {Promise} 지갑 정보
   */
  getBalance: async () => {
    try {
      const response = await apiClient.get('/wallet/balance');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 거래 내역 조회
   * @param {Object} params - 필터 옵션 (type, startDate, endDate, page, limit)
   * @returns {Promise} 거래 내역 목록
   */
  getTransactions: async (params = {}) => {
    try {
      const response = await apiClient.get('/wallet/transactions', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 특정 거래 상세 조회
   * @param {string} transactionId - 거래 ID
   * @returns {Promise} 거래 상세 정보
   */
  getTransactionById: async (transactionId) => {
    try {
      const response = await apiClient.get(`/wallet/transactions/${transactionId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 지갑 통계 조회
   * @returns {Promise} 지갑 통계
   */
  getStatistics: async () => {
    try {
      const response = await apiClient.get('/wallet/statistics');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * DC 충전 요청
   * @param {number} requestedAmount - 요청 금액
   * @param {string} reason - 요청 사유
   * @returns {Promise} 요청 결과
   */
  requestDC: async (requestedAmount, reason) => {
    try {
      const response = await apiClient.post('/wallet/dc/request', {
        requestedAmount,
        reason,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 내 DC 요청 목록 조회
   * @param {Object} params - 필터 옵션 (status, page, limit)
   * @returns {Promise} DC 요청 목록
   */
  getMyDCRequests: async (params = {}) => {
    try {
      const response = await apiClient.get('/wallet/dc/my-requests', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 모든 DC 요청 조회 (관리자용)
   * @param {Object} params - 필터 옵션 (status, page, limit)
   * @returns {Promise} DC 요청 목록
   */
  getAllDCRequests: async (params = {}) => {
    try {
      const response = await apiClient.get('/admin/dc/requests', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * DC 요청 처리 (관리자용)
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
   * ESG-GOLD로 DC 교환
   * @param {number} esgGoldAmount - 교환할 ESG-GOLD 양
   * @returns {Promise} 교환 결과
   */
  exchangeEsgGoldToDC: async (esgGoldAmount) => {
    try {
      const response = await apiClient.post('/wallet/exchange', {
        esgGoldAmount,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

export default walletService;
