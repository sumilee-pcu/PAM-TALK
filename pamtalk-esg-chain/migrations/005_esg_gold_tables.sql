-- ESG-GOLD 디지털 쿠폰 시스템 데이터베이스 스키마
-- 1DC (Digital Carbon) = 1kg CO2 감축량
-- Migration: 005_esg_gold_tables.sql

-- ============================================================================
-- 1. ESG-GOLD 잔액 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_gold_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    wallet_address TEXT NOT NULL,
    balance_dc REAL NOT NULL DEFAULT 0.0,  -- DC 단위 잔액
    balance_micro INTEGER NOT NULL DEFAULT 0,  -- micro units (6 decimals)
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    opted_in BOOLEAN DEFAULT FALSE,
    opt_in_tx_id TEXT,
    opt_in_date TIMESTAMP,

    UNIQUE(user_id),
    UNIQUE(wallet_address)
);

CREATE INDEX idx_esg_gold_balances_user ON esg_gold_balances(user_id);
CREATE INDEX idx_esg_gold_balances_wallet ON esg_gold_balances(wallet_address);


-- ============================================================================
-- 2. ESG-GOLD 변환 기록 (탄소 감축 → ESG-GOLD)
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_gold_conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    wallet_address TEXT NOT NULL,
    activity_type TEXT NOT NULL,  -- local_food_purchase, organic_farming, etc.

    -- 탄소 정보
    carbon_savings_kg REAL NOT NULL,  -- 절약된 탄소량 (kg CO2)
    dc_units REAL NOT NULL,  -- Digital Carbon units

    -- ESG-GOLD 정보
    esg_gold_minted REAL NOT NULL,  -- 발행된 ESG-GOLD (actual)
    esg_gold_micro INTEGER NOT NULL,  -- 발행된 ESG-GOLD (micro units)

    -- PAM 토큰 정보
    pam_tokens_awarded INTEGER DEFAULT 0,

    -- 활동 세부사항
    product_name TEXT,
    quantity REAL,
    origin_region TEXT,
    destination_region TEXT,
    farming_method TEXT,
    transport_method TEXT,
    packaging_type TEXT,

    -- 배출량 세부정보
    transport_emissions REAL,
    production_emissions REAL,
    packaging_emissions REAL,
    total_emissions REAL,
    baseline_emissions REAL,
    reduction_percentage REAL,

    -- 블록체인 정보
    transaction_id TEXT,  -- Algorand tx hash
    block_number INTEGER,

    -- 시간 정보
    activity_date TIMESTAMP,
    conversion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES esg_gold_balances(user_id)
);

CREATE INDEX idx_conversions_user ON esg_gold_conversions(user_id);
CREATE INDEX idx_conversions_wallet ON esg_gold_conversions(wallet_address);
CREATE INDEX idx_conversions_activity_type ON esg_gold_conversions(activity_type);
CREATE INDEX idx_conversions_date ON esg_gold_conversions(conversion_timestamp);
CREATE INDEX idx_conversions_tx ON esg_gold_conversions(transaction_id);


-- ============================================================================
-- 3. ESG-GOLD 거래 내역 (전송, 소각)
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_gold_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT NOT NULL,  -- mint, burn, transfer, payment

    -- 거래 당사자
    sender_wallet TEXT,
    recipient_wallet TEXT,

    -- 금액 정보
    amount_dc REAL NOT NULL,
    amount_micro INTEGER NOT NULL,

    -- 거래 사유/메타데이터
    reason TEXT,  -- carbon_reduction, marketplace_discount, offset_retirement, etc.
    metadata TEXT,  -- JSON 형식 추가 정보

    -- 블록체인 정보
    transaction_id TEXT NOT NULL,  -- Algorand tx hash
    block_number INTEGER,

    -- 시간 정보
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 수수료 (있을 경우)
    fee_algo REAL DEFAULT 0.001
);

