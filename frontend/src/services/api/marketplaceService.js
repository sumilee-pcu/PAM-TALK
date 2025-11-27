/**
 * Marketplace Service
 * 마켓플레이스 관련 API 서비스
 */

const API_BASE_URL = 'https://web-production-1b6c.up.railway.app';

const marketplaceService = {
  /**
   * 상품 목록 조회
   * @param {Object} params - 필터 옵션 (category)
   * @returns {Promise} 상품 목록
   */
  getProducts: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.category) {
        queryParams.append('category', params.category);
      }

      const url = `${API_BASE_URL}/api/mall/products${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      const response = await fetch(url);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '상품 목록 조회 실패');
      }

      return result;
    } catch (error) {
      console.error('Get products error:', error);
      throw error;
    }
  },

  /**
   * 상품 상세 조회
   * @param {string} productId - 상품 ID
   * @returns {Promise} 상품 상세 정보
   */
  getProductById: async (productId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mall/products/${productId}`);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '상품 조회 실패');
      }

      return result;
    } catch (error) {
      console.error('Get product error:', error);
      throw error;
    }
  },

  /**
   * 상품 등록 (Admin)
   * @param {Object} productData - 상품 정보
   * @returns {Promise} 등록 결과
   */
  createProduct: async (productData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mall/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '상품 등록 실패');
      }

      return result;
    } catch (error) {
      console.error('Create product error:', error);
      throw error;
    }
  },

  /**
   * 상품 수정 (Admin)
   * @param {string} productId - 상품 ID
   * @param {Object} productData - 수정할 상품 정보
   * @returns {Promise} 수정 결과
   */
  updateProduct: async (productId, productData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mall/products/${productId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '상품 수정 실패');
      }

      return result;
    } catch (error) {
      console.error('Update product error:', error);
      throw error;
    }
  },

  /**
   * 상품 삭제 (Admin)
   * @param {string} productId - 상품 ID
   * @returns {Promise} 삭제 결과
   */
  deleteProduct: async (productId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mall/products/${productId}`, {
        method: 'DELETE'
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '상품 삭제 실패');
      }

      return result;
    } catch (error) {
      console.error('Delete product error:', error);
      throw error;
    }
  },

  /**
   * 주문하기
   * @param {Object} orderData - 주문 정보 (user_address, items: [{product_id, quantity}], coupon_id, payment_txid)
   * @returns {Promise} 주문 결과
   */
  createOrder: async (orderData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mall/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '주문 생성 실패');
      }

      return result;
    } catch (error) {
      console.error('Create order error:', error);
      throw error;
    }
  },

  /**
   * 사용자 주문 목록 조회
   * @param {string} userAddress - 사용자 주소
   * @returns {Promise} 주문 목록
   */
  getUserOrders: async (userAddress) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mall/users/${userAddress}/orders`);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '주문 목록 조회 실패');
      }

      return result;
    } catch (error) {
      console.error('Get user orders error:', error);
      throw error;
    }
  },

  /**
   * 주문 상세 조회
   * @param {string} orderId - 주문 ID
   * @returns {Promise} 주문 상세 정보
   */
  getOrderById: async (orderId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mall/orders/${orderId}`);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '주문 조회 실패');
      }

      return result;
    } catch (error) {
      console.error('Get order error:', error);
      throw error;
    }
  },

  /**
   * 사용자 쿠폰 목록 조회
   * @param {string} userAddress - 사용자 주소
   * @returns {Promise} 쿠폰 목록
   */
  getUserCoupons: async (userAddress) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mall/users/${userAddress}/coupons`);
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '쿠폰 목록 조회 실패');
      }

      return result;
    } catch (error) {
      console.error('Get user coupons error:', error);
      throw error;
    }
  },

  /**
   * 사용자 등록 (100DC 지급)
   * @param {string} userAddress - 사용자 주소
   * @returns {Promise} 등록 결과
   */
  registerUser: async (userAddress) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/mall/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_address: userAddress })
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error?.message || '사용자 등록 실패');
      }

      return result;
    } catch (error) {
      console.error('Register user error:', error);
      throw error;
    }
  },
};

export default marketplaceService;
