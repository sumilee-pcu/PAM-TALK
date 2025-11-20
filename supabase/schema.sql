-- PAM-TALK Supabase Database Schema
-- Version: 1.0
-- Created: 2025-01-21

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- 1. USERS & PROFILES
-- ============================================

-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(20),
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  algorand_address VARCHAR(58),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_login TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT true,
  avatar_url TEXT
);

-- Profiles
CREATE TABLE public.profiles (
  user_id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
  bio TEXT,
  location VARCHAR(100),
  birth_date DATE,
  gender VARCHAR(10),
  occupation VARCHAR(100),
  interests TEXT[],
  esg_score INTEGER DEFAULT 0,
  carbon_saved DECIMAL(10,2) DEFAULT 0,
  total_activities INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 2. ESG ACTIVITIES
-- ============================================

-- ESG Activity Types
CREATE TABLE public.esg_activity_types (
  id VARCHAR(50) PRIMARY KEY,
  name_ko VARCHAR(100) NOT NULL,
  name_en VARCHAR(100) NOT NULL,
  description TEXT,
  icon VARCHAR(50),
  base_reward DECIMAL(10,2),
  carbon_factor DECIMAL(10,4),
  verification_required BOOLEAN DEFAULT true,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ESG Activities
CREATE TABLE public.esg_activities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  activity_type VARCHAR(50) REFERENCES public.esg_activity_types(id),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  image_url TEXT,
  location VARCHAR(200),
  carbon_reduction DECIMAL(10,2),
  reward_amount DECIMAL(10,2),
  status VARCHAR(20) DEFAULT 'pending',
  submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  reviewed_at TIMESTAMP WITH TIME ZONE,
  reviewed_by UUID REFERENCES public.users(id),
  review_comment TEXT,
  blockchain_hash VARCHAR(64),
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 3. TOKENS & TRANSACTIONS
-- ============================================

-- Wallets
CREATE TABLE public.wallets (
  user_id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
  algorand_address VARCHAR(58) UNIQUE NOT NULL,
  dc_balance DECIMAL(10,2) DEFAULT 0,
  esg_gold_balance DECIMAL(10,2) DEFAULT 0,
  total_earned DECIMAL(10,2) DEFAULT 0,
  total_spent DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Token Transactions
CREATE TABLE public.token_transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  transaction_type VARCHAR(20) NOT NULL,
  token_type VARCHAR(20) NOT NULL,
  from_user_id UUID REFERENCES public.users(id),
  to_user_id UUID REFERENCES public.users(id),
  amount DECIMAL(10,2) NOT NULL,
  blockchain_tx_id VARCHAR(64) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  reason TEXT,
  related_activity_id UUID REFERENCES public.esg_activities(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  confirmed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- 4. MARKETPLACE
-- ============================================

-- Products
CREATE TABLE public.products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farmer_id UUID REFERENCES public.users(id),
  name VARCHAR(200) NOT NULL,
  description TEXT,
  category VARCHAR(50) NOT NULL,
  sub_category VARCHAR(50),
  price_per_kg DECIMAL(10,2) NOT NULL,
  available_quantity DECIMAL(10,2) NOT NULL,
  unit VARCHAR(20) DEFAULT 'kg',
  image_url TEXT,
  images TEXT[],
  certifications TEXT[],
  carbon_footprint DECIMAL(10,4),
  location VARCHAR(200),
  distance_km INTEGER,
  rating DECIMAL(3,2) DEFAULT 0,
  review_count INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  status VARCHAR(20) DEFAULT 'active',
  badge VARCHAR(20),
  discount_rate INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders
CREATE TABLE public.orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  order_number VARCHAR(50) UNIQUE NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  dc_used DECIMAL(10,2) DEFAULT 0,
  cash_amount DECIMAL(10,2) NOT NULL,
  payment_method VARCHAR(20) NOT NULL,
  payment_status VARCHAR(20) DEFAULT 'pending',
  delivery_status VARCHAR(20) DEFAULT 'pending',
  delivery_address TEXT NOT NULL,
  delivery_phone VARCHAR(20) NOT NULL,
  delivery_memo TEXT,
  blockchain_tx_id VARCHAR(64),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order Items
CREATE TABLE public.order_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES public.orders(id) ON DELETE CASCADE,
  product_id UUID REFERENCES public.products(id),
  product_name VARCHAR(200) NOT NULL,
  quantity DECIMAL(10,2) NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reviews
CREATE TABLE public.reviews (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  product_id UUID REFERENCES public.products(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  order_id UUID REFERENCES public.orders(id),
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  comment TEXT,
  images TEXT[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(product_id, user_id, order_id)
);

-- ============================================
-- 5. COMMITTEE & GOVERNANCE
-- ============================================

-- DC Requests
CREATE TABLE public.dc_requests (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id),
  requested_amount DECIMAL(10,2) NOT NULL,
  reason TEXT NOT NULL,
  wallet_address VARCHAR(58) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  reviewed_by UUID REFERENCES public.users(id),
  reviewed_at TIMESTAMP WITH TIME ZONE,
  review_comment TEXT,
  blockchain_tx_id VARCHAR(64),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Carbon Tracking
CREATE TABLE public.carbon_tracking (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tracking_date DATE NOT NULL,
  category VARCHAR(50) NOT NULL,
  sub_category VARCHAR(50),
  amount DECIMAL(10,2) NOT NULL,
  source VARCHAR(100),
  region VARCHAR(100),
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 6. REGIONS & STATISTICS
-- ============================================

-- Regions
CREATE TABLE public.regions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL,
  level VARCHAR(20) NOT NULL,
  parent_id UUID REFERENCES public.regions(id),
  code VARCHAR(20) UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Regional Statistics
CREATE TABLE public.regional_statistics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  region_id UUID REFERENCES public.regions(id),
  stat_date DATE NOT NULL,
  total_users INTEGER DEFAULT 0,
  active_users INTEGER DEFAULT 0,
  total_activities INTEGER DEFAULT 0,
  carbon_reduced DECIMAL(10,2) DEFAULT 0,
  dc_distributed DECIMAL(10,2) DEFAULT 0,
  esg_gold_earned DECIMAL(10,2) DEFAULT 0,
  marketplace_orders INTEGER DEFAULT 0,
  marketplace_revenue DECIMAL(10,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(region_id, stat_date)
);

-- ============================================
-- 7. SYSTEM
-- ============================================

-- Audit Logs
CREATE TABLE public.audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id),
  action VARCHAR(50) NOT NULL,
  resource_type VARCHAR(50),
  resource_id UUID,
  old_value JSONB,
  new_value JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notifications
CREATE TABLE public.notifications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  type VARCHAR(50) NOT NULL,
  title VARCHAR(200) NOT NULL,
  message TEXT NOT NULL,
  link TEXT,
  is_read BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 8. INDEXES
-- ============================================

-- ESG Activities
CREATE INDEX idx_esg_activities_user ON public.esg_activities(user_id);
CREATE INDEX idx_esg_activities_status ON public.esg_activities(status);
CREATE INDEX idx_esg_activities_type ON public.esg_activities(activity_type);

-- Token Transactions
CREATE INDEX idx_token_tx_from ON public.token_transactions(from_user_id);
CREATE INDEX idx_token_tx_to ON public.token_transactions(to_user_id);
CREATE INDEX idx_token_tx_blockchain ON public.token_transactions(blockchain_tx_id);

-- Products
CREATE INDEX idx_products_category ON public.products(category);
CREATE INDEX idx_products_farmer ON public.products(farmer_id);
CREATE INDEX idx_products_status ON public.products(status);

-- Orders
CREATE INDEX idx_orders_user ON public.orders(user_id);
CREATE INDEX idx_orders_status ON public.orders(payment_status, delivery_status);

-- Carbon Tracking
CREATE INDEX idx_carbon_tracking_date ON public.carbon_tracking(tracking_date);
CREATE INDEX idx_carbon_tracking_category ON public.carbon_tracking(category);

-- Audit Logs
CREATE INDEX idx_audit_logs_user ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX idx_audit_logs_created ON public.audit_logs(created_at);

-- Notifications
CREATE INDEX idx_notifications_user ON public.notifications(user_id, is_read);

-- ============================================
-- 9. ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.esg_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.token_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dc_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Users: Can view own profile
CREATE POLICY "users_select_own" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_update_own" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Profiles: Can view and update own profile
CREATE POLICY "profiles_select_own" ON public.profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "profiles_update_own" ON public.profiles
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "profiles_insert_own" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ESG Activities: Users can view own, committee/admin can view all
CREATE POLICY "esg_activities_select" ON public.esg_activities
  FOR SELECT USING (
    auth.uid() = user_id
    OR EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid()
      AND role IN ('committee', 'admin', 'government')
    )
  );

CREATE POLICY "esg_activities_insert_own" ON public.esg_activities
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "esg_activities_update_committee" ON public.esg_activities
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid()
      AND role IN ('committee', 'admin')
    )
  );

-- Wallets: Can view own wallet
CREATE POLICY "wallets_select_own" ON public.wallets
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "wallets_insert_own" ON public.wallets
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Token Transactions: Can view own transactions
CREATE POLICY "token_tx_select" ON public.token_transactions
  FOR SELECT USING (
    auth.uid() = from_user_id
    OR auth.uid() = to_user_id
    OR EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid()
      AND role IN ('admin', 'government')
    )
  );

-- Products: All can view active products
CREATE POLICY "products_select_active" ON public.products
  FOR SELECT USING (status = 'active' OR farmer_id = auth.uid());

CREATE POLICY "products_insert_farmer" ON public.products
  FOR INSERT WITH CHECK (auth.uid() = farmer_id);

CREATE POLICY "products_update_farmer" ON public.products
  FOR UPDATE USING (auth.uid() = farmer_id);

-- Orders: Can view own orders
CREATE POLICY "orders_select_own" ON public.orders
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "orders_insert_own" ON public.orders
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Order Items: Can view items of own orders
CREATE POLICY "order_items_select" ON public.order_items
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.orders
      WHERE id = order_id AND user_id = auth.uid()
    )
  );

