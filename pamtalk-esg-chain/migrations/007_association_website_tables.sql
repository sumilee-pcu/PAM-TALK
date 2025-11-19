-- 협회 홈페이지 데이터베이스 스키마
-- Migration: 007_association_website_tables.sql

-- ============================================================================
-- 1. 회원 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS association_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT NOT NULL UNIQUE,

    -- 회원 정보
    member_type TEXT NOT NULL,  -- individual, corporate
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    password_hash TEXT NOT NULL,

    -- 기업 회원 추가 정보
    company_name TEXT,
    business_number TEXT,
    company_size TEXT,  -- small, medium, large
    industry TEXT,
    ceo_name TEXT,

    -- 주소
    address TEXT,
    city TEXT,
    postal_code TEXT,

    -- 회원 등급
    membership_tier TEXT NOT NULL DEFAULT 'basic',  -- basic, silver, gold, platinum
    membership_status TEXT NOT NULL DEFAULT 'pending',  -- pending, active, suspended, expired
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP,

    -- 추가 정보
    profile_image_url TEXT,
    bio TEXT,
    interests TEXT,  -- JSON array

    -- 통계
    esg_certification_count INTEGER DEFAULT 0,
    education_completed INTEGER DEFAULT 0,
    events_attended INTEGER DEFAULT 0,

    -- 메타데이터
    wallet_address TEXT,
    last_login_at TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_members_email ON association_members(email);
CREATE INDEX idx_members_type ON association_members(member_type);
CREATE INDEX idx_members_status ON association_members(membership_status);
CREATE INDEX idx_members_tier ON association_members(membership_tier);


-- ============================================================================
-- 2. 공지사항 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS association_notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_id TEXT NOT NULL UNIQUE,

    -- 공지사항 정보
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,

    -- 분류
    category TEXT NOT NULL,  -- general, event, policy, urgent
    priority INTEGER DEFAULT 0,  -- 0: normal, 1: important, 2: urgent
    is_pinned BOOLEAN DEFAULT FALSE,

    -- 작성자
    author_id TEXT NOT NULL,
    author_name TEXT,

    -- 첨부파일
    attachments TEXT,  -- JSON array

    -- 공개 설정
    visibility TEXT NOT NULL DEFAULT 'all',  -- all, members_only, tier_specific
    target_tiers TEXT,  -- JSON array: ["gold", "platinum"]

    -- 통계
    view_count INTEGER DEFAULT 0,

    -- 시간
    published_at TIMESTAMP,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (author_id) REFERENCES association_members(member_id)
);

CREATE INDEX idx_notices_category ON association_notices(category);
CREATE INDEX idx_notices_published ON association_notices(published_at);
CREATE INDEX idx_notices_priority ON association_notices(priority);
CREATE INDEX idx_notices_pinned ON association_notices(is_pinned);


-- ============================================================================
-- 3. 뉴스 및 활동 소식 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS association_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    news_id TEXT NOT NULL UNIQUE,

    -- 뉴스 정보
    title TEXT NOT NULL,
    subtitle TEXT,
    content TEXT NOT NULL,
    excerpt TEXT,

    -- 미디어
    featured_image_url TEXT,
    images TEXT,  -- JSON array
    video_url TEXT,

    -- 분류
    category TEXT NOT NULL,  -- event_report, achievement, partnership, research, media
    tags TEXT,  -- JSON array

    -- 작성자
    author_id TEXT,
    author_name TEXT NOT NULL,

    -- 공개 설정
    status TEXT NOT NULL DEFAULT 'draft',  -- draft, published, archived
    visibility TEXT NOT NULL DEFAULT 'public',  -- public, members_only

    -- SEO
    meta_title TEXT,
    meta_description TEXT,
    slug TEXT UNIQUE,

    -- 통계
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,

    -- 시간
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (author_id) REFERENCES association_members(member_id)
);

CREATE INDEX idx_news_category ON association_news(category);
CREATE INDEX idx_news_status ON association_news(status);
CREATE INDEX idx_news_published ON association_news(published_at);
CREATE INDEX idx_news_slug ON association_news(slug);


