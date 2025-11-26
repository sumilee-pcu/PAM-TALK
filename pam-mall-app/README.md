# PAM MALL - 디지털 쿠폰 쇼핑몰

Algorand 블록체인 기반 농산물 쇼핑몰

## 기능

- 농산물 상품 (사과, 당근, 양파)
- 디지털 쿠폰 시스템
- 블록체인 기반 안전한 결제
- 다크모드 지원

## 시작하기

### 개발 서버 실행

```bash
npm install
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 엽니다.

### API 서버

백엔드 API 서버가 필요합니다:

```bash
cd ../PAM-TALK
python api/mall_api.py
```

### 환경 변수

`.env.local` 파일에서 API URL을 설정합니다:

```
NEXT_PUBLIC_API_URL=http://localhost:5001/api/mall
```

## 배포

Vercel을 사용한 배포:

```bash
vercel
```

## 기술 스택

- Next.js 14
- React 18
- TypeScript
- TailwindCSS
- Lucide Icons
