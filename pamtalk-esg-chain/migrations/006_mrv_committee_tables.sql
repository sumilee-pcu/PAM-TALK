-- MRV 및 ESG위원회 시스템 데이터베이스 스키마
-- Migration: 006_mrv_committee_tables.sql

-- ============================================================================
-- 1. MRV 측정 데이터 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrv_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id TEXT NOT NULL UNIQUE,
    user_id TEXT NOT NULL,

    -- 탄소 계산 결과
    carbon_savings_kg REAL NOT NULL,
    dc_units REAL NOT NULL,
    esg_gold_amount REAL NOT NULL,

    -- 측정 정보
    measurement_method TEXT NOT NULL,  -- manual, automated, sensor, manual_verified
    measurement_timestamp TIMESTAMP NOT NULL,
    measurement_location_lat REAL,
    measurement_location_lng REAL,

    -- 활동 정보
    activity_type TEXT NOT NULL,
    product_name TEXT,
    quantity REAL NOT NULL,
    origin_region TEXT,
    destination_region TEXT,
    farming_method TEXT,
    transport_method TEXT,
    packaging_type TEXT,
    activity_date TIMESTAMP,

    -- 측정 상태 및 신뢰도
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, measured, verified, rejected
    confidence_score REAL NOT NULL,

    -- 데이터 무결성
    data_hash TEXT NOT NULL,
    metadata TEXT,  -- JSON 형식

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mrv_measurements_user ON mrv_measurements(user_id);
CREATE INDEX idx_mrv_measurements_status ON mrv_measurements(status);
CREATE INDEX idx_mrv_measurements_timestamp ON mrv_measurements(measurement_timestamp);
CREATE INDEX idx_mrv_measurements_activity_type ON mrv_measurements(activity_type);


-- ============================================================================
-- 2. 증빙 자료 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrv_evidences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id TEXT NOT NULL,

    -- 증빙 정보
    evidence_type TEXT NOT NULL,  -- receipt, photo, gps, sensor_data, invoice, certificate, meter_reading
    file_path TEXT,
    file_hash TEXT,
    data TEXT,  -- JSON 형식 데이터

    -- 메타데이터
    description TEXT,
    timestamp TIMESTAMP NOT NULL,
    evidence_hash TEXT NOT NULL,  -- 위조 방지

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (measurement_id) REFERENCES mrv_measurements(measurement_id) ON DELETE CASCADE
);

CREATE INDEX idx_evidences_measurement ON mrv_evidences(measurement_id);
CREATE INDEX idx_evidences_type ON mrv_evidences(evidence_type);


-- ============================================================================
-- 3. ESG 위원회 위원 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS committee_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT NOT NULL UNIQUE,

    -- 위원 정보
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    wallet_address TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,  -- reviewer, approver, admin, auditor

    -- 전문 분야
    specialization TEXT,  -- JSON array: ["agriculture", "renewable_energy"]

    -- 상태
    active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP,

    -- 통계
    total_reviews INTEGER DEFAULT 0,
    total_approved INTEGER DEFAULT 0,
    total_rejected INTEGER DEFAULT 0,

    -- 메타데이터
    profile_data TEXT,  -- JSON

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_committee_members_role ON committee_members(role);
CREATE INDEX idx_committee_members_active ON committee_members(active);
CREATE INDEX idx_committee_members_wallet ON committee_members(wallet_address);


-- ============================================================================
-- 4. 검증 요청 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS verification_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id TEXT NOT NULL UNIQUE,
    measurement_id TEXT NOT NULL,

    -- 제출 정보
    submitted_by TEXT NOT NULL,
    submitted_at TIMESTAMP NOT NULL,

    -- 검증 상태
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, in_review, approved, rejected, resubmission_required, escalated

    -- 배정 정보
    assigned_to TEXT,  -- committee member_id
    assigned_at TIMESTAMP,

    -- 우선순위
    priority INTEGER DEFAULT 0,  -- 0: normal, 1: high, 2: urgent

    -- 검증 결과
    verification_result TEXT,  -- JSON
    approved_at TIMESTAMP,
    approved_by TEXT,

    -- 반려 사유
    rejection_reason TEXT,

    -- 메타데이터
    comments TEXT,  -- JSON array
    metadata TEXT,  -- JSON

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (measurement_id) REFERENCES mrv_measurements(measurement_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES committee_members(member_id)
);

