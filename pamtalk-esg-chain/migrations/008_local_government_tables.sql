-- ============================================================================
-- 008: Local Government Homepage Tables
-- ============================================================================
-- Purpose: Tables for local government carbon tracking, producer registration,
--          ESG programs, incentive policies, and charging station management
-- Created: 2025-11-02
-- ============================================================================

-- ============================================================================
-- 1. Local Government Entities
-- ============================================================================

-- Local government basic information
CREATE TABLE IF NOT EXISTS local_governments (
    government_id TEXT PRIMARY KEY,
    government_name TEXT NOT NULL,
    government_type TEXT NOT NULL CHECK(government_type IN ('city', 'county', 'district', 'province')),
    region_code TEXT UNIQUE NOT NULL,
    parent_government_id TEXT,

    -- Contact information
    contact_person TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    office_address TEXT,
    website_url TEXT,

    -- Geographic data
    latitude REAL,
    longitude REAL,
    area_sqkm REAL,
    population INTEGER,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    joined_date DATE NOT NULL,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (parent_government_id) REFERENCES local_governments(government_id)
);

CREATE INDEX idx_local_governments_region ON local_governments(region_code);
CREATE INDEX idx_local_governments_type ON local_governments(government_type);

-- ============================================================================
-- 2. Carbon Reduction Statistics
-- ============================================================================

-- Real-time carbon reduction statistics by local government
CREATE TABLE IF NOT EXISTS local_carbon_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    government_id TEXT NOT NULL,
    stat_date DATE NOT NULL,
    stat_period TEXT NOT NULL CHECK(stat_period IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),

    -- Carbon metrics (kg CO2)
    total_carbon_reduction REAL DEFAULT 0,
    baseline_emissions REAL DEFAULT 0,
    current_emissions REAL DEFAULT 0,
    reduction_percentage REAL DEFAULT 0,

    -- Activity breakdown
    ev_usage_reduction REAL DEFAULT 0,
    renewable_energy_reduction REAL DEFAULT 0,
    recycling_reduction REAL DEFAULT 0,
    tree_planting_reduction REAL DEFAULT 0,
    green_products_reduction REAL DEFAULT 0,

    -- Participation metrics
    active_residents INTEGER DEFAULT 0,
    active_businesses INTEGER DEFAULT 0,
    total_activities INTEGER DEFAULT 0,

    -- ESG-Gold metrics
    esg_gold_issued BIGINT DEFAULT 0,
    esg_gold_circulating BIGINT DEFAULT 0,

    -- Rankings
    national_rank INTEGER,
    regional_rank INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (government_id) REFERENCES local_governments(government_id),
    UNIQUE(government_id, stat_date, stat_period)
);

CREATE INDEX idx_local_carbon_stats_gov ON local_carbon_stats(government_id);
CREATE INDEX idx_local_carbon_stats_date ON local_carbon_stats(stat_date);

-- ============================================================================
-- 3. Regional Carbon Reduction Targets
-- ============================================================================

CREATE TABLE IF NOT EXISTS regional_carbon_targets (
    target_id INTEGER PRIMARY KEY AUTOINCREMENT,
    government_id TEXT NOT NULL,
    target_year INTEGER NOT NULL,
    target_period TEXT NOT NULL CHECK(target_period IN ('annual', 'quarterly', 'monthly')),

    -- Target values
    target_reduction_kg REAL NOT NULL,
    baseline_year INTEGER NOT NULL,
    baseline_emissions_kg REAL NOT NULL,

    -- Progress
    current_reduction_kg REAL DEFAULT 0,
    achievement_percentage REAL DEFAULT 0,
    status TEXT DEFAULT 'in_progress' CHECK(status IN ('not_started', 'in_progress', 'achieved', 'exceeded', 'failed')),

    -- Metadata
    set_date DATE NOT NULL,
    review_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (government_id) REFERENCES local_governments(government_id),
    UNIQUE(government_id, target_year, target_period)
);

CREATE INDEX idx_carbon_targets_gov ON regional_carbon_targets(government_id);

-- ============================================================================
-- 4. Regional ESG Programs
-- ============================================================================

