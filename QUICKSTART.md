# 🚀 PAM-TALK 빠른 시작 가이드

## 5분만에 시작하기 ⚡

### 1️⃣ 설치 (1분)
```bash
# 저장소 클론
git clone https://github.com/your-repo/pam-talk.git
cd pam-talk

# 자동 설치
chmod +x setup.sh && ./setup.sh
```

### 2️⃣ 실행 (30초)
```bash
python run_demo.py
```

### 3️⃣ 확인 (즉시)
- 브라우저가 자동으로 열립니다: http://localhost:5000
- 데모 시나리오 중 하나를 선택하세요

### 4️⃣ 데모 선택 (2-3분)
```
1. 농장 등록 및 ESG 토큰 발행 데모    ← 추천 (초보자용)
2. 수요 예측 및 거래 생성 데모
3. 전체 시스템 통합 데모             ← 추천 (전체 기능)
```

---

## 🎯 주요 체험 포인트

### ✅ 보게 될 것들
- **농장 등록**: 실제 농장 정보 입력 과정
- **ESG 평가**: 지속가능성 점수 계산
- **AI 예측**: 농산물 수요 예측 결과
- **블록체인**: 토큰 발행 및 거래 기록
- **대시보드**: 실시간 데이터 시각화

### 📊 예상 결과
```
✅ 농장 등록 성공! (농장 ID: FARM_021)
✅ ESG 평가 완료! (점수: 85/100)
✅ 토큰 발행 성공! (850 SUSTAIN)
✅ 수요 예측 완료! (정확도: 87%)
✅ 거래 생성 완료! (예상 거래액: 3,200,000원)
```

---

## 🆘 문제 발생시

### Python 없음
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# macOS (Homebrew)
brew install python3

# Windows: https://python.org에서 다운로드
```

### 포트 충돌
```bash
# 포트 5000이 사용 중인 경우
export API_PORT=5001
python run_demo.py
```

### 패키지 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📚 더 자세한 정보

- **전체 사용설명서**: [README.md](README.md)
- **API 문서**: http://localhost:5000/api/docs
- **테스트 실행**: `python run_tests.py`

---

**🎉 준비 완료! 이제 PAM-TALK 시스템을 체험해보세요!**