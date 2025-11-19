# ESG위원회 시스템 및 MRV 구현 가이드

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [구현된 컴포넌트](#구현된-컴포넌트)
3. [MRV 시스템](#mrv-시스템)
4. [위원회 검증 워크플로우](#위원회-검증-워크플로우)
5. [블록체인 검증 기록](#블록체인-검증-기록)
6. [배포 가이드](#배포-가이드)
7. [API 사용법](#api-사용법)

---

## 시스템 개요

### MRV (Measurement, Reporting, Verification) 시스템

**MRV란?**
- **M**easurement (측정): 탄소 감축 활동의 정확한 측정
- **R**eporting (보고): 감축량 자동 리포팅
- **V**erification (검증): ESG위원회의 3자 검증

### 핵심 기능

1. **자동 측정 시스템**
   - 탄소 감축량 자동 계산
   - 증빙 자료 수집 및 검증
   - 신뢰도 점수 산출 (0-100)

2. **리포팅 시스템**
   - 일일/주간/월간 리포트 자동 생성
   - JSON, CSV, PDF 형식 지원
   - 검증 요청 리포트

3. **검증 워크플로우**
   - 자동 승인 (신뢰도 95% 이상)
   - 위원회 배정 및 검토
   - 승인/반려/재제출 프로세스

4. **블록체인 기록**
   - Algorand 블록체인 저장
   - 위조 방지 해시 검증
   - NFT 인증서 발행

---

## 구현된 컴포넌트

### 1. MRV 측정 모듈
**파일**: `mrv_measurement_module.py`

```python
from mrv_measurement_module import MRVMeasurementModule, Evidence, EvidenceType

# 초기화
mrv_module = MRVMeasurementModule()

# 측정
measurement = mrv_module.measure_activity(
    activity=carbon_activity,
    measurement_method="manual_verified",
    evidences=[receipt, photo, gps_data],
    location={'lat': 37.5665, 'lng': 126.9780}
)

# 검증
is_valid, issues = mrv_module.validate_measurement(measurement)
```

**주요 기능**:
- ✅ 탄소 발자국 종합 계산
- ✅ 증빙 자료 관리
- ✅ 신뢰도 점수 계산
- ✅ 데이터 무결성 해시
- ✅ 일괄 측정 지원

### 2. 리포팅 서비스
**파일**: `mrv_reporting_service.py`

```python
from mrv_reporting_service import MRVReportingService, ReportType

reporting_service = MRVReportingService()

# 일일 리포트
daily_report = reporting_service.generate_daily_report(
    date="2024-01-15",
    user_id="user123"
)

# 월간 리포트
monthly_report = reporting_service.generate_monthly_report(
    year=2024,
    month=1
)

# 리포트 내보내기
json_data = reporting_service.export_report(daily_report, ReportFormat.JSON)
```

**리포트 유형**:
- 📊 일일 리포트 (daily)
- 📅 주간 리포트 (weekly)
- 📆 월간 리포트 (monthly)
- 📈 분기별 리포트 (quarterly)
- 📋 연간 리포트 (annual)
- 🔍 검증 요청 리포트 (verification_request)

### 3. 위원회 검증 워크플로우
**파일**: `committee_verification_workflow.py`

```python
from committee_verification_workflow import CommitteeVerificationWorkflow

workflow = CommitteeVerificationWorkflow()

# 검증 요청 제출
request = workflow.submit_for_verification(
    measurement=measurement,
    user_id="user123",
    priority=1  # 0: 일반, 1: 높음, 2: 긴급
)

# 검토자 배정
workflow.assign_to_reviewer(request.request_id, "committee001")

# 검증 수행
result = workflow.review_and_verify(
    request_id=request.request_id,
    reviewer_id="committee001",
    approved=True,
    comments="모든 증빙 확인 완료"
)
```

**워크플로우 단계**:
1. 📝 제출 (submit_for_verification)
2. 🔍 검토 중 (in_review)
3. ✅ 승인 (approved) / ❌ 반려 (rejected)
4. 🔄 재제출 요청 (resubmission_required)
5. ⬆️ 에스컬레이션 (escalated)

### 4. 블록체인 검증 서비스
**파일**: `blockchain_verification_service.py`

```python
from blockchain_verification_service import BlockchainVerificationService

blockchain_service = BlockchainVerificationService()

# 블록체인에 저장
result = blockchain_service.store_verification_on_chain(
    verification_result=verification_result,
    verifier_private_key="VERIFIER_PRIVATE_KEY"
)

# 조회
chain_data = blockchain_service.retrieve_verification_from_chain(result['tx_id'])

# 무결성 검증
is_valid, message = blockchain_service.verify_data_integrity(chain_data)

# NFT 인증서 발행
nft = blockchain_service.create_verification_certificate_nft(
    verification_result=verification_result,
    creator_private_key="CREATOR_PRIVATE_KEY"
)
```

---

## MRV 시스템

### 측정 프로세스

#### 1. 활동 데이터 수집
```python
activity = CarbonActivity(
    activity_type=ActivityType.LOCAL_FOOD_PURCHASE,
    user_id="user123",
    product_name="유기농 토마토",
    quantity=5.0,  # kg
    origin_region="경기도",
    destination_region="서울시",
    farming_method="organic",
    transport_method="truck_small",
    packaging_type="paper",
    activity_date="2024-01-15T14:30:00"
)
```

#### 2. 증빙 자료 첨부
```python
evidences = [
    Evidence(
        evidence_type=EvidenceType.RECEIPT,
        file_path="/uploads/receipt_20240115.jpg",
        description="구매 영수증"
    ),
    Evidence(
        evidence_type=EvidenceType.GPS,
        data={'lat': 37.5665, 'lng': 126.9780},
        description="거래 위치"
    ),
    Evidence(
        evidence_type=EvidenceType.PHOTO,
        file_path="/uploads/product_photo.jpg",
        description="제품 사진"
    )
]
```

#### 3. 측정 실행
```python
measurement = mrv_module.measure_activity(
    activity=activity,
    measurement_method="manual_verified",  # manual, automated, sensor
    evidences=evidences,
    location={'lat': 37.5665, 'lng': 126.9780}
)
```

#### 4. 결과 확인
```python
print(f"측정 ID: {measurement.measurement_id}")
print(f"탄소 절약: {measurement.carbon_savings_kg} kg CO₂")
print(f"DC 획득: {measurement.dc_units} DC")
print(f"ESG-Gold: {measurement.esg_gold_amount}")
print(f"신뢰도: {measurement.confidence_score}%")
print(f"상태: {measurement.status.value}")
```

### 신뢰도 점수 계산

**기본 점수 (측정 방법별)**:
- sensor (센서 자동): 95점
- automated (자동화): 85점
- manual_verified (검증된 수동): 75점
- manual (일반 수동): 60점
- self_reported (자가 보고): 40점

**보너스 점수**:
- 증빙 1개 이상: +5점
- 증빙 2개 이상: +10점
- 증빙 3개 이상: +20점
- 영수증 포함: +5점
- GPS 포함: +5점
- 센서 데이터: +10점
- 인증서: +10점

**예시**:
```
기본 점수: 75점 (manual_verified)
+ 증빙 3개: +20점
+ 영수증: +5점
+ GPS: +5점
= 총 105점 → 최대 100점
```

### 자동 승인 조건

다음 조건을 **모두** 만족하면 자동 승인:
1. 신뢰도 점수 ≥ 95%
2. 증빙 자료 ≥ 3개
3. 탄소 절약량 ≤ 50 kg

```python
if (measurement.confidence_score >= 95 and
    len(measurement.evidences) >= 3 and
    measurement.carbon_savings_kg <= 50):
    # 자동 승인
    status = "auto_approved"
else:
    # 위원회 검증 필요
    status = "pending_verification"
```

---

## 위원회 검증 워크플로우

### 위원회 구성

```python
committee_members = [
    CommitteeMember(
        member_id="committee001",
        name="김환경",
        role=CommitteeRole.REVIEWER,
        email="kim@example.com",
        wallet_address="ALGO_WALLET_ADDRESS",
        specialization=["agriculture", "local_food"]
    ),
    CommitteeMember(
        member_id="committee002",
        name="이탄소",
        role=CommitteeRole.APPROVER,
        email="lee@example.com",
        wallet_address="ALGO_WALLET_ADDRESS2",
        specialization=["renewable_energy", "waste_reduction"]
    )
]
```

**역할**:
- **REVIEWER**: 검토자 (1차 검증)
- **APPROVER**: 승인자 (최종 승인)
- **ADMIN**: 관리자 (시스템 관리)
- **AUDITOR**: 감사자 (감사 및 모니터링)

### 검증 프로세스

#### 1. 검증 요청 제출
```python
request = workflow.submit_for_verification(
    measurement=measurement,
    user_id="user123",
    priority=0  # 일반
)
```

#### 2. 자동 배정
시스템이 자동으로 가용한 검토자에게 배정:
- 전문 분야 매칭
- 워크로드 균형
- 우선순위 고려

#### 3. 검토 및 검증
```python
result = workflow.review_and_verify(
    request_id=request.request_id,
    reviewer_id="committee001",
    approved=True,
    comments="증빙 자료가 충분하며, 계산이 정확함",
    adjustments={
        'carbon_savings_kg': 85.0,  # 조정된 값
        'dc_units': 102.0
    }
)
```

**검증 체크리스트**:
- ✅ 증빙 자료 확인
- ✅ 데이터 무결성
- ✅ 계산 정확성
- ✅ 신뢰도 점수
- ✅ 타임스탬프
- ✅ 활동 세부사항

#### 4. 반려 또는 재제출 요청
```python
# 반려
workflow.review_and_verify(
    request_id=request.request_id,
    reviewer_id="committee001",
    approved=False,
    comments="증빙 자료가 불충분합니다"
)

# 재제출 요청
workflow.request_resubmission(
    request_id=request.request_id,
    reviewer_id="committee001",
    feedback="GPS 위치 정보를 추가로 제출해주세요"
)
```

#### 5. 에스컬레이션
복잡한 케이스는 상위 위원회로:
```python
workflow.escalate_to_senior_committee(
    request_id=request.request_id,
    reason="대규모 탄소 감축량 (500kg 이상)"
)
```

---

## 블록체인 검증 기록

### 온체인 저장

```python
blockchain_result = blockchain_service.store_verification_on_chain(
    verification_result=verification_result,
    verifier_private_key="VERIFIER_PRIVATE_KEY"
)

print(f"TX ID: {blockchain_result['tx_id']}")
print(f"Block: {blockchain_result['block']}")
print(f"Hash: {blockchain_result['verification_hash']}")
print(f"Explorer: {blockchain_result['explorer_url']}")
```

**저장되는 데이터**:
```json
{
  "result_id": "VRS-20240115123456",
  "measurement_id": "MRV-user123-20240115",
  "approved": true,
  "carbon_verified": 85.5,
  "dc_verified": 102.6,
  "verified_by": "committee001",
  "verified_at": "2024-01-15T16:30:00",
  "verification_hash": "a3f5d9..."
}
```

### 데이터 조회 및 검증

```python
# 블록체인에서 조회
chain_data = blockchain_service.retrieve_verification_from_chain(tx_id)

# 무결성 검증
is_valid, message = blockchain_service.verify_data_integrity(chain_data)

if is_valid:
    print("✅ 데이터가 변조되지 않았습니다")
else:
    print(f"❌ {message}")
```

### NFT 인증서 발행

```python
nft_result = blockchain_service.create_verification_certificate_nft(
    verification_result=verification_result,
    creator_private_key="CREATOR_PRIVATE_KEY"
)

print(f"NFT Asset ID: {nft_result['asset_id']}")
print(f"Explorer: {nft_result['explorer_url']}")
```

**NFT 메타데이터**:
```json
{
  "name": "Carbon Verification Certificate #VRS-20240115",
  "description": "Verified carbon reduction: 85.5 kg CO₂",
  "properties": {
    "measurement_id": "MRV-user123-20240115",
    "carbon_verified": 85.5,
    "dc_verified": 102.6,
    "verified_by": "committee001",
    "verified_at": "2024-01-15T16:30:00"
  }
}
```

---

## 배포 가이드

### Step 1: 데이터베이스 마이그레이션

```bash
# SQLite
sqlite3 pamtalk.db < migrations/006_mrv_committee_tables.sql

# PostgreSQL
psql -d pamtalk_production -f migrations/006_mrv_committee_tables.sql
```

### Step 2: 위원회 초기 설정

```python
# 위원회 위원 등록
INSERT INTO committee_members (member_id, name, email, wallet_address, role, specialization)
VALUES
  ('committee001', '김환경', 'kim@example.com', 'ALGO_WALLET_1', 'reviewer', '["agriculture"]'),
  ('committee002', '이탄소', 'lee@example.com', 'ALGO_WALLET_2', 'approver', '["renewable_energy"]');
```

### Step 3: API 서버 시작

```python
# app.py
from flask import Flask
from api.mrv_committee_api import mrv_bp, committee_bp, init_mrv_committee_api

app = Flask(__name__)
app.register_blueprint(mrv_bp)
app.register_blueprint(committee_bp)

# 서비스 초기화
from service.mrv_measurement_module import MRVMeasurementModule
from service.mrv_reporting_service import MRVReportingService
from service.committee_verification_workflow import CommitteeVerificationWorkflow
from service.blockchain_verification_service import BlockchainVerificationService
from service.carbon_calculation_engine import CarbonCalculationEngine

carbon_engine = CarbonCalculationEngine()
mrv_module = MRVMeasurementModule(carbon_engine)
reporting_service = MRVReportingService()
verification_workflow = CommitteeVerificationWorkflow()
blockchain_service = BlockchainVerificationService()

init_mrv_committee_api(mrv_module, reporting_service, verification_workflow, blockchain_service)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

### Step 4: 관리자 대시보드 배포

```bash
# 정적 파일 서빙
cp static/committee_dashboard.html /var/www/html/

# 또는 Nginx 설정
server {
    listen 80;
    server_name committee.pam-talk.com;

    location / {
        root /var/www/html;
        index committee_dashboard.html;
    }

    location /api/ {
        proxy_pass http://localhost:5001;
    }
}
```

---

## API 사용법

### 측정 데이터 제출

```bash
curl -X POST http://localhost:5001/api/mrv/measurement/submit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "activity": {
      "activity_type": "local_food_purchase",
      "product_name": "유기농 토마토",
      "quantity": 5.0,
      "origin_region": "경기도",
      "destination_region": "서울시",
      "farming_method": "organic",
      "transport_method": "truck_small",
      "packaging_type": "paper"
    },
    "measurement_method": "manual_verified",
    "evidences": [
      {
        "evidence_type": "receipt",
        "file_path": "/uploads/receipt.jpg",
        "description": "구매 영수증"
      }
    ]
  }'
```

### 검증 요청 제출

```bash
curl -X POST http://localhost:5001/api/committee/verification/submit \
  -H "Content-Type: application/json" \
  -d '{
    "measurement_id": "MRV-user123-20240115",
    "user_id": "user123",
    "priority": 1
  }'
```

### 대기 중인 검증 목록

```bash
curl http://localhost:5001/api/committee/verification/pending?member_id=committee001
```

### 검증 수행

```bash
curl -X POST http://localhost:5001/api/committee/verification/VRQ-123/review \
  -H "Content-Type: application/json" \
  -d '{
    "reviewer_id": "committee001",
    "approved": true,
    "comments": "모든 증빙 확인 완료",
    "verifier_private_key": "VERIFIER_PRIVATE_KEY",
    "store_on_blockchain": true
  }'
```

---

## 통계 및 모니터링

### MRV 통계 조회

```bash
curl "http://localhost:5001/api/mrv/statistics?start_date=2024-01-01&end_date=2024-01-31"
```

**응답**:
```json
{
  "success": true,
  "data": {
    "total_measurements": 150,
    "total_carbon_saved": 3250.5,
    "total_dc_issued": 3900.6,
    "average_confidence": 82.5,
    "by_method": {
      "manual_verified": {"count": 100, "carbon": 2500.0},
      "automated": {"count": 50, "carbon": 750.5}
    }
  }
}
```

### 위원회 성과

```bash
curl http://localhost:5001/api/committee/members/committee001/performance
```

---

## 보안 고려사항

### 1. Private Key 관리
- ❌ 코드에 하드코딩 금지
- ✅ 환경 변수 사용
- ✅ AWS Secrets Manager / HashiCorp Vault

### 2. API 인증
```python
@app.before_request
def verify_token():
    token = request.headers.get('Authorization')
    if not verify_jwt_token(token):
        return jsonify({'error': 'Unauthorized'}), 401
```

### 3. Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/mrv/measurement/submit', methods=['POST'])
@limiter.limit("10 per minute")
def submit_measurement():
    ...
```

---

## 문제 해결

### Q: 측정 검증이 실패해요
**A**:
1. 신뢰도 점수 확인 (최소 40% 필요)
2. 증빙 자료 확인 (최소 1개)
3. 데이터 해시 일치 여부

### Q: 블록체인 저장이 안 돼요
**A**:
1. 지갑에 ALGO 잔액 확인
2. TestNet 연결 상태 확인
3. Private key 권한 확인

### Q: 자동 승인이 안 돼요
**A**: 자동 승인 조건 확인:
- 신뢰도 ≥ 95%
- 증빙 ≥ 3개
- 탄소 ≤ 50kg

---

## 다음 단계

1. **AI 기반 검증**: 머신러닝으로 이상 패턴 탐지
2. **IoT 센서 통합**: 실시간 측정 데이터 수집
3. **모바일 앱**: 현장 측정 및 증빙 촬영
4. **국제 표준 준수**: ISO 14064, GHG Protocol
5. **타사 검증 기관 연동**: TÜV, SGS 등

---

## 라이선스

**개발**: PAM-TALK Platform Team
**문의**: committee@pam-talk.com

---

**구현 완료!** ✅

ESG위원회 시스템과 MRV 시스템이 완전히 구현되었습니다.