CREATE TABLE IF NOT EXISTS regional_esg_programs (
    program_id TEXT PRIMARY KEY,
    government_id TEXT NOT NULL,

    -- Program details
    program_name TEXT NOT NULL,
    program_type TEXT NOT NULL CHECK(program_type IN ('carbon_reduction', 'renewable_energy', 'waste_management', 'green_transport', 'education', 'incentive', 'other')),
    description TEXT,
    objectives TEXT,

    -- Target audience
    target_group TEXT CHECK(target_group IN ('residents', 'businesses', 'farmers', 'students', 'all')),

    -- Budget and support
    budget_amount REAL,
    support_type TEXT CHECK(support_type IN ('financial', 'technical', 'educational', 'equipment', 'mixed')),

    -- Schedule
    start_date DATE NOT NULL,
    end_date DATE,
    application_start DATE,
    application_deadline DATE,

    -- Capacity
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,

    -- Requirements
    eligibility_criteria TEXT,
    required_documents TEXT,

    -- Status
    status TEXT DEFAULT 'planned' CHECK(status IN ('planned', 'recruiting', 'ongoing', 'completed', 'cancelled')),

    -- Results
    expected_carbon_reduction REAL,
    actual_carbon_reduction REAL,

    -- Contact
    manager_name TEXT,
    manager_email TEXT,
    manager_phone TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (government_id) REFERENCES local_governments(government_id)
);

CREATE INDEX idx_regional_programs_gov ON regional_esg_programs(government_id);
CREATE INDEX idx_regional_programs_type ON regional_esg_programs(program_type);
CREATE INDEX idx_regional_programs_status ON regional_esg_programs(status);

-- ============================================================================
-- 5. Local Producer Registration
-- ============================================================================

-- Agricultural and fisheries producers
CREATE TABLE IF NOT EXISTS local_producers (
    producer_id TEXT PRIMARY KEY,
    government_id TEXT NOT NULL,

    -- Producer information
    producer_name TEXT NOT NULL,
    producer_type TEXT NOT NULL CHECK(producer_type IN ('farmer', 'fisherman', 'livestock', 'cooperative', 'other')),
    business_registration_number TEXT UNIQUE,

    -- Contact
    contact_person TEXT NOT NULL,
    contact_phone TEXT NOT NULL,
    contact_email TEXT,

    -- Address
    farm_address TEXT NOT NULL,
    farm_latitude REAL,
    farm_longitude REAL,
    farm_area_sqm REAL,

    -- Certifications
    organic_certified BOOLEAN DEFAULT FALSE,
    gap_certified BOOLEAN DEFAULT FALSE,
    haccp_certified BOOLEAN DEFAULT FALSE,
    other_certifications TEXT,

    -- ESG metrics
    carbon_footprint_kg REAL,
    water_usage_liters REAL,
    renewable_energy_ratio REAL,
    waste_recycling_ratio REAL,

    -- Verification
    verification_status TEXT DEFAULT 'pending' CHECK(verification_status IN ('pending', 'verified', 'rejected', 'suspended')),
    verified_by TEXT,
    verified_at TIMESTAMP,
    verification_notes TEXT,

    -- Algorand wallet
    algorand_address TEXT,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    registration_date DATE NOT NULL,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (government_id) REFERENCES local_governments(government_id)
);

CREATE INDEX idx_producers_gov ON local_producers(government_id);
CREATE INDEX idx_producers_type ON local_producers(producer_type);
CREATE INDEX idx_producers_verification ON local_producers(verification_status);

-- Producer products
CREATE TABLE IF NOT EXISTS producer_products (
    product_id TEXT PRIMARY KEY,
    producer_id TEXT NOT NULL,

    -- Product details
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    product_type TEXT CHECK(product_type IN ('vegetable', 'fruit', 'grain', 'seafood', 'meat', 'dairy', 'processed', 'other')),
    description TEXT,

    -- Production info
    harvest_season TEXT,
    production_method TEXT CHECK(production_method IN ('organic', 'conventional', 'greenhouse', 'aquaculture', 'free_range', 'other')),

    -- Pricing
    unit_type TEXT NOT NULL,
    unit_price REAL,
    minimum_order REAL,

    -- Carbon footprint per unit
    carbon_footprint_per_unit REAL,

    -- Availability
    is_available BOOLEAN DEFAULT TRUE,
    stock_quantity REAL,

    -- Images
    product_image_url TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (producer_id) REFERENCES local_producers(producer_id)
);

CREATE INDEX idx_products_producer ON producer_products(producer_id);
CREATE INDEX idx_products_category ON producer_products(product_category);

