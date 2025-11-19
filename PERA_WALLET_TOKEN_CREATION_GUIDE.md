# 페라 월렛으로 디지털 쿠폰 토큰 생성 가이드

네트워크 API 문제로 Python 스크립트가 작동하지 않을 때, 페라 월렛 앱에서 직접 토큰을 생성할 수 있습니다.

## PAM-POINT 토큰 생성

### 1단계: 페라 월렛 앱 열기

- 10 ALGO를 받은 계정 선택
- 주소: `PWYGE2GDCEOD5LUHBVACTVJVN7KB6XTPSPARBKHBCHVIYXGRY6SNHDRZXE`

### 2단계: 토큰 생성 메뉴 찾기

페라 월렛의 버전에 따라 다를 수 있습니다:

**방법 A: 메인 화면에서**
- 하단 메뉴 또는 더보기(...)
- "Add New Asset" 또는 "Create Asset" 찾기

**방법 B: 설정에서**
- Settings (⚙️)
- "Create Asset" 또는 "Manage Assets"

**방법 C: 웹 버전 사용**
- https://web.perawallet.app
- 니모닉으로 로그인
- "Create Asset"

### 3단계: PAM-POINT 토큰 정보 입력

```
Asset Name: PAM-POINT
Unit Name: PAMP
Total Supply: 1000000000
Decimals: 2
Default Frozen: No (체크 해제)

Manager Address: (본인 주소 - 자동 입력됨)
Reserve Address: (본인 주소)
Freeze Address: (본인 주소)
Clawback Address: (본인 주소)

Asset URL: https://pam-talk.com/point
Metadata Hash: (비워두기)
```

### 4단계: 수수료 확인 및 생성

- 수수료: 약 0.001 ALGO
- "Create Asset" 버튼 클릭
- 비밀번호 입력 (또는 생체인증)
- 확인 대기 (약 5초)

### 5단계: Asset ID 기록

생성 완료 후 표시되는 **Asset ID**를 반드시 기록하세요!

예: `1234567890`

이 ID로 토큰을 찾고 전송할 수 있습니다.

---

## PAM-VOUCHER 토큰 생성 (선택사항)

위 과정을 반복하되, 정보만 변경:

```
Asset Name: PAM-VOUCHER
Unit Name: PAMV
Total Supply: 100000
Decimals: 0
Asset URL: https://pam-talk.com/voucher
```

---

## 생성 후 확인

### 페라 월렛에서 확인
- 메인 화면에 새 토큰이 표시됨
- 잔액: 1,000,000,000 PAMP (또는 100,000 PAMV)

### 기록해야 할 정보

생성이 완료되면 다음 정보를 기록:

```json
{
  "pam_point": {
    "asset_id": "여기에 Asset ID",
    "name": "PAM-POINT",
    "unit": "PAMP",
    "creator": "PWYGE2GDCEOD5LUHBVACTVJVN7KB6XTPSPARBKHBCHVIYXGRY6SNHDRZXE"
  }
}
```

---

## 토큰 전송 방법

### 1. 받는 사람이 먼저 Opt-in 해야 함

알고랜드에서는 토큰을 받기 전에 "opt-in" (수신 동의)를 해야 합니다.

**받는 사람이 해야 할 일:**
1. 페라 월렛 열기
2. "Add Asset" 또는 "+" 버튼
3. Asset ID 검색
4. "Add" 클릭 (수수료: 0.001 ALGO)

### 2. 토큰 전송

**보내는 사람:**
1. 페라 월렛에서 해당 토큰 선택
2. "Send" 버튼
3. 받는 주소 입력
4. 수량 입력
5. 전송 (수수료: 0.001 ALGO)

---

## 문제 해결

### "Create Asset" 메뉴가 없어요
- 페라 월렛 최신 버전으로 업데이트
- 또는 웹 버전 사용: https://web.perawallet.app

### 수수료가 부족해요
- 최소 0.1 ALGO 필요
- 페라 월렛에서 ALGO 잔액 확인

### 토큰이 표시되지 않아요
- 토큰 생성 직후에는 자동으로 표시됨
- Asset ID로 검색하여 추가 가능

---

## 다음 단계

토큰 생성 후:

1. **Asset ID 기록**
2. **테스트 전송** (본인의 다른 계정으로)
3. **거래소/판매 시스템 연동** 준비
4. **사용자에게 배포** 시작

---

생성 완료 후 Asset ID를 알려주시면, Python으로 자동 전송 스크립트를 만들어드리겠습니다!
