# 🎉 PAM 디지털 쿠폰 시스템 완성!

웹사이트에서 사용자에게 알고랜드 블록체인 기반 디지털 쿠폰을 자동으로 지급하는 완전한 시스템

---

## 📋 시스템 개요

```
[사용자] → [웹사이트] → [Flask API] → [알고랜드 블록체인]
                             ↓
                      [PAM-POINT 토큰]
                             ↓
                    [사용자 페라 월렛]
```

---

## ✅ 완성된 구성 요소

### 1. 블록체인 (완료)

**PAM-POINT 토큰 (메인넷 발행)**
- Asset ID: `3330375002`
- Token Name: PAM-POINT
- Unit: PAMP
- Total Supply: 10억 포인트
- Decimals: 2 (0.01 포인트 단위)
- Explorer: https://algoexplorer.io/asset/3330375002

### 2. 백엔드 API (완료)

**Flask API 서버**
- 위치: `algo/api/app.py`
- 포트: 5000
- 상태: ✅ 실행 중

**API 엔드포인트:**
- `GET  /api/health` - 헬스 체크
- `GET  /api/token-info` - 토큰 정보
- `GET  /api/balance` - 마스터 계정 잔액
- `POST /api/check-opt-in` - 사용자 Opt-in 확인
- `POST /api/give-coupon` - **쿠폰 지급** ⭐

### 3. 프론트엔드 (완료)

**React 컴포넌트:**
- `CouponButton.jsx` - 쿠폰 받기 버튼
- `OptInGuide.jsx` - 설정 안내 모달
- `App.jsx` - 완전한 예제 앱

**HTML 단일 파일:**
- `frontend/public/index.html` - 바로 사용 가능

---

## 🚀 실행 방법

### 백엔드 API 시작

```bash
cd algo/api
python app.py
```

서버: http://localhost:5000

### 프론트엔드 시작

**옵션 A: React (고급)**
```bash
cd frontend
npm install
npm start
```

서버: http://localhost:3000

**옵션 B: HTML (간단)**
```bash
cd frontend/public
python -m http.server 8000
```

서버: http://localhost:8000

---

## 📱 사용자 플로우

### 1단계: 지갑 준비
- 페라 월렛 설치
- https://perawallet.app

### 2단계: Asset Opt-in (최초 1회)
1. 페라 월렛 열기
2. "Add Asset" 또는 "+" 탭
3. Asset ID 입력: `3330375002`
4. "Add" 탭 (수수료: 0.001 ALGO)

### 3단계: 쿠폰 받기
1. 웹사이트 접속
2. 알고랜드 주소 입력
3. "쿠폰 받기" 버튼 클릭
4. 페라 월렛에서 즉시 확인!

---

## 🔧 API 사용 예시

### cURL로 쿠폰 지급

```bash
curl -X POST http://localhost:5000/api/give-coupon \
  -H "Content-Type: application/json" \
  -d '{
    "user_address": "알고랜드_주소",
    "amount": 10000
  }'
```

### JavaScript로 쿠폰 지급

```javascript
async function giveCoupon(userAddress) {
  const response = await fetch('http://localhost:5000/api/give-coupon', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_address: userAddress,
      amount: 10000  // 100.00 포인트
    })
  });

  const data = await response.json();

  if (data.success) {
    console.log('쿠폰 지급 성공!', data.txid);
    console.log('Explorer:', data.explorer_url);
  } else {
    console.error('실패:', data.error);
  }
}
```

### Python으로 쿠폰 지급

```python
import requests

def give_coupon(user_address, amount=10000):
    response = requests.post(
        'http://localhost:5000/api/give-coupon',
        json={
            'user_address': user_address,
            'amount': amount
        }
    )

    data = response.json()

    if data['success']:
        print(f"✅ 쿠폰 지급 성공!")
        print(f"TX ID: {data['txid']}")
        print(f"금액: {data['amount_display']} PAMP")
    else:
        print(f"❌ 실패: {data['error']}")

# 사용 예시
give_coupon('ALGORAND_ADDRESS_HERE')
```

---

## 🎨 웹사이트 통합 예시

### 회원 가입 축하 쿠폰