-- Producer verification documents
CREATE TABLE IF NOT EXISTS producer_verification_documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    producer_id TEXT NOT NULL,

    document_type TEXT NOT NULL CHECK(document_type IN ('business_license', 'land_certificate', 'organic_cert', 'gap_cert', 'haccp_cert', 'id_card', 'bank_account', 'other')),
    document_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_type TEXT,
    file_size INTEGER,

    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by TEXT,
    verified_at TIMESTAMP,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (producer_id) REFERENCES local_producers(producer_id)
);

CREATE INDEX idx_verification_docs_producer ON producer_verification_documents(producer_id);

-- ============================================================================
-- 6. Local Government Incentive Policies
-- ============================================================================

CREATE TABLE IF NOT EXISTS local_incentive_policies (
    policy_id TEXT PRIMARY KEY,
    government_id TEXT NOT NULL,

    -- Policy details
    policy_name TEXT NOT NULL,
    policy_type TEXT NOT NULL CHECK(policy_type IN ('subsidy', 'tax_reduction', 'esg_gold_bonus', 'equipment_support', 'loan', 'voucher', 'other')),
    description TEXT NOT NULL,

    -- Eligibility
    target_group TEXT NOT NULL,
    eligibility_criteria TEXT NOT NULL,

    -- Benefits
    benefit_amount REAL,
    benefit_unit TEXT,
    esg_gold_bonus_percentage REAL,

    -- Budget
    total_budget REAL,
    remaining_budget REAL,

    -- Application period
    application_start_date DATE NOT NULL,
    application_end_date DATE,

    -- Requirements
    required_documents TEXT,
    required_activities TEXT,
    minimum_carbon_reduction REAL,

    -- Process
    review_period_days INTEGER DEFAULT 14,
    approval_authority TEXT,

    -- Status
    status TEXT DEFAULT 'active' CHECK(status IN ('draft', 'active', 'suspended', 'closed', 'cancelled')),

    -- Legal basis
    legal_basis TEXT,
    regulation_url TEXT,

    -- Contact
    contact_department TEXT,
    contact_phone TEXT,
    contact_email TEXT,

    -- Metadata
    effective_date DATE NOT NULL,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (government_id) REFERENCES local_governments(government_id)
);

CREATE INDEX idx_incentive_policies_gov ON local_incentive_policies(government_id);
CREATE INDEX idx_incentive_policies_type ON local_incentive_policies(policy_type);
CREATE INDEX idx_incentive_policies_status ON local_incentive_policies(status);

-- Incentive policy applications
CREATE TABLE IF NOT EXISTS incentive_applications (
    application_id TEXT PRIMARY KEY,
    policy_id TEXT NOT NULL,
    government_id TEXT NOT NULL,

    -- Applicant info
    applicant_type TEXT NOT NULL CHECK(applicant_type IN ('individual', 'business', 'producer', 'organization')),
    applicant_id TEXT NOT NULL,
    applicant_name TEXT NOT NULL,
    applicant_email TEXT NOT NULL,
    applicant_phone TEXT NOT NULL,

    -- Application details
    application_date DATE NOT NULL,
    requested_amount REAL,

    -- Supporting data
    carbon_reduction_achieved REAL,
    activities_completed TEXT,
    supporting_documents TEXT,

    -- Review
    status TEXT DEFAULT 'submitted' CHECK(status IN ('submitted', 'under_review', 'approved', 'rejected', 'appealed', 'paid')),
    reviewer_id TEXT,
    review_date DATE,
    review_notes TEXT,

    -- Approval
    approved_amount REAL,
    approval_date DATE,
    payment_date DATE,
    payment_reference TEXT,

    -- Algorand wallet for payment
    recipient_algorand_address TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (policy_id) REFERENCES local_incentive_policies(policy_id),
    FOREIGN KEY (government_id) REFERENCES local_governments(government_id)
);

CREATE INDEX idx_incentive_apps_policy ON incentive_applications(policy_id);
CREATE INDEX idx_incentive_apps_applicant ON incentive_applications(applicant_id);
CREATE INDEX idx_incentive_apps_status ON incentive_applications(status);

-- ============================================================================
-- 7. Charging Station Management
-- ============================================================================

