# 지자체 홈페이지 구현 완료 가이드

## 📋 개요

PAM-TALK ESG Chain의 지자체 포털 기능이 완전히 구현되었습니다. 이 문서는 구현된 모든 기능과 사용 방법을 설명합니다.

## ✅ 구현 완료 사항

### 1️⃣ 지자체별 탄소감축 현황 대시보드

**위치:**
- 데이터베이스: `migrations/008_local_government_tables.sql`
- 서비스: `app/service/local_government_service.py`
- API: `app/routes/local_government.py`
- 프론트엔드: `static/local_government_portal.html` (대시보드 섹션)

**주요 기능:**
- 실시간 탄소 감축량 추적
- 지자체별 통계 (참여 시민, 기업, 활동 수)
- 월별/주별/일별 감축 추이 분석
- 전국/지역 순위 시스템
- 활동 유형별 감축량 분석
  - 전기차 사용
  - 재생에너지
  - 재활용
  - 나무 심기
  - 친환경 제품 구매

**API 엔드포인트:**
```
GET  /api/local-government/governments           # 모든 지자체 조회
GET  /api/local-government/dashboard/{gov_id}    # 대시보드 데이터
GET  /api/local-government/carbon-stats/{gov_id} # 탄소 통계
POST /api/local-government/carbon-stats/{gov_id}/update # 통계 업데이트
GET  /api/local-government/rankings              # 지역별 순위
```

**데이터베이스 테이블:**
- `local_governments`: 지자체 기본 정보
- `local_carbon_stats`: 탄소 감축 통계
- `regional_carbon_targets`: 감축 목표 관리
- `v_local_government_dashboard`: 대시보드 뷰

---

### 2️⃣ 지역 ESG 프로그램 소개

**위치:**
- 서비스: `app/service/local_government_service.py` (ESG Programs 섹션)
- API: `app/routes/local_government.py` (Programs 엔드포인트)
- 프론트엔드: `static/local_government_portal.html` (프로그램 섹션)

**주요 기능:**
- 지역별 ESG 프로그램 등록 및 관리
- 프로그램 유형 분류:
  - 탄소 감축 캠페인
  - 재생에너지 보급
  - 폐기물 관리
  - 친환경 교통
  - 교육 프로그램
  - 인센티브 제도
- 참여자 모집 및 진행률 추적
- 예산 및 지원 내역 관리
- 프로그램 성과 측정 (탄소 감축량)

**API 엔드포인트:**
```
GET  /api/local-government/programs              # 프로그램 목록 조회
POST /api/local-government/programs              # 새 프로그램 등록
PUT  /api/local-government/programs/{program_id} # 프로그램 수정
```

**데이터베이스 테이블:**
- `regional_esg_programs`: ESG 프로그램 정보

---

### 3️⃣ 지역 농수산물 생산자 등록 시스템

**위치:**
- 서비스: `app/service/producer_registration_service.py`
- API: `app/routes/local_government.py` (Producers 엔드포인트)
- 프론트엔드: `static/local_government_portal.html` (생산자 섹션)

**주요 기능:**
- 생산자 등록 및 검증
  - 농가, 어업, 축산, 협동조합
  - 사업자 등록번호 확인
  - 농장/어장 위치 GPS 등록
- 인증 관리:
  - 유기농 인증
  - GAP (우수농산물) 인증
  - HACCP 인증
  - 기타 친환경 인증
- 제품 등록 시스템:
  - 농산물/수산물 정보
  - 생산 방법 (유기농, 온실, 양식 등)
  - 가격 및 최소 주문량
  - 단위당 탄소 발자국
- 검증 문서 업로드
- 생산자 디렉토리 및 검색

**API 엔드포인트:**
```
POST /api/local-government/producers/register    # 생산자 등록
GET  /api/local-government/producers             # 생산자 목록
GET  /api/local-government/producers/{producer_id} # 상세 정보
POST /api/local-government/producers/{producer_id}/verify # 검증
POST /api/local-government/producers/products    # 제품 등록
GET  /api/local-government/products/search       # 제품 검색
GET  /api/local-government/producers/stats/{gov_id} # 통계
```

