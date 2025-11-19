# ESG-Gold (1DC 단위) 디지털 쿠폰 시스템 구현 가이드

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [핵심 개념](#핵심-개념)
3. [구현된 컴포넌트](#구현된-컴포넌트)
4. [배포 가이드](#배포-가이드)
5. [API 사용법](#api-사용법)
6. [프론트엔드 통합](#프론트엔드-통합)
7. [보안 고려사항](#보안-고려사항)

---

## 시스템 개요

### ESG-Gold란?
ESG-Gold는 탄소 감축 활동을 디지털 자산으로 토큰화한 시스템입니다.

**핵심 원리:**
- **1 DC (Digital Carbon)** = **1 kg CO₂ 감축량**
- **1 ESG-GOLD** = **1 DC** = **1 kg CO₂**
- Algorand 블록체인 기반 ASA(Algorand Standard Asset) 토큰
- 6 decimals (1 ESG-GOLD = 1,000,000 micro units)

### 기존 시스템과의 관계
- **PAM 토큰**: 플랫폼 유틸리티 토큰 (기존)
- **ESG-GOLD**: 탄소 크레딧 디지털 쿠폰 (신규)
- 두 토큰은 병행 운영되며 서로 다른 용도로 사용

---

## 핵심 개념

### 1DC = 1kg CO₂ 변환 로직

```python
# 탄소 절약량 계산
carbon_savings = baseline_emissions - actual_emissions

# DC 단위 변환 (1:1)
dc_units = carbon_savings * 1.0  # 1 DC = 1 kg CO₂

# 활동별 보너스 적용
activity_multipliers = {
    'local_food_purchase': 1.2,   # 20% 보너스
    'organic_farming': 1.5,        # 50% 보너스
    'renewable_energy': 2.0,       # 100% 보너스
    'waste_reduction': 1.8,        # 80% 보너스
    'transport_reduction': 1.3,    # 30% 보너스
    'packaging_reduction': 1.3     # 30% 보너스
}

dc_with_bonus = dc_units * multiplier

# ESG-GOLD micro units 계산
esg_gold_micro = int(dc_with_bonus * 1_000_000)
```

### 소각 메커니즘

```python
# 마켓플레이스 할인: 10% 소각
burn_rate_marketplace = 0.1

# 영구 상쇄: 100% 소각
burn_rate_retirement = 1.0

# 사용 예시
사용자가 10 DC 할인 사용 → 1 DC 소각, 9 DC 순환
```

---

## 구현된 컴포넌트

### 1. 토큰 설정 및 배포

#### 파일: `esg_gold_config.json`
```json
{
  "token_name": "ESG-Gold Digital Carbon Credit",
  "token_symbol": "ESG-GOLD",
  "unit_name": "DC",
  "total_supply": 10000000000,
  "decimals": 6
}
```

#### 배포 스크립트: `deploy_esg_gold_token.py`
```bash
python deploy_esg_gold_token.py
```

**배포 단계:**
1. Creator 계정 생성 또는 기존 계정 사용
2. Algorand TestNet에서 ALGO 충전 (https://bank.testnet.algorand.network/)
3. ASA 토큰 생성 (약 0.2 ALGO 필요)
4. Asset ID를 config 파일에 저장

### 2. 탄소 계산 엔진

#### 파일: `carbon_calculation_engine.py`

**주요 함수:**
- `calculate_carbon_footprint()`: 종합 탄소 발자국 계산
- `_convert_to_esg_gold()`: DC → ESG-GOLD 변환
- `calculate_esg_gold_burn()`: 소각량 계산

**사용 예시:**
```python
from carbon_calculation_engine import CarbonCalculationEngine, CarbonActivity, ActivityType

engine = CarbonCalculationEngine()

activity = CarbonActivity(
    activity_type=ActivityType.LOCAL_FOOD_PURCHASE,
    user_id="user123",
    product_name="유기농 토마토",
    quantity=3.0,
    origin_region="경기도",
    destination_region="서울시",
    farming_method="organic",
    transport_method="truck_small",
    packaging_type="paper",
    activity_date="2024-01-15"
)

result = engine.calculate_carbon_footprint(activity)
print(f"탄소 절약: {result.carbon_savings} kg CO₂")
print(f"DC 획득: {result.digital_carbon_units} DC")
print(f"ESG-GOLD: {result.esg_gold_actual} ESG-GOLD")
```

### 3. ESG-Gold 서비스

#### 파일: `esg_gold_service.py`

**주요 기능:**
- `mint_esg_gold()`: ESG-GOLD 발행
- `burn_esg_gold()`: ESG-GOLD 소각
- `transfer_esg_gold()`: ESG-GOLD 전송
- `opt_in_esg_gold()`: 사용자 옵트인
- `get_balance()`: 잔액 조회

**사용 예시:**
```python
from esg_gold_service import ESGGoldService

service = ESGGoldService('esg_gold_config.json')

# 옵트인
result = service.opt_in_esg_gold(
    account_address="USER_WALLET_ADDRESS",
    account_private_key="USER_PRIVATE_KEY"
)

# 발행
mint_result = service.mint_esg_gold(
    recipient_address="USER_WALLET_ADDRESS",
    amount_dc=5.5,  # 5.5 DC
    creator_private_key="CREATOR_PRIVATE_KEY",
    reason="carbon_reduction_organic_farming"
)

# 잔액 조회
balance = service.get_balance("USER_WALLET_ADDRESS")
print(f"잔액: {balance} DC")
```

### 4. 자동 변환 모듈

#### 파일: `esg_gold_conversion_module.py`

**주요 기능:**
- `process_carbon_activity()`: 활동 처리 및 자동 발행
- `calculate_reward_preview()`: 보상 미리보기
- `apply_marketplace_discount()`: 마켓플레이스 할인 적용

**사용 예시:**
```python
from esg_gold_conversion_module import ESGGoldConversionModule

module = ESGGoldConversionModule(
    esg_gold_service=esg_service,
    creator_private_key="CREATOR_PRIVATE_KEY"
)

# 보상 미리보기
preview = module.calculate_reward_preview(activity)

# 실제 처리
result = module.process_carbon_activity(
    activity=activity,
    user_wallet_address="USER_WALLET"
)

print(f"발행 성공: {result.success}")
print(f"ESG-GOLD: {result.esg_gold_minted} DC")
print(f"TX ID: {result.transaction_id}")
```

### 5. 데이터베이스 스키마

#### 파일: `migrations/005_esg_gold_tables.sql`

**주요 테이블:**
- `esg_gold_balances`: 사용자 잔액
- `esg_gold_conversions`: 변환 기록
- `esg_gold_transactions`: 거래 내역
- `esg_gold_burns`: 소각 기록
- `esg_gold_marketplace_discounts`: 마켓플레이스 할인
- `esg_gold_daily_stats`: 일별 통계

**마이그레이션 실행:**
```bash
# SQLite
sqlite3 pamtalk.db < migrations/005_esg_gold_tables.sql

# PostgreSQL
psql -d pamtalk -f migrations/005_esg_gold_tables.sql
```

### 6. API 엔드포인트

#### 파일: `api/esg_gold_api.py`

**주요 엔드포인트:**

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/esg-gold/info` | 토큰 정보 |
| GET | `/api/esg-gold/balance/<wallet>` | 잔액 조회 |
| POST | `/api/esg-gold/opt-in` | 옵트인 |
| POST | `/api/esg-gold/activity/preview` | 보상 미리보기 |
| POST | `/api/esg-gold/activity/submit` | 활동 제출 |
| POST | `/api/esg-gold/transfer` | 전송 |
| POST | `/api/esg-gold/marketplace/apply-discount` | 할인 적용 |
| POST | `/api/esg-gold/burn` | 소각 |
| GET | `/api/esg-gold/user/<user_id>/stats` | 사용자 통계 |

**API 사용 예시:**
```javascript
// 보상 미리보기
const response = await fetch('http://localhost:5000/api/esg-gold/activity/preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        activity_type: 'local_food_purchase',
        product_name: '유기농 토마토',
        quantity: 3.0,
        origin_region: '경기도',
        destination_region: '서울시',
        farming_method: 'organic',
        transport_method: 'truck_small',
        packaging_type: 'paper'
    })
});

const data = await response.json();
console.log(`예상 ESG-GOLD: ${data.data.esg_gold_amount}`);
```

### 7. 프론트엔드 UI

#### 파일: `static/esg_gold_widget.html`

**주요 기능:**
- 💰 ESG-Gold 잔액 표시
- 🌱 탄소 상쇄량 시각화
- 📊 활동 통계
- 🛒 마켓플레이스 할인
- ✍️ 활동 등록 폼
- 📜 거래 내역

**사용법:**
```html
<!-- 기존 마켓플레이스에 위젯 추가 -->
<iframe src="esg_gold_widget.html" width="100%" height="600px"></iframe>
```

---

## 배포 가이드

### Step 1: 환경 설정

```bash
# Python 패키지 설치
pip install py-algorand-sdk flask flask-cors

# 환경 변수 설정
export ALGORAND_NETWORK=testnet
export ALGORAND_ENDPOINT=https://testnet-api.algonode.cloud
```

### Step 2: ESG-GOLD 토큰 배포

```bash
# 1. Creator 계정 생성
python deploy_esg_gold_token.py

# 2. Mnemonic 저장 (안전하게!)
# 출력된 25 단어를 안전한 곳에 보관

# 3. TestNet ALGO 받기
# https://bank.testnet.algorand.network/

# 4. 토큰 생성
# 스크립트가 자동으로 Asset ID를 config에 저장
```

### Step 3: 데이터베이스 마이그레이션

```bash
# SQLite (개발)
sqlite3 pamtalk.db < migrations/005_esg_gold_tables.sql

# PostgreSQL (프로덕션)
psql -d pamtalk_production -f migrations/005_esg_gold_tables.sql
```

### Step 4: API 서버 시작

```python
# app.py
from flask import Flask
from api.esg_gold_api import app, init_esg_gold_api
from service.esg_gold_service import ESGGoldService
from service.esg_gold_conversion_module import ESGGoldConversionModule
from service.carbon_calculation_engine import CarbonCalculationEngine

# 서비스 초기화
esg_service = ESGGoldService('esg_gold_config.json')
carbon_engine = CarbonCalculationEngine()
conversion_module = ESGGoldConversionModule(
    esg_gold_service=esg_service,
    creator_private_key="CREATOR_PRIVATE_KEY",  # 환경 변수에서 로드
    db_connection=db
)

# API 초기화
init_esg_gold_api(esg_service, conversion_module, carbon_engine)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### Step 5: 프론트엔드 배포

```bash
# 정적 파일 서빙
cp static/esg_gold_widget.html /var/www/html/

# 또는 Vercel/Netlify 배포
vercel deploy static/
```

---

## API 사용법

### 잔액 조회

```bash
curl http://localhost:5000/api/esg-gold/balance/WALLET_ADDRESS
```

**응답:**
```json
{
  "success": true,
  "data": {
    "wallet_address": "...",
    "balance_dc": 125.5,
    "balance_micro": 125500000,
    "opted_in": true,
    "carbon_offset": {
      "carbon_offset_kg": 125.5,
      "trees_equivalent": 5.70
    }
  }
}
```

### 활동 제출

```bash
curl -X POST http://localhost:5000/api/esg-gold/activity/submit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "wallet_address": "WALLET_ADDRESS",
    "activity_type": "local_food_purchase",
    "product_name": "유기농 토마토",
    "quantity": 3.0,
    "origin_region": "경기도",
    "destination_region": "서울시",
    "farming_method": "organic",
    "transport_method": "truck_small",
    "packaging_type": "paper"
  }'
```

### 마켓플레이스 할인

```bash
curl -X POST http://localhost:5000/api/esg-gold/marketplace/apply-discount \
  -H "Content-Type: application/json" \
  -d '{
    "user_wallet": "WALLET_ADDRESS",
    "user_private_key": "PRIVATE_KEY",
    "esg_gold_amount": 10.0,
    "purchase_amount": 50000
  }'
```

**응답:**
```json
{
  "success": true,
  "discount_rate": 20.0,
  "discount_amount": 10000,
  "final_amount": 40000,
  "esg_gold_burned": 1.0,
  "burn_tx_id": "TX_HASH"
}
```

---

## 프론트엔드 통합

### Vue.js 예시

```vue
<template>
  <div class="esg-gold-widget">
    <h3>ESG-Gold 잔액: {{ balance }} DC</h3>
    <p>탄소 상쇄: {{ carbonOffset }} kg CO₂</p>
    <button @click="applyDiscount">10% 할인 적용</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      balance: 0,
      carbonOffset: 0,
      walletAddress: ''
    }
  },

  async mounted() {
    await this.loadBalance()
  },

  methods: {
    async loadBalance() {
      const response = await fetch(
        `http://localhost:5000/api/esg-gold/balance/${this.walletAddress}`
      )
      const data = await response.json()
      this.balance = data.data.balance_dc
      this.carbonOffset = data.data.carbon_offset.carbon_offset_kg
    },

    async applyDiscount() {
      const response = await fetch(
        'http://localhost:5000/api/esg-gold/marketplace/apply-discount',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_wallet: this.walletAddress,
            user_private_key: this.privateKey,
            esg_gold_amount: 10.0,
            purchase_amount: this.cartTotal
          })
        }
      )
      const result = await response.json()
      if (result.success) {
        this.cartTotal = result.final_amount
        alert(`${result.discount_amount}원 할인 적용!`)
      }
    }
  }
}
</script>
```

---

## 보안 고려사항

### 1. Private Key 관리

**❌ 절대 하지 말 것:**
```javascript
// 프론트엔드에서 private key 저장
const privateKey = "PRIVATE_KEY_HERE"  // 위험!
```

**✅ 권장 방법:**
```javascript
// 지갑 서명 사용 (AlgoSigner, MyAlgo Wallet 등)
const signedTxn = await AlgoSigner.signTxn([{
  txn: transaction
}])
```

### 2. 백엔드 검증

```python
@app.route('/api/esg-gold/activity/submit', methods=['POST'])
def submit_activity():
    # 1. 사용자 인증 확인
    if not verify_user_token(request.headers.get('Authorization')):
        return jsonify({'error': 'Unauthorized'}), 401

    # 2. Rate limiting
    if exceeded_rate_limit(user_id):
        return jsonify({'error': 'Too many requests'}), 429

    # 3. 데이터 검증
    if not validate_activity_data(data):
        return jsonify({'error': 'Invalid data'}), 400
