# PAM-TALK 프론트엔드 디렉토리 구조

## 📁 완전한 디렉토리 트리

```
frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   ├── manifest.json
│   ├── robots.txt
│   └── assets/
│       ├── images/
│       │   ├── logo.svg
│       │   ├── committee-badge.svg
│       │   └── admin-icon.svg
│       └── fonts/
│
├── src/
│   ├── index.js                    # 앱 진입점
│   ├── App.js                      # 루트 컴포넌트
│   ├── App.css
│   │
│   ├── config/                     # 설정 파일
│   │   ├── constants.js            # 상수 정의
│   │   ├── api.config.js           # API 엔드포인트
│   │   ├── routes.config.js        # 라우트 정의
│   │   └── blockchain.config.js    # 블록체인 설정
│   │
│   ├── routes/                     # 라우팅 설정
│   │   ├── AppRouter.jsx           # 메인 라우터
│   │   ├── UserRoutes.jsx          # 사용자 라우트
│   │   ├── CommitteeRoutes.jsx     # 위원회 라우트
│   │   ├── AdminRoutes.jsx         # 관리자 라우트
│   │   └── ProtectedRoute.jsx      # 보호된 라우트
│   │
│   ├── layouts/                    # 레이아웃 컴포넌트
│   │   ├── UserLayout.jsx          # 사용자 레이아웃
│   │   │   ├── UserHeader.jsx
│   │   │   ├── UserSidebar.jsx
│   │   │   ├── UserFooter.jsx
│   │   │   └── UserLayout.css
│   │   │
│   │   ├── CommitteeLayout.jsx     # 위원회 레이아웃
│   │   │   ├── CommitteeHeader.jsx
│   │   │   ├── CommitteeSidebar.jsx
│   │   │   └── CommitteeLayout.css
│   │   │
│   │   └── AdminLayout.jsx         # 관리자 레이아웃
│   │       ├── AdminHeader.jsx
│   │       ├── AdminSidebar.jsx
│   │       └── AdminLayout.css
│   │
│   ├── pages/                      # 페이지 컴포넌트
│   │   │
│   │   ├── user/                   # 👥 사용자 페이지
│   │   │   ├── Home/
│   │   │   │   ├── HomePage.jsx
│   │   │   │   ├── HeroSection.jsx
│   │   │   │   ├── FeaturesSection.jsx
│   │   │   │   ├── StatsSection.jsx
│   │   │   │   └── HomePage.css
│   │   │   │
│   │   │   ├── Auth/
│   │   │   │   ├── LoginPage.jsx
│   │   │   │   ├── SignupPage.jsx
│   │   │   │   ├── ForgotPasswordPage.jsx
│   │   │   │   ├── ConnectWalletPage.jsx
│   │   │   │   └── Auth.css
│   │   │   │
│   │   │   ├── Dashboard/
│   │   │   │   ├── UserDashboard.jsx
│   │   │   │   ├── PointsWidget.jsx
│   │   │   │   ├── CarbonWidget.jsx
│   │   │   │   ├── RecentActivities.jsx
│   │   │   │   └── Dashboard.css
│   │   │   │
│   │   │   ├── Wallet/
│   │   │   │   ├── WalletPage.jsx
│   │   │   │   ├── BalancePage.jsx
│   │   │   │   ├── ReceivePage.jsx
│   │   │   │   ├── SendPage.jsx
│   │   │   │   ├── TransactionsPage.jsx
│   │   │   │   ├── SetupPage.jsx
│   │   │   │   └── Wallet.css
│   │   │   │
│   │   │   ├── Activities/
│   │   │   │   ├── ActivitiesPage.jsx
│   │   │   │   ├── DiscoverPage.jsx
│   │   │   │   ├── RecordPage.jsx
│   │   │   │   ├── VerifyPage.jsx
│   │   │   │   ├── HistoryPage.jsx
│   │   │   │   └── Activities.css
│   │   │   │
│   │   │   ├── Coupons/
│   │   │   │   ├── CouponsPage.jsx
│   │   │   │   ├── AvailableCoupons.jsx
│   │   │   │   ├── MyCoupons.jsx
│   │   │   │   ├── RedeemCoupon.jsx
│   │   │   │   ├── ExchangePage.jsx
│   │   │   │   └── Coupons.css
│   │   │   │
│   │   │   ├── Community/
│   │   │   │   ├── CommunityPage.jsx
│   │   │   │   ├── FeedPage.jsx
│   │   │   │   ├── ChallengesPage.jsx
│   │   │   │   ├── LeaderboardPage.jsx
│   │   │   │   ├── GroupsPage.jsx
│   │   │   │   └── Community.css
│   │   │   │
│   │   │   ├── Marketplace/
│   │   │   │   ├── MarketplacePage.jsx
│   │   │   │   ├── ProductsPage.jsx
│   │   │   │   ├── PartnersPage.jsx
│   │   │   │   ├── OrdersPage.jsx
│   │   │   │   └── Marketplace.css
│   │   │   │
│   │   │   ├── Rewards/
│   │   │   │   ├── RewardsPage.jsx
│   │   │   │   ├── EarnPage.jsx
│   │   │   │   ├── MissionsPage.jsx
│   │   │   │   ├── ReferralPage.jsx
│   │   │   │   └── Rewards.css
│   │   │   │
│   │   │   ├── Profile/
│   │   │   │   ├── ProfilePage.jsx
│   │   │   │   ├── OverviewPage.jsx
│   │   │   │   ├── EditProfilePage.jsx
│   │   │   │   ├── AchievementsPage.jsx
│   │   │   │   ├── ImpactPage.jsx
│   │   │   │   └── Profile.css
│   │   │   │
│   │   │   └── Settings/
│   │   │       ├── SettingsPage.jsx
│   │   │       ├── AccountSettings.jsx
│   │   │       ├── WalletSettings.jsx
│   │   │       ├── NotificationSettings.jsx
│   │   │       ├── PrivacySettings.jsx
│   │   │       └── Settings.css
│   │   │
│   │   ├── committee/              # 👔 위원회 페이지
│   │   │   ├── Login/
│   │   │   │   ├── CommitteeLoginPage.jsx
│   │   │   │   └── TwoFactorAuth.jsx
│   │   │   │
│   │   │   ├── Dashboard/
│   │   │   │   ├── CommitteeDashboard.jsx
│   │   │   │   ├── PendingVerifications.jsx
│   │   │   │   ├── MyStats.jsx
│   │   │   │   └── Dashboard.css
│   │   │   │
│   │   │   ├── Verification/
│   │   │   │   ├── VerificationPage.jsx
│   │   │   │   ├── PendingList.jsx
│   │   │   │   ├── ReviewDetail.jsx
│   │   │   │   │   ├── MeasurementData.jsx
│   │   │   │   │   ├── EvidenceViewer.jsx
│   │   │   │   │   ├── ConfidenceScore.jsx
│   │   │   │   │   └── ReviewForm.jsx
│   │   │   │   ├── HistoryPage.jsx
│   │   │   │   ├── CertificatesPage.jsx
│   │   │   │   └── Verification.css
│   │   │   │
│   │   │   ├── CouponIssuance/
│   │   │   │   ├── CouponIssuancePage.jsx
│   │   │   │   ├── CreateCoupon.jsx
│   │   │   │   ├── ApproveCoupon.jsx
│   │   │   │   ├── DistributionPage.jsx
│   │   │   │   ├── AnalyticsPage.jsx
│   │   │   │   └── CouponIssuance.css
│   │   │   │
│   │   │   ├── Reports/
│   │   │   │   ├── ReportsPage.jsx
│   │   │   │   ├── DailyReport.jsx
│   │   │   │   ├── WeeklyReport.jsx
│   │   │   │   ├── MonthlyReport.jsx
│   │   │   │   ├── CustomReport.jsx
│   │   │   │   └── Reports.css
│   │   │   │
│   │   │   └── Members/
│   │   │       ├── MembersPage.jsx
│   │   │       ├── ProfilePage.jsx
│   │   │       ├── DirectoryPage.jsx
│   │   │       ├── PerformancePage.jsx
│   │   │       └── Members.css
│   │   │
│   │   └── admin/                  # 🛠️ 관리자 페이지
│   │       ├── Login/
│   │       │   ├── AdminLoginPage.jsx
│   │       │   └── IPVerification.jsx
│   │       │
│   │       ├── Dashboard/
│   │       │   ├── AdminDashboard.jsx
│   │       │   ├── SystemStatus.jsx
│   │       │   ├── RealTimeStats.jsx
│   │       │   ├── ActivityLogs.jsx
│   │       │   └── Dashboard.css
│   │       │
│   │       ├── Blockchain/
│   │       │   ├── BlockchainPage.jsx
│   │       │   ├── Accounts/
│   │       │   │   ├── AccountsPage.jsx
│   │       │   │   ├── MasterAccount.jsx
│   │       │   │   └── BalanceMonitor.jsx
│   │       │   ├── Tokens/
│   │       │   │   ├── TokensPage.jsx
│   │       │   │   ├── TokenDetail.jsx
│   │       │   │   └── TokenManagement.jsx
│   │       │   ├── Transactions/
│   │       │   │   ├── TransactionsPage.jsx
│   │       │   │   ├── TxMonitor.jsx
│   │       │   │   └── FailedTx.jsx
│   │       │   └── Network/
│   │       │       ├── NetworkPage.jsx
│   │       │       └── NetworkStatus.jsx
│   │       │
│   │       ├── Users/
│   │       │   ├── UsersPage.jsx
│   │       │   ├── UserList.jsx
│   │       │   ├── UserDetail.jsx
│   │       │   ├── RolesPage.jsx
│   │       │   ├── KYCPage.jsx
│   │       │   └── Users.css
│   │       │
│   │       ├── Committee/
│   │       │   ├── CommitteeManagement.jsx
│   │       │   ├── MembersManagement.jsx
│   │       │   ├── WorkflowsPage.jsx
│   │       │   ├── PerformancePage.jsx
│   │       │   └── Committee.css
│   │       │
│   │       ├── CouponSystem/
│   │       │   ├── CouponSystemPage.jsx
│   │       │   ├── Templates.jsx
│   │       │   ├── Campaigns.jsx
│   │       │   ├── DistributionRules.jsx
│   │       │   ├── Redemption.jsx
│   │       │   └── CouponSystem.css
│   │       │
│   │       ├── Analytics/
│   │       │   ├── AnalyticsPage.jsx
│   │       │   ├── Overview.jsx
│   │       │   ├── CarbonAnalytics.jsx
│   │       │   ├── TokenEconomy.jsx
│   │       │   ├── ReportsGenerator.jsx
│   │       │   └── Analytics.css
│   │       │
│   │       ├── System/
│   │       │   ├── SystemPage.jsx
│   │       │   ├── Configuration.jsx
│   │       │   ├── Database.jsx
│   │       │   ├── Logs.jsx
│   │       │   ├── Monitoring.jsx
│   │       │   └── System.css
│   │       │
│   │       └── Support/
│   │           ├── SupportPage.jsx
│   │           ├── Tickets.jsx
│   │           ├── FAQManagement.jsx
│   │           └── Support.css
│   │
│   ├── components/                 # 공통 컴포넌트
│   │   ├── common/                 # 범용 컴포넌트
│   │   │   ├── Button/
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── PrimaryButton.jsx
│   │   │   │   ├── SecondaryButton.jsx
│   │   │   │   └── Button.css
│   │   │   │
│   │   │   ├── Input/
│   │   │   │   ├── Input.jsx
│   │   │   │   ├── TextInput.jsx
│   │   │   │   ├── NumberInput.jsx
│   │   │   │   └── Input.css
│   │   │   │
│   │   │   ├── Card/
│   │   │   │   ├── Card.jsx
│   │   │   │   └── Card.css
│   │   │   │
│   │   │   ├── Modal/
│   │   │   │   ├── Modal.jsx
│   │   │   │   ├── ConfirmModal.jsx
│   │   │   │   └── Modal.css
│   │   │   │
│   │   │   ├── Table/
│   │   │   │   ├── Table.jsx
│   │   │   │   ├── DataTable.jsx
│   │   │   │   └── Table.css
│   │   │   │
│   │   │   ├── Loading/
│   │   │   │   ├── Spinner.jsx
│   │   │   │   ├── LoadingPage.jsx
│   │   │   │   └── Loading.css
│   │   │   │
│   │   │   ├── Alert/
│   │   │   │   ├── Alert.jsx
│   │   │   │   ├── Toast.jsx
│   │   │   │   └── Alert.css
│   │   │   │
│   │   │   └── Badge/
│   │   │       ├── Badge.jsx
│   │   │       └── Badge.css
│   │   │
│   │   ├── blockchain/             # 블록체인 관련 컴포넌트
│   │   │   ├── WalletConnect/
│   │   │   │   ├── WalletConnectButton.jsx
│   │   │   │   ├── WalletInfo.jsx
│   │   │   │   └── WalletConnect.css
│   │   │   │
│   │   │   ├── AssetOptIn/
│   │   │   │   ├── OptInGuide.jsx
│   │   │   │   ├── OptInButton.jsx
│   │   │   │   └── OptIn.css
│   │   │   │
│   │   │   ├── TokenDisplay/
│   │   │   │   ├── TokenBalance.jsx
│   │   │   │   ├── TokenInfo.jsx
│   │   │   │   └── TokenDisplay.css
│   │   │   │
│   │   │   └── TransactionStatus/
│   │   │       ├── TxStatus.jsx
│   │   │       ├── TxExplorer.jsx
│   │   │       └── TxStatus.css
│   │   │
│   │   ├── coupon/                 # 쿠폰 관련 컴포넌트
│   │   │   ├── CouponCard/
│   │   │   │   ├── CouponCard.jsx
│   │   │   │   └── CouponCard.css
│   │   │   │
│   │   │   ├── CouponButton/
│   │   │   │   ├── CouponButton.jsx
│   │   │   │   └── CouponButton.css
│   │   │   │
│   │   │   └── CouponCreator/
│   │   │       ├── CouponForm.jsx
│   │   │       ├── CouponPreview.jsx
│   │   │       └── CouponCreator.css
│   │   │
│   │   ├── verification/           # 검증 관련 컴포넌트
│   │   │   ├── EvidenceUpload/
│   │   │   │   ├── FileUploader.jsx
│   │   │   │   ├── ImageUploader.jsx
│   │   │   │   └── Upload.css
│   │   │   │
│   │   │   ├── VerificationCard/
│   │   │   │   ├── VerificationCard.jsx
│   │   │   │   └── VerificationCard.css
│   │   │   │
│   │   │   └── ConfidenceScore/
│   │   │       ├── ScoreDisplay.jsx
│   │   │       ├── ScoreBreakdown.jsx
│   │   │       └── Score.css
│   │   │
│   │   ├── charts/                 # 차트 컴포넌트
│   │   │   ├── LineChart.jsx
│   │   │   ├── BarChart.jsx
│   │   │   ├── PieChart.jsx
│   │   │   ├── AreaChart.jsx
│   │   │   └── Charts.css
│   │   │
│   │   └── navigation/             # 네비게이션 컴포넌트
│   │       ├── Navbar.jsx
│   │       ├── Sidebar.jsx
│   │       ├── Breadcrumb.jsx
│   │       ├── Tabs.jsx
│   │       └── Navigation.css
│   │
│   ├── services/                   # API 서비스
│   │   ├── api/
│   │   │   ├── apiClient.js        # Axios 인스턴스
│   │   │   ├── userApi.js          # 사용자 API
│   │   │   ├── committeeApi.js     # 위원회 API
│   │   │   ├── adminApi.js         # 관리자 API
│   │   │   ├── couponApi.js        # 쿠폰 API
│   │   │   ├── verificationApi.js  # 검증 API
│   │   │   └── blockchainApi.js    # 블록체인 API
│   │   │
│   │   ├── blockchain/
│   │   │   ├── algorand.service.js # Algorand 서비스
│   │   │   ├── wallet.service.js   # 지갑 서비스
│   │   │   └── transaction.service.js # 트랜잭션 서비스
│   │   │
│   │   └── auth/
│   │       ├── auth.service.js     # 인증 서비스
│   │       ├── token.service.js    # 토큰 관리
│   │       └── permission.service.js # 권한 관리
│   │
│   ├── hooks/                      # 커스텀 훅
│   │   ├── useAuth.js              # 인증 훅
│   │   ├── useWallet.js            # 지갑 훅
│   │   ├── useApi.js               # API 호출 훅
│   │   ├── useBlockchain.js        # 블록체인 훅
│   │   ├── useForm.js              # 폼 관리 훅
│   │   └── usePermission.js        # 권한 확인 훅
│   │
│   ├── store/                      # 상태 관리 (Redux/Context)
│   │   ├── index.js
│   │   ├── slices/
│   │   │   ├── authSlice.js
│   │   │   ├── walletSlice.js
│   │   │   ├── couponSlice.js
│   │   │   ├── userSlice.js
│   │   │   └── committeeSlice.js
│   │   └── store.js
│   │
│   ├── utils/                      # 유틸리티 함수
│   │   ├── format.js               # 포맷팅 (날짜, 숫자 등)
│   │   ├── validation.js           # 유효성 검사
│   │   ├── helpers.js              # 헬퍼 함수
│   │   ├── constants.js            # 상수
│   │   └── algorand.utils.js       # Algorand 유틸리티
│   │
│   ├── styles/                     # 전역 스타일
│   │   ├── variables.css           # CSS 변수
│   │   ├── global.css              # 전역 스타일
│   │   ├── themes/
│   │   │   ├── light.css           # 라이트 테마
│   │   │   └── dark.css            # 다크 테마
│   │   └── responsive.css          # 반응형
│   │
│   └── assets/                     # 정적 자산
│       ├── images/
│       ├── icons/
│       └── videos/
│
├── .env.example                    # 환경 변수 예제
├── .env.development                # 개발 환경
├── .env.production                 # 프로덕션 환경
├── .gitignore
├── package.json
├── package-lock.json
└── README.md
```

