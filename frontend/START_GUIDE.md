# 🚀 PAM-TALK 홈페이지 실행 가이드

## ✅ 설치 완료!

모든 패키지가 설치되었습니다:
- ✅ react (18.2.0)
- ✅ react-dom (18.2.0)
- ✅ react-router-dom (6.20.0)
- ✅ react-scripts (5.0.1)
- ✅ 총 1,327개 패키지

---

## 🎯 지금 바로 실행하기

### PowerShell 명령어:
```powershell
cd C:\Users\user\journal\algo\frontend
npm start
```

또는 현재 위치에서:
```powershell
npm start
```

---

## 📺 실행 결과

몇 초 후 자동으로 브라우저가 열립니다:
- **URL**: http://localhost:3000
- **포트**: 3000

### 보게 될 화면:
```
✅ Header (PAM-TALK 로고 + 네비게이션)
   └─ 스크롤 시 배경색 변경

✅ Hero Section
   ├─ "작은 실천으로 지구를 지키고 리워드를 받으세요"
   ├─ [무료로 시작하기] [더 알아보기] 버튼
   ├─ 실사 이미지 + 3개 floating 카드
   └─ 통계 (12,500+ 참여자, 285톤 CO₂, ₩8.5M)

✅ Stats Section (그린 배경)
   └─ 4개의 통계 카드

✅ Features Section
   └─ 4개 주요 기능 (좌우 교차 레이아웃)

✅ How It Works
   └─ 6단계 타임라인

✅ Blockchain Section (다크 배경)
   └─ Algorand 네트워크 애니메이션

✅ Testimonials
   └─ Carousel (좌우 버튼으로 이동)

✅ Partners
   └─ 8개 파트너사

✅ CTA Section (그린 배경)
   └─ 웰컴 보너스 100 포인트

✅ Footer
   └─ 회사 정보, 링크, SNS
```

---

## 🎨 테스트할 것

### 1. 반응형 확인
- **F12** 눌러서 개발자 도구 열기
- **Ctrl + Shift + M** 눌러서 반응형 모드
- 다양한 화면 크기에서 테스트:
  - Desktop (1400px+)
  - Tablet (768px - 1024px)
  - Mobile (< 768px)

### 2. 인터랙션 확인
- ✅ Hero 카드가 위아래로 floating하는지
- ✅ 버튼에 마우스 올리면 hover 효과
- ✅ 카드에 마우스 올리면 shadow 변화
- ✅ Testimonials carousel 좌우 버튼 동작
- ✅ 스크롤 시 header 배경 변경

### 3. 애니메이션 확인
- ✅ 페이지 로드 시 slide-in 애니메이션
- ✅ Blockchain 섹션 네트워크 pulse 애니메이션
- ✅ Floating 카드 애니메이션

---

## 🛠️ 문제 해결

### 포트 3000이 이미 사용 중인 경우:
```
? Something is already running on port 3000.

Would you like to run the app on another port instead? › (Y/n)
```
→ **Y** 입력하면 다른 포트(3001)에서 실행

### 브라우저가 자동으로 안 열리는 경우:
수동으로 열기: http://localhost:3000

### 에러가 발생하는 경우:
```powershell
# node_modules 삭제 후 재설치
rm -r node_modules
npm install
npm start
```

---

## 📱 모바일에서 확인하기

같은 WiFi 네트워크에 연결된 경우:

1. PowerShell에서 확인:
   ```powershell
   ipconfig
   ```
   IPv4 주소 확인 (예: 192.168.0.10)

2. 모바일 브라우저에서 접속:
   ```
   http://192.168.0.10:3000
   ```

---

## 🎯 다음 단계

### 1. 페이지 확인 후:
- [ ] 디자인 만족스러운지 확인
- [ ] 텍스트 내용 수정 필요 여부 확인
- [ ] 이미지 교체 필요 여부 확인

### 2. 추가 작업:
- [ ] LoginPage 구현
- [ ] SignupPage 구현
- [ ] Dashboard 구현
- [ ] API 연결

---

## 💡 유용한 명령어

```powershell
# 개발 서버 시작
npm start

# 프로덕션 빌드
npm run build

# 테스트 실행
npm test

# 빌드 결과물 확인
cd build
ls
```

---

## 🎉 성공!

이제 프로페셔널한 홈페이지를 확인하실 수 있습니다!

**지금 실행하세요:**
```powershell
npm start
```

브라우저가 자동으로 열리면서 http://localhost:3000 에서 멋진 홈페이지를 볼 수 있습니다! 🚀
