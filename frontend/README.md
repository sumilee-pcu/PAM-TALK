# PAM 디지털 쿠폰 프론트엔드

알고랜드 블록체인 기반 디지털 쿠폰 시스템의 프론트엔드 컴포넌트

## 📁 파일 구조

```
frontend/
├── src/
│   ├── components/
│   │   ├── CouponButton.jsx        # 쿠폰 받기 버튼
│   │   ├── CouponButton.css
│   │   ├── OptInGuide.jsx         # Opt-in 안내 모달
│   │   └── OptInGuide.css
│   ├── App.jsx                    # 메인 앱
│   └── App.css
├── public/
│   └── index.html                 # HTML-only 버전
└── package.json
```

## 🚀 사용 방법

### 옵션 1: React 앱 (권장)

**설치:**
```bash
cd frontend
npm install
```

**개발 서버 실행:**
```bash
npm start
```

http://localhost:3000 에서 앱이 실행됩니다.

**프로덕션 빌드:**
```bash
npm run build
```

### 옵션 2: HTML 단일 파일 (간단)

`public/index.html` 파일을 웹 서버에서 바로 실행:

```bash
# Python 간이 서버
cd frontend/public
python -m http.server 8000
```

http://localhost:8000 에서 확인

## 🎨 컴포넌트 사용법

### CouponButton 컴포넌트

```jsx
import CouponButton from './components/CouponButton';

function MyPage() {
  return (
    <CouponButton
      userAddress="사용자_알고랜드_주소"
      amount={10000}  // 100.00 포인트
      apiUrl="http://localhost:5000"
      onSuccess={(data) => console.log('성공!', data)}
      onError={(error) => console.log('실패:', error)}
    />
  );
}
```

**Props:**
- `userAddress` (required): 사용자 알고랜드 주소
- `amount` (optional): 지급할 포인트 (기본값: 10000 = 100.00 PAMP)
- `apiUrl` (optional): API 서버 URL (기본값: http://localhost:5000)
- `onSuccess` (optional): 성공 시 콜백 함수
- `onError` (optional): 실패 시 콜백 함수

### OptInGuide 컴포넌트

```jsx
import OptInGuide from './components/OptInGuide';

function MyPage() {
  const [showGuide, setShowGuide] = useState(false);

  return (
    <>
      <button onClick={() => setShowGuide(true)}>
        설정 방법 보기
      </button>

      {showGuide && (
        <OptInGuide
          assetId={3330375002}
          onClose={() => setShowGuide(false)}
        />
      )}
    </>
  );
}
```

## 🔧 커스터마이징

### 스타일 변경

각 컴포넌트의 CSS 파일을 수정하여 스타일을 변경할 수 있습니다:

- `CouponButton.css` - 버튼 스타일
- `OptInGuide.css` - 모달 스타일
- `App.css` - 전체 앱 스타일

### API URL 변경

프로덕션 환경에서는 API URL을 변경해야 합니다:

```jsx
<CouponButton
  apiUrl="https://your-production-api.com"
  // ...
/>
```

또는 환경 변수 사용:

```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
```

## 📱 사용자 플로우

1. **지갑 준비**
   - 페라 월렛 설치
   - 계정 생성

2. **Asset Opt-in**
   - 페라 월렛에서 Asset ID: 3330375002 추가
   - 수수료: 0.001 ALGO

3. **쿠폰 받기**
   - 웹사이트에서 알고랜드 주소 입력
   - "쿠폰 받기" 버튼 클릭
   - 페라 월렛에서 즉시 확인 가능

## 🌐 배포

### Vercel 배포

```bash
npm install -g vercel
vercel
```

### Netlify 배포

```bash
npm run build
# build 폴더를 Netlify에 업로드
```

### GitHub Pages 배포

```bash
npm run build
# build 폴더 내용을 gh-pages 브랜치에 푸시
```

## 🔐 보안 고려사항

1. **HTTPS 사용**: 프로덕션에서는 반드시 HTTPS 사용
2. **API CORS 설정**: 백엔드에서 허용된 도메인만 접근 가능하도록 설정
3. **Rate Limiting**: API 호출 제한 설정

## 📝 예제

### 간단한 통합 예제

```jsx
import React, { useState } from 'react';
import CouponButton from './components/CouponButton';

function WelcomePage() {
  const [address, setAddress] = useState('');

  return (
    <div>
      <h1>신규 가입 축하 쿠폰!</h1>

      <input
        value={address}
        onChange={(e) => setAddress(e.target.value)}
        placeholder="알고랜드 주소"
      />

      <CouponButton
        userAddress={address}
        amount={50000}  // 500 포인트
        onSuccess={() => alert('가입 축하 쿠폰 받기 완료!')}
      />
    </div>
  );
}
```

## 🆘 문제 해결

### "Asset Opt-in이 필요합니다" 오류

→ 페라 월렛에서 Asset ID 3330375002를 추가하세요

### "주소가 유효하지 않습니다" 오류

→ 알고랜드 주소는 정확히 58자여야 합니다

### API 연결 실패

→ 백엔드 API 서버가 실행 중인지 확인하세요

## 🔗 링크

- Asset Explorer: https://algoexplorer.io/asset/3330375002
- Pera Wallet: https://perawallet.app
- Algorand Docs: https://developer.algorand.org
