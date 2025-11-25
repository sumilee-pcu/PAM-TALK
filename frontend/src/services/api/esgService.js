/**
 * ESG Service
 * ESG 활동 관련 API 서비스
 */

import apiClient from './client';

const esgService = {
  /**
   * ESG 활동 제출
   * @param {Object} activityData - 활동 정보 (title, description, activityType, carbonReduction, proof)
   * @returns {Promise} 제출 결과
   */
  submitActivity: async (activityData) => {
    try {
      const response = await apiClient.post('/esg/activities', activityData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 내 ESG 활동 목록 조회
   * @param {Object} params - 필터 옵션 (status, activityType, page, limit)
   * @returns {Promise} 활동 목록
   */
  getMyActivities: async (params = {}) => {
    try {
      const response = await apiClient.get('/esg/activities', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * ESG 활동 상세 조회
   * @param {string} activityId - 활동 ID
   * @returns {Promise} 활동 상세 정보
   */
  getActivityById: async (activityId) => {
    try {
      const response = await apiClient.get(`/esg/activities/${activityId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * ESG 활동 통계 조회
   * @returns {Promise} 활동 통계
   */
  getActivityStats: async () => {
    try {
      const response = await apiClient.get('/esg/stats');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 활동 유형 목록 조회
   * @returns {Promise} 활동 유형 목록
   */
  getActivityTypes: async () => {
    try {
      const response = await apiClient.get('/esg/types');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 전역 ESG 통계 조회
   * @returns {Promise} 전역 통계
   */
  getGlobalStats: async () => {
    try {
      const response = await apiClient.get('/esg/global-stats');
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
      const response = await apiClient.get('/esg/pending', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

export default esgService;