CREATE TABLE IF NOT EXISTS charging_stations (
    station_id TEXT PRIMARY KEY,
    government_id TEXT NOT NULL,

    -- Station details
    station_name TEXT NOT NULL,
    station_type TEXT NOT NULL CHECK(station_type IN ('slow', 'fast', 'super_fast', 'mixed')),
    operator_name TEXT NOT NULL,
    operator_contact TEXT,

    -- Location
    address TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,

    -- Facility info
    total_chargers INTEGER NOT NULL,
    available_chargers INTEGER NOT NULL,
    charger_types TEXT, -- JSON array: ["AC 3kW", "DC 50kW", "DC 100kW"]

    -- Charging power
    max_power_kw REAL NOT NULL,

    -- Pricing
    price_per_kwh REAL,
    parking_fee_per_hour REAL,

    -- Payment methods
    accepts_esg_gold BOOLEAN DEFAULT FALSE,
    accepts_pam_token BOOLEAN DEFAULT FALSE,
    accepts_credit_card BOOLEAN DEFAULT TRUE,
    esg_gold_discount_percentage REAL DEFAULT 0,

    -- Operating hours
    operating_hours TEXT, -- JSON: {"monday": "00:00-24:00", ...}
    is_24_hours BOOLEAN DEFAULT TRUE,

    -- Amenities
    has_wifi BOOLEAN DEFAULT FALSE,
    has_restroom BOOLEAN DEFAULT FALSE,
    has_convenience_store BOOLEAN DEFAULT FALSE,
    has_cafe BOOLEAN DEFAULT FALSE,
    has_parking BOOLEAN DEFAULT TRUE,
    parking_capacity INTEGER,

    -- Accessibility
    wheelchair_accessible BOOLEAN DEFAULT FALSE,

    -- Status
    operational_status TEXT DEFAULT 'operational' CHECK(operational_status IN ('operational', 'maintenance', 'out_of_service', 'planned')),
    is_public BOOLEAN DEFAULT TRUE,

    -- Statistics
    total_charging_sessions INTEGER DEFAULT 0,
    total_energy_delivered_kwh REAL DEFAULT 0,
    total_carbon_reduction_kg REAL DEFAULT 0,
    average_rating REAL DEFAULT 0,
    review_count INTEGER DEFAULT 0,

    -- Installation
    installation_date DATE,
    last_maintenance_date DATE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (government_id) REFERENCES local_governments(government_id)
);

CREATE INDEX idx_charging_stations_gov ON charging_stations(government_id);
CREATE INDEX idx_charging_stations_location ON charging_stations(latitude, longitude);
CREATE INDEX idx_charging_stations_status ON charging_stations(operational_status);

-- Charging station usage records
CREATE TABLE IF NOT EXISTS charging_station_usage (
    usage_id TEXT PRIMARY KEY,
    station_id TEXT NOT NULL,

    -- User info
    user_algorand_address TEXT NOT NULL,
    user_id TEXT,

    -- Session details
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER,

    -- Energy
    energy_delivered_kwh REAL,
    max_power_kw REAL,

    -- Carbon reduction
    carbon_reduction_kg REAL,

    -- Payment
    total_cost REAL,
    payment_method TEXT CHECK(payment_method IN ('esg_gold', 'pam_token', 'credit_card', 'debit_card', 'mobile_pay', 'free')),
    esg_gold_amount BIGINT,
    pam_token_amount BIGINT,
    discount_applied REAL DEFAULT 0,

    -- Transaction
    payment_transaction_id TEXT,
    blockchain_tx_id TEXT,

    -- Status
    session_status TEXT DEFAULT 'in_progress' CHECK(session_status IN ('in_progress', 'completed', 'interrupted', 'failed')),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (station_id) REFERENCES charging_stations(station_id)
);

CREATE INDEX idx_station_usage_station ON charging_station_usage(station_id);
CREATE INDEX idx_station_usage_user ON charging_station_usage(user_algorand_address);
CREATE INDEX idx_station_usage_time ON charging_station_usage(start_time);

-- Charging station reviews
CREATE TABLE IF NOT EXISTS charging_station_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_id TEXT NOT NULL,
    user_id TEXT NOT NULL,

    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,

    -- Review aspects
    charger_speed_rating INTEGER CHECK(charger_speed_rating >= 1 AND charger_speed_rating <= 5),
    facility_rating INTEGER CHECK(facility_rating >= 1 AND facility_rating <= 5),
    accessibility_rating INTEGER CHECK(accessibility_rating >= 1 AND accessibility_rating <= 5),

    -- Status
    is_verified_usage BOOLEAN DEFAULT FALSE,
    is_visible BOOLEAN DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (station_id) REFERENCES charging_stations(station_id)
);

