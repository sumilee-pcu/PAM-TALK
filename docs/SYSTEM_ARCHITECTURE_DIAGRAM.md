# PAM-TALK 시스템 아키텍처 다이어그램

## 전체 시스템 아키텍처

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React SPA<br/>Port: 3000]
        A1[User Dashboard]
        A2[Community Feed]
        A3[Marketplace]
        A4[Farmer Dashboard]
        A5[Admin Panel]
        A --> A1
        A --> A2
        A --> A3
        A --> A4
        A --> A5
    end

    subgraph "API Gateway Layer"
        B[Main API Server<br/>Flask - Port 5000]
        C[Token API Server<br/>Flask - Port 5000]
        D[Mall API Server<br/>Flask - Port 5001]
    end

    subgraph "Business Logic Layer"
        E[Carbon Calculation Engine]
        F[Coupon Manager]
        G[MRV Module]
        H[Committee Workflow]
        I[Auth Middleware]
    end

    subgraph "Blockchain Layer - Algorand"
        J[Algorand SDK]
        K[Asset: PAM Token<br/>ID: 746418487]
        L[Asset: ESG-GOLD<br/>Decimals: 6]
        M[Collateral Pool Contract]
        N[AlgoExplorer<br/>Verification]
    end

    subgraph "Database Layer"
        O[(Supabase PostgreSQL)]
        O1[Users Table]
        O2[Farms Table]
        O3[Products Table]
        O4[Coupons Table]
        O5[Carbon Tracking]
        O6[ESG Gold Transactions]
        O --> O1
        O --> O2
        O --> O3
        O --> O4
        O --> O5
        O --> O6
    end

    subgraph "External Services"
        P[Socket.IO<br/>Real-time Chat]
        Q[Vercel<br/>Deployment]
        R[GitHub<br/>Version Control]
    end

    %% Frontend to API
    A -->|REST API| B
    A -->|REST API| C
    A -->|REST API| D
    A -->|WebSocket| P

    %% API to Business Logic
    B --> E
    B --> F
    B --> I
    C --> F
    C --> I
    D --> F
    D --> I

    %% Business Logic to Blockchain
    E --> J
    F --> J
    G --> J
    H --> J

    %% Blockchain Assets
    J --> K
    J --> L
    J --> M
    J --> N

    %% API to Database
    B --> O
    C --> O
    D --> O

    %% Deployment
    A -.->|Deploy| Q
    A -.->|Source| R
    B -.->|Source| R
    C -.->|Source| R

    style A fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style B fill:#50C878,stroke:#2E7D4E,color:#fff
    style C fill:#50C878,stroke:#2E7D4E,color:#fff
    style D fill:#50C878,stroke:#2E7D4E,color:#fff
    style J fill:#FF6B6B,stroke:#C44545,color:#fff
    style O fill:#FFA07A,stroke:#CC7F5F,color:#fff
```

## 데이터 흐름 다이어그램

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant F as Frontend (React)
    participant A as API Server
    participant BL as Business Logic
    participant BC as Blockchain (Algorand)
    participant DB as Database

    U->>F: 1. 로그인
    F->>A: POST /api/auth/login
    A->>DB: 사용자 정보 조회
    DB-->>A: 사용자 데이터
    A-->>F: 토큰 발급
    F-->>U: 로그인 성공

    U->>F: 2. 탄소 절약 활동 등록
    F->>A: POST /api/carbon/activity
    A->>BL: 탄소 계산 요청
    BL->>BL: 탄소 절감량 계산
    BL-->>A: 계산 결과 (12.5kg CO2)
    A->>BC: ESG-GOLD 토큰 발행
    BC-->>A: 트랜잭션 ID
    A->>DB: 활동 기록 저장
    DB-->>A: 저장 완료
    A-->>F: 포인트 지급 완료
    F-->>U: 성공 메시지 + 포인트 표시

    U->>F: 3. 쿠폰 구매
    F->>A: POST /api/mall/orders
    A->>DB: 재고 확인
    DB-->>A: 재고 정보
    A->>BC: 포인트 차감 트랜잭션
    BC-->>A: 트랜잭션 성공
    A->>DB: 주문 생성
    DB-->>A: 주문 ID
    A-->>F: 주문 완료
    F-->>U: 구매 성공 알림
```

