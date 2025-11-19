-- PAM-TALK ESG Chain Database Schema Migration
-- Version: 001
-- Description: Initial table creation for token distribution system

-- 위원회 테이블
CREATE TABLE IF NOT EXISTS committees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    wallet_address VARCHAR(58) NOT NULL UNIQUE,
    wallet_mnemonic TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 공급자 테이블
CREATE TABLE IF NOT EXISTS providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    wallet_address VARCHAR(58) NOT NULL UNIQUE,
    wallet_mnemonic TEXT NOT NULL,
    region VARCHAR(100),
    farm_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 소비자 테이블
CREATE TABLE IF NOT EXISTS consumers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    wallet_address VARCHAR(58) NOT NULL UNIQUE,
    wallet_mnemonic TEXT NOT NULL,
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 토큰 발행 히스토리
CREATE TABLE IF NOT EXISTS token_mint_history (
    id SERIAL PRIMARY KEY,
    amount INTEGER NOT NULL,
    unit_name VARCHAR(50) NOT NULL,
    description TEXT,
    issued_by VARCHAR(255) NOT NULL,
    asset_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ESG 쿠폰 테이블
CREATE TABLE IF NOT EXISTS esg_coupons (
    id SERIAL PRIMARY KEY,
    coupon_code VARCHAR(100) NOT NULL UNIQUE,
    asset_id BIGINT NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    mint_history_id INTEGER REFERENCES token_mint_history(id),

    -- 배분 관련
    committee_id INTEGER REFERENCES committees(id),
    provider_id INTEGER REFERENCES providers(id),
    consumer_id INTEGER REFERENCES consumers(id),

    -- 상태 관리
    status VARCHAR(20) NOT NULL DEFAULT 'ISSUED'
           CHECK (status IN ('ISSUED', 'COMMITTEE', 'PROVIDER', 'CONSUMER', 'USED', 'EXPIRED')),

    -- 타임스탬프
    committee_assigned_at TIMESTAMP NULL,
    provider_assigned_at TIMESTAMP NULL,
    consumer_assigned_at TIMESTAMP NULL,
    used_at TIMESTAMP NULL,
    redeemed_at TIMESTAMP NULL,
    expired_at TIMESTAMP NULL,

    -- 블록체인 정보
    tx_hash VARCHAR(64),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 토큰 배분 로그 테이블
CREATE TABLE IF NOT EXISTS token_distributions (
    id SERIAL PRIMARY KEY,
    committee_id INTEGER REFERENCES committees(id),
    provider_id INTEGER REFERENCES providers(id),
    consumer_id INTEGER REFERENCES consumers(id),
    amount INTEGER NOT NULL,
    tx_hash VARCHAR(64) NOT NULL,
    distribution_type VARCHAR(20) NOT NULL
                     CHECK (distribution_type IN ('COMMITTEE', 'PROVIDER', 'CONSUMER')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_esg_coupons_status ON esg_coupons(status);
CREATE INDEX IF NOT EXISTS idx_esg_coupons_coupon_code ON esg_coupons(coupon_code);
CREATE INDEX IF NOT EXISTS idx_esg_coupons_asset_id ON esg_coupons(asset_id);
CREATE INDEX IF NOT EXISTS idx_token_distributions_tx_hash ON token_distributions(tx_hash);
CREATE INDEX IF NOT EXISTS idx_committees_wallet_address ON committees(wallet_address);
CREATE INDEX IF NOT EXISTS idx_providers_wallet_address ON providers(wallet_address);
CREATE INDEX IF NOT EXISTS idx_consumers_wallet_address ON consumers(wallet_address);

-- 트리거 함수: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- updated_at 트리거 적용
CREATE TRIGGER update_committees_updated_at BEFORE UPDATE ON committees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_providers_updated_at BEFORE UPDATE ON providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consumers_updated_at BEFORE UPDATE ON consumers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_esg_coupons_updated_at BEFORE UPDATE ON esg_coupons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();