# PAM-TALK 데이터베이스 스키마

## 1. 사용자 관리

### 1.1 users (사용자)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255), -- 소셜 로그인은 NULL
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(20),
  role VARCHAR(20) NOT NULL DEFAULT 'user', -- user, committee, admin, government
  algorand_address VARCHAR(58), -- Algorand 지갑 주소
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP,
  is_active BOOLEAN DEFAULT true,
  email_verified BOOLEAN DEFAULT false,
  avatar_url TEXT
);

-- RLS Policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
ON users FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
ON users FOR UPDATE
USING (auth.uid() = id);
```

### 1.2 profiles (프로필 확장)
```sql
CREATE TABLE profiles (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  bio TEXT,
  location VARCHAR(100),
  birth_date DATE,
  gender VARCHAR(10),
  occupation VARCHAR(100),
  interests TEXT[], -- 관심사 배열
  esg_score INTEGER DEFAULT 0, -- ESG 점수
  carbon_saved DECIMAL(10,2) DEFAULT 0, -- 절감한 탄소량 (kg)
  total_activities INTEGER DEFAULT 0, -- 총 활동 수
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## 2. ESG 활동

### 2.1 esg_activities (ESG 활동)
```sql
CREATE TABLE esg_activities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  activity_type VARCHAR(50) NOT NULL, -- recycling, tree_planting, energy_saving, etc.
  title VARCHAR(200) NOT NULL,
  description TEXT,
  image_url TEXT,
  location VARCHAR(200),
  carbon_reduction DECIMAL(10,2), -- 예상 탄소 절감량 (kg)
  reward_amount DECIMAL(10,2), -- ESG-GOLD 보상
  status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, verified
  submitted_at TIMESTAMP DEFAULT NOW(),
  reviewed_at TIMESTAMP,
  reviewed_by UUID REFERENCES users(id),
  review_comment TEXT,
  blockchain_hash VARCHAR(64), -- 블록체인 거래 해시
  metadata JSONB, -- 추가 메타데이터
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_esg_activities_user ON esg_activities(user_id);
CREATE INDEX idx_esg_activities_status ON esg_activities(status);
CREATE INDEX idx_esg_activities_type ON esg_activities(activity_type);

-- RLS Policies
ALTER TABLE esg_activities ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own activities"
ON esg_activities FOR SELECT
USING (auth.uid() = user_id OR auth.jwt() ->> 'role' IN ('committee', 'admin', 'government'));

CREATE POLICY "Users can insert own activities"
ON esg_activities FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Committee can update activities"
ON esg_activities FOR UPDATE
USING (auth.jwt() ->> 'role' IN ('committee', 'admin'));
```

### 2.2 esg_activity_types (활동 유형)
```sql
CREATE TABLE esg_activity_types (
  id VARCHAR(50) PRIMARY KEY,
  name_ko VARCHAR(100) NOT NULL,
  name_en VARCHAR(100) NOT NULL,
  description TEXT,
  icon VARCHAR(50),
  base_reward DECIMAL(10,2), -- 기본 보상
  carbon_factor DECIMAL(10,4), -- 탄소 계산 계수
  verification_required BOOLEAN DEFAULT true,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 기본 데이터
INSERT INTO esg_activity_types (id, name_ko, name_en, base_reward, carbon_factor) VALUES
('recycling', '재활용', 'Recycling', 10.0, 0.5),
('tree_planting', '나무 심기', 'Tree Planting', 50.0, 5.0),
('energy_saving', '에너지 절약', 'Energy Saving', 20.0, 2.0),
('eco_transport', '친환경 교통', 'Eco Transport', 15.0, 1.5),
('zero_waste', '제로웨이스트', 'Zero Waste', 25.0, 3.0);
```

## 3. 토큰 및 거래

### 3.1 token_transactions (토큰 거래)
```sql
CREATE TABLE token_transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  transaction_type VARCHAR(20) NOT NULL, -- mint, burn, transfer, reward
  token_type VARCHAR(20) NOT NULL, -- DC, ESG-GOLD
  from_user_id UUID REFERENCES users(id),
  to_user_id UUID REFERENCES users(id),
  amount DECIMAL(10,2) NOT NULL,
  blockchain_tx_id VARCHAR(64) NOT NULL, -- Algorand 거래 ID
  status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, failed
  reason TEXT, -- 거래 사유
  related_activity_id UUID REFERENCES esg_activities(id),
  created_at TIMESTAMP DEFAULT NOW(),
  confirmed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_token_tx_from ON token_transactions(from_user_id);
CREATE INDEX idx_token_tx_to ON token_transactions(to_user_id);
CREATE INDEX idx_token_tx_blockchain ON token_transactions(blockchain_tx_id);

-- RLS Policies
ALTER TABLE token_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own transactions"
ON token_transactions FOR SELECT
USING (
  auth.uid() = from_user_id
  OR auth.uid() = to_user_id
  OR auth.jwt() ->> 'role' IN ('admin', 'government')
);
```

### 3.2 wallets (지갑)
```sql
CREATE TABLE wallets (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  algorand_address VARCHAR(58) UNIQUE NOT NULL,
  dc_balance DECIMAL(10,2) DEFAULT 0,
  esg_gold_balance DECIMAL(10,2) DEFAULT 0,
  total_earned DECIMAL(10,2) DEFAULT 0,
  total_spent DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## 4. 마켓플레이스

### 4.1 products (상품)
```sql
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farmer_id UUID REFERENCES users(id),
  name VARCHAR(200) NOT NULL,
  description TEXT,
  category VARCHAR(50) NOT NULL,
  sub_category VARCHAR(50),
  price_per_kg DECIMAL(10,2) NOT NULL,
  available_quantity DECIMAL(10,2) NOT NULL,
  unit VARCHAR(20) DEFAULT 'kg',
  image_url TEXT,
  images TEXT[], -- 추가 이미지들
  certifications TEXT[], -- 인증 목록
  carbon_footprint DECIMAL(10,4), -- 탄소 발자국
  location VARCHAR(200),
  distance_km INTEGER,
  rating DECIMAL(3,2) DEFAULT 0,
  review_count INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  status VARCHAR(20) DEFAULT 'active', -- active, sold_out, inactive
  badge VARCHAR(20), -- best, new, hot, premium
  discount_rate INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_farmer ON products(farmer_id);
CREATE INDEX idx_products_status ON products(status);
```

### 4.2 orders (주문)
```sql
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  order_number VARCHAR(50) UNIQUE NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  dc_used DECIMAL(10,2) DEFAULT 0,
  cash_amount DECIMAL(10,2) NOT NULL,
  payment_method VARCHAR(20) NOT NULL, -- dc, cash, hybrid
  payment_status VARCHAR(20) DEFAULT 'pending', -- pending, paid, failed, refunded
  delivery_status VARCHAR(20) DEFAULT 'pending', -- pending, preparing, shipped, delivered
  delivery_address TEXT NOT NULL,
  delivery_phone VARCHAR(20) NOT NULL,
  delivery_memo TEXT,
  blockchain_tx_id VARCHAR(64), -- DC 사용 시 거래 ID
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(payment_status, delivery_status);
```

### 4.3 order_items (주문 상품)
```sql
CREATE TABLE order_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  product_name VARCHAR(200) NOT NULL,
  quantity DECIMAL(10,2) NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.4 reviews (리뷰)
```sql
CREATE TABLE reviews (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  order_id UUID REFERENCES orders(id),
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  comment TEXT,
  images TEXT[],
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(product_id, user_id, order_id)
);
```

## 5. 위원회 관리

### 5.1 dc_requests (DC 배포 요청)
```sql
CREATE TABLE dc_requests (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  requested_amount DECIMAL(10,2) NOT NULL,
  reason TEXT NOT NULL,
  wallet_address VARCHAR(58) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
  reviewed_by UUID REFERENCES users(id),
  reviewed_at TIMESTAMP,
  review_comment TEXT,
  blockchain_tx_id VARCHAR(64),
  created_at TIMESTAMP DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE dc_requests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own requests"
ON dc_requests FOR SELECT
USING (auth.uid() = user_id OR auth.jwt() ->> 'role' IN ('committee', 'admin'));

CREATE POLICY "Committee can update requests"
ON dc_requests FOR UPDATE
USING (auth.jwt() ->> 'role' IN ('committee', 'admin'));
```

### 5.2 carbon_tracking (탄소 추적)
```sql
CREATE TABLE carbon_tracking (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tracking_date DATE NOT NULL,
  category VARCHAR(50) NOT NULL, -- transport, energy, waste, agriculture, etc.
  sub_category VARCHAR(50),
  amount DECIMAL(10,2) NOT NULL, -- 탄소량 (kg)
  source VARCHAR(100), -- 데이터 출처
  region VARCHAR(100),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_carbon_tracking_date ON carbon_tracking(tracking_date);
CREATE INDEX idx_carbon_tracking_category ON carbon_tracking(category);
```

## 6. 지자체 관리

### 6.1 regions (지역)
```sql
CREATE TABLE regions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL,
  level VARCHAR(20) NOT NULL, -- province, city, district
  parent_id UUID REFERENCES regions(id),
  code VARCHAR(20) UNIQUE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 regional_statistics (지역 통계)
```sql
CREATE TABLE regional_statistics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  region_id UUID REFERENCES regions(id),
  stat_date DATE NOT NULL,
  total_users INTEGER DEFAULT 0,
  active_users INTEGER DEFAULT 0,
  total_activities INTEGER DEFAULT 0,
  carbon_reduced DECIMAL(10,2) DEFAULT 0,
  dc_distributed DECIMAL(10,2) DEFAULT 0,
  esg_gold_earned DECIMAL(10,2) DEFAULT 0,
  marketplace_orders INTEGER DEFAULT 0,
  marketplace_revenue DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(region_id, stat_date)
);
```

## 7. 시스템

### 7.1 audit_logs (감사 로그)
```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  action VARCHAR(50) NOT NULL,
  resource_type VARCHAR(50),
  resource_id UUID,
  old_value JSONB,
  new_value JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