## 인증 및 권한 체계

```mermaid
graph LR
    subgraph "User Roles"
        R1[ADMIN]
        R2[COMMITTEE]
        R3[SUPPLIER]
        R4[CONSUMER]
        R5[FARMER]
        R6[COMPANY]
    end

    subgraph "Authentication Flow"
        S1[Login Request]
        S2[Token Generation]
        S3[Shared Token Store]
        S4[Token Validation]
    end

    subgraph "Protected Resources"
        P1[Coupon Minting]
        P2[Token Transfer]
        P3[Product Management]
        P4[User Dashboard]
    end

    S1 --> S2
    S2 --> S3
    S3 --> S4

    R1 --> S4
    R2 --> S4
    R3 --> S4
    R4 --> S4
    R5 --> S4
    R6 --> S4

    S4 -->|ADMIN, COMMITTEE| P1
    S4 -->|ADMIN, COMMITTEE| P2
    S4 -->|ADMIN, SUPPLIER| P3
    S4 -->|All Roles| P4

    style R1 fill:#E74C3C,color:#fff
    style R2 fill:#F39C12,color:#fff
    style R3 fill:#3498DB,color:#fff
    style R4 fill:#2ECC71,color:#fff
    style S3 fill:#9B59B6,color:#fff
```

## 블록체인 통합 아키텍처

```mermaid
graph TB
    subgraph "PAM-TALK Application"
        APP[Application Layer]
        WS[Wallet Service]
        TS[Transaction Service]
    end

    subgraph "Algorand Integration"
        SDK[Algorand SDK<br/>algosdk]
        API[Algorand Node API]
    end

    subgraph "Algorand TestNet"
        NODE[Algorand Node]
        ASA1[PAM Token<br/>746418487]
        ASA2[ESG-GOLD Token<br/>Decimals: 6]
        POOL[Collateral Pool]
    end

    subgraph "Verification"
        EXP[AlgoExplorer<br/>testnet.algoexplorer.io]
    end

    APP --> WS
    APP --> TS
    WS --> SDK
    TS --> SDK
    SDK --> API
    API --> NODE
    NODE --> ASA1
    NODE --> ASA2
    NODE --> POOL
    NODE --> EXP

    style ASA1 fill:#00D4AA,color:#fff
    style ASA2 fill:#00D4AA,color:#fff
    style EXP fill:#FFD700,color:#000
```

## 탄소 계산 시스템 아키텍처

```mermaid
graph TB
    subgraph "Input Sources"
        I1[User Activity]
        I2[Farm Data]
        I3[Transport Info]
        I4[Product Data]
    end

    subgraph "Carbon Calculation Engine"
        E1[Activity Analyzer]
        E2[Transport Emissions Calculator]
        E3[Production Emissions Calculator]
        E4[Packaging Emissions Calculator]
        E5[Distance Calculator]
        E6[Multiplier Engine]
    end

    subgraph "Output"
        O1[Carbon Savings<br/>kg CO2]
        O2[ESG Points]
        O3[ESG-GOLD Tokens]
        O4[Dashboard Display]
    end

    I1 --> E1
    I2 --> E1
    I3 --> E2
    I4 --> E3
    I4 --> E4

    E1 --> E5
    E2 --> E6
    E3 --> E6
    E4 --> E6
    E5 --> E6

    E6 --> O1
    O1 --> O2
    O2 --> O3
    O3 --> O4

    style E6 fill:#E67E22,color:#fff
    style O1 fill:#27AE60,color:#fff
```

## 배포 아키텍처

