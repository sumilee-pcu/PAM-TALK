/**
 * API 설정
 */

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5002';
export const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:5002';

export const API_ENDPOINTS = {
  // 커뮤니티 API
  COMMUNITY: {
    USERS: '/api/community/users',
    POSTS: '/api/community/posts',
    COMMENTS: '/api/community/comments',
    LIKES: '/api/community/likes',
    CHAT_ROOMS: '/api/community/chat/rooms',
    REPORTS: '/api/community/reports',
    STATISTICS: '/api/community/statistics',
    HEALTH: '/api/community/health',
  },

  // 쇼핑몰 API
  MALL: {
    PRODUCTS: '/api/mall/products',
    COUPONS: '/api/mall/coupons',
    ORDERS: '/api/mall/orders',
    HEALTH: '/api/mall/health',
  }
};

export default {
  API_BASE_URL,
  WS_BASE_URL,
  API_ENDPOINTS,
};
