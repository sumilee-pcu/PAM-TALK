# 🌱 PAM-TALK: Platform for Active Meta

## 지역 농수축산물 유통 혁신 SNS 플랫폼

PAM-TALK는 **Platform for Active Meta** - 지역 농수축산물 유통 혁신을 위한 소셜 네트워킹 플랫폼입니다.
단순한 농업 홈페이지가 아닌, 농촌과 도시를 연결하는 완전한 소셜 생태계를 구현합니다.

---

## 🎯 **핵심 미션**

### **1. 탄소발자국 제거에 개인별 참여 가능**
- 🌍 개인별 탄소발자국 실시간 추적
- 🏆 에코 포인트 리워드 시스템
- 📊 탄소 절약량 가시화 및 챌린지

### **2. 농촌-도시 연결**
- 👨‍🌾 농부와 소비자 직접 소통 SNS
- 🤝 생산자-소비자 실시간 매칭
- 📱 농산물 스토리텔링 플랫폼

### **3. 이윤 창출 구조**
- 💰 중간 유통업체 제거로 농부 수익 극대화
- 🏪 지역 기반 직거래 활성화
- 🔄 순환 경제 생태계 구축

### **4. 지역 기반 유통 및 거래 활성화 SNS**
- 🗺️ 지역별 농산물 네트워킹
- 📍 로컬 푸드 커뮤니티 형성
- 🚚 최적화된 지역 물류 네트워크

---

## 🚀 **라이브 데모**