CREATE INDEX idx_transactions_type ON esg_gold_transactions(transaction_type);
CREATE INDEX idx_transactions_sender ON esg_gold_transactions(sender_wallet);
CREATE INDEX idx_transactions_recipient ON esg_gold_transactions(recipient_wallet);
CREATE INDEX idx_transactions_tx_id ON esg_gold_transactions(transaction_id);
CREATE INDEX idx_transactions_date ON esg_gold_transactions(timestamp);


-- ============================================================================
-- 4. ESG-GOLD 소각 기록
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_gold_burns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    wallet_address TEXT NOT NULL,

    -- 소각 정보
    amount_burned_dc REAL NOT NULL,
    amount_burned_micro INTEGER NOT NULL,
    burn_mechanism TEXT NOT NULL,  -- marketplace_discount, offset_retirement, premium_service
    burn_rate REAL NOT NULL,  -- 소각 비율 (0.0 ~ 1.0)

    -- 연관 거래 정보
    related_transaction_id TEXT,  -- 마켓플레이스 구매 등
    purchase_amount REAL,  -- 구매 금액 (원)
    discount_amount REAL,  -- 할인 금액

    -- 블록체인 정보
    burn_tx_id TEXT NOT NULL,
    block_number INTEGER,

    -- 탄소 상쇄 정보
    carbon_offset_kg REAL,  -- 상쇄된 탄소량
    permanent_retirement BOOLEAN DEFAULT FALSE,  -- 영구 제거 여부

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_burns_user ON esg_gold_burns(user_id);
CREATE INDEX idx_burns_wallet ON esg_gold_burns(wallet_address);
CREATE INDEX idx_burns_mechanism ON esg_gold_burns(burn_mechanism);
CREATE INDEX idx_burns_date ON esg_gold_burns(timestamp);


-- ============================================================================
-- 5. 마켓플레이스 ESG-GOLD 할인 기록
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_gold_marketplace_discounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    wallet_address TEXT NOT NULL,

    -- 주문 정보
    order_id TEXT,
    product_id TEXT,
    seller_wallet TEXT,

    -- ESG-GOLD 사용 정보
    esg_gold_used REAL NOT NULL,  -- 사용된 ESG-GOLD
    esg_gold_burned REAL NOT NULL,  -- 소각된 ESG-GOLD (10%)

    -- 구매 정보
    original_amount REAL NOT NULL,  -- 원래 가격
    discount_amount REAL NOT NULL,  -- 할인 금액
    discount_rate REAL,  -- 할인율 (%)
    final_amount REAL NOT NULL,  -- 최종 결제 금액

    -- 블록체인 정보
    burn_tx_id TEXT,
    payment_tx_id TEXT,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_marketplace_discounts_user ON esg_gold_marketplace_discounts(user_id);
CREATE INDEX idx_marketplace_discounts_wallet ON esg_gold_marketplace_discounts(wallet_address);
CREATE INDEX idx_marketplace_discounts_order ON esg_gold_marketplace_discounts(order_id);
CREATE INDEX idx_marketplace_discounts_date ON esg_gold_marketplace_discounts(timestamp);


-- ============================================================================
-- 6. ESG-GOLD 통계 (일별 집계)
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_gold_daily_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_date DATE NOT NULL,

    -- 발행 통계
    total_conversions INTEGER DEFAULT 0,
    total_dc_minted REAL DEFAULT 0.0,
    total_esg_gold_minted REAL DEFAULT 0.0,

    -- 소각 통계
    total_burns INTEGER DEFAULT 0,
    total_dc_burned REAL DEFAULT 0.0,
    total_esg_gold_burned REAL DEFAULT 0.0,

    -- 활동별 통계
    local_food_purchases INTEGER DEFAULT 0,
    organic_farming_activities INTEGER DEFAULT 0,
    renewable_energy_activities INTEGER DEFAULT 0,
    waste_reduction_activities INTEGER DEFAULT 0,
    transport_reduction_activities INTEGER DEFAULT 0,
    packaging_reduction_activities INTEGER DEFAULT 0,

    -- 탄소 통계
    total_carbon_saved_kg REAL DEFAULT 0.0,
    total_carbon_offset_kg REAL DEFAULT 0.0,

    -- 사용자 통계
    active_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,

    -- 마켓플레이스 통계
    marketplace_transactions INTEGER DEFAULT 0,
    total_discounts_applied REAL DEFAULT 0.0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(stat_date)
);

