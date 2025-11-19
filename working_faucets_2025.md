# 2025년 작동하는 알고랜드 테스트넷 Faucet 목록

## 🟢 확인된 작동 중인 Faucet들

### 1. **공식 알고랜드 테스트넷 뱅크** (최우선 추천)
- **URL**: https://bank.testnet.algorand.network/
- **연결 상태**: ✅ 정상 작동
- **제공량**: 5 ALGO / 24시간
- **인증**: Google 로그인 필요
- **특징**: 공식 알고랜드 재단 운영

### 2. **Triangle Platform Faucet**
- **URL**: https://faucet.triangleplatform.com/algorand/testnet
- **연결 상태**: ✅ 정상 작동
- **제공량**: 1 ALGO / 24시간
- **특징**: 40개 이상 네트워크 지원하는 믿을만한 플랫폼

### 3. **Folks Finance Faucet**
- **URL**: Folks Finance DeFi 플랫폼 내
- **제공량**: 1 ALGO / 24시간
- **특징**: DeFi 테스트용으로 최적화

## ❌ 현재 작동하지 않는 Faucet

### testnet.algoexplorer.io/dispenser
- **문제**: DNS는 해석되지만 실제 연결 불가
- **원인**: 서비스 중단 또는 지역 차단
- **상태**: 2025년 9월 현재 한국에서 접근 불가

## 🚀 즉시 사용 가능한 해결책

### 방법 1: 공식 뱅크 사용 (가장 확실)
```
1. https://bank.testnet.algorand.network/ 접속
2. Google 계정으로 로그인
3. reCAPTCHA 완료
4. 지갑 주소 입력: MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM
5. "Dispense" 클릭
6. 200 상태 코드 확인으로 성공 여부 판단
```

### 방법 2: Triangle Platform 사용
```
1. https://faucet.triangleplatform.com/algorand/testnet 접속
2. 지갑 주소 입력
3. CAPTCHA 완료
4. "Request Tokens" 클릭
5. 몇 분 내 토큰 도착
```

## 🔧 프로그래밍 방식 액세스

### AlgoKit 사용
```bash
# AlgoKit 설치 (Python)
pip install algokit

# 계정 자동 충전
algokit fund --receiver MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM --amount 5
```

### API 직접 호출
```python
import requests

# 공식 테스트넷 뱅크 API 사용
def request_test_algo(address):
    url = "https://bank.testnet.algorand.network/api/dispense"
    payload = {"address": address}
    response = requests.post(url, json=payload)
    return response.status_code == 200
```

## 📊 추천 순서

1. **1순위**: 공식 알고랜드 테스트넷 뱅크 (5 ALGO)
2. **2순위**: Triangle Platform (1 ALGO)
3. **3순위**: Folks Finance (1 ALGO)

## ⚠️ 중요 사항

- 각 faucet마다 24시간 제한 있음
- VPN 사용 시 일부 faucet 차단될 수 있음
- 테스트넷 토큰은 실제 가치 없음
- 계정 주소 정확히 입력 필수

## 🎯 PAM-TALK 프로젝트용 권장 방법

현재 상황에서는 **공식 알고랜드 테스트넷 뱅크**를 사용하는 것이 가장 확실합니다:

```
https://bank.testnet.algorand.network/
계정: MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM
```

충전 후 PAM 토큰 재발행과 블록체인 연동 테스트를 진행할 수 있습니다.