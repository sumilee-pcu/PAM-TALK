-- ============================================
-- COLLATERAL DEPOSIT & DC MINTING SYSTEM
-- Migration: 002_collateral_system
-- Created: 2025-01-25
-- ============================================

-- ============================================
-- 1. COLLATERAL DEPOSITS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.collateral_deposits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

  -- 담보 정보
  algo_amount DECIMAL(20,6) NOT NULL CHECK (algo_amount >= 10),
  usd_value DECIMAL(20,2), -- 예치 시점의 USD 가치
  algo_price_at_deposit DECIMAL(10,4), -- 예치 시점 ALGO 가격

  -- DC 발급 관련
  dc_minting_capacity DECIMAL(20,6) NOT NULL, -- 최대 발급 가능량
  dc_minted DECIMAL(20,6) DEFAULT 0, -- 실제 발급된 양
  dc_available DECIMAL(20,6) GENERATED ALWAYS AS (dc_minting_capacity - dc_minted) STORED,

  -- 담보 비율 (예: 1000 = 1 ALGO당 1000 DC)
  collateral_ratio INTEGER NOT NULL DEFAULT 1000,

  -- 상태
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'partial_redeemed', 'fully_redeemed', 'liquidated')),

  -- 블록체인 정보
  deposit_tx_id VARCHAR(64) NOT NULL,
  deposit_block_round BIGINT,

  -- 타임스탬프
  deposited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_minted_at TIMESTAMP WITH TIME ZONE,
  redeemed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_collateral_deposits_user ON public.collateral_deposits(user_id);
CREATE INDEX idx_collateral_deposits_status ON public.collateral_deposits(status);
CREATE INDEX idx_collateral_deposits_deposited_at ON public.collateral_deposits(deposited_at DESC);

-- ============================================
-- 2. DC MINTING RECORDS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.dc_minting_records (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  collateral_id UUID REFERENCES public.collateral_deposits(id) ON DELETE CASCADE,

  -- 발급 정보
  dc_amount DECIMAL(20,6) NOT NULL CHECK (dc_amount > 0),
  fee_amount DECIMAL(20,6) DEFAULT 0, -- 발급 수수료 (0.1%)
  net_dc_amount DECIMAL(20,6) NOT NULL, -- 실제 수령액

  -- 담보 사용
  algo_collateral_used DECIMAL(20,6) NOT NULL,

  -- 블록체인 정보
  minting_tx_id VARCHAR(64) NOT NULL,
  minting_block_round BIGINT,

  -- 상태
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
  failure_reason TEXT,

  -- 메타데이터
  metadata JSONB,

  -- 타임스탬프
  minted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_dc_minting_user ON public.dc_minting_records(user_id);
CREATE INDEX idx_dc_minting_collateral ON public.dc_minting_records(collateral_id);
CREATE INDEX idx_dc_minting_status ON public.dc_minting_records(status);
CREATE INDEX idx_dc_minting_minted_at ON public.dc_minting_records(minted_at DESC);

-- ============================================
-- 3. COLLATERAL REDEMPTIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.collateral_redemptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  collateral_id UUID REFERENCES public.collateral_deposits(id) ON DELETE CASCADE,

  -- 상환 정보
  dc_burned DECIMAL(20,6) NOT NULL CHECK (dc_burned > 0),
  algo_returned DECIMAL(20,6) NOT NULL,
  fee_amount DECIMAL(20,6) DEFAULT 0, -- 상환 수수료 (0.5%)
  net_algo_returned DECIMAL(20,6) NOT NULL, -- 실제 수령액

  -- 블록체인 정보
  burn_tx_id VARCHAR(64) NOT NULL,
  return_tx_id VARCHAR(64) NOT NULL,
  burn_block_round BIGINT,
  return_block_round BIGINT,

  -- 상태
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),
  failure_reason TEXT,

  -- 타임스탬프
  redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_redemptions_user ON public.collateral_redemptions(user_id);
CREATE INDEX idx_redemptions_collateral ON public.collateral_redemptions(collateral_id);
CREATE INDEX idx_redemptions_status ON public.collateral_redemptions(status);
CREATE INDEX idx_redemptions_redeemed_at ON public.collateral_redemptions(redeemed_at DESC);

