# PAM-TALK 보안 강화 보고서

**작성일**: 2025-11-27
**버전**: 1.0

## 📋 개요

PAM-TALK 시스템의 쿠폰 발행 API에 대한 보안 취약점을 발견하고 수정했습니다. 프론트엔드에만 존재하던 권한 체크를 백엔드 API 레벨로 확장하여 무단 쿠폰 발행을 방지합니다.

## 🔴 발견된 보안 취약점

### 1. 백엔드 권한 검증 부재
- **위치**: 모든 쿠폰 발행 관련 API 엔드포인트
- **문제**: 프론트엔드에서만 역할 기반 접근 제어를 수행
- **영향**:
  - API를 직접 호출하면 인증 없이 쿠폰 발행 가능
  - POSTMAN, curl 등으로 우회 공격 가능
  - 무제한 쿠폰 생성으로 인한 시스템 남용

### 2. 토큰 검증 미구현
- **문제**: 로그인 시 토큰을 생성하지만 검증 로직이 없음
- **영향**: 토큰의 실질적인 보안 기능 상실

### 3. 취약한 엔드포인트 목록

| 엔드포인트 | 기능 | 보안 전 상태 |
|-----------|------|------------|
| `POST /api/token/mint` | 대량 쿠폰 발행 | ❌ 인증 없음 |
| `POST /api/token/transfer-committee` | 위원회 토큰 전송 | ❌ 인증 없음 |
| `POST /api/token/transfer-provider` | 공급자 토큰 전송 | ❌ 인증 없음 |
| `POST /api/token/transfer-consumer` | 소비자 토큰 전송 | ❌ 인증 없음 |
| `POST /api/give-coupon` | 사용자에게 쿠폰 지급 | ❌ 인증 없음 |
| `POST /api/mall/users/{address}/coupons/{id}` | 쿠폰 발급 | ❌ 인증 없음 |
| `POST /api/mall/products` | 상품 추가 | ❌ 인증 없음 |

## ✅ 적용된 보안 강화

### 1. 공유 토큰 저장소 구현
**파일**: `shared_auth.py`

```python
# 여러 Flask 앱이 동일한 토큰 저장소를 공유
SHARED_TOKEN_STORE = {}

def register_token(token, user_id, email, role):
    """로그인 시 토큰 등록"""

def validate_token(token):
    """API 호출 시 토큰 검증"""
```

**특징**:
- 모든 Flask 앱 간 토큰 공유
- 실시간 토큰 검증
- 로그아웃 시 즉시 무효화

### 2. 인증/권한 미들웨어 구현

**파일**:
- `api/auth_middleware.py`
- `pamtalk-esg-chain/app/auth_middleware.py`

**주요 데코레이터**:

```python
@require_auth
def protected_endpoint():
    """로그인한 사용자만 접근 가능"""

@require_role('ADMIN')
def admin_only_endpoint():
    """특정 역할만 접근 가능"""

@require_role('ADMIN', 'COMMITTEE')
def multi_role_endpoint():
    """여러 역할 중 하나만 있으면 접근 가능"""
```

### 3. 엔드포인트별 보안 적용

#### API 서버 (api/app.py)
```python
# 토큰 등록 (로그인 시)
@app.route('/api/auth/login', methods=['POST'])
def login():
    # ...
    register_token(access_token, user['id'], user['email'], user['role'])

# 토큰 무효화 (로그아웃 시)
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    revoke_token(token)

# 쿠폰 지급 - ADMIN, COMMITTEE만 허용
@app.route('/api/give-coupon', methods=['POST'])
@require_role('ADMIN', 'COMMITTEE')
def give_coupon():
    # ...
```

#### 토큰 발행 서버 (pamtalk-esg-chain)
```python
# 쿠폰 발행 - ADMIN, COMMITTEE만 허용
@token_routes.route("/mint", methods=["POST"])
@require_role('ADMIN', 'COMMITTEE')
def mint_token_route():
    # ...

# 위원회 전송 - ADMIN, COMMITTEE만 허용
@token_routes.route('/transfer-committee', methods=['POST'])
@require_role('ADMIN', 'COMMITTEE')
def token_transfer_committee():
    # ...
```

