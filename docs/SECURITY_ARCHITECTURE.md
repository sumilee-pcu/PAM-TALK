# PAM-TALK 보안 아키텍처

## 1. 개요
PAM-TALK는 블록체인과 중앙 데이터베이스를 결합한 하이브리드 구조로,
투명성과 효율성을 동시에 달성합니다.

## 2. 보안 계층 구조

### 2.1 인증 계층 (Authentication Layer)
- **JWT 기반 토큰 인증**
  - Access Token (15분 유효)
  - Refresh Token (7일 유효)
  - HttpOnly 쿠키로 저장

- **다중 인증 방식**
  - 이메일/비밀번호
  - 소셜 로그인 (Google, Kakao)
  - Algorand 지갑 연동

### 2.2 권한 계층 (Authorization Layer)
- **역할 기반 접근 제어 (RBAC)**
  ```
  User Roles:
  - user: 일반 사용자 (마켓플레이스, ESG 활동)
  - committee: 위원회 (ESG 검증, 탄소 추적)
  - admin: 관리자 (DC 배포, 전체 관리)
  - government: 지자체 (지역 통계, 정책 관리)
  ```

- **Row Level Security (RLS)**
  - Supabase RLS로 데이터 레벨 권한 관리
  - 사용자는 자신의 데이터만 조회/수정
  - 위원회/관리자는 승인된 범위 내 접근

### 2.3 데이터 무결성 계층
- **블록체인 온체인 데이터**
  - DC(Digital Coupon) 거래 내역
  - ESG-GOLD 토큰 발행/소각
  - 주요 탄소 배출 인증 해시
  - 스마트 컨트랙트 실행 기록

- **오프체인 데이터 (DB)**
  - 사용자 프로필
  - ESG 활동 상세 정보
  - 이미지 및 첨부 파일
  - 임시 데이터 및 캐시

- **하이브리드 검증**
  ```
  1. ESG 활동 제출 → DB 저장 + 해시 생성
  2. 위원회 검증 → DB 업데이트
  3. 승인 시 → 블록체인에 해시 기록
  4. 토큰 발행 → 스마트 컨트랙트 실행
  ```

## 3. 데이터 흐름

### 3.1 ESG 활동 인증 플로우
```
[사용자]
  → ESG 활동 제출 (이미지 + 메타데이터)
  → DB 저장 + 블록체인 해시 생성
  → 대기 상태

[위원회]
  → 활동 검증 (AI + 수동)
  → 승인/거부 결정
  → DB 상태 업데이트

[블록체인]
  → 승인 시 해시 온체인 기록
  → ESG-GOLD 토큰 발행
  → 거래 내역 영구 보존
```

### 3.2 DC 배포 플로우
```
[관리자]
  → DC 배포 요청
  → 수신자 지갑 검증

[블록체인]
  → 스마트 컨트랙트 실행
  → DC 토큰 전송
  → 거래 해시 생성

[DB]
  → 거래 내역 기록
  → 사용자 잔액 업데이트
  → 알림 발송
```

## 4. 보안 기능

### 4.1 암호화
- **전송 중 암호화**: HTTPS/TLS 1.3
- **저장 시 암호화**: AES-256
- **비밀번호**: bcrypt (salt rounds: 12)
- **민감 정보**: 환경 변수로 관리

### 4.2 입력 검증
- **프론트엔드**: React Hook Form + Yup
- **백엔드**: Express Validator
- **SQL Injection 방지**: Parameterized Queries
- **XSS 방지**: DOMPurify, CSP 헤더

### 4.3 Rate Limiting
```javascript
// API 요청 제한
- 일반 API: 100 req/15min
- 인증 API: 5 req/15min
- 파일 업로드: 10 req/hour
```

### 4.4 감사 로그 (Audit Log)
```sql
-- 모든 중요 작업 기록
- 사용자 로그인/로그아웃
- 권한 변경
- DC 배포
- ESG 검증
- 블록체인 거래
```

## 5. 데이터베이스 보안

### 5.1 Supabase 보안 설정
```sql
-- Row Level Security 예시
CREATE POLICY "Users can view own profile"
ON profiles FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Committee can verify ESG activities"
ON esg_activities FOR UPDATE
USING (
  auth.jwt() ->> 'role' = 'committee'
  AND status = 'pending'
);
```

### 5.2 민감 데이터 관리
- **PII (개인식별정보)**: 암호화 저장
- **지갑 주소**: 앞 6자리 + ... + 뒤 4자리 표시
- **거래 내역**: 당사자만 조회 가능

## 6. 블록체인 보안

### 6.1 Algorand 네트워크
- **합의 알고리즘**: Pure Proof of Stake (PPoS)
- **트랜잭션 최종성**: 4.5초
- **네트워크**: TestNet (개발) / MainNet (운영)

### 6.2 스마트 컨트랙트
- **PyTeal 사용**: 안전한 컨트랙트 작성
- **멀티시그**: 주요 관리 작업은 다중 서명 필요
- **업그레이드 가능**: 프록시 패턴 적용

## 7. 모니터링 및 대응

### 7.1 실시간 모니터링
- **이상 거래 탐지**: 패턴 분석
- **무단 접근 시도**: IP 차단
- **성능 모니터링**: Response Time, Error Rate

### 7.2 사고 대응 프로세스
```
1. 탐지 → 2. 격리 → 3. 분석 → 4. 복구 → 5. 사후 검토
```

## 8. 컴플라이언스

### 8.1 개인정보보호
- **GDPR 준수**: 데이터 이동권, 삭제권
- **개인정보보호법**: 동의 절차, 암호화

### 8.2 블록체인 규제
- **가상자산법**: DC는 유틸리티 토큰
- **탄소배출권 거래법**: ESG-GOLD 인증 연계

## 9. 기술 스택

```
Frontend:
- React 18 + React Router
- JWT 토큰 관리
- Algorand SDK (algosdk)

Backend:
- Node.js + Express
- Supabase Client
- Algorand SDK

Database:
- Supabase (PostgreSQL)
- Row Level Security
- Real-time Subscriptions

Blockchain:
- Algorand TestNet/MainNet
- PyTeal Smart Contracts
- Algorand Indexer API
```

## 10. 향후 개선 계획

- [ ] 2FA (Two-Factor Authentication) 추가
- [ ] 생체 인증 (지문, 얼굴 인식)
- [ ] Zero-Knowledge Proof 도입
- [ ] 탈중앙화 신원 (DID) 연동
- [ ] 완전 감사 추적 (Full Audit Trail)
