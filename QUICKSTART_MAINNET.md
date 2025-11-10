# 🚀 Algorand 메인넷 빠른 시작 가이드

5분 안에 메인넷에 연결하는 간단한 가이드입니다!

## 📝 단계별 가이드

### 1️⃣ 지갑 준비 (2분)

**Pera Wallet 설치 및 설정:**
1. 앱 스토어에서 "Pera Wallet" 다운로드
2. "Create a New Wallet" 선택
3. **25단어 니모닉을 종이에 적어서 안전하게 보관** ⚠️
4. 지갑 주소 복사 (algo로 시작하는 긴 문자열)

### 2️⃣ ALGO 전송 (1분)

- 거래소에서 구매한 ALGO를 Pera Wallet 주소로 전송
- 최소 1 ALGO 권장

### 3️⃣ 환경 설정 (1분)

```bash
cd PAM-TALK

# .env 파일 생성
cp .env.mainnet.example .env

# .env 파일 편집
nano .env
```

**최소 설정 (3줄만 변경):**
```bash
ALGORAND_NETWORK=mainnet
ALGORAND_ALGOD_ADDRESS=https://mainnet-api.algonode.cloud
SIMULATION_MODE=False
```

### 4️⃣ 연결 테스트 (1분)

```bash
# 테스트 실행
python test_mainnet_connection.py
```

**예상 출력:**
```
✅ 메인넷 연결 성공!
📊 네트워크: mainnet-v1.0
```

---

## ✅ 완료!

이제 메인넷에서 실제 거래를 할 수 있습니다!

---

## 🔗 다음 단계

- **상세 가이드**: [MAINNET_SETUP.md](MAINNET_SETUP.md)
- **API 문서**: [README.md](README.md)
- **보안 가이드**: [MAINNET_SETUP.md#보안-모범-사례](MAINNET_SETUP.md#보안-모범-사례)

---

## 💡 자주 묻는 질문

**Q: 얼마나 많은 ALGO가 필요한가요?**
- 최소: 0.1 ALGO (계정 유지)
- 권장: 1-5 ALGO (트랜잭션 수수료 포함)

**Q: 무료 API로 충분한가요?**
- 테스트/개발: 충분합니다 (AlgoNode 무료)
- 프로덕션: PureStake 유료 플랜 권장

**Q: 니모닉을 잃어버리면?**
- ⚠️ **복구 불가능합니다!** 안전하게 보관하세요!

---

## 🆘 문제가 있나요?

**연결 실패:**
```bash
# 설정 확인
cat .env | grep ALGORAND

# 네트워크 연결 확인
curl https://mainnet-api.algonode.cloud/health
```

**잔액 조회 실패:**
- 지갑 주소가 올바른지 확인
- 메인넷에 ALGO를 전송했는지 확인

---

**더 자세한 내용**: [MAINNET_SETUP.md](MAINNET_SETUP.md) 참조