-- ============================================================================
-- 4. ESG 정책 및 가이드라인 문서
-- ============================================================================
CREATE TABLE IF NOT EXISTS esg_policy_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL UNIQUE,

    -- 문서 정보
    title TEXT NOT NULL,
    description TEXT,
    content TEXT NOT NULL,

    -- 분류
    category TEXT NOT NULL,  -- policy, guideline, standard, report, regulation
    subcategory TEXT,
    document_type TEXT,  -- internal, external, reference

    -- 버전 관리
    version TEXT NOT NULL DEFAULT '1.0',
    version_notes TEXT,
    is_latest BOOLEAN DEFAULT TRUE,

    -- 파일
    file_url TEXT,
    file_type TEXT,  -- pdf, docx, xlsx
    file_size INTEGER,

    -- 적용 범위
    applicable_to TEXT,  -- JSON array: ["all", "corporate_members"]
    effective_date TIMESTAMP,
    expiry_date TIMESTAMP,

    -- 승인
    approval_status TEXT NOT NULL DEFAULT 'draft',  -- draft, review, approved, archived
    approved_by TEXT,
    approved_at TIMESTAMP,

    -- 작성자
    author_id TEXT,
    author_name TEXT NOT NULL,

    -- 통계
    download_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,

    -- 관련 문서
    related_documents TEXT,  -- JSON array of document_ids

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (author_id) REFERENCES association_members(member_id)
);

CREATE INDEX idx_policy_docs_category ON esg_policy_documents(category);
CREATE INDEX idx_policy_docs_status ON esg_policy_documents(approval_status);
CREATE INDEX idx_policy_docs_latest ON esg_policy_documents(is_latest);
CREATE INDEX idx_policy_docs_effective ON esg_policy_documents(effective_date);


-- ============================================================================
-- 5. 교육 프로그램
-- ============================================================================
CREATE TABLE IF NOT EXISTS education_programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id TEXT NOT NULL UNIQUE,

    -- 프로그램 정보
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    objectives TEXT,  -- JSON array
    curriculum TEXT,  -- JSON

    -- 분류
    category TEXT NOT NULL,  -- basic, advanced, specialized, certification
    level TEXT,  -- beginner, intermediate, advanced
    format TEXT NOT NULL,  -- online, offline, hybrid

    -- 일정
    duration_hours INTEGER,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    registration_deadline TIMESTAMP,

    -- 정원 및 비용
    capacity INTEGER,
    enrolled_count INTEGER DEFAULT 0,
    fee_basic INTEGER DEFAULT 0,
    fee_silver INTEGER DEFAULT 0,
    fee_gold INTEGER DEFAULT 0,
    fee_platinum INTEGER DEFAULT 0,

    -- 강사
    instructor_name TEXT,
    instructor_bio TEXT,

    -- 장소 (오프라인)
    venue TEXT,
    address TEXT,

    -- 온라인 링크
    online_url TEXT,

    -- 인증
    provides_certificate BOOLEAN DEFAULT FALSE,
    certificate_type TEXT,

    -- 상태
    status TEXT NOT NULL DEFAULT 'upcoming',  -- upcoming, ongoing, completed, cancelled

    -- 첨부자료
    materials TEXT,  -- JSON array

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_education_category ON education_programs(category);
CREATE INDEX idx_education_status ON education_programs(status);
CREATE INDEX idx_education_start ON education_programs(start_date);


-- ============================================================================
-- 6. 교육 신청 및 수료
-- ============================================================================
CREATE TABLE IF NOT EXISTS education_enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id TEXT NOT NULL UNIQUE,

    -- 관계
    program_id TEXT NOT NULL,
    member_id TEXT NOT NULL,

    -- 신청 정보
    enrollment_status TEXT NOT NULL DEFAULT 'pending',  -- pending, confirmed, cancelled, completed
    payment_status TEXT NOT NULL DEFAULT 'pending',  -- pending, paid, refunded
    payment_amount INTEGER,

    -- 수료
    attendance_rate REAL DEFAULT 0.0,
    completion_status TEXT DEFAULT 'not_started',  -- not_started, in_progress, completed, failed
    final_score REAL,
    certificate_issued BOOLEAN DEFAULT FALSE,
    certificate_url TEXT,

    -- 피드백
    feedback TEXT,
    rating INTEGER,  -- 1-5

    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    FOREIGN KEY (program_id) REFERENCES education_programs(program_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES association_members(member_id) ON DELETE CASCADE
);

CREATE INDEX idx_enrollments_program ON education_enrollments(program_id);
CREATE INDEX idx_enrollments_member ON education_enrollments(member_id);
CREATE INDEX idx_enrollments_status ON education_enrollments(enrollment_status);


