# 웹사이트에서 디지털 쿠폰 지급 시스템 구축 가이드

## 생성된 토큰 정보

```
Token Name: PAM-POINT
Unit Name: PAMP
Asset ID: 3330375002
Total Supply: 10억 포인트
Decimals: 2 (0.01 포인트 단위)
Creator: PWYGE2GDCEOD5LUHBVACTVJVN7KB6XTPSPARBKHBCHVIYXGRY6SNHDRZXE
```

## 시스템 아키텍처

```
[사용자] → [웹사이트] → [백엔드 API] → [알고랜드 블록체인]
                              ↓
                        [토큰 전송]
                              ↓
                     [사용자 페라 월렛]
```

## 1. 백엔드 API 구현

### Flask 예시

```python
from flask import Flask, request, jsonify
from token_creation_api import AlgorandTokenAPI
import json

app = Flask(__name__)

# 마스터 계정 로드
with open('pam_mainnet_account_20251116_181939.json', 'r') as f:
    account_data = json.load(f)

# API 초기화
token_api = AlgorandTokenAPI(account_data['mnemonic'])

# 토큰 설정
PAM_POINT_ASSET_ID = 3330375002

@app.route('/api/give-coupon', methods=['POST'])
def give_coupon():
    """
    사용자에게 디지털 쿠폰(포인트) 지급

    Request:
    {
        "user_address": "알고랜드 주소",
        "amount": 100  # 지급할 포인트 (100 = 1.00 포인트, decimals=2)
    }
    """
    data = request.json
    user_address = data.get('user_address')
    amount = data.get('amount')  # 실제 값 * 100 (decimals=2)

    # 검증
    if not user_address or not amount:
        return jsonify({'error': 'Missing parameters'}), 400

    # 토큰 전송
    result = token_api.transfer_token(
        asset_id=PAM_POINT_ASSET_ID,
        recipient_address=user_address,
        amount=amount
    )

    return jsonify(result)

@app.route('/api/check-balance', methods=['GET'])
def check_balance():
    """마스터 계정 잔액 확인"""
    balance = token_api._check_balance()
    return jsonify({'balance_algo': balance})

if __name__ == '__main__':
    app.run(port=5000)
```

### FastAPI 예시

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from token_creation_api import AlgorandTokenAPI
import json

app = FastAPI()

# 마스터 계정 로드
with open('pam_mainnet_account_20251116_181939.json', 'r') as f:
    account_data = json.load(f)

token_api = AlgorandTokenAPI(account_data['mnemonic'])
PAM_POINT_ASSET_ID = 3330375002

class CouponRequest(BaseModel):
    user_address: str
    amount: int

@app.post("/api/give-coupon")
async def give_coupon(request: CouponRequest):
    result = token_api.transfer_token(
        asset_id=PAM_POINT_ASSET_ID,
        recipient_address=request.user_address,
        amount=request.amount
    )

    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])

    return result
```

## 2. 프론트엔드 연동

### React 예시

```javascript
// CouponButton.jsx
import React, { useState } from 'react';

function CouponButton({ userAddress }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const receiveCoupon = async () => {
    setLoading(true);

    try {
      const response = await fetch('/api/give-coupon', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_address: userAddress,
          amount: 10000  // 100.00 포인트 (decimals=2)
        })
      });

      const data = await response.json();
      setResult(data);

      if (data.success) {
        alert('✅ 쿠폰이 지급되었습니다!');
      } else {
        alert('❌ 지급 실패: ' + data.error);
      }
    } catch (error) {
      alert('❌ 오류: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={receiveCoupon} disabled={loading}>
      {loading ? '처리 중...' : '쿠폰 받기'}
    </button>
  );
}

export default CouponButton;
```

### HTML + JavaScript 예시

```html
<!DOCTYPE html>
<html>
<head>
    <title>PAM 디지털 쿠폰</title>