---

## 📝 주요 파일 설명

### 🔧 설정 파일

#### `src/config/constants.js`
```javascript
export const APP_CONFIG = {
  APP_NAME: 'PAM-TALK',
  VERSION: '1.0.0',
  ASSET_ID: 3330375002,
};

export const USER_ROLES = {
  USER: 'user',
  COMMITTEE: 'committee',
  ADMIN: 'admin',
};

export const ROUTE_PATHS = {
  USER_HOME: '/',
  COMMITTEE_DASHBOARD: '/committee/dashboard',
  ADMIN_DASHBOARD: '/admin/dashboard',
};
```

#### `src/config/api.config.js`
```javascript
export const API_ENDPOINTS = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',

  // User APIs
  USER: {
    PROFILE: '/api/user/profile',
    BALANCE: '/api/user/balance',
    ACTIVITIES: '/api/user/activities',
  },

  // Committee APIs
  COMMITTEE: {
    VERIFICATION_PENDING: '/api/committee/verification/pending',
    VERIFICATION_REVIEW: '/api/committee/verification/review',
    COUPON_CREATE: '/api/committee/coupon/create',
  },

  // Admin APIs
  ADMIN: {
    USERS: '/api/admin/users',
    BLOCKCHAIN: '/api/admin/blockchain',
    ANALYTICS: '/api/admin/analytics',
  },
};
```

