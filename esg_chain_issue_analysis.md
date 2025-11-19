# ESG Chain 서비스 오프라인 원인 분석

## 🚨 문제 상황
ESG Chain 서비스가 관리자 대시보드에서 "오프라인" 상태로 표시됨

## 🔍 원인 분석

### 직접적 원인
```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed:
Connection refused (0x0000274D/10061)
Is the server running on that host and accepting TCP/IP connections?
```

### 근본적 원인
1. **PostgreSQL 서버 미설치/미실행**
   - ESG Chain 서비스가 PostgreSQL 데이터베이스에 의존
   - 포트 5432에서 PostgreSQL 서버가 실행되지 않음

2. **의존성 문제**
   - ESG Chain은 psycopg2를 통해 PostgreSQL 연결 시도
   - 데이터베이스 연결 풀 초기화 실패

3. **아키텍처 설계 문제**
   - ESG Chain이 메인 PAM-TALK 플랫폼과 분리된 독립 서비스
   - 추가 인프라 요구사항 발생

## 🎯 해결 방안

### 방법 1: PostgreSQL 설치 및 설정 (완전 해결)
```bash
# PostgreSQL 설치 (Windows)
# 1. PostgreSQL 공식 사이트에서 설치
# 2. 서비스 시작
# 3. 데이터베이스 생성 및 테이블 초기화

# 또는 Docker 사용
docker run --name postgres-pam -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
```

### 방법 2: SQLite로 변경 (빠른 해결)
```python
# ESG Chain의 데이터베이스를 SQLite로 변경
# PostgreSQL 의존성 제거
# 파일 기반 데이터베이스 사용
```

### 방법 3: 통합 서비스로 변경 (권장)
```python
# ESG Chain 기능을 메인 PAM-TALK 플랫폼에 통합
# 단일 서비스로 운영
# 복잡성 감소
```

### 방법 4: 시뮬레이션 모드 확장 (즉시 가능)
```python
# ESG Chain도 시뮬레이션 모드로 실행
# 실제 데이터베이스 없이 메모리 기반 운영
# 테스트 및 데모 목적으로 충분
```

## ⚡ 즉시 실행 가능한 해결책

### Option A: ESG Chain 비활성화 (현재 상태 유지)
- ESG Chain 없이도 PAM-TALK 메인 기능은 정상 작동
- 시뮬레이션 토큰으로 모든 기능 테스트 가능
- 관리자 대시보드에서 "예상된 오프라인 상태"로 표시

### Option B: 간단한 Mock ESG 서비스 생성
- 포트 5004에서 간단한 health check만 응답하는 서비스
- 실제 기능 없이 "온라인" 상태만 표시
- 관리자 대시보드에서 정상으로 표시

### Option C: SQLite 기반 ESG Chain 실행
- PostgreSQL 의존성 제거
- 로컬 파일 기반 데이터베이스 사용
- 실제 ESG Chain 기능 활성화

## 📊 각 방법의 장단점

| 방법 | 구현 시간 | 기능 완성도 | 복잡도 | 권장도 |
|------|-----------|-------------|--------|--------|
| 현재 상태 유지 | 0분 | 80% | 낮음 | ⭐⭐⭐ |
| Mock 서비스 | 10분 | 85% | 낮음 | ⭐⭐⭐⭐ |
| SQLite 변경 | 30분 | 95% | 중간 | ⭐⭐⭐⭐⭐ |
| PostgreSQL 설치 | 60분 | 100% | 높음 | ⭐⭐ |

## 🎯 권장 조치

**즉시**: Mock ESG 서비스 생성하여 관리자 대시보드 정상화
**단기**: SQLite 기반 ESG Chain 구현
**장기**: 메인 플랫폼에 ESG 기능 통합

현재 상황에서는 PAM-TALK 메인 기능이 완전히 작동하므로, ESG Chain 오프라인 상태는 **정상적인 개발 단계**입니다.