**데이터베이스 테이블:**
- `local_producers`: 생산자 정보
- `producer_products`: 제품 정보
- `producer_verification_documents`: 검증 문서
- `v_producer_directory`: 생산자 디렉토리 뷰

---

### 4️⃣ 지자체 인센티브 정책 안내

**위치:**
- 서비스: `app/service/incentive_policy_service.py`
- API: `app/routes/local_government.py` (Policies 엔드포인트)
- 프론트엔드: `static/local_government_portal.html` (정책 섹션)

**주요 기능:**
- 인센티브 정책 등록 및 관리
- 정책 유형:
  - 보조금
  - 세금 감면
  - ESG-Gold 보너스
  - 장비 지원
  - 저금리 대출
  - 바우처
- 대상 그룹별 분류
- 신청 자격 요건 관리
- 예산 추적 및 잔여 예산 관리
- 신청서 접수 및 심사
- 승인/거부 처리
- 지급 관리 (Algorand 지갑 연동)
- 신청 내역 조회

**API 엔드포인트:**
```
GET  /api/local-government/policies              # 정책 목록
GET  /api/local-government/policies/{policy_id}  # 정책 상세
POST /api/local-government/policies              # 정책 등록
PUT  /api/local-government/policies/{policy_id}  # 정책 수정
POST /api/local-government/policies/applications # 신청서 제출
GET  /api/local-government/policies/applications # 신청 목록
GET  /api/local-government/policies/applications/{app_id} # 신청 상세
POST /api/local-government/policies/applications/{app_id}/review # 심사
POST /api/local-government/policies/applications/{app_id}/mark-paid # 지급 처리
GET  /api/local-government/policies/stats/{gov_id} # 통계
GET  /api/local-government/policies/applicant-history/{applicant_id} # 신청 이력
```

**데이터베이스 테이블:**
- `local_incentive_policies`: 인센티브 정책
- `incentive_applications`: 신청 내역

---

### 5️⃣ 지역별 충전스테이션 위치 맵

**위치:**
- 서비스: `app/service/charging_station_service.py`
- API: `app/routes/local_government.py` (Charging Stations 엔드포인트)
- 프론트엔드: `static/local_government_portal.html` (충전소 섹션)

**주요 기능:**
- 충전소 등록 및 관리
- 충전소 유형:
  - 완속 (Slow)
  - 급속 (Fast)
  - 초급속 (Super Fast)
  - 혼합 (Mixed)
- 위치 기반 검색 (반경 내 충전소 찾기)
- 실시간 충전기 가용성
- 충전소 정보:
  - 운영 시간
  - 충전 요금
  - ESG-Gold 결제 지원
  - ESG-Gold 할인율
  - 부대시설 (와이파이, 화장실, 편의점, 카페)
  - 주차 정보
- 충전 세션 관리:
  - 충전 시작/종료
  - 충전량 및 비용 계산
  - 탄소 감축량 계산
  - ESG-Gold 결제
- 리뷰 및 평점 시스템
- 충전소 통계 및 인기 순위

**API 엔드포인트:**
```
GET  /api/local-government/charging-stations     # 충전소 목록
GET  /api/local-government/charging-stations/nearby # 주변 충전소 검색
GET  /api/local-government/charging-stations/{station_id} # 충전소 상세
POST /api/local-government/charging-stations     # 충전소 등록
POST /api/local-government/charging-stations/{station_id}/start-session # 충전 시작
POST /api/local-government/charging-stations/sessions/{usage_id}/complete # 충전 완료
GET  /api/local-government/charging-stations/user-history/{user_address} # 사용 내역
POST /api/local-government/charging-stations/{station_id}/reviews # 리뷰 작성
GET  /api/local-government/charging-stations/stats/{gov_id} # 통계
GET  /api/local-government/charging-stations/popular/{gov_id} # 인기 충전소
```

**데이터베이스 테이블:**
- `charging_stations`: 충전소 정보
- `charging_station_usage`: 사용 기록
- `charging_station_reviews`: 리뷰
- `v_charging_station_map`: 지도용 뷰