```mermaid
graph LR
    subgraph "Development"
        D1[Local Development]
        D2[Git Commit]
    end

    subgraph "Version Control"
        G1[GitHub Repository]
        G2[Main Branch]
        G3[Feature Branches]
    end

    subgraph "Deployment"
        V1[Vercel Platform]
        V2[Build Process]
        V3[Production URL<br/>pam-talk.vercel.app]
    end

    subgraph "Monitoring"
        M1[Vercel Dashboard]
        M2[Build Logs]
        M3[Analytics]
    end

    D1 --> D2
    D2 --> G1
    G1 --> G2
    G1 --> G3
    G2 --> V1
    V1 --> V2
    V2 --> V3
    V3 --> M1
    V1 --> M2
    V1 --> M3

    style V3 fill:#0070F3,color:#fff
    style M1 fill:#7928CA,color:#fff
```

## 실시간 통신 아키텍처

```mermaid
graph TB
    subgraph "Client Side"
        C1[React Component]
        C2[Socket.IO Client]
        C3[Event Handlers]
    end

    subgraph "Server Side"
        S1[Socket.IO Server]
        S2[Room Manager]
        S3[Message Handler]
    end

    subgraph "Chat Rooms"
        R1[Global Chat]
        R2[Regional: Seoul]
        R3[Regional: Gyeonggi]
        R4[Interest: Organic]
        R5[Interest: Challenges]
        R6[Interest: Recipes]
    end

    C1 --> C2
    C2 --> C3
    C2 <-->|WebSocket| S1
    S1 --> S2
    S1 --> S3
    S2 --> R1
    S2 --> R2
    S2 --> R3
    S2 --> R4
    S2 --> R5
    S2 --> R6

    style S1 fill:#25D366,color:#fff
    style C2 fill:#128C7E,color:#fff
```

## 데이터베이스 접근 패턴

```mermaid
graph TB
    subgraph "Application Layer"
        A1[API Endpoints]
        A2[Service Layer]
    end

    subgraph "Data Access Layer"
        D1[Coupon Repository]
        D2[User Repository]
        D3[Farm Repository]
        D4[Carbon Repository]
    end

    subgraph "Database"
        DB[(Supabase PostgreSQL)]
        V1[Views]
        T1[Triggers]
        RLS[Row Level Security]
    end

    A1 --> A2
    A2 --> D1
    A2 --> D2
    A2 --> D3
    A2 --> D4

    D1 --> DB
    D2 --> DB
    D3 --> DB
    D4 --> DB

    DB --> V1
    DB --> T1
    DB --> RLS

    style DB fill:#3ECF8E,color:#fff
    style RLS fill:#E74C3C,color:#fff
```

## 보안 계층 구조

```mermaid
graph TB
    subgraph "Client Security"
        CS1[HTTPS Only]
        CS2[JWT Tokens]
        CS3[XSS Protection]
    end

    subgraph "API Security"
        AS1[Authentication Middleware]
        AS2[Role-Based Access Control]
        AS3[Rate Limiting]
        AS4[Input Validation]
    end

    subgraph "Database Security"
        DS1[Row Level Security]
        DS2[Encrypted Connections]
        DS3[Prepared Statements]
    end

    subgraph "Blockchain Security"
        BS1[Private Key Management]
        BS2[Transaction Signing]
        BS3[Multi-sig Support]
    end

    CS1 --> AS1
    CS2 --> AS1
    CS3 --> AS1

    AS1 --> AS2
    AS2 --> AS3
    AS3 --> AS4

    AS4 --> DS1
    AS4 --> DS2
    AS4 --> DS3

    AS4 --> BS1
    BS1 --> BS2
    BS2 --> BS3

    style AS2 fill:#E74C3C,color:#fff
    style DS1 fill:#F39C12,color:#fff
    style BS1 fill:#9B59B6,color:#fff
```

## 기술 스택 전체 맵