CREATE INDEX idx_station_reviews_station ON charging_station_reviews(station_id);

-- ============================================================================
-- 8. Regional Achievements and Rankings
-- ============================================================================

CREATE TABLE IF NOT EXISTS regional_achievements (
    achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    government_id TEXT NOT NULL,

    achievement_type TEXT NOT NULL CHECK(achievement_type IN ('carbon_reduction_milestone', 'participation_rate', 'program_success', 'innovation', 'ranking', 'other')),
    achievement_title TEXT NOT NULL,
    achievement_description TEXT,

    -- Metrics
    metric_value REAL,
    metric_unit TEXT,

    -- Achievement date
    achieved_date DATE NOT NULL,

    -- Recognition
    certificate_nft_id TEXT,
    award_level TEXT CHECK(award_level IN ('bronze', 'silver', 'gold', 'platinum')),

    -- Visibility
    is_featured BOOLEAN DEFAULT FALSE,
    display_priority INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (government_id) REFERENCES local_governments(government_id)
);

CREATE INDEX idx_achievements_gov ON regional_achievements(government_id);

-- ============================================================================
-- 9. Regional News and Announcements
-- ============================================================================

CREATE TABLE IF NOT EXISTS regional_announcements (
    announcement_id TEXT PRIMARY KEY,
    government_id TEXT NOT NULL,

    title TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    category TEXT CHECK(category IN ('policy', 'program', 'event', 'achievement', 'notice', 'emergency')),

    -- Priority
    priority INTEGER DEFAULT 1 CHECK(priority >= 0 AND priority <= 3),
    is_pinned BOOLEAN DEFAULT FALSE,

    -- Publishing
    author_name TEXT,
    published_at TIMESTAMP,
    expires_at TIMESTAMP,

    -- Attachments
    attachments TEXT, -- JSON array

    -- Engagement
    view_count INTEGER DEFAULT 0,

    -- Status
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'archived')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (government_id) REFERENCES local_governments(government_id)
);

CREATE INDEX idx_announcements_gov ON regional_announcements(government_id);
CREATE INDEX idx_announcements_published ON regional_announcements(published_at);

-- ============================================================================
-- 10. Views for Dashboard
-- ============================================================================

-- Local government dashboard summary
CREATE VIEW IF NOT EXISTS v_local_government_dashboard AS
SELECT
    lg.government_id,
    lg.government_name,
    lg.government_type,
    lg.region_code,
    lg.population,

    -- Latest carbon stats
    lcs.total_carbon_reduction,
    lcs.reduction_percentage,
    lcs.active_residents,
    lcs.active_businesses,
    lcs.esg_gold_issued,
    lcs.national_rank,
    lcs.regional_rank,

    -- Target progress
    rct.target_reduction_kg,
    rct.achievement_percentage,

    -- Programs and policies
    (SELECT COUNT(*) FROM regional_esg_programs WHERE government_id = lg.government_id AND status = 'ongoing') as active_programs,
    (SELECT COUNT(*) FROM local_incentive_policies WHERE government_id = lg.government_id AND status = 'active') as active_policies,

    -- Producers
    (SELECT COUNT(*) FROM local_producers WHERE government_id = lg.government_id AND is_active = TRUE) as total_producers,
    (SELECT COUNT(*) FROM local_producers WHERE government_id = lg.government_id AND verification_status = 'verified') as verified_producers,

    -- Charging stations
    (SELECT COUNT(*) FROM charging_stations WHERE government_id = lg.government_id AND operational_status = 'operational') as operational_stations,
    (SELECT SUM(total_chargers) FROM charging_stations WHERE government_id = lg.government_id) as total_chargers

FROM local_governments lg
LEFT JOIN (
    SELECT * FROM local_carbon_stats
    WHERE (government_id, stat_date) IN (
        SELECT government_id, MAX(stat_date) FROM local_carbon_stats GROUP BY government_id
    )
) lcs ON lg.government_id = lcs.government_id
LEFT JOIN (
    SELECT * FROM regional_carbon_targets
    WHERE target_year = strftime('%Y', 'now') AND target_period = 'annual'
) rct ON lg.government_id = rct.government_id;