### 7.2 notifications (알림)
```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL, -- esg_approved, token_received, order_shipped, etc.
  title VARCHAR(200) NOT NULL,
  message TEXT NOT NULL,
  link TEXT,
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
```

## 8. 뷰 (Views)

### 8.1 user_dashboard_stats
```sql
CREATE VIEW user_dashboard_stats AS
SELECT
  u.id as user_id,
  u.name,
  p.esg_score,
  p.carbon_saved,
  p.total_activities,
  w.dc_balance,
  w.esg_gold_balance,
  COUNT(DISTINCT ea.id) as pending_activities,
  COUNT(DISTINCT o.id) as total_orders
FROM users u
LEFT JOIN profiles p ON u.id = p.user_id
LEFT JOIN wallets w ON u.id = w.user_id
LEFT JOIN esg_activities ea ON u.id = ea.user_id AND ea.status = 'pending'
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name, p.esg_score, p.carbon_saved, p.total_activities, w.dc_balance, w.esg_gold_balance;
```

## 9. 함수 (Functions)

### 9.1 업데이트 타임스탬프 트리거
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 각 테이블에 적용
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- ... (다른 테이블들도 동일하게 적용)
```

## 10. 초기 데이터

### 10.1 관리자 계정
```sql
-- 초기 관리자 생성은 Supabase Auth를 통해 수행
-- 이후 role을 'admin'으로 업데이트
```

### 10.2 기본 카테고리
```sql
-- ESG 활동 유형은 위에서 이미 정의됨
```
