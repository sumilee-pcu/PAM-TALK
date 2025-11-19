# PAM 디지털 쿠폰 시스템 - Docker & Kubernetes 배포 가이드

논문용 컨테이너 기반 배포 아키텍처

---

## 📐 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    Ingress Controller                   │ │
│  │         (Nginx Ingress - Traffic Management)           │ │
│  └─────────────────┬──────────────────┬───────────────────┘ │
│                    │                  │                      │
│         ┌──────────▼──────────┐  ┌───▼──────────────┐      │
│         │   Frontend Service  │  │   API Service    │      │
│         │   (LoadBalancer)    │  │   (ClusterIP)    │      │
│         └──────────┬──────────┘  └───┬──────────────┘      │
│                    │                  │                      │
│    ┌───────────────▼──────────────┐  │                      │
│    │  Frontend Pods (Replicas: 2) │  │                      │
│    │  ┌────────┐    ┌────────┐   │  │                      │
│    │  │ Nginx  │    │ Nginx  │   │  │                      │
│    │  │ Alpine │    │ Alpine │   │  │                      │
│    │  └────────┘    └────────┘   │  │                      │
│    └──────────────────────────────┘  │                      │
│                                       │                      │
│         ┌─────────────────────────────▼──────────────┐      │
│         │  API Pods (Replicas: 3, Auto-scaling)      │      │
│         │  ┌────────┐  ┌────────┐  ┌────────┐       │      │
│         │  │ Flask  │  │ Flask  │  │ Flask  │       │      │
│         │  │ Python │  │ Python │  │ Python │       │      │
│         │  └────────┘  └────────┘  └────────┘       │      │
│         │           ▲                                 │      │
│         │           │                                 │      │
│         │  ┌────────┴──────────┐                    │      │
│         │  │ HPA (Auto-scaler) │                    │      │
│         │  │ Min: 2, Max: 10   │                    │      │
│         │  └───────────────────┘                    │      │
│         └──────────────────┬─────────────────────────┘      │
│                            │                                 │
│                   ┌────────▼────────┐                       │
│                   │ Secret (Account) │                       │
│                   │  - Mnemonic      │                       │
│                   └──────────────────┘                       │
└───────────────────────────────┬──────────────────────────────┘
                                │
                     ┌──────────▼────────────┐
                     │ Algorand Blockchain   │
                     │ Asset ID: 3330375002  │
                     └───────────────────────┘
```

---

## 🐳 Docker 설치 (Windows)

### 1. Docker Desktop 다운로드
```
https://www.docker.com/products/docker-desktop/
```

### 2. 설치 요구사항
- Windows 10/11 Pro, Enterprise, or Education
- WSL 2 (자동 설치됨)
- 4GB RAM 이상

### 3. 설치 후 확인
```bash
docker --version
docker-compose --version
```

---

## 🚀 Docker Compose로 로컬 실행

### 1. 이미지 빌드 및 실행

```bash
cd algo

# 컨테이너 빌드 및 시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 상태 확인
docker-compose ps
```

### 2. 접속 테스트

- **Frontend**: http://localhost
- **API**: http://localhost:5000/api/health
- **Token Info**: http://localhost:5000/api/token-info

### 3. 중지 및 삭제

```bash
# 중지
docker-compose stop

# 삭제
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

---

## ☸️ Kubernetes 배포

### 전제조건

1. **Kubernetes 클러스터**
   - Minikube (로컬 테스트)
   - Docker Desktop Kubernetes
   - AWS EKS, GCP GKE, Azure AKS (프로덕션)

2. **kubectl 설치**
```bash
# Windows (Chocolatey)
choco install kubernetes-cli

# 확인
kubectl version --client
```

### Minikube 설치 및 시작

```bash
# Windows (Chocolatey)
choco install minikube

# Minikube 시작
minikube start --driver=docker

# 대시보드 실행
minikube dashboard
```

### 배포 단계

#### 1. Docker 이미지 빌드

```bash
cd algo/api

# API 이미지 빌드
docker build -t pam-coupon-api:latest .

# Minikube에 이미지 로드
minikube image load pam-coupon-api:latest
```

#### 2. Secret 생성 (계정 정보)

```bash
cd algo

# Algorand 계정을 Secret으로 생성
kubectl create secret generic algorand-account \
  --from-file=account.json=pam_mainnet_account_20251116_181939.json \
  -n pam-coupon
```

#### 3. Kubernetes 리소스 배포

```bash
cd k8s

# 네임스페이스 생성
kubectl apply -f namespace.yaml

# API 배포
kubectl apply -f api-deployment.yaml

# Frontend 배포
kubectl apply -f frontend-deployment.yaml

# Ingress 및 HPA
kubectl apply -f ingress.yaml
```

#### 4. 배포 확인

