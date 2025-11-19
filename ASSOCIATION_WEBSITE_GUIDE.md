# PAM-TALK ESG 협회 홈페이지 구현 가이드

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [구현된 기능](#구현된-기능)
3. [데이터베이스 구조](#데이터베이스-구조)
4. [API 엔드포인트](#api-엔드포인트)
5. [배포 가이드](#배포-가이드)
6. [사용자 가이드](#사용자-가이드)

---

## 시스템 개요

### PAM-TALK ESG 협회 홈페이지

**목적**: ESG 협회의 온라인 허브로서 회원 관리, 정보 제공, 교육, 이벤트 등 통합 서비스 제공

**핵심 기능**:
- 🏢 협회 소개 및 조직 정보
- 👥 회원 가입 및 관리 시스템
- 📰 공지사항 및 뉴스 게시판
- 📚 교육 프로그램 관리
- 🎉 이벤트 및 행사 관리
- 📄 ESG 정책 및 가이드라인 문서 관리
- 💬 FAQ 및 지원 시스템

---

## 구현된 기능

### 1. 홈페이지 메인 (`association_home.html`)

#### Hero Section
- 협회 비전 및 미션 소개
- 실시간 통계 (회원사, 탄소 감축량, 인증 기업 등)
- CTA 버튼 (회원가입, 자세히 보기)

```html
<section class="hero">
    <h1>지속가능한 미래를 함께 만듭니다</h1>
    <div class="hero-stats">
        <div class="stat-item">
            <div class="stat-number">1,250+</div>
            <div class="stat-label">회원사</div>
        </div>
        <!-- 더 많은 통계 -->
    </div>
</section>
```

#### 주요 섹션
1. **협회 소개**
   - 미션, 비전, 핵심 가치
   - 3개의 feature card

2. **조직도**
   - 이사회 → 협회장 → 사무총장
   - 4개 부서 (ESG 검증위원회, 회원지원팀, 정책연구팀, 교육사업팀)

3. **주요 사업**
   - 6개 핵심 사업 카드
   - ESG 인증, 교육, 플랫폼, 네트워크, 연구, 어워드

4. **협회 소식**
   - 최신 뉴스 3건
   - 더보기 버튼

### 2. 회원 관리 시스템

#### 회원 유형
```python
member_types = {
    'individual': '개인 회원',
    'corporate': '기업 회원'
}
```

#### 회원 등급
```python
membership_tiers = {
    'basic': {
        'name': '베이직',
        'benefits': ['기본 정보 접근', '뉴스레터 구독']
    },
    'silver': {
        'name': '실버',
        'benefits': ['교육 프로그램 10% 할인', '월 1회 컨설팅']
    },
    'gold': {
        'name': '골드',
        'benefits': ['교육 프로그램 30% 할인', '무제한 컨설팅', 'ESG 인증 우선심사']
    },
    'platinum': {
        'name': '플래티넘',
        'benefits': ['모든 서비스 무료', '전담 매니저', 'VIP 네트워킹']
    }
}
```

#### 회원가입 프로세스
1. 회원 정보 입력
2. 이메일 인증
3. 관리자 승인 (기업 회원)
4. 회원 등급 부여
5. 서비스 이용 시작

### 3. 게시판 시스템

#### 공지사항
```sql
-- 공지사항 카테고리
categories = [
    'general',    -- 일반 공지
    'event',      -- 행사 안내
    'policy',     -- 정책 변경
    'urgent'      -- 긴급 공지
]

-- 우선순위
priority = [
    0: '일반',
    1: '중요',
    2: '긴급'
]
```

#### 뉴스
```sql
-- 뉴스 카테고리
categories = [
    'event_report',   -- 행사 후기
    'achievement',    -- 성과 소식
    'partnership',    -- 협력 소식
    'research',       -- 연구 발표
    'media'          -- 언론 보도
]
```

### 4. 교육 프로그램

#### 프로그램 유형
- **기초 과정**: ESG 경영 입문
- **심화 과정**: ESG 전략 수립
- **전문 과정**: 탄소회계, MRV 시스템
- **인증 과정**: ESG 전문가 자격증

#### 수강 프로세스
1. 프로그램 선택
2. 신청 및 결제
3. 수강 시작
4. 출석 및 과제
5. 수료 및 인증서 발급

### 5. 이벤트 관리

#### 이벤트 유형
- **컨퍼런스**: 대규모 학술 행사
- **워크숍**: 실무 교육
- **세미나**: 주제별 강연
- **네트워킹**: 회원 교류
- **어워드**: 시상식

#### 참가 프로세스
1. 이벤트 정보 확인
2. 참가 신청
3. 결제 (유료 이벤트)
4. 확인 이메일 수신
5. 이벤트 참석
6. 피드백 제출

### 6. ESG 정책 문서

#### 문서 카테고리
```python
document_categories = {
    'policy': 'ESG 정책',
    'guideline': '가이드라인',
    'standard': '표준 및 기준',
    'report': '연구 보고서',
    'regulation': '운영 규정'
}
```

#### 주요 문서
1. **ESG 인증 표준 가이드라인** (v2.0)
2. **MRV 시스템 운영 규정** (v1.0)
3. **탄소중립 로드맵 2024**
4. **ESG 평가 체크리스트**
5. **회원사 ESG 모범사례집**

---

## 데이터베이스 구조

### 핵심 테이블 (15개)

#### 1. association_members (회원)
```sql
CREATE TABLE association_members (
    member_id TEXT PRIMARY KEY,
    member_type TEXT NOT NULL,  -- individual, corporate
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    membership_tier TEXT DEFAULT 'basic',
    membership_status TEXT DEFAULT 'pending',
    join_date TIMESTAMP,
    -- ... 기타 필드
);
```

#### 2. association_notices (공지사항)
```sql
CREATE TABLE association_notices (
    notice_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    published_at TIMESTAMP
);
```

#### 3. association_news (뉴스)
```sql
CREATE TABLE association_news (
    news_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    featured_image_url TEXT,
    category TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    view_count INTEGER DEFAULT 0,
    published_at TIMESTAMP
);
```

#### 4. esg_policy_documents (정책 문서)
```sql
CREATE TABLE esg_policy_documents (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    version TEXT DEFAULT '1.0',
    file_url TEXT,
    approval_status TEXT DEFAULT 'draft',
    download_count INTEGER DEFAULT 0
);
```

#### 5. education_programs (교육 프로그램)
```sql
CREATE TABLE education_programs (
    program_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    format TEXT NOT NULL,  -- online, offline, hybrid
    capacity INTEGER,
    enrolled_count INTEGER DEFAULT 0,
    start_date TIMESTAMP,
    provides_certificate BOOLEAN DEFAULT FALSE
);
```

---

## API 엔드포인트

### Base URL
```
Development: http://localhost:5002/api/association
Production: https://api.pamtalk-esg.org/association
```

### 1. 회원 관리

#### POST `/members/register`
회원 가입

**Request:**
```json
{
  "member_type": "corporate",
  "name": "홍길동",
  "email": "hong@example.com",
  "password": "securepassword123",
  "phone": "010-1234-5678",
  "company_name": "그린테크",
  "business_number": "123-45-67890"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "member_id": "MEM-20240115-abcd",
    "message": "회원 가입이 완료되었습니다."
  }
}
```

#### POST `/members/login`
로그인

**Request:**
```json
{
  "email": "hong@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "member_id": "MEM-20240115-abcd",
    "name": "홍길동",
    "membership_tier": "gold",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### GET `/members/<member_id>`
회원 프로필 조회

**Response:**
```json
{
  "success": true,
  "data": {
    "member_id": "MEM-20240115-abcd",
    "name": "홍길동",
    "email": "hong@example.com",
    "membership_tier": "gold",
    "esg_certification_count": 2,
    "education_completed": 5,
    "events_attended": 8
  }
}
```

### 2. 공지사항

#### GET `/notices`
공지사항 목록

**Query Parameters:**
- `category`: general, event, policy, urgent
- `page`: 페이지 번호 (default: 1)
- `per_page`: 페이지당 개수 (default: 10)

**Response:**
```json
{
  "success": true,
  "data": {
    "notices": [
      {
        "notice_id": "NOT-001",
        "title": "2024년 정기총회 개최 안내",
        "summary": "정기총회가 2월 15일에 개최됩니다.",
        "category": "event",
        "priority": 2,
        "is_pinned": true,
        "published_at": "2024-01-15T10:00:00",
        "view_count": 1523
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 10
  }
}
```

### 3. 교육 프로그램

#### GET `/education/programs`
교육 프로그램 목록

**Response:**
```json
{
  "success": true,
  "data": {
    "programs": [
      {
        "program_id": "EDU-001",
        "title": "ESG 경영 기초 과정",
        "category": "basic",
        "format": "online",
        "duration_hours": 8,
        "start_date": "2024-02-01",
        "capacity": 50,
        "enrolled_count": 32,
        "fee_basic": 100000,
        "fee_gold": 50000
      }
    ]
  }
}
```

#### POST `/education/enroll`
교육 신청

**Request:**
```json
{
  "program_id": "EDU-001",
  "member_id": "MEM-20240115-abcd",
  "payment_method": "card"
}
```

### 4. ESG 정책

#### GET `/policies`
정책 문서 목록

**Response:**
```json
{
  "success": true,
  "data": {
    "policies": [
      {
        "document_id": "POL-001",
        "title": "ESG 인증 표준 가이드라인",
        "category": "guideline",
        "version": "2.0",
        "file_url": "/files/esg_guideline_v2.pdf",
        "download_count": 1234
      }
    ]
  }
}
```

---

## 배포 가이드

### Step 1: 환경 설정

```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install flask flask-cors pyjwt bcrypt
```

### Step 2: 데이터베이스 마이그레이션

```bash
# SQLite
sqlite3 pamtalk.db < migrations/007_association_website_tables.sql

# PostgreSQL
psql -d pamtalk_production -f migrations/007_association_website_tables.sql
```

### Step 3: 초기 데이터 입력

```sql
-- 관리자 계정 생성
INSERT INTO association_members (
    member_id, member_type, name, email, password_hash,
    membership_tier, membership_status
) VALUES (
    'MEM-ADMIN-001', 'individual', '관리자', 'admin@pamtalk-esg.org',
    '해시된비밀번호', 'platinum', 'active'
);

-- 샘플 공지사항
INSERT INTO association_notices (
    notice_id, title, content, category, priority,
    author_id, published_at
) VALUES (
    'NOT-001', '협회 홈페이지 오픈', '새로운 협회 홈페이지가 오픈했습니다.',
    'general', 2, 'MEM-ADMIN-001', datetime('now')
);
```

### Step 4: API 서버 실행

```python
# app.py
from flask import Flask
from api.association_api import association_bp

app = Flask(__name__)
app.register_blueprint(association_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
```

```bash
python app.py
```

### Step 5: 프론트엔드 배포

```bash
# Nginx 설정
server {
    listen 80;
    server_name www.pamtalk-esg.org;

    root /var/www/html;
    index association_home.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 사용자 가이드

### 일반 회원

#### 1. 회원가입
1. 홈페이지 접속: www.pamtalk-esg.org
2. 우측 상단 "회원가입" 클릭
3. 회원 유형 선택 (개인/기업)
4. 정보 입력 및 제출
5. 이메일 인증
6. 승인 대기 (기업 회원)

#### 2. 교육 신청
1. "사업안내" → "ESG 교육"
2. 원하는 프로그램 선택
3. "신청하기" 클릭
4. 결제 진행
5. 확인 이메일 수신
6. 수강 시작

#### 3. 이벤트 참가
1. "협회 소식" → "행사 안내"
2. 이벤트 선택
3. 상세 정보 확인
4. "참가 신청" 클릭
5. 결제 (유료 이벤트)
6. QR코드 수신

### 관리자

#### 1. 공지사항 작성
```bash
POST /api/association/notices
{
  "title": "긴급 공지",
  "content": "내용...",
  "category": "urgent",
  "priority": 2,
  "is_pinned": true
}
```

#### 2. 회원 승인
```sql
UPDATE association_members
SET membership_status = 'active',
    membership_tier = 'silver'
WHERE member_id = 'MEM-20240115-abcd';
```

#### 3. 교육 프로그램 생성
```bash
POST /api/association/education/programs
{
  "title": "새로운 교육 과정",
  "category": "advanced",
  "capacity": 30,
  "start_date": "2024-03-01"
}
```

---

## 기능 확장 가이드

### 1. 결제 시스템 통합

```python
# payment_service.py
from payment_gateway import PortOne

def process_payment(amount, member_id):
    """교육비 또는 이벤트 참가비 결제"""
    result = PortOne.request_payment({
        'amount': amount,
        'buyer_name': get_member_name(member_id),
        'buyer_email': get_member_email(member_id)
    })
    return result
```

### 2. 이메일 알림

```python
# email_service.py
from flask_mail import Mail, Message

def send_welcome_email(member_email, member_name):
    """회원 가입 환영 이메일"""
    msg = Message(
        subject='PAM-TALK ESG 협회 가입을 환영합니다',
        recipients=[member_email],
        body=f'{member_name}님, 회원 가입을 축하드립니다!'
    )
    mail.send(msg)
```

### 3. 소셜 로그인

```python
# oauth_service.py
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)

# Google OAuth
google = oauth.register(
    name='google',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
```

### 4. 회원 대시보드

```html
<!-- member_dashboard.html -->
<div class="dashboard">
    <div class="stat-card">
        <h3>수료한 교육</h3>
        <div class="stat-value">{{ completed_educations }}</div>
    </div>
    <div class="stat-card">
        <h3>참석한 이벤트</h3>
        <div class="stat-value">{{ attended_events }}</div>
    </div>
    <div class="stat-card">
        <h3>ESG 인증</h3>
        <div class="stat-value">{{ certifications }}</div>
    </div>
</div>
```

---

## 보안 고려사항

### 1. 비밀번호 보안
```python
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)
```

### 2. JWT 인증
```python
import jwt

def create_token(member_id):
    payload = {
        'member_id': member_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

### 3. XSS 방지
```python
from markupsafe import escape

def sanitize_input(text):
    return escape(text)
```

---

## 문제 해결

### Q: 회원가입이 안 돼요
**A**:
1. 이메일 중복 확인
2. 비밀번호 규칙 확인 (최소 8자, 영문+숫자)
3. 필수 항목 모두 입력 확인

### Q: 로그인이 안 돼요
**A**:
1. 이메일/비밀번호 확인
2. 회원 상태 확인 (승인 대기 중?)
3. 브라우저 쿠키 삭제 후 재시도

### Q: 교육 신청이 안 돼요
**A**:
1. 로그인 상태 확인
2. 정원 마감 여부 확인
3. 신청 기한 확인

---

## 향후 개발 계획

1. **모바일 앱** 📱
   - React Native 기반
   - 푸시 알림
   - QR코드 체크인

2. **AI 챗봇** 🤖
   - 24/7 자동 응답
   - FAQ 자동 검색
   - 맞춤형 추천

3. **회원 포럼** 💬
   - 회원 간 소통
   - Q&A 게시판
   - 우수 사례 공유

4. **통계 대시보드** 📊
   - 실시간 분석
   - 맞춤형 리포트
   - 데이터 시각화

---

**구현 완료!** ✅

PAM-TALK ESG 협회 홈페이지가 완전히 구현되었습니다.