CREATE INDEX idx_verification_requests_status ON verification_requests(status);
CREATE INDEX idx_verification_requests_assigned ON verification_requests(assigned_to);
CREATE INDEX idx_verification_requests_submitted_by ON verification_requests(submitted_by);
CREATE INDEX idx_verification_requests_priority ON verification_requests(priority);
CREATE INDEX idx_verification_requests_measurement ON verification_requests(measurement_id);


-- ============================================================================
-- 5. 검증 결과 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS verification_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id TEXT NOT NULL UNIQUE,
    request_id TEXT NOT NULL,
    measurement_id TEXT NOT NULL,

    -- 검증 판정
    approved BOOLEAN NOT NULL,
    confidence_score_verified REAL NOT NULL,
    carbon_savings_verified REAL NOT NULL,
    dc_units_verified REAL NOT NULL,

    -- 검증 세부사항
    verification_method TEXT NOT NULL,
    verified_by TEXT NOT NULL,
    verified_at TIMESTAMP NOT NULL,

    -- 체크리스트
    evidence_verified BOOLEAN NOT NULL,
    data_integrity_verified BOOLEAN NOT NULL,
    calculation_verified BOOLEAN NOT NULL,
    checklist_results TEXT,  -- JSON

    -- 피드백
    verifier_comments TEXT,
    recommendations TEXT,  -- JSON array

    -- 블록체인 기록
    blockchain_tx_id TEXT,
    verification_hash TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (request_id) REFERENCES verification_requests(request_id) ON DELETE CASCADE,
    FOREIGN KEY (measurement_id) REFERENCES mrv_measurements(measurement_id),
    FOREIGN KEY (verified_by) REFERENCES committee_members(member_id)
);

CREATE INDEX idx_verification_results_request ON verification_results(request_id);
CREATE INDEX idx_verification_results_measurement ON verification_results(measurement_id);
CREATE INDEX idx_verification_results_verified_by ON verification_results(verified_by);
CREATE INDEX idx_verification_results_blockchain ON verification_results(blockchain_tx_id);


-- ============================================================================
-- 6. MRV 리포트 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrv_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL UNIQUE,

    -- 리포트 정보
    report_type TEXT NOT NULL,  -- daily, weekly, monthly, quarterly, annual, custom, verification_request
    title TEXT NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,

    -- 리포트 데이터
    summary TEXT NOT NULL,  -- JSON
    detailed_data TEXT NOT NULL,  -- JSON array

    -- 생성 정보
    generated_by TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL,

    -- 파일 정보
    format TEXT NOT NULL DEFAULT 'json',  -- json, pdf, csv, xlsx
    file_path TEXT,

    -- 메타데이터
    metadata TEXT,  -- JSON

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mrv_reports_type ON mrv_reports(report_type);
CREATE INDEX idx_mrv_reports_generated_by ON mrv_reports(generated_by);
CREATE INDEX idx_mrv_reports_period ON mrv_reports(period_start, period_end);


-- ============================================================================
-- 7. 블록체인 검증 기록 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS blockchain_verification_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verification_result_id TEXT NOT NULL,

    -- 블록체인 정보
    tx_id TEXT NOT NULL UNIQUE,
    block_number INTEGER NOT NULL,
    verification_hash TEXT NOT NULL,

    -- 데이터
    on_chain_data TEXT NOT NULL,  -- JSON

    -- 검증
    data_integrity_verified BOOLEAN DEFAULT TRUE,
    last_verified_at TIMESTAMP,

    -- 링크
    explorer_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (verification_result_id) REFERENCES verification_results(result_id)
);

CREATE INDEX idx_blockchain_records_tx ON blockchain_verification_records(tx_id);
CREATE INDEX idx_blockchain_records_result ON blockchain_verification_records(verification_result_id);
CREATE INDEX idx_blockchain_records_hash ON blockchain_verification_records(verification_hash);


