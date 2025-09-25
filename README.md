# PAM-TALK: Platform for Active Meta
## 지역 농수축산물 유통 혁신 SNS 플랫폼

PAM-TALK는 단순한 농업 플랫폼이 아닌, **Platform for Active Meta** - 지역 농수축산물 유통 혁신을 위한 소셜 네트워킹 플랫폼입니다.

### 🌟 핵심 기능
- 🌱 **탄소발자국 추적** 및 개인 참여 시스템
- 🤝 **농촌-도시 직접 연결** SNS
- 💰 **지역 기반 유통 활성화**
- ⚡ **이윤 창출 구조**

---

## 📋 목차

1. [시스템 요구사항](#-시스템-요구사항)
2. [설치 가이드](#-설치-가이드)
3. [첫 실행 가이드](#-첫-실행-가이드)
4. [데모 시나리오](#-데모-시나리오)
5. [주요 기능](#-주요-기능)
6. [API 사용법](#-api-사용법)
7. [문제해결](#-문제해결)
8. [고급 사용법](#-고급-사용법)

---

## 🖥️ 시스템 요구사항

### 필수 요구사항
- **Python**: 3.8 이상 (권장: 3.9+)
- **운영체제**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **메모리**: 최소 4GB RAM (권장: 8GB+)
- **저장공간**: 최소 2GB 여유공간

### 권장 사항
- **인터넷 연결**: 외부 API 및 블록체인 접근용
- **웹브라우저**: Chrome, Firefox, Safari 최신 버전

---

## 🚀 설치 가이드

### 방법 1: 자동 설치 (권장)

1. **저장소 다운로드**
```bash
git clone https://github.com/your-repo/pam-talk.git
cd pam-talk
```

2. **자동 환경 설정 실행**
```bash
# Linux/macOS
chmod +x setup.sh
./setup.sh

# Windows
setup.sh  # Git Bash 사용
```

3. **설치 완료 확인**
```bash
source activate_env.sh  # 가상환경 활성화
python run_demo.py      # 데모 실행
```

### 방법 2: 수동 설치

1. **가상환경 생성**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **환경변수 설정**
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 설정값 입력
```

4. **디렉토리 구조 확인**
```
pam-talk/
├── api/                 # REST API 서버
├── ai_models/           # AI 모델 파일
├── contracts/           # 스마트 계약
├── data/               # 데이터 파일
├── static/             # 프론트엔드 자원
├── tests/              # 테스트 코드
├── run_demo.py         # 메인 데모 실행기
├── demo_scenarios.py   # 데모 시나리오
├── setup.sh           # 환경 설정 스크립트
└── README.md          # 이 파일
```

---

## 🎯 첫 실행 가이드

### 단계별 실행 방법

#### 1단계: 환경 준비
```bash
# 가상환경 활성화
source activate_env.sh  # Linux/macOS
# 또는
activate_env.bat       # Windows
```

#### 2단계: 데모 시스템 시작
```bash
python run_demo.py
```

#### 3단계: 브라우저에서 확인
- 자동으로 브라우저가 열립니다
- 수동 접속: http://localhost:5000

#### 4단계: 데모 선택
콘솔에서 다음 중 선택:
```
1. 농장 등록 및 ESG 토큰 발행 데모
2. 수요 예측 및 거래 생성 데모
3. 전체 시스템 통합 데모
0. 데모 스킵
```

### 실행 화면 예시
```
╔══════════════════════════════════════════════════════════════╗
║                    🚀 PAM-TALK 데모 시스템                    ║
║          블록체인 기반 AI 농업 예측 플랫폼 데모                  ║
╚══════════════════════════════════════════════════════════════╝

📦 1단계: 의존성 확인 중...
✅ Python 3.9.7 확인
✅ flask 설치됨
✅ 모든 의존성 확인 완료

📊 2단계: 모의 데이터 생성 중...
✅ 농장 데이터 생성 완료
✅ 거래 데이터 생성 완료
✅ 수요 예측 데이터 생성 완료

🚀 3단계: API 서버 시작 중...
✅ API 서버 시작 완료!

🌐 4단계: 대시보드 열기...
✅ 웹 브라우저에서 대시보드 열기 완료
```

---

## 🎭 데모 시나리오

### 시나리오 1: 농장 등록 및 ESG 토큰 발행

**목적**: 새로운 농장을 시스템에 등록하고 지속가능성 평가를 통해 토큰을 발행합니다.

**실행 과정**:
1. 기존 농장 현황 조회
2. 새 농장 등록 (그린팜 데모농장)
3. ESG 평가 실행 (환경, 사회, 지배구조)
4. 지속가능성 토큰 발행
5. 결과 요약

**예상 결과**:
```
✅ 농장 등록 성공!
   농장 ID: FARM_021
   할당된 지갑 주소: 0x742d35Cc...

✅ ESG 평가 완료!
   종합 ESG 점수: 85/100
   환경(E): 83
   사회(S): 88
   지배구조(G): 84

✅ 토큰 발행 성공!
   발행량: 850 SUSTAIN
   트랜잭션 해시: 0x9f4b2a1c...
```

### 시나리오 2: 수요 예측 및 거래 생성

**목적**: AI를 활용해 농산물 수요를 예측하고 스마트 계약 기반 거래를 자동 생성합니다.

**실행 과정**:
1. 현재 시장 데이터 조회
2. AI 수요 예측 실행 (Prophet 모델)
3. 스마트 계약 기반 거래 생성
4. 공급업체 매칭 프로세스
5. 결과 요약

**예상 결과**:
```
✅ 수요 예측 완료!
   예측 기간: 30일
   평균 일일 수요: 1,250kg
   최대 수요일: 2024-01-15
   모델 정확도 (MAPE): 12.5%

✅ 스마트 계약 거래 생성 완료!
   거래 ID: TRADE_045
   예상 거래액: 3,200,000원

✅ 3개 공급업체 매칭 완료!
   1. 스마트팜 A - 매칭 점수: 92.5/100
```

### 시나리오 3: 전체 시스템 통합

**목적**: 농장 등록부터 거래 완료까지 전체 워크플로우를 시연합니다.

**실행 과정**:
1. 시스템 전체 상태 점검
2. 다중 농장 일괄 등록 (5개 농장)
3. 통합 ESG 평가 프로세스
4. 다중 작물 수요 예측 (쌀, 밀, 옥수수, 콩)
5. 자동화된 다중 거래 생성
6. 토큰 경제 시뮬레이션
7. 종합 결과 대시보드

**예상 결과**:
```
🎯 PAM-TALK 시스템 통합 데모 완료!
══════════════════════════════════════════════

📊 처리된 데이터:
   • 등록된 농장: 5개
   • 완료된 ESG 평가: 5건
   • 수행된 수요 예측: 4개 작물
   • 생성된 거래: 4건
   • 발행된 토큰: 4,200 SUSTAIN

🌟 시스템 성능:
   • 응답 시간: < 2초
   • 예측 정확도: > 85%
   • 거래 성공률: 100%
```

---

## 🔧 주요 기능

### 1. 농장 관리
- **농장 등록**: 농장 정보, 작물 유형, 지속가능성 실천사항 등록
- **ESG 평가**: 환경(E), 사회(S), 지배구조(G) 종합 평가
- **인증 관리**: 유기농 인증, 지속가능성 인증 추적

### 2. AI 예측 시스템
- **수요 예측**: Prophet 모델 기반 농산물 수요 예측
- **가격 예측**: 시장 데이터 분석을 통한 가격 동향 예측
- **이상 탐지**: 비정상적인 거래 패턴 감지

### 3. 블록체인 통합
- **스마트 계약**: 자동화된 거래 실행
- **토큰 발행**: ESG 점수 기반 지속가능성 토큰 생성
- **투명성**: 모든 거래 기록의 불변성 보장

### 4. 대시보드
- **실시간 모니터링**: 농장 현황, 거래 상태 실시간 추적
- **통계 분석**: 성과 지표, 트렌드 분석
- **시각화**: 차트와 그래프를 통한 데이터 시각화

---

## 📡 API 사용법

### 기본 엔드포인트

#### 시스템 상태
```bash
# 헬스 체크
curl http://localhost:5000/health

# 시스템 통계
curl http://localhost:5000/api/dashboard/stats
```

#### 농장 관리
```bash
# 농장 목록 조회
curl http://localhost:5000/api/farms

# 새 농장 등록
curl -X POST http://localhost:5000/api/farms/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트 농장",
    "location": "경기도 용인시",
    "crop_type": "rice",
    "area": 100.5,
    "organic_certified": true
  }'
```

#### 예측 서비스
```bash
# 수요 예측
curl -X POST http://localhost:5000/api/predict/demand \
  -H "Content-Type: application/json" \
  -d '{
    "crop_type": "rice",
    "prediction_period": 30,
    "include_weather": true
  }'
```

#### 거래 관리
```bash
# 거래 생성
curl -X POST http://localhost:5000/api/trades/create \
  -H "Content-Type: application/json" \
  -d '{
    "crop_type": "rice",
    "quantity": 1000,
    "max_price": 3.5,
    "delivery_date": "2024-02-01"
  }'
```

### 응답 형식

모든 API는 JSON 형식으로 응답합니다:

```json
{
  "success": true,
  "data": {
    "farm_id": "FARM_001",
    "name": "테스트 농장",
    "wallet_address": "0x742d35Cc6Db050e3AAf7543e..."
  },
  "message": "농장이 성공적으로 등록되었습니다",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🔍 문제해결

### 자주 발생하는 문제

#### 1. 의존성 설치 오류
**문제**: `pip install` 시 패키지 설치 실패
**해결**:
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. API 서버 시작 실패
**문제**: 포트 5000이 이미 사용 중
**해결**:
```bash
# 포트 사용 프로세스 확인
netstat -an | findstr :5000    # Windows
lsof -i :5000                  # Linux/macOS

# 다른 포트 사용
export API_PORT=5001
python run_demo.py
```

#### 3. 브라우저에서 접속 불가
**문제**: `localhost:5000` 접속 안됨
**해결**:
```bash
# 방화벽 확인
# Windows: Windows Defender 방화벽 설정
# macOS: 시스템 환경설정 > 보안 및 개인 정보 보호 > 방화벽

# 수동 브라우저 접속
http://127.0.0.1:5000
```

#### 4. 데이터 생성 실패
**문제**: 모의 데이터 생성 중 오류
**해결**:
```bash
# 데이터 디렉토리 권한 확인
chmod 755 data/
mkdir -p data

# 수동 데이터 생성
python basic_setup.py
```

### 로그 확인

문제 발생 시 로그를 확인하세요:
```bash
# 일반 로그
tail -f pamtalk.log

# API 서버 로그
cd api && python app.py
```

### 지원 요청

문제가 지속되면:
1. 로그 파일 수집
2. 시스템 정보 확인: `python --version`, `pip list`
3. GitHub Issues에 문제 보고

---

## 🎓 고급 사용법

### 커스텀 설정

#### 환경변수 커스터마이징
`.env` 파일 수정:
```bash
# API 설정
API_HOST=0.0.0.0
API_PORT=8080
API_DEBUG=False

# AI 모델 설정
AI_MODEL_PATH=./custom_models
PREDICTION_CACHE_TTL=7200

# 블록체인 설정
BLOCKCHAIN_NETWORK=mainnet
PRIVATE_KEY=your-production-key
```

#### 커스텀 농장 데이터
`data/custom_farms.json` 생성:
```json
{
  "farms": [
    {
      "name": "나의 농장",
      "location": "전라북도 김제시",
      "crop_type": "organic_rice",
      "area": 200.0,
      "sustainability_practices": [
        "드론 기반 정밀농업",
        "IoT 센서 모니터링"
      ]
    }
  ]
}
```

### 개발자 모드

#### API 개발 서버 실행
```bash
cd api
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

#### 테스트 실행
```bash
# 전체 테스트
python run_tests.py

# 개별 테스트
pytest tests/test_api.py -v

# 커버리지 포함
pytest --cov=. --cov-report=html
```

#### 새로운 예측 모델 추가
```python
# ai_models/custom_model.py
class CustomPredictor:
    def predict(self, data):
        # 사용자 정의 예측 로직
        return predictions
```

### 프로덕션 배포

#### Docker 컨테이너화
```bash
# Dockerfile 생성 후
docker build -t pam-talk .
docker run -p 5000:5000 pam-talk
```

#### 클라우드 배포
- AWS EC2 / GCP Compute Engine
- Heroku / Vercel
- Azure App Service

---

## 🎯 다음 단계

### 학습 권장 사항
1. **블록체인 기초**: Algorand 스마트 계약 개발
2. **AI/ML**: Prophet 모델, 시계열 예측
3. **웹 개발**: Flask, RESTful API 설계
4. **DevOps**: Docker, CI/CD 파이프라인

### 확장 가능성
- **모바일 앱**: React Native / Flutter
- **IoT 연동**: 센서 데이터 실시간 수집
- **DeFi 통합**: 탈중앙화 금융 서비스 연계
- **글로벌 확장**: 다국어 지원, 지역별 특화

---

**📞 지원 문의**: GitHub Issues 또는 이메일
**📚 추가 문서**: `/docs` 디렉토리 참조
**🔗 공식 사이트**: https://pam-talk.io

---
*PAM-TALK v1.0 | 2024년 1월 업데이트*

## Testing

### 통합 테스트 시스템

PAM-TALK는 완전한 통합 테스트 시스템을 포함합니다:

#### 테스트 실행 방법:

1. **자동화된 테스트 실행:**
```bash
python run_tests.py
```

2. **Windows 환경:**
```cmd
run_tests.bat
```

3. **개별 테스트 실행:**
```bash
# 통합 테스트만
pytest tests/integration_test.py -v

# 모든 테스트
pytest -v

# 커버리지 포함
pytest --cov=. --cov-report=html
```

#### 테스트 구성:

- **농장 등록 → ESG 점수 계산 → 토큰 발행 플로우**
- **수요 예측 → 거래 생성 → 이상 탐지 플로우**
- **블록체인 기록 → 데이터 조회 → 대시보드 표시 플로우**
- **API 엔드포인트 전체 테스트**
- **성능 측정 (응답 시간, 처리량)**

#### 테스트 보고서:

테스트 완료 후 다음 보고서가 생성됩니다:
- `test_report.html` - HTML 형식 상세 보고서
- `test_report.json` - JSON 형식 데이터
- `htmlcov/index.html` - 코드 커버리지 보고서

#### 테스트 실행 전 준비사항:

1. API 서버 실행:
```bash
cd api && python app.py
```

2. 필요한 의존성 설치:
```bash
pip install -r requirements.txt
```

## Development

The project is structured to support:
- Smart contract development (contracts/)
- AI model development (ai_models/)
- API development (api/)
- Testing (tests/)

Each directory contains its own components for modular development.
## 🚀 온라인 데모

**라이브 데모**: https://pam-talk.vercel.app
**GitHub**: https://github.com/sumilee-pcu/PAM-TALK

---

## 💻 기술 스택

- **백엔드**: Python Flask, REST API
- **프론트엔드**: HTML5, CSS3, ES6+ JavaScript
- **배포**: Vercel + GitHub
- **스타일링**: 반응형 웹 디자인