-- ============================================================================
-- 7. 이벤트 및 행사
-- ============================================================================
CREATE TABLE IF NOT EXISTS association_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,

    -- 이벤트 정보
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    event_type TEXT NOT NULL,  -- conference, workshop, seminar, networking, awards

    -- 일정
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    registration_start TIMESTAMP,
    registration_end TIMESTAMP,

    -- 장소
    format TEXT NOT NULL,  -- online, offline, hybrid
    venue TEXT,
    address TEXT,
    online_url TEXT,

    -- 정원 및 비용
    capacity INTEGER,
    registered_count INTEGER DEFAULT 0,
    registration_fee INTEGER DEFAULT 0,
    member_discount_rate REAL DEFAULT 0.0,

    -- 이미지 및 자료
    poster_image_url TEXT,
    program_file_url TEXT,

    -- 주최/주관
    organizer TEXT,
    sponsors TEXT,  -- JSON array

    -- 상태
    status TEXT NOT NULL DEFAULT 'upcoming',  -- upcoming, ongoing, completed, cancelled

    -- 태그
    tags TEXT,  -- JSON array

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_type ON association_events(event_type);
CREATE INDEX idx_events_status ON association_events(status);
CREATE INDEX idx_events_start ON association_events(start_datetime);


-- ============================================================================
-- 8. 이벤트 참가 신청
-- ============================================================================
CREATE TABLE IF NOT EXISTS event_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id TEXT NOT NULL UNIQUE,

    -- 관계
    event_id TEXT NOT NULL,
    member_id TEXT NOT NULL,

    -- 참가 정보
    registration_status TEXT NOT NULL DEFAULT 'pending',  -- pending, confirmed, cancelled, attended
    payment_status TEXT NOT NULL DEFAULT 'pending',
    payment_amount INTEGER,

    -- 추가 정보
    dietary_requirements TEXT,
    special_needs TEXT,
    questions TEXT,

    -- 출석
    attended BOOLEAN DEFAULT FALSE,
    check_in_time TIMESTAMP,

    -- 피드백
    feedback TEXT,
    rating INTEGER,

    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (event_id) REFERENCES association_events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES association_members(member_id) ON DELETE CASCADE,

    UNIQUE(event_id, member_id)
);

CREATE INDEX idx_event_reg_event ON event_registrations(event_id);
CREATE INDEX idx_event_reg_member ON event_registrations(member_id);
CREATE INDEX idx_event_reg_status ON event_registrations(registration_status);


-- ============================================================================
-- 9. FAQ (자주 묻는 질문)
-- ============================================================================
CREATE TABLE IF NOT EXISTS association_faqs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faq_id TEXT NOT NULL UNIQUE,

    -- FAQ 정보
    question TEXT NOT NULL,
    answer TEXT NOT NULL,

    -- 분류
    category TEXT NOT NULL,  -- membership, certification, education, payment, technical
    subcategory TEXT,

    -- 표시 순서
    display_order INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,

    -- 통계
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,

    -- 관련 문서
    related_documents TEXT,  -- JSON array

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_faqs_category ON association_faqs(category);
CREATE INDEX idx_faqs_featured ON association_faqs(is_featured);
CREATE INDEX idx_faqs_order ON association_faqs(display_order);


-- ============================================================================
-- 10. 문의 및 지원 티켓
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL UNIQUE,

    -- 문의 정보
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    category TEXT NOT NULL,  -- general, technical, membership, certification, payment

    -- 문의자
    member_id TEXT,
    contact_name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    contact_phone TEXT,

    -- 상태
    status TEXT NOT NULL DEFAULT 'open',  -- open, in_progress, resolved, closed
    priority TEXT NOT NULL DEFAULT 'normal',  -- low, normal, high, urgent

    -- 담당자
    assigned_to TEXT,
    assigned_at TIMESTAMP,

    -- 응답
    response TEXT,
    resolved_at TIMESTAMP,

    -- 첨부파일
    attachments TEXT,  -- JSON array

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (member_id) REFERENCES association_members(member_id)
);

CREATE INDEX idx_tickets_status ON support_tickets(status);
CREATE INDEX idx_tickets_priority ON support_tickets(priority);
CREATE INDEX idx_tickets_member ON support_tickets(member_id);
CREATE INDEX idx_tickets_assigned ON support_tickets(assigned_to);


