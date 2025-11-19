# 🎉 PAM-TALK 프론트엔드 계층도 구성 완료!

## ✅ 완료된 작업

### 1. 📋 프론트엔드 아키텍처 문서
- **파일**: `FRONTEND_ARCHITECTURE.md`
- **내용**: 3-Portal 시스템 전체 페이지 계층도
  - 👥 User Portal (사용자 포털)
  - 👔 Committee Portal (위원회 포털)
  - 🛠️ Admin Dashboard (관리자 대시보드)

### 2. 📁 디렉토리 구조 설계
- **파일**: `FRONTEND_DIRECTORY_STRUCTURE.md`
- **내용**:
  - 완전한 디렉토리 트리
  - 설정 파일 예제
  - 패키지 의존성
  - 환경 변수 설정

### 3. 🎨 시각적 계층도
- **파일**: `FRONTEND_VISUAL_HIERARCHY.md`
- **내용**:
  - 시각적 다이어그램
  - 사용자 플로우
  - 데이터 흐름도
  - 와이어프레임

### 4. 🛤️ 라우팅 구조 생성
- **디렉토리**: `frontend/src/routes/`
- **파일들**:
  - `AppRouter.jsx` - 메인 라우터
  - `ProtectedRoute.jsx` - 권한 보호 라우트
  - `UserRoutes.jsx` - 사용자 포털 라우트
  - `CommitteeRoutes.jsx` - 위원회 포털 라우트
  - `AdminRoutes.jsx` - 관리자 대시보드 라우트

### 5. ⚙️ 설정 파일 생성
- **디렉토리**: `frontend/src/config/`
- **파일**:
  - `routes.config.js` - 모든 라우트 경로 정의

### 6. 🎣 기본 훅 생성
- **디렉토리**: `frontend/src/hooks/`
- **파일**:
  - `useAuth.js` - 인증 관리 훅

---

## 📊 3-Portal 시스템 구조

```
PAM-TALK Platform
├── 👥 User Portal (/)
│   ├── Home & Dashboard
│   ├── Wallet Management
│   ├── Activities & Verification
│   ├── Coupons & Rewards
│   ├── Community & Social
│   └── Profile & Settings
│
├── 👔 Committee Portal (/committee)
│   ├── MRV Verification
│   ├── Coupon Issuance
│   ├── Reports & Analytics
│   └── Member Management
│
└── 🛠️ Admin Dashboard (/admin)
    ├── Blockchain Management
    ├── User Management
    ├── Committee Management
    ├── Coupon System
    ├── Analytics & Reports
    └── System Configuration
```

---

## 🚀 다음 단계

### 즉시 진행 가능한 작업:

#### 1. 레이아웃 컴포넌트 생성
```bash
# 생성할 파일:
frontend/src/layouts/
├── UserLayout.jsx
├── CommitteeLayout.jsx
└── AdminLayout.jsx
```

**UserLayout.jsx 예시:**
```jsx
import React from 'react';
import { Outlet } from 'react-router-dom';
import UserHeader from './UserHeader';
import UserFooter from './UserFooter';

function UserLayout() {
  return (
    <div className="user-layout">
      <UserHeader />
      <main className="user-main">
        <Outlet />
      </main>
      <UserFooter />
    </div>
  );
}

export default UserLayout;
```

#### 2. 페이지 컴포넌트 생성

**우선순위 1 - User Portal:**
```bash
# 사용자 포털 핵심 페이지
frontend/src/pages/user/
├── Home/HomePage.jsx              # 랜딩 페이지
├── Auth/LoginPage.jsx             # 로그인
├── Dashboard/UserDashboard.jsx    # 사용자 대시보드
├── Wallet/WalletPage.jsx          # 지갑 관리
└── Coupons/CouponsPage.jsx        # 쿠폰 센터
```

**우선순위 2 - Committee Portal:**
```bash
# 위원회 포털 핵심 페이지
frontend/src/pages/committee/
├── Login/CommitteeLoginPage.jsx
├── Dashboard/CommitteeDashboard.jsx
├── Verification/VerificationPage.jsx
└── CouponIssuance/CouponIssuancePage.jsx
```

**우선순위 3 - Admin Dashboard:**
```bash
# 관리자 대시보드 핵심 페이지
frontend/src/pages/admin/
├── Login/AdminLoginPage.jsx
├── Dashboard/AdminDashboard.jsx
├── Blockchain/BlockchainPage.jsx
└── Users/UsersPage.jsx
```

#### 3. API 서비스 연결
```bash
# API 서비스 파일 생성
frontend/src/services/api/
├── apiClient.js        # Axios 기본 설정
├── userApi.js          # 사용자 API
├── committeeApi.js     # 위원회 API
├── adminApi.js         # 관리자 API
└── blockchainApi.js    # 블록체인 API
```

**apiClient.js 예시:**
```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (토큰 추가)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('pam_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (에러 처리)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 - 로그아웃
      localStorage.removeItem('pam_token');
      localStorage.removeItem('pam_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

#### 4. package.json 업데이트

필요한 패키지 설치:
```bash
cd frontend

# React Router
npm install react-router-dom

# 상태 관리
npm install @reduxjs/toolkit react-redux

# API 통신
npm install axios

# Algorand 관련
npm install algosdk @perawallet/connect

# UI/차트
npm install recharts react-icons

# 폼 관리
npm install react-hook-form yup

# 유틸리티
npm install date-fns classnames

# 알림
npm install react-toastify
```

#### 5. App.js 업데이트

```javascript
// frontend/src/App.js
import React from 'react';
import AppRouter from './routes/AppRouter';
import { AuthProvider } from './hooks/useAuth';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <AppRouter />
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </AuthProvider>
  );
}

