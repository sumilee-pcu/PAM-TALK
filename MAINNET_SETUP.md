# Algorand 메인넷 전환 가이드 🚀

PAM-TALK 프로젝트를 테스트넷에서 메인넷으로 전환하는 방법을 안내합니다.

## 📋 목차
1. [사전 준비](#사전-준비)
2. [지갑 설정](#지갑-설정)
3. [환경 변수 설정](#환경-변수-설정)
4. [API 서비스 설정](#api-서비스-설정)
5. [계정 연결](#계정-연결)
6. [테스트 및 검증](#테스트-및-검증)

---

## 🎯 사전 준비

### 필요한 것들
- ✅ **ALGO 보유** (메인넷용 - 이미 구매하셨다고 하셨네요!)
- ✅ **Algorand 지갑** (Pera Wallet 또는 Defly Wallet 권장)
- ✅ **Algorand API 서비스** (AlgoNode 또는 PureStake)

### ALGO 최소 필요량
- 계정 생성: 0.1 ALGO (최소 잔액)
- 트랜잭션 수수료: 0.001 ALGO/건
- **권장**: 최소 1 ALGO 이상 보유

---

## 💳 지갑 설정

### 1. Pera Wallet 설정 (권장)

#### 모바일 앱 다운로드
- **iOS**: App Store에서 "Pera Wallet" 검색
- **Android**: Google Play에서 "Pera Wallet" 검색

#### 지갑 생성
```
1. 앱 실행
2. "Create a New Wallet" 선택
3. 25단어 복구 구문(Mnemonic) 안전하게 보관 ⚠️ 절대 공유 금지!
4. PIN 또는 생체 인증 설정
5. 메인넷 계정 주소 확인 (algo로 시작)
```

### 2. Defly Wallet (대안)
- Chrome Extension 또는 모바일 앱 설치
- 동일한 과정으로 계정 생성

### 3. 계정 정보 기록
```
지갑 주소: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
니모닉 구문: (25단어 - 안전한 곳에 보관!)
```

⚠️ **보안 주의사항**
- 니모닉 구문은 절대 온라인에 공유하지 마세요
- 스크린샷도 피하고 종이에 적어 안전하게 보관하세요
- Private Key도 마찬가지로 절대 노출 금지

---

## ⚙️ 환경 변수 설정

### 1. `.env` 파일 생성

PAM-TALK 프로젝트 루트에 `.env` 파일을 생성합니다:

```bash
cd PAM-TALK
cp .env.example .env
```

### 2. `.env` 파일 수정

```bash
# Algorand 메인넷 설정
ALGORAND_NETWORK=mainnet

# AlgoNode 무료 API (권장)
ALGORAND_ALGOD_ADDRESS=https://mainnet-api.algonode.cloud
ALGORAND_ALGOD_TOKEN=
ALGORAND_INDEXER_ADDRESS=https://mainnet-idx.algonode.cloud
ALGORAND_INDEXER_TOKEN=

# 시뮬레이션 모드 OFF (실제 메인넷 사용)
SIMULATION_MODE=False

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=your-super-secret-production-key-here

# Database Configuration
DATABASE_URL=sqlite:///pam_talk_mainnet.db
```

### 3. 설정 설명

| 항목 | 테스트넷 | 메인넷 |
|------|---------|--------|
| `ALGORAND_NETWORK` | `testnet` | `mainnet` |
| `ALGORAND_ALGOD_ADDRESS` | testnet URL | `https://mainnet-api.algonode.cloud` |
| `SIMULATION_MODE` | `True` | `False` |
| `FLASK_ENV` | `development` | `production` |

---

## 🌐 API 서비스 설정

### 옵션 1: AlgoNode (무료, 권장)

```bash
# 별도 가입 불필요!
ALGORAND_ALGOD_ADDRESS=https://mainnet-api.algonode.cloud
ALGORAND_ALGOD_TOKEN=
ALGORAND_INDEXER_ADDRESS=https://mainnet-idx.algonode.cloud
ALGORAND_INDEXER_TOKEN=
```

✅ **장점**: 무료, 가입 불필요, 안정적
❌ **단점**: Rate limit (분당 15 요청)

### 옵션 2: PureStake (프리미엄)

1. **가입**: https://developer.purestake.io/signup
2. **API Key 발급**: Dashboard에서 API Key 생성
3. **.env 설정**:

```bash
ALGORAND_ALGOD_ADDRESS=https://mainnet-algorand.api.purestake.io/ps2
ALGORAND_ALGOD_TOKEN=your-purestake-api-key
ALGORAND_INDEXER_ADDRESS=https://mainnet-algorand.api.purestake.io/idx2
ALGORAND_INDEXER_TOKEN=your-purestake-api-key
```

✅ **장점**: 높은 처리량, 프로덕션 적합
❌ **단점**: 유료 (무료 티어는 제한적)

---

## 🔗 계정 연결

### 방법 1: 니모닉 구문 사용 (개발/테스트용)

⚠️ **주의**: 프로덕션 환경에서는 니모닉을 코드에 직접 넣지 마세요!

```python
from algosdk import mnemonic, account

# 지갑에서 받은 25단어 니모닉
my_mnemonic = "word1 word2 word3 ... word25"

# Private Key 복원
private_key = mnemonic.to_private_key(my_mnemonic)

# 주소 확인
address = account.address_from_private_key(private_key)
print(f"계정 주소: {address}")
```

### 방법 2: 환경 변수로 관리 (권장)

`.env` 파일에 추가:

```bash
# 메인 계정 (절대 Git에 커밋하지 말 것!)
MAIN_ACCOUNT_MNEMONIC=word1 word2 word3 ... word25
```

`config.py`에 추가:

```python
class Config:
    # ... 기존 설정 ...

    # 메인넷 계정 설정
    MAIN_ACCOUNT_MNEMONIC = os.getenv('MAIN_ACCOUNT_MNEMONIC', '')
```

### 방법 3: WalletConnect 통합 (가장 안전)

웹 애플리케이션에서 Pera Wallet과 연동:

```javascript
// Frontend에서 WalletConnect 사용
import { PeraWalletConnect } from "@perawallet/connect";

const peraWallet = new PeraWalletConnect();

// 지갑 연결
const accounts = await peraWallet.connect();
console.log("연결된 계정:", accounts);

// 트랜잭션 서명 요청
const signedTxn = await peraWallet.signTransaction([txn]);
```

---

## 🧪 테스트 및 검증

### 1. 연결 테스트 스크립트 생성

`test_mainnet_connection.py` 파일 생성:

```python
from algorand_utils import AlgorandSimulator
from algosdk import account, mnemonic

def test_mainnet_connection():
    """메인넷 연결 테스트"""
    print("=" * 50)
    print("🔍 Algorand 메인넷 연결 테스트")
    print("=" * 50)

    # AlgorandSimulator 초기화
    algo_sim = AlgorandSimulator()

    # 네트워크 상태 확인
    status = algo_sim.get_network_status()
    print(f"\n📊 네트워크 상태:")
    print(f"  - 모드: {status.get('mode')}")
    print(f"  - 연결 상태: {status.get('connected')}")
    print(f"  - 네트워크: {status.get('network')}")

    if status.get('connected'):
        print(f"  - 마지막 라운드: {status.get('last_round')}")
        print(f"  - 노드 주소: {status.get('node_address')}")
        print("\n✅ 메인넷 연결 성공!")
    else:
        print("\n❌ 메인넷 연결 실패!")
        print("⚠️  .env 파일 설정을 확인하세요")
        return False

    return True

def test_account_balance(address):
    """계정 잔액 확인"""
    algo_sim = AlgorandSimulator()

    print(f"\n💰 계정 잔액 조회: {address[:8]}...{address[-8:]}")

    try:
        balance = algo_sim.get_balance(address)
        balance_algo = balance / 1_000_000  # microAlgos to ALGOs

        print(f"  - 잔액: {balance_algo:.6f} ALGO")
        print(f"  - microAlgos: {balance:,}")

        if balance_algo < 0.1:
            print("  ⚠️  잔액이 부족합니다. 최소 0.1 ALGO 필요")
        else:
            print("  ✅ 잔액 충분")

        return balance_algo
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return 0

if __name__ == "__main__":
    # 1. 연결 테스트
    if test_mainnet_connection():
        print("\n" + "=" * 50)

        # 2. 계정 잔액 테스트
        my_address = input("\n지갑 주소를 입력하세요: ").strip()
        if my_address:
            test_account_balance(my_address)

        print("\n" + "=" * 50)
        print("✅ 모든 테스트 완료!")
```

### 2. 테스트 실행

```bash
python test_mainnet_connection.py
```

### 3. 예상 출력

```
==================================================
🔍 Algorand 메인넷 연결 테스트
==================================================

📊 네트워크 상태:
  - 모드: real
  - 연결 상태: True
  - 네트워크: mainnet-v1.0
  - 마지막 라운드: 35123456
  - 노드 주소: https://mainnet-api.algonode.cloud

✅ 메인넷 연결 성공!

==================================================

지갑 주소를 입력하세요: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

💰 계정 잔액 조회: XXXXXXXX...XXXXXXXX
  - 잔액: 5.234567 ALGO
  - microAlgos: 5,234,567
  ✅ 잔액 충분

==================================================
✅ 모든 테스트 완료!
```

---

## 🚀 프로덕션 체크리스트

메인넷 배포 전 확인사항:

- [ ] `.env` 파일에 `ALGORAND_NETWORK=mainnet` 설정
- [ ] `SIMULATION_MODE=False` 설정
- [ ] API 엔드포인트가 메인넷용으로 설정됨
- [ ] 지갑에 충분한 ALGO 보유 (최소 1 ALGO)
- [ ] 니모닉 구문과 Private Key를 안전하게 보관
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있음
- [ ] 연결 테스트 스크립트 실행 완료
- [ ] 계정 잔액 확인 완료
- [ ] 백업 계획 수립 (키 복구 방법)

---

## 🔐 보안 모범 사례

### 절대 하지 말아야 할 것
- ❌ Private Key나 Mnemonic을 Git에 커밋
- ❌ 코드에 직접 하드코딩
- ❌ 스크린샷으로 저장
- ❌ 이메일이나 메신저로 전송
- ❌ 클라우드에 평문으로 저장

### 해야 할 것
- ✅ 환경 변수로 관리 (`.env` 사용)
- ✅ `.env`를 `.gitignore`에 추가
- ✅ 니모닉을 종이에 적어 금고에 보관
- ✅ 프로덕션에서는 WalletConnect 사용
- ✅ 정기적으로 계정 잔액 모니터링
- ✅ 트랜잭션 로그 기록

---

## 📚 추가 리소스

- **Algorand 공식 문서**: https://developer.algorand.org/
- **Pera Wallet**: https://perawallet.app/
- **AlgoNode**: https://algonode.io/
- **Algorand Explorer**: https://algoexplorer.io/
- **테스트넷 디스펜서**: https://dispenser.testnet.aws.algodev.network/

---

## 🆘 문제 해결

### "Connection refused" 오류
```
✅ 해결: ALGORAND_ALGOD_ADDRESS가 올바른지 확인
✅ AlgoNode 사용: https://mainnet-api.algonode.cloud
```

### "Insufficient balance" 오류
```
✅ 해결: 계정에 ALGO 전송 필요
✅ 최소: 0.1 ALGO (계정 생성) + 0.001 ALGO (트랜잭션)
```

### "Invalid mnemonic" 오류
```
✅ 해결: 25단어가 정확한지 확인
✅ 단어 사이 공백 하나만 사용
✅ 철자 확인
```

---

## 💬 도움이 필요하신가요?

- Algorand Discord: https://discord.gg/algorand
- 한국 커뮤니티: Algorand Korea 텔레그램

---

**마지막 업데이트**: 2025년 1월
**작성자**: Claude Code Assistant 🤖