---

## 🚀 라우팅 구조

### `src/routes/AppRouter.jsx`
```javascript
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import UserRoutes from './UserRoutes';
import CommitteeRoutes from './CommitteeRoutes';
import AdminRoutes from './AdminRoutes';
import ProtectedRoute from './ProtectedRoute';

function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/*" element={<UserRoutes />} />

        {/* Committee Routes - Protected */}
        <Route
          path="/committee/*"
          element={
            <ProtectedRoute role="committee">
              <CommitteeRoutes />
            </ProtectedRoute>
          }
        />

        {/* Admin Routes - Protected */}
        <Route
          path="/admin/*"
          element={
            <ProtectedRoute role="admin">
              <AdminRoutes />
            </ProtectedRoute>
          }
        />

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRouter;
```

---

## 🎨 스타일링 가이드

### CSS 변수 (`src/styles/variables.css`)
```css
:root {
  /* Colors - User Portal */
  --user-primary: #4CAF50;
  --user-secondary: #8BC34A;
  --user-accent: #CDDC39;

  /* Colors - Committee Portal */
  --committee-primary: #2196F3;
  --committee-secondary: #03A9F4;
  --committee-accent: #00BCD4;

  /* Colors - Admin Portal */
  --admin-primary: #9C27B0;
  --admin-secondary: #673AB7;
  --admin-accent: #3F51B5;

  /* Common Colors */
  --success: #4CAF50;
  --warning: #FF9800;
  --error: #F44336;
  --info: #2196F3;

  /* Typography */
  --font-family: 'Pretendard', -apple-system, sans-serif;
  --font-size-base: 16px;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Breakpoints */
  --mobile: 480px;
  --tablet: 768px;
  --desktop: 1024px;
  --wide: 1280px;
}
```