export default App;
```

---

## 📝 구현 체크리스트

### Phase 1: 기본 구조 (현재 완료 ✅)
- [x] 프론트엔드 아키텍처 설계
- [x] 디렉토리 구조 생성
- [x] 라우팅 시스템 구축
- [x] 인증 시스템 기본 구조

### Phase 2: 레이아웃 & 공통 컴포넌트
- [ ] UserLayout 구현
- [ ] CommitteeLayout 구현
- [ ] AdminLayout 구현
- [ ] 공통 컴포넌트 (Button, Input, Card, Modal 등)
- [ ] 네비게이션 컴포넌트

### Phase 3: User Portal
- [ ] HomePage (랜딩)
- [ ] LoginPage / SignupPage
- [ ] UserDashboard
- [ ] WalletPage
- [ ] CouponsPage
- [ ] ActivitiesPage

### Phase 4: Committee Portal
- [ ] CommitteeLoginPage
- [ ] CommitteeDashboard
- [ ] VerificationPage
- [ ] CouponIssuancePage
- [ ] ReportsPage

### Phase 5: Admin Dashboard
- [ ] AdminLoginPage
- [ ] AdminDashboard
- [ ] BlockchainPage
- [ ] UsersPage
- [ ] AnalyticsPage

### Phase 6: API 연결
- [ ] API Client 설정
- [ ] User API 연결
- [ ] Committee API 연결
- [ ] Admin API 연결
- [ ] Blockchain API 연결

### Phase 7: 블록체인 통합
- [ ] Pera Wallet 연결
- [ ] Asset Opt-in 기능
- [ ] 토큰 전송 기능
- [ ] 트랜잭션 모니터링

### Phase 8: 테스트 & 배포
- [ ] 단위 테스트
- [ ] 통합 테스트
- [ ] 프로덕션 빌드
- [ ] 배포 (Vercel/Netlify)

---

## 🎨 스타일링 가이드

### CSS 변수 설정

**frontend/src/styles/variables.css:**
```css
:root {
  /* User Portal Colors */
  --user-primary: #4CAF50;
  --user-secondary: #8BC34A;

  /* Committee Portal Colors */
  --committee-primary: #2196F3;
  --committee-secondary: #03A9F4;

  /* Admin Portal Colors */
  --admin-primary: #9C27B0;
  --admin-secondary: #673AB7;

  /* Common Colors */
  --success: #4CAF50;
  --warning: #FF9800;
  --error: #F44336;
  --info: #2196F3;

  /* Typography */
  --font-family: 'Pretendard', -apple-system, sans-serif;
  --font-size-base: 16px;
  --font-size-sm: 14px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

---

## 🔧 개발 서버 실행

```bash
# 백엔드 API 서버 시작
cd algo/api
python app.py
# Running on http://localhost:5000

# 프론트엔드 개발 서버 시작 (새 터미널)
cd algo/frontend
npm install  # 최초 1회
npm start
# Running on http://localhost:3000
```

---

## 📚 참고 문서

1. **FRONTEND_ARCHITECTURE.md** - 전체 페이지 계층도
2. **FRONTEND_DIRECTORY_STRUCTURE.md** - 디렉토리 구조 상세
3. **FRONTEND_VISUAL_HIERARCHY.md** - 시각적 다이어그램
4. **COMPLETE_SYSTEM_GUIDE.md** - 전체 시스템 가이드
5. **MRV_COMMITTEE_IMPLEMENTATION_GUIDE.md** - MRV 위원회 구현 가이드

---

## 🎯 핵심 포인트

### 1. 3-Portal 분리
- **User Portal**: 일반 사용자용 (모바일 최적화)
- **Committee Portal**: ESG 위원회용 (검증 & 쿠폰 발행)
- **Admin Dashboard**: 시스템 관리자용 (데스크톱 최적화)

### 2. 역할 기반 접근 제어
- `ProtectedRoute` 컴포넌트로 권한 관리
- 각 포털별 독립적인 인증 플로우
- 역할별 다른 UI/UX

### 3. 확장 가능한 구조
- Lazy loading으로 성능 최적화
- 모듈화된 컴포넌트 구조
- 재사용 가능한 공통 컴포넌트

### 4. 블록체인 통합
- Algorand 네트워크 연결
- Pera Wallet 통합
- 실시간 트랜잭션 모니터링

---

## 🚀 빠른 시작 가이드

### Step 1: 프론트엔드 초기 설정
```bash
cd algo/frontend
npm install
```

### Step 2: 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# 환경 변수 편집
REACT_APP_API_URL=http://localhost:5000
REACT_APP_PAM_ASSET_ID=3330375002
```

### Step 3: 개발 서버 실행
```bash
npm start
```

### Step 4: 첫 페이지 구현
1. `HomePage.jsx` - 랜딩 페이지
2. `LoginPage.jsx` - 로그인
3. `UserDashboard.jsx` - 대시보드

---

## 💡 다음 작업 추천

1. **HomePage 구현** - 서비스 소개 랜딩 페이지
2. **LoginPage 구현** - 3-Portal 통합 로그인
3. **레이아웃 컴포넌트** - Header, Sidebar, Footer
4. **공통 컴포넌트** - Button, Card, Modal 등
5. **API 연결** - 백엔드 API 통합

---

## 🎉 축하합니다!

프론트엔드 계층도 구성이 완료되었습니다!

이제 실제 페이지 구현을 시작할 준비가 되었습니다. 🚀