-- ============================================
-- 4. COLLATERAL POOL STATS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.collateral_pool_stats (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  stat_date DATE NOT NULL UNIQUE,

  -- 담보 통계
  total_algo_locked DECIMAL(20,6) DEFAULT 0,
  total_algo_locked_usd DECIMAL(20,2) DEFAULT 0,

  -- DC 통계
  total_dc_capacity DECIMAL(20,6) DEFAULT 0,
  total_dc_minted DECIMAL(20,6) DEFAULT 0,
  total_dc_available DECIMAL(20,6) DEFAULT 0,

  -- 사용자 통계
  total_depositors INTEGER DEFAULT 0,
  active_depositors INTEGER DEFAULT 0,

  -- 거래 통계
  total_deposits_count INTEGER DEFAULT 0,
  total_mintings_count INTEGER DEFAULT 0,
  total_redemptions_count INTEGER DEFAULT 0,

  -- 평균 통계
  avg_collateral_ratio DECIMAL(10,4),
  avg_deposit_size DECIMAL(20,6),
  avg_minting_size DECIMAL(20,6),

  -- 수수료 수익
  total_minting_fees DECIMAL(20,6) DEFAULT 0,
  total_redemption_fees DECIMAL(20,6) DEFAULT 0,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_pool_stats_date ON public.collateral_pool_stats(stat_date DESC);

-- ============================================
-- 5. LIQUIDATION EVENTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.liquidation_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  collateral_id UUID REFERENCES public.collateral_deposits(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,

  -- 청산 정보
  algo_amount DECIMAL(20,6) NOT NULL,
  dc_amount DECIMAL(20,6) NOT NULL,
  collateral_ratio_at_liquidation DECIMAL(10,4),

  -- 가격 정보
  algo_price DECIMAL(10,4),
  threshold_ratio DECIMAL(10,4) DEFAULT 1.1, -- 110%

  -- 청산 결과
  penalty_amount DECIMAL(20,6) DEFAULT 0,
  liquidation_tx_id VARCHAR(64),

  -- 상태
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed')),

  liquidated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_liquidations_user ON public.liquidation_events(user_id);
CREATE INDEX idx_liquidations_collateral ON public.liquidation_events(collateral_id);
CREATE INDEX idx_liquidations_liquidated_at ON public.liquidation_events(liquidated_at DESC);

-- ============================================
-- 6. TRIGGERS
-- ============================================

-- updated_at 자동 업데이트
CREATE TRIGGER update_collateral_deposits_updated_at
  BEFORE UPDATE ON public.collateral_deposits
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pool_stats_updated_at
  BEFORE UPDATE ON public.collateral_pool_stats
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 7. FUNCTIONS
-- ============================================

-- 담보 상태 자동 업데이트 함수
CREATE OR REPLACE FUNCTION update_collateral_status()
RETURNS TRIGGER AS $$
BEGIN
  -- dc_minted가 0이면 fully_redeemed
  IF NEW.dc_minted = 0 AND OLD.dc_minted > 0 THEN
    NEW.status = 'fully_redeemed';
    NEW.redeemed_at = NOW();
  -- dc_minted가 증가했으면 active
  ELSIF NEW.dc_minted > 0 AND NEW.status != 'liquidated' THEN
    NEW.status = 'active';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_collateral_status
  BEFORE UPDATE ON public.collateral_deposits
  FOR EACH ROW
  WHEN (OLD.dc_minted IS DISTINCT FROM NEW.dc_minted)
  EXECUTE FUNCTION update_collateral_status();

-- ============================================
-- 8. ROW LEVEL SECURITY
-- ============================================

-- Collateral Deposits RLS
ALTER TABLE public.collateral_deposits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "collateral_deposits_select_own" ON public.collateral_deposits
  FOR SELECT USING (
    auth.uid() = user_id
    OR EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid() AND role IN ('admin', 'committee')
    )
  );

CREATE POLICY "collateral_deposits_insert_own" ON public.collateral_deposits
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "collateral_deposits_update_own" ON public.collateral_deposits
  FOR UPDATE USING (auth.uid() = user_id);

-- DC Minting Records RLS
ALTER TABLE public.dc_minting_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dc_minting_select_own" ON public.dc_minting_records
  FOR SELECT USING (
    auth.uid() = user_id
    OR EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid() AND role IN ('admin', 'committee')
    )
  );

CREATE POLICY "dc_minting_insert_own" ON public.dc_minting_records
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Redemptions RLS
ALTER TABLE public.collateral_redemptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "redemptions_select_own" ON public.collateral_redemptions
  FOR SELECT USING (
    auth.uid() = user_id
    OR EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid() AND role IN ('admin', 'committee')
    )
  );

CREATE POLICY "redemptions_insert_own" ON public.collateral_redemptions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Pool Stats - Admin only
ALTER TABLE public.collateral_pool_stats ENABLE ROW LEVEL SECURITY;

CREATE POLICY "pool_stats_select_all" ON public.collateral_pool_stats
  FOR SELECT USING (true);

CREATE POLICY "pool_stats_modify_admin" ON public.collateral_pool_stats
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Liquidations - View own or admin
ALTER TABLE public.liquidation_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "liquidations_select" ON public.liquidation_events
  FOR SELECT USING (
    auth.uid() = user_id
    OR EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid() AND role IN ('admin', 'committee')
    )
  );

-- ============================================
-- 9. INITIAL DATA
-- ============================================

-- 오늘 날짜의 초기 통계 레코드
INSERT INTO public.collateral_pool_stats (stat_date)
VALUES (CURRENT_DATE)
ON CONFLICT (stat_date) DO NOTHING;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================

COMMENT ON TABLE public.collateral_deposits IS 'ALGO 담보 예치 기록';
COMMENT ON TABLE public.dc_minting_records IS 'DC 토큰 발급 기록';
COMMENT ON TABLE public.collateral_redemptions IS 'ALGO 담보 상환 기록';
COMMENT ON TABLE public.collateral_pool_stats IS '담보 풀 일일 통계';
COMMENT ON TABLE public.liquidation_events IS '담보 청산 이벤트';