---

## 📦 패키지 의존성

### `package.json` (추가 필요)
```json
{
  "name": "pam-talk-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@reduxjs/toolkit": "^1.9.7",
    "react-redux": "^8.1.3",
    "axios": "^1.6.0",
    "@perawallet/connect": "^1.3.1",
    "algosdk": "^2.7.0",
    "recharts": "^2.10.0",
    "react-icons": "^4.12.0",
    "date-fns": "^2.30.0",
    "react-hook-form": "^7.48.0",
    "yup": "^1.3.0",
    "react-toastify": "^9.1.0",
    "classnames": "^2.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "tailwindcss": "^3.3.0",
    "eslint": "^8.54.0",
    "prettier": "^3.1.0"
  }
}
```

---

## 🔐 환경 변수 예제

### `.env.example`
```env
# API Configuration
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=development

# Algorand Configuration
REACT_APP_ALGORAND_NETWORK=mainnet
REACT_APP_ALGOD_URL=https://mainnet-api.algonode.cloud
REACT_APP_INDEXER_URL=https://mainnet-idx.algonode.cloud

# Token Configuration
REACT_APP_PAM_ASSET_ID=3330375002
REACT_APP_PAM_SYMBOL=PAMP

# Feature Flags
REACT_APP_ENABLE_DARK_MODE=true
REACT_APP_ENABLE_NOTIFICATIONS=true

# Analytics (Optional)
REACT_APP_GA_TRACKING_ID=
```

---

## 🛠️ 다음 단계

1. ✅ **디렉토리 구조 문서 완성**
2. ⏭️ **실제 디렉토리 생성**
3. ⏭️ **라우팅 파일 생성**
4. ⏭️ **기본 레이아웃 컴포넌트 생성**
5. ⏭️ **API 서비스 구현**