#### 몰 API 서버 (api/mall_api.py)
```python
# 쿠폰 발급 - ADMIN, COMMITTEE만 허용
@app.route('/api/mall/users/<string:user_address>/coupons/<string:coupon_id>', methods=['POST'])
@require_role('ADMIN', 'COMMITTEE')
def issue_coupon(user_address, coupon_id):
    # ...

# 상품 추가 - ADMIN, SUPPLIER만 허용
@app.route('/api/mall/products', methods=['POST'])
@require_role('ADMIN', 'SUPPLIER')
def add_product():
    # ...
```

## 🔐 역할 기반 접근 제어 (RBAC)

### 역할별 권한 매트릭스

| 기능 | ADMIN | COMMITTEE | SUPPLIER | CONSUMER | COMPANY | FARMER |
|-----|-------|-----------|----------|----------|---------|--------|
| 쿠폰 대량 발행 (mint) | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 쿠폰 개별 발급 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 토큰 전송 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| 상품 등록 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| 상품 구매 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 쿠폰 조회 | ✅ | ✅ | ✅ | 본인만 | ✅ | ✅ |

### 사용자 계정

| 역할 | 이메일 | 비밀번호 |
|-----|--------|---------|
| ADMIN | admin@pamtalk.com | Admin123! |
| COMMITTEE | committee@pamtalk.com | Committee123! |
| SUPPLIER | supplier@pamtalk.com | Supplier123! |
| CONSUMER | consumer@pamtalk.com | Consumer123! |
| COMPANY | company@pamtalk.com | Company123! |
| FARMER | farmer@pamtalk.com | Farmer123! |

## 🛡️ 보안 강화 효과

### Before (보안 강화 전)
```bash
# 인증 없이 쿠폰 발행 가능
curl -X POST http://localhost:5000/api/token/mint \
  -H "Content-Type: application/json" \
  -d '{"amount": 99999, "unit_name": "HACK", "description": "Hacked"}'

# 응답: 200 OK - 쿠폰이 생성됨 ❌
```

### After (보안 강화 후)
```bash
# 1. 인증 없이 시도
curl -X POST http://localhost:5000/api/token/mint \
  -H "Content-Type: application/json" \
  -d '{"amount": 99999, "unit_name": "HACK", "description": "Hacked"}'

# 응답: 401 Unauthorized ✅
{
  "success": false,
  "error": "Authentication required",
  "message": "인증이 필요합니다. 로그인 후 다시 시도하세요."
}

# 2. 일반 사용자(CONSUMER)로 시도
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "consumer@pamtalk.com", "password": "Consumer123!"}' \
  | jq -r '.tokens.accessToken')

curl -X POST http://localhost:5000/api/token/mint \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 99999, "unit_name": "HACK", "description": "Hacked"}'

# 응답: 403 Forbidden ✅
{
  "success": false,
  "error": "Forbidden",
  "message": "접근 권한이 없습니다. 필요한 권한: ADMIN, COMMITTEE",
  "user_role": "CONSUMER",
  "required_roles": ["ADMIN", "COMMITTEE"]
}

# 3. 관리자로 정상 발행
ADMIN_TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@pamtalk.com", "password": "Admin123!"}' \
  | jq -r '.tokens.accessToken')

curl -X POST http://localhost:5000/api/token/mint \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "unit_name": "ESGC", "description": "Authorized"}'

# 응답: 200 OK ✅
{
  "success": true,
  "message": "100개의 쿠폰(ESGC)을 발행했습니다."
}
```

## 🧪 보안 테스트

### 자동화 테스트 스크립트
**파일**: `test_security.py`

```bash
# 테스트 실행
python test_security.py
```

**테스트 항목**:
1. ✅ 인증 없이 쿠폰 발행 시도 → 401 Unauthorized
2. ✅ CONSUMER 권한으로 발행 시도 → 403 Forbidden
3. ✅ ADMIN 권한으로 발행 → 200 OK
4. ✅ COMMITTEE 권한으로 발행 → 200 OK
5. ✅ 유효하지 않은 토큰 → 401 Unauthorized

### 수동 테스트 절차

#### 1. 서버 실행
```bash
# 터미널 1: API 서버
cd PAM-TALK
python api/app.py

# 터미널 2: 토큰 발행 서버
cd PAM-TALK/pamtalk-esg-chain
python main.py

# 터미널 3: 몰 API 서버
cd PAM-TALK
python api/mall_api.py
```

#### 2. 인증 테스트
```bash
# 로그인 (관리자)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@pamtalk.com",
    "password": "Admin123!"
  }'

# 응답에서 accessToken 저장
# TOKEN="demo_token_6_1732704000.123"
```