```mermaid
mindmap
  root((PAM-TALK))
    Frontend
      React 18
      React Router
      Socket.IO Client
      CSS Modules
      PWA Support
    Backend
      Flask
      Python 3.8+
      Flask-CORS
      Socket.IO Server
    Blockchain
      Algorand SDK
      PyTeal
      AlgoExplorer API
      TestNet Integration
    Database
      Supabase
      PostgreSQL
      Row Level Security
      Real-time Subscriptions
    DevOps
      Vercel
      GitHub
      Git
      npm/pip
    Security
      JWT Tokens
      RBAC
      Auth Middleware
      Shared Token Store
```

## 주요 컴포넌트 상호작용

```mermaid
C4Context
    title PAM-TALK 시스템 컨텍스트 다이어그램

    Person(user, "사용자", "농부, 소비자, 위원회")
    System(pamtalk, "PAM-TALK Platform", "탄소 절감 추적 및 보상 플랫폼")
    System_Ext(algorand, "Algorand Blockchain", "토큰 발행 및 관리")
    System_Ext(supabase, "Supabase", "데이터베이스 및 인증")
    System_Ext(vercel, "Vercel", "호스팅 및 배포")

    Rel(user, pamtalk, "사용", "HTTPS")
    Rel(pamtalk, algorand, "토큰 거래", "SDK")
    Rel(pamtalk, supabase, "데이터 저장", "PostgreSQL")
    Rel(pamtalk, vercel, "배포됨", "")
```

---

## 파일 구조 맵

```
PAM-TALK/
├── frontend/               # React SPA
│   ├── src/
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── services/      # API 서비스
│   │   ├── routes/        # 라우팅
│   │   └── styles/        # CSS 파일
│   └── build/             # 프로덕션 빌드
│
├── api/                   # Flask API 서버
│   ├── app.py            # 메인 API (Port 5000)
│   ├── mall_api.py       # 몰 API (Port 5001)
│   ├── auth_middleware.py # 인증 미들웨어
│   └── coupon_manager.py  # 쿠폰 관리
│
├── pamtalk-esg-chain/    # 블록체인 서비스
│   ├── app/
│   │   ├── api/          # 토큰 API
│   │   └── service/      # 비즈니스 로직
│   └── migrations/       # DB 마이그레이션
│
├── supabase/             # 데이터베이스
│   └── schema.sql        # DB 스키마
│
├── static/               # 정적 HTML 페이지
│   ├── index.html
│   ├── community.html
│   └── farms.html
│
└── docs/                 # 문서
    ├── SYSTEM_ARCHITECTURE_DIAGRAM.md (이 파일)
    ├── DATABASE_SCHEMA.md
    └── API_DOCUMENTATION.md
```

---

## 성능 최적화 전략

```mermaid
graph LR
    subgraph "Frontend Optimization"
        F1[Code Splitting]
        F2[Lazy Loading]
        F3[Asset Compression]
        F4[CDN Caching]
    end

    subgraph "Backend Optimization"
        B1[Connection Pooling]
        B2[Query Optimization]
        B3[Response Caching]
        B4[Load Balancing]
    end

    subgraph "Database Optimization"
        D1[Indexes]
        D2[Views]
        D3[Partitioning]
        D4[Read Replicas]
    end

    F1 --> B1
    F2 --> B2
    F3 --> B3
    F4 --> B4

    B1 --> D1
    B2 --> D2
    B3 --> D3
    B4 --> D4

    style F1 fill:#3498DB,color:#fff
    style B1 fill:#2ECC71,color:#fff
    style D1 fill:#E67E22,color:#fff
```

---

## 참고 문서

- [데이터베이스 스키마](./DATABASE_SCHEMA.md)
- [API 문서](../api/API_DOCUMENTATION.md)
- [보안 아키텍처](./SECURITY_ARCHITECTURE.md)
- [Algorand 담보 시스템](../doc/ALGO-Collateral-DC-Minting-System.md)

---

**마지막 업데이트**: 2025-11-28
**다이어그램 형식**: Mermaid (Markdown에서 렌더링 가능)
**뷰어**: GitHub, VS Code (Mermaid 플러그인), Obsidian, Notion