-- Reviews: All can view, users can insert own
CREATE POLICY "reviews_select_all" ON public.reviews
  FOR SELECT USING (true);

CREATE POLICY "reviews_insert_own" ON public.reviews
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "reviews_update_own" ON public.reviews
  FOR UPDATE USING (auth.uid() = user_id);

-- DC Requests: Users can view own, committee can view all
CREATE POLICY "dc_requests_select" ON public.dc_requests
  FOR SELECT USING (
    auth.uid() = user_id
    OR EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid()
      AND role IN ('committee', 'admin')
    )
  );

CREATE POLICY "dc_requests_insert_own" ON public.dc_requests
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "dc_requests_update_committee" ON public.dc_requests
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid()
      AND role IN ('committee', 'admin')
    )
  );

-- Notifications: Can view and update own
CREATE POLICY "notifications_select_own" ON public.notifications
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "notifications_update_own" ON public.notifications
  FOR UPDATE USING (auth.uid() = user_id);

-- ============================================
-- 10. FUNCTIONS & TRIGGERS
-- ============================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_esg_activities_updated_at
  BEFORE UPDATE ON public.esg_activities
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wallets_updated_at
  BEFORE UPDATE ON public.wallets
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
  BEFORE UPDATE ON public.products
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at
  BEFORE UPDATE ON public.orders
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at
  BEFORE UPDATE ON public.reviews
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 11. INITIAL DATA
-- ============================================

-- ESG Activity Types
INSERT INTO public.esg_activity_types (id, name_ko, name_en, base_reward, carbon_factor) VALUES
('recycling', '재활용', 'Recycling', 10.0, 0.5),
('tree_planting', '나무 심기', 'Tree Planting', 50.0, 5.0),
('energy_saving', '에너지 절약', 'Energy Saving', 20.0, 2.0),
('eco_transport', '친환경 교통', 'Eco Transport', 15.0, 1.5),
('zero_waste', '제로웨이스트', 'Zero Waste', 25.0, 3.0),
('plastic_free', '플라스틱 프리', 'Plastic Free', 18.0, 1.8),
('local_food', '로컬푸드 구매', 'Local Food', 12.0, 1.0),
('composting', '퇴비화', 'Composting', 15.0, 1.2);