### **🌐 온라인 플랫폼**
**메인 사이트**: [https://pam-talk.vercel.app](https://pam-talk.vercel.app)

**주요 기능 체험:**
- 실시간 소셜 피드
- 탄소 챌린지 참여
- 농부-소비자 소통
- 에코 포인트 시스템

---

## 🔗 **Algorand 메인넷 블록체인 통합**

### **블록체인 기반 신뢰성 보장**

#### **🏛️ Algorand 메인넷 활용**
- **스마트 계약**: 투명한 거래 보장
- **ESG 토큰**: 탄소 절약 기여도 토큰화
- **탈중앙화 신원 인증**: 농부/소비자 신원 검증
- **공급망 추적**: Farm-to-Table 완전 투명성

#### **🪙 토큰 이코노미**
```
PAM Token (Algorand ASA)
├── 탄소 절약 보상
├── 지역 거래 인센티브
├── 플랫폼 거버넌스 참여
└── ESG 임팩트 증명
```

#### **⛓️ 블록체인 인프라**
- **네트워크**: Algorand MainNet
- **합의 알고리즘**: Pure Proof-of-Stake (PPoS)
- **트랜잭션**: 초당 1,000+ TPS, 4.5초 완결성
- **수수료**: 0.001 ALGO (약 $0.0003)

---

## 🏗️ **시스템 아키텍처**

### **프론트엔드 (소셜 플랫폼)**
```
├── 실시간 소셜 피드
├── 탄소발자국 대시보드
├── 농산물 마켓플레이스
├── 지역별 커뮤니티
└── 모바일 반응형 UI
```

### **백엔드 (API & 블록체인)**
```
├── Flask REST API 서버
├── Algorand SDK 통합
├── 스마트 계약 인터페이스
├── 실시간 데이터 처리
└── AI 기반 매칭 알고리즘
```

### **블록체인 레이어**
```
├── 농산물 정보 온체인 저장
├── 탄소 크레딧 토큰 발행
├── 거래 내역 불변 기록
├── ESG 임팩트 검증
└── 커뮤니티 거버넌스
```

---

## 📊 **플랫폼 임팩트**

### **🌍 환경적 임팩트**
- **탄소 절약량**: 실시간 측정 및 토큰화
- **로컬 푸드**: 운송 거리 최소화
- **친환경 농법**: 인센티브 제공

### **💰 경제적 임팩트**
- **농부 소득 증대**: 중간 마진 제거
- **소비자 가격 절약**: 직거래 할인
- **지역 경제 활성화**: 로컬 순환 경제

### **🤝 사회적 임팩트**
- **농촌-도시 소통**: SNS를 통한 이해 증진
- **식품 안전성**: 투명한 공급망
- **커뮤니티 형성**: 지역 기반 네트워킹

---

## 🛠️ **기술 스택**

### **프론트엔드**
- HTML5, CSS3, ES6+ JavaScript
- 반응형 웹 디자인 (Mobile-First)
- Real-time API Integration
- Progressive Web App (PWA) 지원

### **백엔드**
- **Python Flask**: REST API 서버
- **Algorand SDK**: 블록체인 통합
- **SQLite/PostgreSQL**: 데이터베이스
- **Redis**: 캐싱 및 세션 관리

### **블록체인**
- **Algorand MainNet**: 메인 블록체인
- **PyTeal**: 스마트 계약 개발
- **Algorand Standard Assets (ASA)**: 토큰 발행
- **Algorand Indexer**: 온체인 데이터 조회

### **배포 및 인프라**
- **Vercel**: 프론트엔드 배포
- **Railway/Heroku**: 백엔드 API 서버
- **GitHub Actions**: CI/CD 파이프라인
- **CloudFlare**: CDN 및 보안

---

## 🚀 **빠른 시작**

### **1. 저장소 클론**
```bash
git clone https://github.com/sumilee-pcu/PAM-TALK.git
cd PAM-TALK
```

### **2. 환경 설정**
```bash
# Python 환경 설정
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에서 Algorand 설정 입력
```

### **3. Algorand 연결 설정**
```python
# config.py에서 설정
ALGORAND_NODE = "https://mainnet-api.algonode.cloud"
ALGORAND_INDEXER = "https://mainnet-idx.algonode.cloud"
```

### **4. 로컬 서버 실행**
```bash
# 백엔드 API 서버
python pamtalk_social_platform.py

# 프론트엔드 (정적 파일 서빙)
# http://localhost:5003 에서 확인
```

---

## 📋 **주요 파일 구조**

```
PAM-TALK/
├── static/                    # 프론트엔드 파일
│   ├── index.html            # 메인 소셜 플랫폼
│   ├── demo.html             # 논문 발표용 데모
│   └── css/, js/             # 스타일 및 스크립트
├── pamtalk_social_platform.py # Flask API 서버
├── algorand_utils.py          # Algorand 블록체인 통합
├── contracts/                 # 스마트 계약
├── ai_models/                 # AI 예측 모델
└── vercel.json               # 배포 설정
```

---

## 🌟 **주요 기능**

### **📱 소셜 네트워킹**
- 농부 수확 스토리 공유
- 소비자 리뷰 및 평점
- 실시간 댓글 및 좋아요
- 지역별 트렌딩 토픽

### **🌱 탄소발자국 추적**
- 개인별 탄소 절약량 계산
- 로컬 푸드 구매 보상
- 탄소 챌린지 참여
- ESG 임팩트 토큰 획득

### **🛒 직거래 마켓플레이스**
- 농부-소비자 직접 거래
- 스마트 계약 기반 결제
- 지역별 배송 최적화
- 품질 보장 시스템

### **🏆 리워드 시스템**
- 에코 포인트 적립
- PAM 토큰 보상
- 커뮤니티 기여도 평가
- VIP 멤버십 혜택

---

## 📈 **로드맵**

### **Phase 1: MVP 출시** ✅
- 소셜 플랫폼 베타 버전
- 기본 탄소발자국 추적
- Algorand 테스트넷 연동

### **Phase 2: 메인넷 런칭** 🚧
- Algorand 메인넷 배포
- PAM 토큰 발행 및 유통
- 실제 농가 파트너십

### **Phase 3: 글로벌 확장** 📅
- 다국가 서비스 확장
- 대규모 농업 협동조합 연동
- 글로벌 탄소 크레딧 거래소

---

## 👥 **기여하기**

### **개발 참여**
1. Fork 후 새로운 기능 브랜치 생성
2. 코드 작성 및 테스트
3. Pull Request 제출

### **커뮤니티 참여**
- **Issues**: 버그 리포트 및 기능 제안
- **Discussions**: 아이디어 공유 및 토론
- **Wiki**: 문서화 기여

---

## 📞 **연락처**

### **프로젝트 문의**
- **Email**: support@pamtalk.co.kr
- **GitHub**: [@sumilee-pcu](https://github.com/sumilee-pcu)

### **파트너십 문의**
- 농가 및 농업 협동조합
- 지방자치단체
- ESG 관련 기업

---

## 📄 **라이선스**

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🏆 **수상 및 인증**

- 🥇 **농업 혁신 해커톤** 대상 (2024)
- 🌱 **지속가능발전 플랫폼** 인증
- 🔗 **Algorand Foundation** 공식 파트너

---

**PAM-TALK: Platform for Active Meta**
*지역 농수축산물 유통 혁신을 통한 지속 가능한 농업 생태계*

⭐ **Star this repository if you find it helpful!**