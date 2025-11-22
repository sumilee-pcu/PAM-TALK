/**
 * Marketplace Service
 * 마켓플레이스 관련 API 서비스
 */

import apiClient from './client';

const marketplaceService = {
  /**
   * 상품 목록 조회
   * @param {Object} params - 필터 옵션 (category, minPrice, maxPrice, inStock, search, page, limit)
   * @returns {Promise} 상품 목록
   */
  getProducts: async (params = {}) => {
    try {
      const response = await apiClient.get('/marketplace/products', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 상품 상세 조회
   * @param {string} productId - 상품 ID
   * @returns {Promise} 상품 상세 정보
   */
  getProductById: async (productId) => {
    try {
      const response = await apiClient.get(`/marketplace/products/${productId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 상품 등록 (농부용)
   * @param {Object} productData - 상품 정보
   * @returns {Promise} 등록 결과
   */
  createProduct: async (productData) => {
    try {
      const response = await apiClient.post('/marketplace/products', productData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 상품 수정 (농부용)
   * @param {string} productId - 상품 ID
   * @param {Object} updates - 수정할 정보
   * @returns {Promise} 수정 결과
   */
  updateProduct: async (productId, updates) => {
    try {
      const response = await apiClient.put(`/marketplace/products/${productId}`, updates);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 상품 삭제 (농부용)
   * @param {string} productId - 상품 ID
   * @returns {Promise} 삭제 결과
   */
  deleteProduct: async (productId) => {
    try {
      const response = await apiClient.delete(`/marketplace/products/${productId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 내 상품 목록 조회 (농부용)
   * @param {Object} params - 필터 옵션 (page, limit)
   * @returns {Promise} 상품 목록
   */
  getMyProducts: async (params = {}) => {
    try {
      const response = await apiClient.get('/marketplace/my-products', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 주문하기
   * @param {Object} orderData - 주문 정보 (items: [{productId, quantity}], shippingAddress, useDC)
   * @returns {Promise} 주문 결과
   */
  createOrder: async (orderData) => {
    try {
      const response = await apiClient.post('/marketplace/orders', orderData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 주문 목록 조회
   * @param {Object} params - 필터 옵션 (status, page, limit)
   * @returns {Promise} 주문 목록
   */
  getOrders: async (params = {}) => {
    try {
      const response = await apiClient.get('/marketplace/orders', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 주문 상세 조회
   * @param {string} orderId - 주문 ID
   * @returns {Promise} 주문 상세 정보
   */
  getOrderById: async (orderId) => {
    try {
      const response = await apiClient.get(`/marketplace/orders/${orderId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 주문 취소
   * @param {string} orderId - 주문 ID
   * @param {string} reason - 취소 사유
   * @returns {Promise} 취소 결과
   */
  cancelOrder: async (orderId, reason) => {
    try {
      const response = await apiClient.post(`/marketplace/orders/${orderId}/cancel`, {
        reason,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  /**
   * 카테고리 목록 조회
   * @returns {Promise} 카테고리 목록
   */
  getCategories: async () => {
    try {
      const response = await apiClient.get('/marketplace/categories');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

export default marketplaceService;
