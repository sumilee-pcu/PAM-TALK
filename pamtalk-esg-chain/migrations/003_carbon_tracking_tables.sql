-- PAM-TALK ESG Chain Database Schema Migration
-- Version: 003
-- Description: 탄소 추적 및 절약량 관리 테이블 생성

-- 사용자별 탄소 프로필 테이블
CREATE TABLE IF NOT EXISTS carbon_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(100),

    -- 프로필 정보
    household_size INTEGER DEFAULT 1,
    lifestyle_type VARCHAR(50) DEFAULT 'standard', -- eco, standard, premium
    preferred_transport VARCHAR(50) DEFAULT 'mixed',

    -- 기준 배출량 (월간, kg CO2)
    baseline_monthly_emissions DECIMAL(10,3) DEFAULT 0,
    current_monthly_emissions DECIMAL(10,3) DEFAULT 0,

    -- 목표 설정
    carbon_reduction_goal DECIMAL(5,2) DEFAULT 10.0, -- 목표 절약 비율(%)
    monthly_token_goal INTEGER DEFAULT 100,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 탄소 활동 기록 테이블
CREATE TABLE IF NOT EXISTS carbon_activities (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    activity_type VARCHAR(50) NOT NULL, -- local_food_purchase, organic_farming, etc.

    -- 활동 상세 정보
    product_name VARCHAR(255),
    quantity DECIMAL(10,3),
    origin_region VARCHAR(100),
    destination_region VARCHAR(100),
    farming_method VARCHAR(50),
    transport_method VARCHAR(50),
    packaging_type VARCHAR(50),

    -- 계산된 탄소 정보
    total_emissions DECIMAL(10,3) NOT NULL,
    transport_emissions DECIMAL(10,3) DEFAULT 0,
    production_emissions DECIMAL(10,3) DEFAULT 0,
    packaging_emissions DECIMAL(10,3) DEFAULT 0,
    baseline_emissions DECIMAL(10,3) NOT NULL,
    carbon_savings DECIMAL(10,3) NOT NULL,
    reduction_percentage DECIMAL(5,2) DEFAULT 0,

    -- 보상 정보
    token_reward_eligible BOOLEAN DEFAULT FALSE,
    token_reward_amount INTEGER DEFAULT 0,
    token_reward_claimed BOOLEAN DEFAULT FALSE,
    reward_claimed_at TIMESTAMP NULL,

    -- 검증 정보
    verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    verified_at TIMESTAMP NULL,

    -- 메타데이터
    metadata JSONB,

    activity_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 월별 탄소 통계 테이블
CREATE TABLE IF NOT EXISTS carbon_monthly_stats (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,

    -- 월간 활동 통계
    total_activities INTEGER DEFAULT 0,
    total_emissions DECIMAL(10,3) DEFAULT 0,
    total_baseline_emissions DECIMAL(10,3) DEFAULT 0,
    total_carbon_savings DECIMAL(10,3) DEFAULT 0,
    average_reduction_percentage DECIMAL(5,2) DEFAULT 0,

    -- 월간 토큰 통계
    total_tokens_earned INTEGER DEFAULT 0,
    total_tokens_claimed INTEGER DEFAULT 0,
    pending_tokens INTEGER DEFAULT 0,

    -- 활동별 통계 (JSON)
    activity_breakdown JSONB,

    -- 랭킹 정보
    regional_rank INTEGER,
    global_rank INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, year, month)
);

-- 탄소 절약 챌린지 테이블
CREATE TABLE IF NOT EXISTS carbon_challenges (
    id SERIAL PRIMARY KEY,
    challenge_name VARCHAR(255) NOT NULL,
    description TEXT,
    challenge_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly

    -- 챌린지 조건
    target_activity_type VARCHAR(50), -- 특정 활동 타입 제한
    target_savings_amount DECIMAL(10,3), -- 목표 절약량 (kg CO2)
    target_activities_count INTEGER, -- 목표 활동 횟수
    min_reduction_percentage DECIMAL(5,2), -- 최소 절약 비율

    -- 보상 정보
    reward_tokens INTEGER NOT NULL,
    bonus_multiplier DECIMAL(3,2) DEFAULT 1.0,

    -- 챌린지 기간
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    -- 상태
    active BOOLEAN DEFAULT TRUE,
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 챌린지 참여 테이블
CREATE TABLE IF NOT EXISTS user_challenge_participations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    challenge_id INTEGER REFERENCES carbon_challenges(id),

    -- 참여 상태
    participation_status VARCHAR(20) DEFAULT 'active', -- active, completed, failed, abandoned
    progress_percentage DECIMAL(5,2) DEFAULT 0,

    -- 달성 정보
    current_savings DECIMAL(10,3) DEFAULT 0,
    current_activities INTEGER DEFAULT 0,
    target_achieved BOOLEAN DEFAULT FALSE,
    completion_date TIMESTAMP NULL,

    -- 보상
    reward_tokens INTEGER DEFAULT 0,
    reward_claimed BOOLEAN DEFAULT FALSE,
    reward_claimed_at TIMESTAMP NULL,

    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, challenge_id)
);