-- Charging station map view
CREATE VIEW IF NOT EXISTS v_charging_station_map AS
SELECT
    cs.station_id,
    cs.government_id,
    lg.government_name,
    cs.station_name,
    cs.station_type,
    cs.operator_name,
    cs.address,
    cs.latitude,
    cs.longitude,
    cs.total_chargers,
    cs.available_chargers,
    cs.charger_types,
    cs.max_power_kw,
    cs.price_per_kwh,
    cs.accepts_esg_gold,
    cs.esg_gold_discount_percentage,
    cs.is_24_hours,
    cs.operational_status,
    cs.average_rating,
    cs.total_charging_sessions,
    cs.total_carbon_reduction_kg
FROM charging_stations cs
JOIN local_governments lg ON cs.government_id = lg.government_id
WHERE cs.is_public = TRUE;

-- Producer directory view
CREATE VIEW IF NOT EXISTS v_producer_directory AS
SELECT
    lp.producer_id,
    lp.government_id,
    lg.government_name,
    lp.producer_name,
    lp.producer_type,
    lp.contact_person,
    lp.contact_phone,
    lp.contact_email,
    lp.farm_address,
    lp.farm_latitude,
    lp.farm_longitude,
    lp.organic_certified,
    lp.gap_certified,
    lp.haccp_certified,
    lp.verification_status,
    lp.carbon_footprint_kg,

    (SELECT COUNT(*) FROM producer_products WHERE producer_id = lp.producer_id AND is_available = TRUE) as available_products

FROM local_producers lp
JOIN local_governments lg ON lp.government_id = lg.government_id
WHERE lp.is_active = TRUE;

-- ============================================================================
-- 11. Triggers
-- ============================================================================

-- Update charging station available chargers
CREATE TRIGGER IF NOT EXISTS update_station_availability
AFTER INSERT ON charging_station_usage
WHEN NEW.session_status = 'in_progress'
BEGIN
    UPDATE charging_stations
    SET available_chargers = available_chargers - 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE station_id = NEW.station_id;
END;

CREATE TRIGGER IF NOT EXISTS release_station_charger
AFTER UPDATE ON charging_station_usage
WHEN NEW.session_status IN ('completed', 'interrupted', 'failed')
AND OLD.session_status = 'in_progress'
BEGIN
    UPDATE charging_stations
    SET available_chargers = available_chargers + 1,
        total_charging_sessions = total_charging_sessions + 1,
        total_energy_delivered_kwh = total_energy_delivered_kwh + COALESCE(NEW.energy_delivered_kwh, 0),
        total_carbon_reduction_kg = total_carbon_reduction_kg + COALESCE(NEW.carbon_reduction_kg, 0),
        updated_at = CURRENT_TIMESTAMP
    WHERE station_id = NEW.station_id;
END;

-- Update carbon stats when new reduction is recorded
CREATE TRIGGER IF NOT EXISTS update_local_carbon_stats
AFTER INSERT ON charging_station_usage
WHEN NEW.session_status = 'completed'
BEGIN
    UPDATE local_carbon_stats
    SET ev_usage_reduction = ev_usage_reduction + COALESCE(NEW.carbon_reduction_kg, 0),
        total_carbon_reduction = total_carbon_reduction + COALESCE(NEW.carbon_reduction_kg, 0),
        updated_at = CURRENT_TIMESTAMP
    WHERE government_id = (SELECT government_id FROM charging_stations WHERE station_id = NEW.station_id)
        AND stat_date = DATE('now')
        AND stat_period = 'daily';
END;

-- Update announcement view count
CREATE TRIGGER IF NOT EXISTS increment_announcement_views
AFTER UPDATE ON regional_announcements
WHEN NEW.view_count > OLD.view_count
BEGIN
    UPDATE regional_announcements
    SET updated_at = CURRENT_TIMESTAMP
    WHERE announcement_id = NEW.announcement_id;
END;

-- Update policy budget when application approved
CREATE TRIGGER IF NOT EXISTS deduct_policy_budget
AFTER UPDATE ON incentive_applications
WHEN NEW.status = 'approved' AND OLD.status != 'approved'
BEGIN
    UPDATE local_incentive_policies
    SET remaining_budget = remaining_budget - COALESCE(NEW.approved_amount, 0),
        updated_at = CURRENT_TIMESTAMP
    WHERE policy_id = NEW.policy_id;