```

### 3. 일일 한도 설정

```python
# conversion_module.py에 구현됨
daily_conversion_limit_dc = 1000.0  # 1000 DC/day per user
```

### 4. 트랜잭션 확인

```python
# 모든 트랜잭션은 블록 확인 대기
confirmed_txn = wait_for_confirmation(client, tx_id, 4)
```

---

## 모니터링 및 관리

### 시스템 통계 조회

```sql
-- 일별 발행/소각 통계
SELECT
    stat_date,
    total_dc_minted,
    total_dc_burned,
    total_carbon_saved_kg
FROM esg_gold_daily_stats
ORDER BY stat_date DESC
LIMIT 30;
```

### 사용자 순위

```sql
-- 탄소 절약 상위 사용자
SELECT
    user_id,
    total_carbon_saved_kg,
    total_esg_gold_earned
FROM v_user_esg_gold_summary
ORDER BY total_carbon_saved_kg DESC
LIMIT 10;
```

---

## 문제 해결

### Q: 옵트인이 안 돼요
**A:** 지갑에 최소 0.1 ALGO가 있어야 합니다.

### Q: 발행이 실패해요
**A:**
1. 수신자가 옵트인했는지 확인
2. Creator 계정 잔액 확인
3. Asset ID가 올바른지 확인

### Q: 소각 트랜잭션이 안 돼요
**A:** 잔액이 충분한지 확인하고, 지갑에 트랜잭션 수수료용 ALGO가 있는지 확인

---

## 다음 단계

1. **MainNet 배포**: TestNet 테스트 완료 후 MainNet으로 이전
2. **DAO 거버넌스**: ESG-GOLD 홀더 투표 시스템
3. **스테이킹**: ESG-GOLD 스테이킹으로 추가 보상
4. **NFT 인증서**: 탄소 상쇄 NFT 증서 발행
5. **크로스체인**: Ethereum, Polygon 등 다른 체인 지원

---

## 라이선스 및 연락처

**개발:** PAM-TALK Platform Team
**문의:** support@pam-talk.com
**GitHub:** https://github.com/pamtalk/esg-gold

---

## 변경 이력

- **v1.0.0** (2024-01-15): 초기 ESG-Gold 시스템 구현
  - 1DC = 1kg CO₂ 변환 로직
  - Algorand ASA 토큰 배포
  - 자동 발행/소각 시스템
  - 마켓플레이스 통합
  - API 및 프론트엔드 UI

---

**구현 완료!** 🎉

이제 PAM-TALK 플랫폼에서 ESG-Gold 디지털 쿠폰 시스템을 사용할 수 있습니다.