-- 탄소 리워드 히스토리 테이블
CREATE TABLE IF NOT EXISTS carbon_reward_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,

    -- 보상 소스
    source_type VARCHAR(50) NOT NULL, -- activity, challenge, bonus
    source_id INTEGER, -- activity_id 또는 challenge_id

    -- 보상 정보
    carbon_savings DECIMAL(10,3) NOT NULL,
    token_amount INTEGER NOT NULL,
    multiplier DECIMAL(3,2) DEFAULT 1.0,

    -- 상태
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, claimed
    approved_by VARCHAR(100),
    approved_at TIMESTAMP NULL,
    claimed_at TIMESTAMP NULL,

    -- 블록체인 정보
    mint_tx_hash VARCHAR(64),
    transfer_tx_hash VARCHAR(64),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_carbon_profiles_user_id ON carbon_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_carbon_profiles_region ON carbon_profiles(region);

CREATE INDEX IF NOT EXISTS idx_carbon_activities_user_id ON carbon_activities(user_id);
CREATE INDEX IF NOT EXISTS idx_carbon_activities_activity_date ON carbon_activities(activity_date);
CREATE INDEX IF NOT EXISTS idx_carbon_activities_activity_type ON carbon_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_carbon_activities_reward_eligible ON carbon_activities(token_reward_eligible);

CREATE INDEX IF NOT EXISTS idx_carbon_monthly_stats_user_id ON carbon_monthly_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_carbon_monthly_stats_year_month ON carbon_monthly_stats(year, month);

CREATE INDEX IF NOT EXISTS idx_carbon_challenges_active ON carbon_challenges(active);
CREATE INDEX IF NOT EXISTS idx_carbon_challenges_dates ON carbon_challenges(start_date, end_date);

CREATE INDEX IF NOT EXISTS idx_user_challenge_participations_user_id ON user_challenge_participations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_challenge_participations_challenge_id ON user_challenge_participations(challenge_id);
CREATE INDEX IF NOT EXISTS idx_user_challenge_participations_status ON user_challenge_participations(participation_status);

CREATE INDEX IF NOT EXISTS idx_carbon_reward_history_user_id ON carbon_reward_history(user_id);
CREATE INDEX IF NOT EXISTS idx_carbon_reward_history_status ON carbon_reward_history(status);
CREATE INDEX IF NOT EXISTS idx_carbon_reward_history_source ON carbon_reward_history(source_type, source_id);

-- 트리거 함수: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_carbon_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- updated_at 트리거 적용
CREATE TRIGGER update_carbon_profiles_updated_at BEFORE UPDATE ON carbon_profiles
    FOR EACH ROW EXECUTE FUNCTION update_carbon_updated_at_column();

CREATE TRIGGER update_carbon_activities_updated_at BEFORE UPDATE ON carbon_activities
    FOR EACH ROW EXECUTE FUNCTION update_carbon_updated_at_column();

CREATE TRIGGER update_carbon_monthly_stats_updated_at BEFORE UPDATE ON carbon_monthly_stats
    FOR EACH ROW EXECUTE FUNCTION update_carbon_updated_at_column();

CREATE TRIGGER update_carbon_challenges_updated_at BEFORE UPDATE ON carbon_challenges
    FOR EACH ROW EXECUTE FUNCTION update_carbon_updated_at_column();

CREATE TRIGGER update_user_challenge_participations_updated_at BEFORE UPDATE ON user_challenge_participations
    FOR EACH ROW EXECUTE FUNCTION update_carbon_updated_at_column();

CREATE TRIGGER update_carbon_reward_history_updated_at BEFORE UPDATE ON carbon_reward_history
    FOR EACH ROW EXECUTE FUNCTION update_carbon_updated_at_column();