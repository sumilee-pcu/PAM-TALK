-- PAM-TALK ESG Chain Database Schema Migration
-- Version: 002
-- Description: Seed data for initial system setup

-- 샘플 위원회 데이터
INSERT INTO committees (name, wallet_address, wallet_mnemonic) VALUES
('한국 농업 위원회', 'SAMPLE_COMMITTEE_ADDRESS_1', 'SAMPLE_COMMITTEE_MNEMONIC_1'),
('지역 ESG 위원회', 'SAMPLE_COMMITTEE_ADDRESS_2', 'SAMPLE_COMMITTEE_MNEMONIC_2')
ON CONFLICT (wallet_address) DO NOTHING;

-- 샘플 공급자 데이터
INSERT INTO providers (name, wallet_address, wallet_mnemonic, region, farm_type) VALUES
('김농부 농장', 'SAMPLE_PROVIDER_ADDRESS_1', 'SAMPLE_PROVIDER_MNEMONIC_1', '경기도', '유기농'),
('이채소 농원', 'SAMPLE_PROVIDER_ADDRESS_2', 'SAMPLE_PROVIDER_MNEMONIC_2', '전라남도', '친환경'),
('박과수 농장', 'SAMPLE_PROVIDER_ADDRESS_3', 'SAMPLE_PROVIDER_MNEMONIC_3', '경상북도', '무농약')
ON CONFLICT (wallet_address) DO NOTHING;

-- 샘플 소비자 데이터
INSERT INTO consumers (name, email, wallet_address, wallet_mnemonic, region) VALUES
('소비자A', 'consumer_a@example.com', 'SAMPLE_CONSUMER_ADDRESS_1', 'SAMPLE_CONSUMER_MNEMONIC_1', '서울시'),
('소비자B', 'consumer_b@example.com', 'SAMPLE_CONSUMER_ADDRESS_2', 'SAMPLE_CONSUMER_MNEMONIC_2', '부산시'),
('소비자C', 'consumer_c@example.com', 'SAMPLE_CONSUMER_ADDRESS_3', 'SAMPLE_CONSUMER_MNEMONIC_3', '대구시')
ON CONFLICT (wallet_address) DO NOTHING;

-- 주의사항 메모
-- 실제 운영 시에는 다음 작업이 필요합니다:
-- 1. wallet_address와 wallet_mnemonic을 실제 Algorand 지갑으로 교체
-- 2. 민감한 정보는 환경변수나 암호화된 저장소에 보관
-- 3. 샘플 데이터 삭제 후 실제 데이터로 교체