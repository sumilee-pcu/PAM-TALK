/**
 * PAM-TALK 라우트 설정
 * 3-Portal 시스템 라우트 정의
 */

export const ROUTE_PATHS = {
  // ============ User Portal Routes ============
  USER: {
    // Home & Auth
    HOME: '/',
    LOGIN: '/login',
    SIGNUP: '/signup',
    FORGOT_PASSWORD: '/forgot-password',
    CONNECT_WALLET: '/connect-wallet',

    // Dashboard
    DASHBOARD: '/dashboard',

    // Wallet
    WALLET: '/wallet',
    WALLET_BALANCE: '/wallet/balance',
    WALLET_RECEIVE: '/wallet/receive',
    WALLET_SEND: '/wallet/send',
    WALLET_TRANSACTIONS: '/wallet/transactions',
    WALLET_SETUP: '/wallet/setup',

    // Activities
    ACTIVITIES: '/activities',
    ACTIVITIES_DISCOVER: '/activities/discover',
    ACTIVITIES_RECORD: '/activities/record',
    ACTIVITIES_VERIFY: '/activities/verify',
    ACTIVITIES_HISTORY: '/activities/history',

    // Coupons
    COUPONS: '/coupons',
    COUPONS_AVAILABLE: '/coupons/available',
    COUPONS_MY: '/coupons/my-coupons',
    COUPONS_REDEEM: '/coupons/redeem',
    COUPONS_EXCHANGE: '/coupons/exchange',

    // Community
    COMMUNITY: '/community',
    COMMUNITY_FEED: '/community/feed',
    COMMUNITY_CHALLENGES: '/community/challenges',
    COMMUNITY_LEADERBOARD: '/community/leaderboard',
    COMMUNITY_GROUPS: '/community/groups',

    // Marketplace
    MARKETPLACE: '/marketplace',
    MARKETPLACE_PRODUCTS: '/marketplace/products',
    MARKETPLACE_PARTNERS: '/marketplace/partners',
    MARKETPLACE_ORDERS: '/marketplace/orders',

    // Rewards
    REWARDS: '/rewards',
    REWARDS_EARN: '/rewards/earn',
    REWARDS_MISSIONS: '/rewards/missions',
    REWARDS_REFERRAL: '/rewards/referral',

    // Profile
    PROFILE: '/profile',
    PROFILE_OVERVIEW: '/profile/overview',
    PROFILE_EDIT: '/profile/edit',
    PROFILE_ACHIEVEMENTS: '/profile/achievements',
    PROFILE_IMPACT: '/profile/impact',

    // Settings
    SETTINGS: '/settings',
    SETTINGS_ACCOUNT: '/settings/account',
    SETTINGS_WALLET: '/settings/wallet',
    SETTINGS_NOTIFICATIONS: '/settings/notifications',
    SETTINGS_PRIVACY: '/settings/privacy',
  },

  // ============ Committee Portal Routes ============
  COMMITTEE: {
    // Base
    BASE: '/committee',
    LOGIN: '/committee/login',
    DASHBOARD: '/committee/dashboard',

    // Verification
    VERIFICATION: '/committee/verification',
    VERIFICATION_PENDING: '/committee/verification/pending',
    VERIFICATION_REVIEW: '/committee/verification/review/:id',
    VERIFICATION_HISTORY: '/committee/verification/history',
    VERIFICATION_CERTIFICATES: '/committee/verification/certificates',

    // Coupon Issuance
    COUPON_ISSUANCE: '/committee/coupon-issuance',
    COUPON_CREATE: '/committee/coupon-issuance/create',
    COUPON_APPROVE: '/committee/coupon-issuance/approve',
    COUPON_DISTRIBUTION: '/committee/coupon-issuance/distribution',
    COUPON_ANALYTICS: '/committee/coupon-issuance/analytics',

    // Reports
    REPORTS: '/committee/reports',
    REPORTS_DAILY: '/committee/reports/daily',
    REPORTS_WEEKLY: '/committee/reports/weekly',
    REPORTS_MONTHLY: '/committee/reports/monthly',
    REPORTS_CUSTOM: '/committee/reports/custom',

    // Members
    MEMBERS: '/committee/members',
    MEMBERS_PROFILE: '/committee/members/profile',
    MEMBERS_DIRECTORY: '/committee/members/directory',
    MEMBERS_PERFORMANCE: '/committee/members/performance',

    // Settings
    SETTINGS: '/committee/settings',
  },

  // ============ Admin Dashboard Routes ============
  ADMIN: {
    // Base
    BASE: '/admin',
    LOGIN: '/admin/login',
    DASHBOARD: '/admin/dashboard',

    // Blockchain
    BLOCKCHAIN: '/admin/blockchain',
    BLOCKCHAIN_ACCOUNTS: '/admin/blockchain/accounts',
    BLOCKCHAIN_TOKENS: '/admin/blockchain/tokens',
    BLOCKCHAIN_TRANSACTIONS: '/admin/blockchain/transactions',
    BLOCKCHAIN_NETWORK: '/admin/blockchain/network',

    // Users
    USERS: '/admin/users',
    USERS_LIST: '/admin/users/list',
    USERS_DETAIL: '/admin/users/detail/:id',
    USERS_ROLES: '/admin/users/roles',
    USERS_KYC: '/admin/users/kyc',

    // Committee Management
    COMMITTEE_MANAGEMENT: '/admin/committee-management',
    COMMITTEE_MEMBERS: '/admin/committee-management/members',
    COMMITTEE_WORKFLOWS: '/admin/committee-management/workflows',
    COMMITTEE_PERFORMANCE: '/admin/committee-management/performance',

    // Coupon System
    COUPON_SYSTEM: '/admin/coupon-system',
    COUPON_TEMPLATES: '/admin/coupon-system/templates',
    COUPON_CAMPAIGNS: '/admin/coupon-system/campaigns',
    COUPON_RULES: '/admin/coupon-system/distribution-rules',
    COUPON_REDEMPTION: '/admin/coupon-system/redemption',

    // Analytics
    ANALYTICS: '/admin/analytics',
    ANALYTICS_OVERVIEW: '/admin/analytics/overview',
    ANALYTICS_CARBON: '/admin/analytics/carbon',
    ANALYTICS_TOKEN_ECONOMY: '/admin/analytics/token-economy',
    ANALYTICS_REPORTS: '/admin/analytics/reports',

    // System
    SYSTEM: '/admin/system',
    SYSTEM_CONFIGURATION: '/admin/system/configuration',
    SYSTEM_DATABASE: '/admin/system/database',
    SYSTEM_LOGS: '/admin/system/logs',
    SYSTEM_MONITORING: '/admin/system/monitoring',

    // Support
    SUPPORT: '/admin/support',
    SUPPORT_TICKETS: '/admin/support/tickets',
    SUPPORT_FAQ: '/admin/support/faq-management',
    SUPPORT_ANNOUNCEMENTS: '/admin/support/announcements',
  },
};