-- ============================================================================
-- 8. 검증 인증서 NFT 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS verification_certificate_nfts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verification_result_id TEXT NOT NULL,

    -- NFT 정보
    asset_id INTEGER NOT NULL UNIQUE,
    nft_name TEXT NOT NULL,
    nft_url TEXT,

    -- 메타데이터
    metadata TEXT NOT NULL,  -- JSON

    -- 블록체인 정보
    creation_tx_id TEXT NOT NULL,
    creator_address TEXT NOT NULL,

    -- 소유권
    current_owner TEXT,
    issued_to TEXT NOT NULL,

    -- 링크
    explorer_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (verification_result_id) REFERENCES verification_results(result_id)
);

CREATE INDEX idx_certificate_nfts_asset ON verification_certificate_nfts(asset_id);
CREATE INDEX idx_certificate_nfts_owner ON verification_certificate_nfts(current_owner);
CREATE INDEX idx_certificate_nfts_result ON verification_certificate_nfts(verification_result_id);


-- ============================================================================
-- 9. 위원회 활동 로그 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS committee_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT NOT NULL,

    -- 활동 정보
    action_type TEXT NOT NULL,  -- assign, review, approve, reject, comment, escalate
    target_type TEXT NOT NULL,  -- verification_request, measurement
    target_id TEXT NOT NULL,

    -- 세부사항
    action_details TEXT,  -- JSON
    comments TEXT,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (member_id) REFERENCES committee_members(member_id)
);

CREATE INDEX idx_committee_log_member ON committee_activity_log(member_id);
CREATE INDEX idx_committee_log_action ON committee_activity_log(action_type);
CREATE INDEX idx_committee_log_target ON committee_activity_log(target_type, target_id);
CREATE INDEX idx_committee_log_timestamp ON committee_activity_log(timestamp);


-- ============================================================================
-- 10. MRV 통계 (일별 집계)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrv_daily_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_date DATE NOT NULL UNIQUE,

    -- 측정 통계
    total_measurements INTEGER DEFAULT 0,
    pending_measurements INTEGER DEFAULT 0,
    verified_measurements INTEGER DEFAULT 0,
    rejected_measurements INTEGER DEFAULT 0,

    -- 탄소 통계
    total_carbon_measured_kg REAL DEFAULT 0.0,
    total_carbon_verified_kg REAL DEFAULT 0.0,
    total_dc_issued REAL DEFAULT 0.0,

    -- 검증 통계
    total_verification_requests INTEGER DEFAULT 0,
    pending_verifications INTEGER DEFAULT 0,
    approved_verifications INTEGER DEFAULT 0,
    rejected_verifications INTEGER DEFAULT 0,

    -- 위원회 통계
    active_reviewers INTEGER DEFAULT 0,
    average_review_time_hours REAL DEFAULT 0.0,
    auto_approved_count INTEGER DEFAULT 0,

    -- 신뢰도 통계
    average_confidence_score REAL DEFAULT 0.0,
    high_confidence_count INTEGER DEFAULT 0,  -- >= 80
    low_confidence_count INTEGER DEFAULT 0,   -- < 60

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mrv_daily_stats_date ON mrv_daily_stats(stat_date);


-- ============================================================================
-- 11. 뷰(View): 검증 대기 목록
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_pending_verifications AS
SELECT
    vr.request_id,
    vr.measurement_id,
    vr.status,
    vr.priority,
    vr.submitted_by,
    vr.submitted_at,
    vr.assigned_to,
    vr.assigned_at,

    m.carbon_savings_kg,
    m.dc_units,
    m.esg_gold_amount,
    m.confidence_score,
    m.activity_type,
    m.measurement_method,

    cm.name as reviewer_name,
    cm.email as reviewer_email,

    COUNT(e.id) as evidence_count,

    (julianday('now') - julianday(vr.submitted_at)) * 24 as hours_waiting

FROM verification_requests vr
JOIN mrv_measurements m ON vr.measurement_id = m.measurement_id
LEFT JOIN committee_members cm ON vr.assigned_to = cm.member_id
LEFT JOIN mrv_evidences e ON m.measurement_id = e.measurement_id

WHERE vr.status IN ('pending', 'in_review')

GROUP BY vr.request_id
ORDER BY vr.priority DESC, vr.submitted_at ASC;