END;

-- ============================================================================
-- 12. Sample Data for Testing
-- ============================================================================

-- Sample local government
INSERT INTO local_governments (government_id, government_name, government_type, region_code, population, contact_email, contact_phone, is_active, joined_date)
VALUES
('GOV-SEOUL-001', '서울특별시', 'city', 'KR-11', 9700000, 'carbon@seoul.go.kr', '02-1234-5678', TRUE, '2024-01-01'),
('GOV-BUSAN-001', '부산광역시', 'city', 'KR-26', 3400000, 'esg@busan.go.kr', '051-1234-5678', TRUE, '2024-01-01'),
('GOV-JEJU-001', '제주특별자치도', 'province', 'KR-49', 670000, 'green@jeju.go.kr', '064-1234-5678', TRUE, '2024-01-15');

-- Sample carbon stats
INSERT INTO local_carbon_stats (government_id, stat_date, stat_period, total_carbon_reduction, active_residents, active_businesses, national_rank)
VALUES
('GOV-SEOUL-001', DATE('now'), 'daily', 125000, 8500, 1200, 1),
('GOV-BUSAN-001', DATE('now'), 'daily', 67000, 4200, 680, 2),
('GOV-JEJU-001', DATE('now'), 'daily', 18000, 1500, 200, 8);

-- Sample charging stations
INSERT INTO charging_stations (station_id, government_id, station_name, station_type, operator_name, address, latitude, longitude, total_chargers, available_chargers, max_power_kw, price_per_kwh, accepts_esg_gold, esg_gold_discount_percentage, operational_status, installation_date)
VALUES
('CS-SEOUL-001', 'GOV-SEOUL-001', '강남역 급속충전소', 'fast', '한국전력', '서울시 강남구 강남대로 396', 37.4979, 127.0276, 8, 6, 100, 350, TRUE, 15, 'operational', '2023-06-15'),
('CS-BUSAN-001', 'GOV-BUSAN-001', '해운대 충전센터', 'super_fast', 'SK네트웍스', '부산시 해운대구 해운대해변로 264', 35.1587, 129.1603, 12, 10, 350, 450, TRUE, 20, 'operational', '2023-08-01'),
('CS-JEJU-001', 'GOV-JEJU-001', '제주공항 충전소', 'mixed', '제주도시공사', '제주시 공항로 2', 33.5066, 126.4929, 6, 5, 50, 300, TRUE, 25, 'operational', '2023-05-10');

-- Sample ESG programs
INSERT INTO regional_esg_programs (program_id, government_id, program_name, program_type, description, target_group, budget_amount, start_date, end_date, status, max_participants, manager_name)
VALUES
('PROG-SEOUL-001', 'GOV-SEOUL-001', '서울시 탄소중립 챌린지', 'carbon_reduction', '시민 참여형 탄소감축 캠페인', 'all', 500000000, '2024-03-01', '2024-12-31', 'ongoing', 100000, '김환경'),
('PROG-BUSAN-002', 'GOV-BUSAN-001', '부산 그린뉴딜 프로젝트', 'renewable_energy', '재생에너지 보급 확대 사업', 'businesses', 1000000000, '2024-01-01', '2024-12-31', 'ongoing', 500, '이지구');

-- Sample incentive policies
INSERT INTO local_incentive_policies (policy_id, government_id, policy_name, policy_type, description, target_group, benefit_amount, total_budget, remaining_budget, application_start_date, status, effective_date)
VALUES
('POL-SEOUL-001', 'GOV-SEOUL-001', '전기차 충전 지원금', 'subsidy', '전기차 이용자 충전비 50% 지원', 'residents', 100000, 5000000000, 4800000000, '2024-01-01', 'active', '2024-01-01'),
('POL-JEJU-001', 'GOV-JEJU-001', '친환경 농산물 생산 장려금', 'esg_gold_bonus', '유기농 인증 농가 ESG-Gold 30% 추가 지급', 'farmers', NULL, 200000000, 180000000, '2024-02-01', 'active', '2024-02-01');

-- ============================================================================
-- End of 008: Local Government Homepage Tables
-- ============================================================================