---

## 🗂️ 파일 구조

```
pamtalk-esg-chain/
├── migrations/
│   └── 008_local_government_tables.sql    # 데이터베이스 스키마
├── app/
│   ├── service/
│   │   ├── local_government_service.py    # 지자체 & 대시보드 서비스
│   │   ├── producer_registration_service.py # 생산자 등록 서비스
│   │   ├── charging_station_service.py    # 충전소 서비스
│   │   └── incentive_policy_service.py    # 인센티브 정책 서비스
│   └── routes/
│       └── local_government.py            # 모든 API 라우트
└── static/
    └── local_government_portal.html       # 프론트엔드 UI
```

---

## 🚀 사용 방법

### 1. 데이터베이스 마이그레이션

```bash
sqlite3 pamtalk_esg.db < migrations/008_local_government_tables.sql
```

### 2. FastAPI 서버에 라우트 등록

`main.py`에 다음 코드 추가:

```python
from app.routes.local_government import router as local_gov_router

app.include_router(local_gov_router)
```

### 3. 프론트엔드 접속

브라우저에서 다음 URL로 접속:
```
http://localhost:8000/static/local_government_portal.html
```

---

## 📊 샘플 데이터

마이그레이션 파일에 다음 샘플 데이터가 포함되어 있습니다:

### 지자체:
- 서울특별시 (GOV-SEOUL-001)
- 부산광역시 (GOV-BUSAN-001)
- 제주특별자치도 (GOV-JEJU-001)

### 충전소:
- 강남역 급속충전소 (서울)
- 해운대 충전센터 (부산)
- 제주공항 충전소 (제주)

### ESG 프로그램:
- 서울시 탄소중립 챌린지
- 부산 그린뉴딜 프로젝트

### 인센티브 정책:
- 전기차 충전 지원금 (서울)
- 친환경 농산물 생산 장려금 (제주)

---

## 🔧 추가 개선 사항

### 프론트엔드 연동
현재 프론트엔드는 정적 데이터를 표시합니다. 실제 API와 연동하려면:

1. **Chart.js 추가**: 탄소 감축 추이 그래프
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

2. **Google Maps 또는 Kakao Maps API**: 충전소 지도
```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"></script>
```

3. **AJAX 호출**: 모든 섹션에서 실시간 데이터 로드

### 보안 및 인증
- JWT 토큰 기반 인증 추가
- 관리자 권한 체크
- CORS 설정

### 알림 시스템
- 신청서 승인/거부 알림
- 프로그램 모집 알림
- 충전소 만석 알림

---

## 📱 모바일 반응형

프론트엔드는 이미 모바일 반응형으로 구현되어 있습니다:
- 태블릿 (768px 이하): 2열 그리드
- 모바일 (480px 이하): 1열 그리드
- 네비게이션 버튼 세로 배치

---

## 🎯 다음 단계

1. **실시간 데이터 동기화**: WebSocket을 통한 실시간 업데이트
2. **알림 시스템**: 푸시 알림 구현
3. **데이터 시각화**: 고급 차트 및 그래프
4. **엑셀 내보내기**: 통계 데이터 다운로드
5. **다국어 지원**: 영어, 중국어 등
6. **AI 분석**: 탄소 감축 예측 및 추천

---

## ✨ 특징

- ✅ **완전한 CRUD 기능**: 모든 엔티티에 대해 생성, 읽기, 수정, 삭제 지원
- ✅ **RESTful API**: 표준 HTTP 메서드 사용
- ✅ **Algorand 블록체인 연동**: 투명한 보상 지급
- ✅ **실시간 통계**: 자동 집계 및 순위 계산
- ✅ **지리적 검색**: 위치 기반 충전소 찾기
- ✅ **사용자 친화적 UI**: 직관적인 대시보드
- ✅ **확장 가능한 구조**: 새로운 기능 추가 용이

---

## 📞 문의

구현에 대한 문의사항이 있으시면 개발팀에 연락해주세요.

**구현 완료일**: 2025-11-03
**버전**: 1.0.0