</head>
<body>
    <h1>디지털 쿠폰 받기</h1>

    <input type="text" id="userAddress" placeholder="알고랜드 주소 입력">
    <button onclick="receiveCoupon()">쿠폰 받기</button>

    <div id="result"></div>

    <script>
    async function receiveCoupon() {
        const address = document.getElementById('userAddress').value;

        if (!address) {
            alert('주소를 입력하세요');
            return;
        }

        try {
            const response = await fetch('/api/give-coupon', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_address: address,
                    amount: 10000  // 100.00 포인트
                })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('result').innerHTML =
                    `✅ 쿠폰 지급 완료!<br>
                     Transaction: ${data.txid}`;
            } else {
                document.getElementById('result').innerHTML =
                    `❌ 실패: ${data.error}`;
            }
        } catch (error) {
            alert('오류: ' + error.message);
        }
    }
    </script>
</body>
</html>
```

## 3. 사용자 플로우

### 사용자가 쿠폰을 받는 과정

1. **사용자 준비**
   - 페라 월렛 설치
   - Asset Opt-in (최초 1회만)

2. **Opt-in 방법**
   ```
   페라 월렛 → Add Asset → Asset ID 입력: 3330375002 → Add
   수수료: 0.001 ALGO
   ```

3. **쿠폰 받기**
   - 웹사이트에서 "쿠폰 받기" 버튼 클릭
   - 알고랜드 주소 입력
   - 자동으로 토큰 전송됨
   - 페라 월렛에서 즉시 확인 가능

## 4. Opt-in 자동화 (선택사항)

사용자가 Opt-in을 안 한 경우 자동으로 안내:

```python
def check_opt_in(user_address, asset_id):
    """사용자가 Asset을 Opt-in 했는지 확인"""
    url = f"{API_BASE}/accounts/{user_address}"
    response = requests.get(url)

    if response.status_code != 200:
        return False

    data = response.json()
    assets = data.get('assets', [])

    for asset in assets:
        if asset['asset-id'] == asset_id:
            return True

    return False

@app.route('/api/give-coupon', methods=['POST'])
def give_coupon():
    data = request.json
    user_address = data['user_address']

    # Opt-in 확인
    if not check_opt_in(user_address, PAM_POINT_ASSET_ID):
        return jsonify({
            'error': 'NOT_OPTED_IN',
            'message': '먼저 페라 월렛에서 Asset Opt-in을 해주세요',
            'asset_id': PAM_POINT_ASSET_ID
        }), 400

    # 토큰 전송
    result = token_api.transfer_token(...)
    return jsonify(result)
```

## 5. 보안 고려사항

### ⚠️ 중요: 마스터 계정 보안

```python
# ❌ 나쁜 예: 니모닉을 코드에 하드코딩
MASTER_MNEMONIC = "paddle wait feed..."  # 절대 금지!

# ✅ 좋은 예: 환경 변수 사용
import os
MASTER_MNEMONIC = os.getenv('ALGORAND_MASTER_MNEMONIC')

# ✅ 더 좋은 예: 암호화된 파일 사용
from cryptography.fernet import Fernet

def load_encrypted_mnemonic():
    key = os.getenv('ENCRYPTION_KEY').encode()
    fernet = Fernet(key)

    with open('encrypted_account.bin', 'rb') as f:
        encrypted_data = f.read()

    decrypted = fernet.decrypt(encrypted_data)
    return json.loads(decrypted)['mnemonic']
```

### API 접근 제한

```python
# IP 화이트리스트
ALLOWED_IPS = ['your-frontend-server-ip']

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in ALLOWED_IPS:
        abort(403)

# Rate limiting
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/api/give-coupon')
@limiter.limit("10 per minute")
def give_coupon():
    ...
```

## 6. 배포

### Docker 예시

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### requirements.txt

```
flask==3.0.0
py-algorand-sdk==2.6.0
requests==2.31.0
gunicorn==21.2.0
```

## 7. 모니터링

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/give-coupon', methods=['POST'])
def give_coupon():
    logger.info(f"Coupon request from {request.remote_addr}")

    result = token_api.transfer_token(...)

    if result['success']:
        logger.info(f"✅ Coupon sent: {result['txid']}")
    else:
        logger.error(f"❌ Failed: {result['error']}")

    return jsonify(result)
```

## 다음 단계

1. ✅ 토큰 생성 완료
2. ⏳ 백엔드 API 구현
3. ⏳ 프론트엔드 연동
4. ⏳ 테스트 (소량 전송)
5. ⏳ 프로덕션 배포

---

**Asset ID: 3330375002** 을 꼭 기억하세요!

이 ID로 사용자들이 Opt-in하고 토큰을 받을 수 있습니다.