```bash
# Pod 상태 확인
kubectl get pods -n pam-coupon

# Service 확인
kubectl get svc -n pam-coupon

# Ingress 확인
kubectl get ingress -n pam-coupon

# HPA 확인
kubectl get hpa -n pam-coupon
```

#### 5. 로그 확인

```bash
# API Pod 로그
kubectl logs -f -l app=pam-api -n pam-coupon

# Frontend Pod 로그
kubectl logs -f -l app=pam-frontend -n pam-coupon
```

#### 6. 포트 포워딩 (로컬 테스트)

```bash
# API 포트 포워딩
kubectl port-forward svc/pam-api-service 5000:5000 -n pam-coupon

# Frontend 포트 포워딩
kubectl port-forward svc/pam-frontend-service 8080:80 -n pam-coupon
```

---

## 📊 모니터링 및 스케일링

### Auto-scaling 테스트

```bash
# 부하 생성 (논문 실험용)
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh

# Pod 내부에서
while true; do wget -q -O- http://pam-api-service.pam-coupon.svc.cluster.local:5000/api/health; done
```

### HPA 상태 모니터링

```bash
# HPA 실시간 모니터링
kubectl get hpa pam-api-hpa -n pam-coupon --watch

# Pod 스케일링 확인
kubectl get pods -n pam-coupon -w
```

### 수동 스케일링

```bash
# API Pod 수동 스케일
kubectl scale deployment pam-api --replicas=5 -n pam-coupon

# 현재 상태 확인
kubectl get deployment pam-api -n pam-coupon
```

---

## 🔬 논문용 성능 측정

### 1. 응답 시간 측정

```bash
# Apache Bench 사용
ab -n 1000 -c 10 http://localhost:5000/api/health

# 결과 분석
# - Requests per second
# - Time per request
# - Transfer rate
```

### 2. 부하 테스트

```bash
# Locust 설치
pip install locust

# 부하 테스트 실행
locust -f loadtest.py --host=http://localhost:5000
```

### 3. 리소스 사용량 측정

```bash
# Pod 리소스 사용량
kubectl top pods -n pam-coupon

# Node 리소스 사용량
kubectl top nodes
```

---

## 📝 논문 작성 시 포함할 내용

### 1. 아키텍처 다이어그램
- 위의 ASCII 다이어그램 또는 Draw.io로 시각화
- 컨테이너 구조
- 네트워크 플로우

### 2. 기술 스택
```
- Container Runtime: Docker 24.x
- Orchestration: Kubernetes 1.28+
- Frontend: Nginx Alpine
- Backend: Python 3.11 + Flask
- Blockchain: Algorand Mainnet
- Load Balancer: Nginx Ingress Controller
- Auto-scaling: Horizontal Pod Autoscaler
```

### 3. 성능 지표
- 처리량 (Throughput): Requests/sec
- 응답 시간 (Latency): ms
- 리소스 효율성: CPU/Memory 사용률
- 확장성: Auto-scaling 시간

### 4. 고가용성 (High Availability)
- Pod Replicas: 3개 (API), 2개 (Frontend)
- Health Check: Liveness & Readiness Probes
- Auto-healing: Failed Pod 자동 재시작
- Load Balancing: Service-level 부하 분산

### 5. 보안
- Secret Management: Kubernetes Secrets
- Network Policies: 네임스페이스 격리
- RBAC: 역할 기반 접근 제어
- Image Security: Alpine 기반 경량 이미지

---

## 🔧 트러블슈팅

### Pod가 시작하지 않을 때

```bash
# Pod 상세 정보
kubectl describe pod <pod-name> -n pam-coupon

# 이벤트 확인
kubectl get events -n pam-coupon --sort-by='.lastTimestamp'
```

### 이미지 Pull 실패

```bash
# Minikube 환경에서
minikube image ls | grep pam-coupon

# 이미지 재로드
minikube image load pam-coupon-api:latest
```

### Service 접속 불가

```bash
# Service Endpoints 확인
kubectl get endpoints -n pam-coupon

# Pod IP 확인
kubectl get pods -o wide -n pam-coupon
```

---

## 📚 참고 자료

- Docker Documentation: https://docs.docker.com/
- Kubernetes Documentation: https://kubernetes.io/docs/
- Minikube Guide: https://minikube.sigs.k8s.io/docs/
- Algorand Developer Docs: https://developer.algorand.org/

---

## 🎓 논문 기여도

이 시스템은 다음을 입증합니다:

1. **컨테이너화 이점**
   - 환경 독립성
   - 배포 일관성
   - 리소스 효율성

2. **Kubernetes 오케스트레이션**
   - 자동 스케일링
   - 자가 복구
   - 서비스 디스커버리

3. **블록체인 통합**
   - 컨테이너에서 블록체인 API 연동
   - 분산 시스템 구축
   - 트랜잭션 처리 성능

4. **마이크로서비스 아키텍처**
   - Frontend/Backend 분리
   - API Gateway 패턴
   - 확장 가능한 설계