CREATE INDEX idx_daily_stats_date ON esg_gold_daily_stats(stat_date);


-- ============================================================================
-- 7. ESG-GOLD 보상 규칙 설정
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_gold_reward_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL UNIQUE,

    -- 변환 배율
    dc_multiplier REAL NOT NULL DEFAULT 1.0,  -- DC 변환 배율
    pam_token_multiplier REAL NOT NULL DEFAULT 1.0,  -- PAM 토큰 배율

    -- 제한
    min_dc_amount REAL DEFAULT 0.1,  -- 최소 발행 DC
    max_daily_dc REAL DEFAULT 100.0,  -- 일일 최대 DC

    -- 활성화 여부
    is_active BOOLEAN DEFAULT TRUE,

    -- 시간 정보
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 기본 보상 규칙 삽입
INSERT OR IGNORE INTO esg_gold_reward_rules (activity_type, dc_multiplier, pam_token_multiplier, max_daily_dc) VALUES
    ('local_food_purchase', 1.2, 1.0, 100.0),
    ('organic_farming', 1.5, 1.0, 150.0),
    ('renewable_energy', 2.0, 1.0, 200.0),
    ('waste_reduction', 1.8, 1.0, 150.0),
    ('transport_reduction', 1.3, 1.0, 100.0),
    ('packaging_reduction', 1.3, 1.0, 100.0);


-- ============================================================================
-- 8. ESG-GOLD 챌린지 참여 기록
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_gold_challenge_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,

    -- 보상 정보
    dc_reward REAL NOT NULL,
    esg_gold_reward REAL NOT NULL,
    bonus_multiplier REAL DEFAULT 1.0,

    -- 블록체인 정보
    reward_tx_id TEXT,

    claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (challenge_id) REFERENCES carbon_challenges(id)
);

CREATE INDEX idx_challenge_rewards_challenge ON esg_gold_challenge_rewards(challenge_id);
CREATE INDEX idx_challenge_rewards_user ON esg_gold_challenge_rewards(user_id);


-- ============================================================================
-- 9. ESG-GOLD 감사 로그 (Audit Trail)
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_gold_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,  -- mint, burn, transfer, update_balance

    -- 대상
    target_user_id TEXT,
    target_wallet TEXT,

    -- 변경 정보
    old_balance_dc REAL,
    new_balance_dc REAL,
    change_amount_dc REAL,

    -- 사유
    reason TEXT,

    -- 관련 트랜잭션
    related_tx_id TEXT,
    related_table TEXT,
    related_record_id INTEGER,

    -- 실행 정보
    executed_by TEXT,  -- system, admin, user
    ip_address TEXT,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_action ON esg_gold_audit_log(action_type);
CREATE INDEX idx_audit_log_user ON esg_gold_audit_log(target_user_id);
CREATE INDEX idx_audit_log_wallet ON esg_gold_audit_log(target_wallet);
CREATE INDEX idx_audit_log_date ON esg_gold_audit_log(timestamp);