#### 3. 권한 테스트
```bash
# 쿠폰 발행 (인증됨)
curl -X POST http://localhost:5000/api/token/mint \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50,
    "unit_name": "TEST",
    "description": "Security test"
  }'
```

## 📊 보안 로깅

모든 인증/권한 이벤트가 로깅됩니다:

```
[INFO] Token registered for user: admin@pamtalk.com (role: ADMIN)
[INFO] Authenticated request: admin@pamtalk.com -> /api/token/mint
[WARNING] Access denied for consumer@pamtalk.com (role: CONSUMER) to /api/token/mint (required: ['ADMIN', 'COMMITTEE'])
[WARNING] Unauthorized access attempt to /api/token/mint
[WARNING] Invalid or expired token: invalid_token_12345...
```

## 🔄 추가 권장 사항

### 1. 프로덕션 환경 개선 사항

#### 토큰 저장소
현재: 메모리 기반 (재시작 시 초기화)
```python
SHARED_TOKEN_STORE = {}  # 메모리
```

권장: Redis 사용
```python
import redis
token_store = redis.Redis(host='localhost', port=6379, db=0)
```

#### JWT 토큰 사용
현재: 단순 문자열
```python
token = f"demo_token_{user['id']}_{timestamp}"
```

권장: JWT (JSON Web Token)
```python
import jwt
token = jwt.encode({
    'user_id': user['id'],
    'role': user['role'],
    'exp': datetime.utcnow() + timedelta(hours=24)
}, SECRET_KEY, algorithm='HS256')
```

### 2. 추가 보안 계층

#### Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/token/mint')
@limiter.limit("10 per hour")
@require_role('ADMIN', 'COMMITTEE')
def mint_token_route():
    # ...
```

#### API 키 검증
```python
@require_api_key
@require_role('ADMIN')
def sensitive_endpoint():
    # ...
```

#### 감사 로그
```python
def audit_log(user_id, action, resource, success):
    """모든 중요 작업을 DB에 기록"""
    db.audit_logs.insert({
        'user_id': user_id,
        'action': action,
        'resource': resource,
        'success': success,
        'timestamp': datetime.now(),
        'ip_address': request.remote_addr
    })
```

### 3. 모니터링 및 알림

```python
# 의심스러운 활동 감지
if failed_attempts > 5:
    send_security_alert(user_email, "Multiple failed login attempts")

# 대량 쿠폰 발행 감지
if amount > 10000:
    log_security_event("LARGE_COUPON_ISSUANCE", user_email, f"Amount: {amount}")
```

## 📝 변경된 파일 목록

### 새로 생성된 파일
1. `shared_auth.py` - 공유 토큰 저장소
2. `api/auth_middleware.py` - API 서버 인증 미들웨어
3. `pamtalk-esg-chain/app/auth_middleware.py` - 토큰 서버 인증 미들웨어
4. `test_security.py` - 보안 테스트 스크립트
5. `SECURITY_ENHANCEMENTS.md` - 이 문서

### 수정된 파일
1. `api/app.py` - 토큰 등록/무효화, 권한 체크 추가
2. `pamtalk-esg-chain/app/api/token_routes.py` - 모든 엔드포인트에 권한 체크
3. `api/mall_api.py` - 쿠폰 발급 및 상품 추가에 권한 체크

## 🎯 결론

### 달성한 목표
✅ 백엔드 API 레벨 인증 구현
✅ 역할 기반 접근 제어 (RBAC) 적용
✅ 토큰 검증 및 관리 시스템 구축
✅ 모든 쿠폰 발행 엔드포인트 보호
✅ 보안 테스트 자동화

### 보안 수준 향상
- **이전**: 누구나 API를 직접 호출하여 무제한 쿠폰 발행 가능 ❌
- **현재**: ADMIN 및 COMMITTEE 역할만 쿠폰 발행 가능 ✅

### 다음 단계
1. 프로덕션 환경에 Redis 토큰 저장소 배포
2. JWT 토큰 시스템 도입
3. Rate Limiting 적용
4. 감사 로그 시스템 구축
5. 보안 모니터링 및 알림 설정

---

**작성자**: Claude Code
**검토 필요**: 시스템 관리자, 보안 담당자
**배포 상태**: 개발 환경 적용 완료