// 역할별 접근 권한 매핑
export const ROLE_ACCESS = {
  user: [
    ROUTE_PATHS.USER.HOME,
    '/dashboard',
    '/wallet/*',
    '/activities/*',
    '/coupons/*',
    '/community/*',
    '/marketplace/*',
    '/rewards/*',
    '/profile/*',
    '/settings/*',
  ],
  committee: [
    ...ROUTE_PATHS.USER, // 위원회는 사용자 포털도 접근 가능
    '/committee/*',
  ],
  admin: [
    '*', // 관리자는 모든 페이지 접근 가능
  ],
};

// 공개 라우트 (인증 불필요)
export const PUBLIC_ROUTES = [
  ROUTE_PATHS.USER.HOME,
  ROUTE_PATHS.USER.LOGIN,
  ROUTE_PATHS.USER.SIGNUP,
  ROUTE_PATHS.USER.FORGOT_PASSWORD,
  ROUTE_PATHS.COMMITTEE.LOGIN,
  ROUTE_PATHS.ADMIN.LOGIN,
];

// 라우트 헬퍼 함수
export const getCommitteeReviewPath = (id) =>
  `/committee/verification/review/${id}`;

export const getUserDetailPath = (id) =>
  `/admin/users/detail/${id}`;

export const isPublicRoute = (path) =>
  PUBLIC_ROUTES.some(route => path === route || path.startsWith(route));

export const hasAccess = (role, path) => {
  const accessPaths = ROLE_ACCESS[role] || [];
  return accessPaths.some(allowedPath => {
    if (allowedPath === '*') return true;
    if (allowedPath.endsWith('/*')) {
      const basePath = allowedPath.slice(0, -2);
      return path.startsWith(basePath);
    }
    return path === allowedPath;
  });
};

export default ROUTE_PATHS;