-- ============================================================================
-- 11. 댓글 시스템 (공지사항, 뉴스 등)
-- ============================================================================
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id TEXT NOT NULL UNIQUE,

    -- 댓글 대상
    target_type TEXT NOT NULL,  -- notice, news, event, policy
    target_id TEXT NOT NULL,

    -- 댓글 내용
    content TEXT NOT NULL,
    parent_comment_id TEXT,  -- For threaded comments

    -- 작성자
    member_id TEXT NOT NULL,
    member_name TEXT NOT NULL,

    -- 상태
    status TEXT NOT NULL DEFAULT 'active',  -- active, deleted, hidden

    -- 통계
    like_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (member_id) REFERENCES association_members(member_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id) ON DELETE CASCADE
);

CREATE INDEX idx_comments_target ON comments(target_type, target_id);
CREATE INDEX idx_comments_member ON comments(member_id);
CREATE INDEX idx_comments_parent ON comments(parent_comment_id);


-- ============================================================================
-- 12. 배너 및 슬라이드
-- ============================================================================
CREATE TABLE IF NOT EXISTS website_banners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    banner_id TEXT NOT NULL UNIQUE,

    -- 배너 정보
    title TEXT NOT NULL,
    description TEXT,
    image_url TEXT NOT NULL,
    link_url TEXT,

    -- 배치
    position TEXT NOT NULL,  -- main_hero, sidebar, top, bottom
    display_order INTEGER DEFAULT 0,

    -- 표시 기간
    start_date TIMESTAMP,
    end_date TIMESTAMP,

    -- 상태
    is_active BOOLEAN DEFAULT TRUE,

    -- 통계
    click_count INTEGER DEFAULT 0,
    impression_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_banners_position ON website_banners(position);
CREATE INDEX idx_banners_active ON website_banners(is_active);
CREATE INDEX idx_banners_order ON website_banners(display_order);


-- ============================================================================
-- 13. 사이트 통계
-- ============================================================================
CREATE TABLE IF NOT EXISTS website_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL UNIQUE,

    -- 방문 통계
    total_visits INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    page_views INTEGER DEFAULT 0,

    -- 회원 활동
    new_members INTEGER DEFAULT 0,
    active_members INTEGER DEFAULT 0,
    member_logins INTEGER DEFAULT 0,

    -- 콘텐츠 활동
    notices_published INTEGER DEFAULT 0,
    news_published INTEGER DEFAULT 0,
    comments_posted INTEGER DEFAULT 0,

    -- 교육 및 이벤트
    education_enrollments INTEGER DEFAULT 0,
    event_registrations INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_date ON website_analytics(date);


-- ============================================================================
-- 14. 뷰(View): 회원 대시보드
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_member_dashboard AS
SELECT
    m.member_id,
    m.name,
    m.email,
    m.membership_tier,
    m.membership_status,
    m.join_date,

    -- 교육 통계
    COUNT(DISTINCT ee.id) as total_educations,
    SUM(CASE WHEN ee.completion_status = 'completed' THEN 1 ELSE 0 END) as completed_educations,

    -- 이벤트 통계
    COUNT(DISTINCT er.id) as total_events,
    SUM(CASE WHEN er.attended = 1 THEN 1 ELSE 0 END) as attended_events,

    -- 활동 통계
    COUNT(DISTINCT c.id) as total_comments,

    m.last_login_at

FROM association_members m
LEFT JOIN education_enrollments ee ON m.member_id = ee.member_id
LEFT JOIN event_registrations er ON m.member_id = er.member_id
LEFT JOIN comments c ON m.member_id = c.member_id

GROUP BY m.member_id;


-- ============================================================================
-- 15. 트리거: 회원 가입 시 환영 메시지
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS trg_member_welcome
AFTER INSERT ON association_members
WHEN NEW.membership_status = 'active'
BEGIN
    -- 실제로는 이메일 발송 큐에 추가
    INSERT INTO support_tickets (
        ticket_id,
        subject,
        message,
        category,
        member_id,
        contact_name,
        contact_email,
        status
    ) VALUES (
        'WELCOME-' || NEW.member_id,
        'PAM-TALK ESG 협회 가입을 환영합니다',
        '회원 가입이 완료되었습니다. 다양한 ESG 프로그램을 이용해보세요.',
        'general',
        NEW.member_id,
        NEW.name,
        NEW.email,
        'resolved'
    );
END;


-- ============================================================================
-- 마이그레이션 완료
-- ============================================================================
