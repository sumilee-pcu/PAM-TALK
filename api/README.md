# PAM Digital Coupon API

웹사이트에서 사용자에게 디지털 쿠폰을 지급하는 Flask 백엔드 API

## 생성된 토큰 정보

- **Asset ID**: 3330375002  
- **Token Name**: PAM-POINT
- **Unit**: PAMP
- **Total Supply**: 10억 포인트
- **Decimals**: 2 (0.01 포인트 단위)

## 설치

```bash
cd algo/api
pip install -r requirements.txt
```

## 실행

```bash
python app.py
```

서버가 http://localhost:5000 에서 시작됩니다.

## API 엔드포인트

### 1. GET / 
API 정보

### 2. GET /api/health
헬스 체크

### 3. GET /api/token-info
토큰 정보 조회

### 4. GET /api/balance
마스터 계정 잔액 확인

### 5. POST /api/check-opt-in
사용자 Opt-in 상태 확인

**Request:**
```json
{
  "user_address": "알고랜드 주소"
}
```

### 6. POST /api/give-coupon
사용자에게 쿠폰 지급

**Request:**
```json
{
  "user_address": "알고랜드 주소",
  "amount": 10000
}
```

**Response (성공):**
```json
{
  "success": true,
  "txid": "...",
  "asset_id": 3330375002,
  "amount": 10000,
  "amount_display": "100.00",
  "explorer_url": "https://algoexplorer.io/tx/..."
}
```

**Response (Opt-in 필요):**
```json
{
  "success": false,
  "error": "NOT_OPTED_IN",
  "message": "User must opt-in first",
  "asset_id": 3330375002
}
```

## 테스트

```bash
# 터미널 1: API 서버 시작
python app.py

# 터미널 2: 테스트 실행
python test_api.py
```

## Curl 예시

```bash
# 토큰 정보
curl http://localhost:5000/api/token-info

# Opt-in 확인
curl -X POST http://localhost:5000/api/check-opt-in \
  -H "Content-Type: application/json" \
  -d '{"user_address":"YOUR_ADDRESS"}'

# 쿠폰 지급
curl -X POST http://localhost:5000/api/give-coupon \
  -H "Content-Type: application/json" \
  -d '{"user_address":"YOUR_ADDRESS","amount":10000}'
```

## 프로덕션 배포

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