-- ============================================================================
-- 12. 뷰(View): 위원회 위원 성과
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_committee_performance AS
SELECT
    cm.member_id,
    cm.name,
    cm.role,
    cm.specialization,
    cm.active,

    -- 검증 통계
    COUNT(DISTINCT vr.request_id) as total_assigned,
    SUM(CASE WHEN vr.status = 'approved' THEN 1 ELSE 0 END) as total_approved,
    SUM(CASE WHEN vr.status = 'rejected' THEN 1 ELSE 0 END) as total_rejected,
    SUM(CASE WHEN vr.status IN ('pending', 'in_review') THEN 1 ELSE 0 END) as currently_reviewing,

    -- 탄소 통계
    SUM(CASE WHEN vr.status = 'approved' THEN m.carbon_savings_kg ELSE 0 END) as total_carbon_verified_kg,
    SUM(CASE WHEN vr.status = 'approved' THEN m.dc_units ELSE 0 END) as total_dc_verified,

    -- 평균 리뷰 시간 (승인된 건만)
    AVG(CASE
        WHEN vr.status = 'approved' AND vr.approved_at IS NOT NULL
        THEN (julianday(vr.approved_at) - julianday(vr.assigned_at)) * 24
        ELSE NULL
    END) as avg_review_time_hours,

    -- 승인율
    CASE
        WHEN COUNT(DISTINCT CASE WHEN vr.status IN ('approved', 'rejected') THEN vr.request_id END) > 0
        THEN ROUND(
            100.0 * SUM(CASE WHEN vr.status = 'approved' THEN 1 ELSE 0 END) /
            COUNT(DISTINCT CASE WHEN vr.status IN ('approved', 'rejected') THEN vr.request_id END),
            2
        )
        ELSE 0
    END as approval_rate,

    -- 활동 정보
    cm.last_active_at,
    cm.joined_at

FROM committee_members cm
LEFT JOIN verification_requests vr ON cm.member_id = vr.assigned_to
LEFT JOIN mrv_measurements m ON vr.measurement_id = m.measurement_id

GROUP BY cm.member_id;


-- ============================================================================
-- 13. 트리거: 검증 요청 상태 변경 시 위원 통계 업데이트
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS trg_update_committee_stats_on_verification
AFTER UPDATE ON verification_requests
WHEN NEW.status != OLD.status AND NEW.status IN ('approved', 'rejected')
BEGIN
    UPDATE committee_members
    SET
        total_reviews = total_reviews + 1,
        total_approved = CASE WHEN NEW.status = 'approved' THEN total_approved + 1 ELSE total_approved END,
        total_rejected = CASE WHEN NEW.status = 'rejected' THEN total_rejected + 1 ELSE total_rejected END,
        last_active_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE member_id = NEW.assigned_to;
END;


-- ============================================================================
-- 14. 트리거: 측정 데이터 검증 시 MRV 측정 상태 업데이트
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS trg_update_measurement_on_verification
AFTER INSERT ON verification_results
BEGIN
    UPDATE mrv_measurements
    SET
        status = CASE WHEN NEW.approved = 1 THEN 'verified' ELSE 'rejected' END,
        carbon_savings_kg = NEW.carbon_savings_verified,
        dc_units = NEW.dc_units_verified,
        confidence_score = NEW.confidence_score_verified,
        updated_at = CURRENT_TIMESTAMP
    WHERE measurement_id = NEW.measurement_id;
END;


-- ============================================================================
-- 15. 시스템 설정 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS mrv_system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 기본 설정 삽입
INSERT OR IGNORE INTO mrv_system_config (key, value, description) VALUES
    ('auto_approve_confidence_threshold', '95', '자동 승인 신뢰도 기준 (%)'),
    ('auto_approve_evidence_count', '3', '자동 승인 최소 증빙 개수'),
    ('auto_approve_carbon_max', '50', '자동 승인 최대 탄소 절약량 (kg)'),
    ('review_sla_hours', '48', '검증 SLA 시간'),
    ('high_priority_carbon_threshold', '100', '높은 우선순위 기준 (kg)'),
    ('blockchain_enabled', 'true', '블록체인 기록 활성화'),
    ('nft_certificate_enabled', 'true', 'NFT 인증서 발행 활성화');


-- ============================================================================
-- 마이그레이션 완료
-- ============================================================================
