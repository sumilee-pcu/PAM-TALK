/**
 * Committee Service
 * 위원회 관련 API 서비스
 */

import apiClient from './client';

const committeeService = {
  /**
   * 대시보드 통계 조회
   * @returns {Promise} 위원회 대시보드 통계
   */
  getDashboard: async () => {
    try {
      const response = await apiClient.get('/committee/dashboard');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 검증 대기 중인 활동 목록 조회
   * @param {Object} params - 필터 옵션 (page, limit)
   * @returns {Promise} 활동 목록
   */
  getPendingActivities: async (params = {}) => {
    try {
      const response = await apiClient.get('/committee/pending-activities', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * ESG 활동 검증 (승인/거부)
   * @param {string} activityId - 활동 ID
   * @param {string} status - 검증 상태 (APPROVED, REJECTED)
   * @param {string} reviewComment - 검토 코멘트 (선택)
   * @returns {Promise} 검증 결과
   */
  verifyActivity: async (activityId, status, reviewComment = '') => {
    try {
      const response = await apiClient.post(`/committee/verify/${activityId}`, {
        status,
        reviewComment,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 탄소 저감 추적 통계
   * @returns {Promise} 탄소 저감 통계
   */
  getCarbonTracking: async () => {
    try {
      const response = await apiClient.get('/committee/carbon-tracking');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 위원회 활동 내역 조회
   * @param {Object} params - 필터 옵션 (startDate, endDate, page, limit)
   * @returns {Promise} 활동 내역
   */
  getActivityHistory: async (params = {}) => {
    try {
      const response = await apiClient.get('/committee/history', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 특정 활동 상세 조회 (검증용)
   * @param {string} activityId - 활동 ID
   * @returns {Promise} 활동 상세 정보
   */
  getActivityDetail: async (activityId) => {
    try {
      const response = await apiClient.get(`/esg/activities/${activityId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 일괄 검증
   * @param {Array} verifications - 검증 목록 [{activityId, status, reviewComment}]
   * @returns {Promise} 일괄 검증 결과
   */
  bulkVerify: async (verifications) => {
    try {
      const promises = verifications.map((v) =>
        committeeService.verifyActivity(v.activityId, v.status, v.reviewComment)
      );
      const results = await Promise.allSettled(promises);
      return results;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

export default committeeService;