```html
<!DOCTYPE html>
<html>
<head>
    <title>회원 가입 완료</title>
</head>
<body>
    <h1>🎉 회원 가입을 축하합니다!</h1>
    <p>가입 축하 쿠폰 100 포인트를 받으세요</p>

    <input type="text" id="address" placeholder="알고랜드 주소">
    <button onclick="receiveCoupon()">쿠폰 받기</button>

    <div id="result"></div>

    <script>
    async function receiveCoupon() {
        const address = document.getElementById('address').value;

        const response = await fetch('http://localhost:5000/api/give-coupon', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_address: address,
                amount: 10000
            })
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('result').innerHTML =
                `✅ 쿠폰 ${data.amount_display} PAMP 받기 완료!<br>
                 <a href="${data.explorer_url}" target="_blank">거래 확인</a>`;
        } else {
            document.getElementById('result').innerHTML =
                `❌ ${data.error}`;
        }
    }
    </script>
</body>
</html>
```

---

## 📊 관리자 대시보드

### 마스터 계정 잔액 확인

```bash
curl http://localhost:5000/api/balance
```

응답:
```json
{
  "success": true,
  "balance_algo": 9.998,
  "address": "PWYGE2GD..."
}
```

### 토큰 정보 확인

```bash
curl http://localhost:5000/api/token-info
```

응답:
```json
{
  "asset_id": 3330375002,
  "asset_name": "PAM-POINT",
  "unit_name": "PAMP",
  "total_supply": 1000000000,
  "decimals": 2,
  "explorer_url": "https://algoexplorer.io/asset/3330375002"
}
```

---

## 🔐 프로덕션 배포

### 1. 환경 변수 설정

```bash
# .env 파일
FLASK_ENV=production
PORT=5000
ALGORAND_MASTER_MNEMONIC=암호화된_니모닉
```

### 2. Gunicorn으로 실행

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 3. Nginx 리버스 프록시

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }
}
```

### 4. HTTPS 설정 (Let's Encrypt)

```bash
sudo certbot --nginx -d your-domain.com
```

---

## 📈 확장 아이디어

### 1. 포인트 등급 시스템

```python
def give_coupon_by_level(user_address, user_level):
    amount_map = {
        'bronze': 5000,   # 50 포인트
        'silver': 10000,  # 100 포인트
        'gold': 20000,    # 200 포인트
        'platinum': 50000 # 500 포인트
    }

    amount = amount_map.get(user_level, 10000)

    return token_api.transfer_token(
        asset_id=3330375002,
        recipient_address=user_address,
        amount=amount
    )
```

### 2. 이벤트 쿠폰

```python
@app.route('/api/event-coupon', methods=['POST'])
def event_coupon():
    """특정 이벤트 참여자에게 쿠폰 지급"""
    data = request.get_json()
    event_code = data.get('event_code')

    if event_code == 'WELCOME2025':
        amount = 50000  # 500 포인트
    elif event_code == 'FRIEND':
        amount = 30000  # 300 포인트
    else:
        return jsonify({'error': 'Invalid code'}), 400

    # 쿠폰 지급
    # ...
```

### 3. 자동 리워드 시스템

```python
def auto_reward(user_id, action):
    """사용자 행동에 따른 자동 리워드"""
    reward_rules = {
        'signup': 10000,      # 회원가입: 100 포인트
        'review': 5000,       # 리뷰 작성: 50 포인트
        'share': 3000,        # SNS 공유: 30 포인트
        'purchase': 20000     # 구매: 200 포인트
    }

    amount = reward_rules.get(action, 0)

    if amount > 0:
        user_address = get_user_algorand_address(user_id)
        give_coupon(user_address, amount)
```

---

## 🆘 문제 해결

### Q: "Asset Opt-in이 필요합니다" 오류
**A:** 페라 월렛에서 Asset ID 3330375002를 추가하세요

### Q: API 연결 실패
**A:** 백엔드 서버가 실행 중인지 확인: `http://localhost:5000/api/health`

### Q: 쿠폰을 받았는데 페라 월렛에 안 보여요
**A:**
1. Asset Opt-in을 했는지 확인
2. 올바른 메인넷 주소인지 확인
3. 거래 탐색기에서 TX ID 확인

### Q: 마스터 계정 ALGO가 부족해요
**A:** 페라 월렛에서 마스터 계정으로 ALGO 전송

---

## 📞 지원

- Asset Explorer: https://algoexplorer.io/asset/3330375002
- Pera Wallet: https://perawallet.app
- Algorand Docs: https://developer.algorand.org

---

## 🎉 축하합니다!

완전한 디지털 쿠폰 시스템이 구축되었습니다!

이제 사용자들에게 블록체인 기반 디지털 쿠폰을 자동으로 지급할 수 있습니다.

**다음 단계:**
1. 테스트 전송 (소량)
2. 웹사이트 통합
3. 프로덕션 배포
4. 사용자 모니터링

**성공을 기원합니다! 🚀**
