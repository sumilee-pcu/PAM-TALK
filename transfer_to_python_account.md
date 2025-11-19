# ALGO 전송 가이드

## Python 계정으로 ALGO 전송하기

### 받는 주소 (복사용)
```
PWYGE2GDCEOD5LUHBVACTVJVN7KB6XTPSPARBKHBCHVIYXGRY6SNHDRZXE
```

### 페라 월렛에서 전송 방법

1. **페라 월렛 앱 열기**
2. **Send 버튼 클릭**
3. **받는 주소 입력:**
   ```
   PWYGE2GDCEOD5LUHBVACTVJVN7KB6XTPSPARBKHBCHVIYXGRY6SNHDRZXE
   ```
4. **전송 금액: 10 ALGO**
   - 토큰 발행 수수료: ~0.001 ALGO
   - 여유분 포함하여 10 ALGO 권장

5. **확인 및 전송**

### 전송 후

전송이 완료되면 다음 명령어로 확인:

```bash
cd algo
python -c "
import requests
address = 'PWYGE2GDCEOD5LUHBVACTVJVN7KB6XTPSPARBKHBCHVIYXGRY6SNHDRZXE'
response = requests.get(f'https://mainnet-api.algonode.cloud/v2/accounts/{address}')
balance = response.json().get('amount', 0) / 1000000
print(f'Balance: {balance:.6f} ALGO')
"
```

### 다음 단계

잔액이 확인되면:
```bash
python create_digital_coupon_token.py
```
