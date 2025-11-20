# PAM-TALK Web Platform

블록체인 기반 탄소 감축 커뮤니티 **PAM-TALK** 의 최신 프론트엔드/서비스 구성입니다. 이 저장소에는 React 18 기반의 신규 사용자 포털(https://pam-talk.vercel.app)과 Algorand 연동을 위한 파이썬 백엔드 도구가 함께 보관되어 있습니다.

## 핵심 포인트
- **React 18 + Create React App** 으로 구축된 3-포털 UX (사용자 · 위원회 · 관리자)
- React Router 기반 SPA 라우팅, Lazy Loading, 전역 스타일 시스템, Auth Context 기본 제공
- Algorand 메인넷 연동을 위한 Python/Flask 도구(`api/`, `pamtalk_social_platform.py`) 포함
- `vercel.json` 으로 Vercel 빌드/라우트 자동화 → 모든 경로가 `index.html` 로 안전하게 포워딩
- 풍부한 문서(`FRONTEND_*.md`, `HOMEPAGE_COMPLETE.md` 등)로 화면 기획/설계 내역 추적 가능

## 저장소 구조
```
PAM-TALK/
├─ frontend/                  # React 18 SPA (localhost:3000)
│  ├─ public/                 # index.html, manifest, 정적 자원
│  ├─ src/                    # pages/, layouts/, hooks/, styles/
│  └─ package.json            # CRA 스크립트(start/build/test)
├─ api/                       # Flask 기반 REST API 예제(선택 실행)
├─ contracts/, ai_models/,…   # Algorand + ESG 업무 자동화 스크립트
├─ static/                    # 기존 HTML 데모 (보존)
├─ vercel.json                # Vercel 빌드/라우팅 설정
└─ README.md                  # 현재 문서
```

## 프론트엔드 빠른 시작 (localhost:3000)
```bash
cd frontend
npm install
npm start
```
- CRA 기본 dev 서버가 `http://localhost:3000` 에서 실행됩니다.
- 코드 수정 시 HMR(Hot Module Replacement) 로 즉시 반영됩니다.
- `src/pages/user/Home` 이하에 신규 랜딩 페이지 섹션이 모두 포함되어 있습니다.

### 환경 변수 (선택)
필요 시 CRA 규칙에 따라 `REACT_APP_*` 값을 사용하세요.
```
# .env.local 예시 (frontend/.env.local)
REACT_APP_API_BASE_URL=https://api.pamtalk.dev
REACT_APP_SOCKET_URL=wss://ws.pamtalk.dev
```
현재는 Mock Auth 로직만 동작하므로 API 주소가 비어 있어도 UI 확인이 가능합니다.

## 백엔드 / 블록체인 도구 실행 (옵션)
React 앱은 정적 자원이지만, Algorand 연동을 시험하려면 아래 스크립트를 활용하세요.
```bash
pip install -r requirements.txt
python pamtalk_social_platform.py  # 기본 Flask API
```
필요 시 `config.py` 와 `.env` 에 Algorand 노드/토큰 정보를 넣습니다. 추가 가이드: `COMPLETE_SYSTEM_GUIDE.md`, `PERA_WALLET_TOKEN_CREATION_GUIDE.md` 등.

## 빌드 & 배포 (Vercel)
1. **빌드**
   ```bash
   cd frontend
   npm run build
   ```
2. **Vercel 로그인/프로젝트 연결**
   ```bash
   npm install -g vercel
   vercel login
   ```
3. **배포**
   ```bash
   # 루트(PAM-TALK)에서 실행하면 vercel.json 이 frontend/package.json 을 자동 인식
   vercel --prod
   ```
   - `vercel.json` 이 `@vercel/static-build` 를 이용해 `frontend` 를 빌드합니다.
   - `routes` 설정으로 모든 SPA 경로(`/committee/*`, `/admin/*` 등)가 `index.html` 로 포워딩되어 404 없이 작동합니다.
   - 한 번 연결하면 이후 `vercel --prod` 만으로 https://pam-talk.vercel.app 를 갱신할 수 있습니다.

## 품질 점검 체크리스트
- `npm run build` : 프로덕션 번들 생성 (빌드 에러 확인)
- `npm test` : CRA 기본 테스트 러너
- `npx serve -s build` : 실제 배포와 동일한 정적 파일을 로컬에서 검수
- Git 저장 시 `frontend/node_modules` 와 `frontend/build` 는 `.gitignore` 로 제외됨을 확인하세요.

## GitHub 반영 흐름 예시
```bash
git add frontend vercel.json README.md .gitignore
git commit -m "feat: add React portal and Vercel config"
git push origin main  # 또는 master
```
필요 시 `frontend/README.md`, `FRONTEND_ARCHITECTURE.md`, `HOMEPAGE_COMPLETE.md` 등을 함께 업데이트하면 기획/개발 기록을 한 번에 관리할 수 있습니다.

## 참고 문서
- `FRONTEND_ARCHITECTURE.md` : 페이지/레이아웃 IA
- `FRONTEND_DIRECTORY_STRUCTURE.md` : src 디렉터리 표준
- `FRONTEND_SETUP_COMPLETE.md` : 설치/설정 히스토리
- `HOMEPAGE_COMPLETE.md` : 랜딩 페이지 UX 카피/디자인 스펙
- `MAINNET_SETUP.md`, `PERA_WALLET_TOKEN_CREATION_GUIDE.md` : Algorand 운영 절차

---
필요한 다른 화면/기능(페이지, 컴포넌트, API 연동 등)이 있다면 `frontend/src` 하위에 바로 추가하고 `npm run build` → `vercel --prod` 순서로 배포하면 됩니다.
# Vercel deployment trigger