-- ============================================================================
-- 10. 뷰(View) 생성: 사용자별 ESG-GOLD 요약
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_user_esg_gold_summary AS
SELECT
    b.user_id,
    b.wallet_address,
    b.balance_dc as current_balance_dc,
    b.opted_in,

    -- 변환 통계
    COUNT(DISTINCT c.id) as total_conversions,
    COALESCE(SUM(c.carbon_savings_kg), 0) as total_carbon_saved_kg,
    COALESCE(SUM(c.dc_units), 0) as total_dc_earned,
    COALESCE(SUM(c.esg_gold_minted), 0) as total_esg_gold_earned,
    COALESCE(SUM(c.pam_tokens_awarded), 0) as total_pam_tokens,

    -- 소각 통계
    COALESCE(SUM(burn.amount_burned_dc), 0) as total_dc_burned,
    COALESCE(SUM(burn.carbon_offset_kg), 0) as total_carbon_offset_kg,

    -- 마켓플레이스 사용
    COALESCE(SUM(d.esg_gold_used), 0) as total_marketplace_usage,
    COALESCE(SUM(d.discount_amount), 0) as total_discounts_received,

    -- 시간 정보
    MIN(c.conversion_timestamp) as first_conversion_date,
    MAX(c.conversion_timestamp) as last_conversion_date,
    b.last_updated

FROM esg_gold_balances b
LEFT JOIN esg_gold_conversions c ON b.user_id = c.user_id
LEFT JOIN esg_gold_burns burn ON b.user_id = burn.user_id
LEFT JOIN esg_gold_marketplace_discounts d ON b.user_id = d.user_id
GROUP BY b.user_id, b.wallet_address;


-- ============================================================================
-- 11. 트리거: 잔액 자동 업데이트
-- ============================================================================

-- 변환 시 잔액 증가
CREATE TRIGGER IF NOT EXISTS trg_update_balance_after_conversion
AFTER INSERT ON esg_gold_conversions
BEGIN
    UPDATE esg_gold_balances
    SET
        balance_dc = balance_dc + NEW.dc_units,
        balance_micro = balance_micro + NEW.esg_gold_micro,
        last_updated = CURRENT_TIMESTAMP
    WHERE wallet_address = NEW.wallet_address;

    -- 감사 로그 기록
    INSERT INTO esg_gold_audit_log (
        action_type, target_user_id, target_wallet,
        change_amount_dc, reason, related_tx_id, executed_by
    ) VALUES (
        'mint', NEW.user_id, NEW.wallet_address,
        NEW.dc_units, NEW.activity_type, NEW.transaction_id, 'system'
    );
END;

-- 소각 시 잔액 감소
CREATE TRIGGER IF NOT EXISTS trg_update_balance_after_burn
AFTER INSERT ON esg_gold_burns
BEGIN
    UPDATE esg_gold_balances
    SET
        balance_dc = balance_dc - NEW.amount_burned_dc,
        balance_micro = balance_micro - NEW.amount_burned_micro,
        last_updated = CURRENT_TIMESTAMP
    WHERE wallet_address = NEW.wallet_address;

    -- 감사 로그 기록
    INSERT INTO esg_gold_audit_log (
        action_type, target_user_id, target_wallet,
        change_amount_dc, reason, related_tx_id, executed_by
    ) VALUES (
        'burn', NEW.user_id, NEW.wallet_address,
        -NEW.amount_burned_dc, NEW.burn_mechanism, NEW.burn_tx_id, 'system'
    );
END;


-- ============================================================================
-- 12. 초기 데이터 및 설정
-- ============================================================================

-- ESG-GOLD 시스템 설정 테이블
CREATE TABLE IF NOT EXISTS esg_gold_system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 기본 설정 삽입
INSERT OR IGNORE INTO esg_gold_system_config (key, value, description) VALUES
    ('asset_id', '', 'ESG-GOLD Algorand ASA ID'),
    ('creator_address', '', 'ESG-GOLD 발행 계정 주소'),
    ('daily_conversion_limit_dc', '1000.0', '사용자당 일일 변환 한도 (DC)'),
    ('min_conversion_dc', '0.1', '최소 변환 단위 (DC)'),
    ('marketplace_discount_burn_rate', '0.1', '마켓플레이스 할인 소각 비율'),
    ('max_marketplace_discount_rate', '0.2', '최대 마켓플레이스 할인율'),
    ('system_enabled', 'true', 'ESG-GOLD 시스템 활성화 여부');


-- ============================================================================
-- 마이그레이션 완료
-- ============================================================================
