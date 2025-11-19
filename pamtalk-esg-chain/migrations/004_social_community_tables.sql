-- PAM-TALK ESG Chain Database Schema Migration
-- Version: 004
-- Description: SNS/커뮤니티 기능을 위한 소셜 테이블 생성

-- 사용자 소셜 프로필 테이블
CREATE TABLE IF NOT EXISTS social_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL UNIQUE,

    -- 프로필 정보
    display_name VARCHAR(100) NOT NULL,
    bio TEXT,
    avatar_url VARCHAR(500),
    cover_image_url VARCHAR(500),

    -- 농업/환경 관련 정보
    farmer_type VARCHAR(50), -- organic, conventional, mixed
    specialties TEXT[], -- 전문 분야 배열
    farm_location VARCHAR(100),
    farm_size_ha DECIMAL(8,2), -- 농장 크기 (ha)

    -- 소셜 통계
    followers_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,
    carbon_points INTEGER DEFAULT 0, -- 탄소 포인트

    -- 레벨/뱃지 시스템
    level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 0,
    badges JSONB DEFAULT '[]', -- 획득한 뱃지들

    -- 설정
    is_verified BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    allow_messages BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 팔로우 관계 테이블
CREATE TABLE IF NOT EXISTS social_follows (
    id SERIAL PRIMARY KEY,
    follower_id VARCHAR(100) NOT NULL, -- 팔로우하는 사람
    following_id VARCHAR(100) NOT NULL, -- 팔로우당하는 사람

    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(follower_id, following_id),
    CHECK(follower_id != following_id) -- 자기 자신을 팔로우 불가
);

-- 소셜 피드 포스트 테이블
CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,

    -- 포스트 내용
    post_type VARCHAR(30) NOT NULL DEFAULT 'text', -- text, image, carbon_activity, poll, article
    title VARCHAR(200),
    content TEXT NOT NULL,

    -- 미디어 정보
    images JSONB, -- 이미지 URL 배열
    video_url VARCHAR(500),

    -- 탄소 활동 연동 (null이면 일반 포스트)
    carbon_activity_id INTEGER REFERENCES carbon_activities(id),

    -- 위치 정보
    location VARCHAR(100),
    coordinates POINT, -- PostGIS 좌표

    -- 태그 및 카테고리
    hashtags TEXT[], -- 해시태그 배열
    categories TEXT[], -- 카테고리 배열

    -- 소셜 통계
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,

    -- 보상 관련
    token_rewards_given INTEGER DEFAULT 0,
    engagement_score DECIMAL(5,2) DEFAULT 0, -- 참여도 점수

    -- 상태 관리
    status VARCHAR(20) DEFAULT 'published', -- draft, published, archived, deleted
    is_pinned BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,

    -- 모더레이션
    is_reported BOOLEAN DEFAULT FALSE,
    report_count INTEGER DEFAULT 0,
    moderation_status VARCHAR(20) DEFAULT 'approved', -- pending, approved, rejected

    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 포스트 좋아요 테이블
CREATE TABLE IF NOT EXISTS social_post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES social_posts(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,

    -- 좋아요 타입 (확장 가능)
    like_type VARCHAR(20) DEFAULT 'like', -- like, love, helpful, inspiring

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(post_id, user_id)
);

-- 포스트 댓글 테이블
CREATE TABLE IF NOT EXISTS social_post_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES social_posts(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    parent_comment_id INTEGER REFERENCES social_post_comments(id), -- 대댓글 지원

    -- 댓글 내용
    content TEXT NOT NULL,

    -- 통계
    likes_count INTEGER DEFAULT 0,
    replies_count INTEGER DEFAULT 0,

    -- 상태
    status VARCHAR(20) DEFAULT 'published',
    is_reported BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 댓글 좋아요 테이블
CREATE TABLE IF NOT EXISTS social_comment_likes (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER NOT NULL REFERENCES social_post_comments(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(comment_id, user_id)
);

-- 커뮤니티 그룹 테이블
CREATE TABLE IF NOT EXISTS community_groups (
    id SERIAL PRIMARY KEY,

    -- 그룹 기본 정보
    name VARCHAR(100) NOT NULL,
    description TEXT,
    avatar_url VARCHAR(500),
    cover_image_url VARCHAR(500),

    -- 그룹 타입 및 카테고리
    group_type VARCHAR(30) NOT NULL, -- regional, topic, farming_method, crop_type
    category VARCHAR(50), -- vegetables, fruits, livestock, organic, etc.
    region VARCHAR(100), -- 지역 그룹인 경우

    -- 그룹 설정
    is_private BOOLEAN DEFAULT FALSE,
    require_approval BOOLEAN DEFAULT FALSE,
    allow_member_posts BOOLEAN DEFAULT TRUE,

    -- 통계
    members_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,

    -- 관리
    created_by VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 그룹 멤버십 테이블
CREATE TABLE IF NOT EXISTS community_group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES community_groups(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,

    -- 역할
    role VARCHAR(20) DEFAULT 'member', -- admin, moderator, member

    -- 상태
    status VARCHAR(20) DEFAULT 'active', -- pending, active, banned

    -- 참여 통계
    posts_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    last_activity_at TIMESTAMP,

    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(group_id, user_id)
);

-- 그룹 포스트 테이블 (social_posts와 연결)
CREATE TABLE IF NOT EXISTS community_group_posts (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES community_groups(id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES social_posts(id) ON DELETE CASCADE,

    -- 그룹 내 포스트 상태
    is_pinned BOOLEAN DEFAULT FALSE,
    is_announcement BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(group_id, post_id)
);

-- 트렌딩 토픽 테이블
CREATE TABLE IF NOT EXISTS trending_topics (
    id SERIAL PRIMARY KEY,

    -- 토픽 정보
    topic_name VARCHAR(100) NOT NULL,
    hashtag VARCHAR(100) UNIQUE NOT NULL, -- #로컬푸드 #유기농 등
    category VARCHAR(50),

    -- 지역별 트렌딩 (null이면 전국)
    region VARCHAR(100),

    -- 트렌딩 통계
    posts_count INTEGER DEFAULT 0,
    mentions_count INTEGER DEFAULT 0,
    engagement_score DECIMAL(10,2) DEFAULT 0,
    trend_score DECIMAL(10,2) DEFAULT 0, -- 트렌딩 점수

    -- 시간대별 통계
    daily_mentions INTEGER DEFAULT 0,
    weekly_mentions INTEGER DEFAULT 0,
    monthly_mentions INTEGER DEFAULT 0,

    -- 상태
    is_active BOOLEAN DEFAULT TRUE,
    is_promoted BOOLEAN DEFAULT FALSE, -- 프로모션 토픽 여부

    -- 시간 정보
    trend_started_at TIMESTAMP,
    peak_time TIMESTAMP,
    last_mention_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 알림 테이블
CREATE TABLE IF NOT EXISTS social_notifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL, -- 알림 받는 사람

    -- 알림 타입
    notification_type VARCHAR(30) NOT NULL, -- like, comment, follow, mention, carbon_reward

    -- 알림 발생시킨 사용자
    triggered_by_user_id VARCHAR(100),

    -- 관련 객체 참조
    post_id INTEGER REFERENCES social_posts(id),
    comment_id INTEGER REFERENCES social_post_comments(id),
    group_id INTEGER REFERENCES community_groups(id),
    carbon_activity_id INTEGER REFERENCES carbon_activities(id),

    -- 알림 내용
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    action_url VARCHAR(500), -- 클릭 시 이동할 URL

    -- 상태
    is_read BOOLEAN DEFAULT FALSE,
    is_pushed BOOLEAN DEFAULT FALSE, -- 푸시 알림 발송 여부

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

-- 콘텐츠 보상 기록 테이블
CREATE TABLE IF NOT EXISTS social_content_rewards (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,

    -- 보상 대상
    content_type VARCHAR(30) NOT NULL, -- post, comment, engagement
    content_id INTEGER NOT NULL, -- post_id 또는 comment_id

    -- 보상 정보
    reward_type VARCHAR(30) NOT NULL, -- quality_content, viral_post, helpful_comment
    token_amount INTEGER NOT NULL,
    carbon_impact DECIMAL(10,3), -- 탄소 임팩트 (있는 경우)

    -- 보상 기준
    engagement_score DECIMAL(5,2),
    quality_score DECIMAL(5,2),
    reach_count INTEGER, -- 도달 수

    -- 상태
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, paid
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,

    -- 지급 정보
    tx_hash VARCHAR(64), -- 토큰 지급 트랜잭션
    paid_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_social_profiles_user_id ON social_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_social_follows_follower_id ON social_follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_social_follows_following_id ON social_follows(following_id);

CREATE INDEX IF NOT EXISTS idx_social_posts_user_id ON social_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_social_posts_post_type ON social_posts(post_type);
CREATE INDEX IF NOT EXISTS idx_social_posts_published_at ON social_posts(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_posts_status ON social_posts(status);
CREATE INDEX IF NOT EXISTS idx_social_posts_carbon_activity_id ON social_posts(carbon_activity_id);

CREATE INDEX IF NOT EXISTS idx_social_post_likes_post_id ON social_post_likes(post_id);
CREATE INDEX IF NOT EXISTS idx_social_post_likes_user_id ON social_post_likes(user_id);

CREATE INDEX IF NOT EXISTS idx_social_post_comments_post_id ON social_post_comments(post_id);
CREATE INDEX IF NOT EXISTS idx_social_post_comments_user_id ON social_post_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_social_post_comments_parent_id ON social_post_comments(parent_comment_id);

CREATE INDEX IF NOT EXISTS idx_community_groups_group_type ON community_groups(group_type);
CREATE INDEX IF NOT EXISTS idx_community_groups_region ON community_groups(region);
CREATE INDEX IF NOT EXISTS idx_community_groups_category ON community_groups(category);

CREATE INDEX IF NOT EXISTS idx_community_group_members_group_id ON community_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_community_group_members_user_id ON community_group_members(user_id);

CREATE INDEX IF NOT EXISTS idx_trending_topics_region ON trending_topics(region);
CREATE INDEX IF NOT EXISTS idx_trending_topics_trend_score ON trending_topics(trend_score DESC);
CREATE INDEX IF NOT EXISTS idx_trending_topics_hashtag ON trending_topics(hashtag);

CREATE INDEX IF NOT EXISTS idx_social_notifications_user_id ON social_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_social_notifications_is_read ON social_notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_social_notifications_created_at ON social_notifications(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_social_content_rewards_user_id ON social_content_rewards(user_id);
CREATE INDEX IF NOT EXISTS idx_social_content_rewards_status ON social_content_rewards(status);
CREATE INDEX IF NOT EXISTS idx_social_content_rewards_content_type ON social_content_rewards(content_type, content_id);

-- 트리거 함수: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_social_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- updated_at 트리거 적용
CREATE TRIGGER update_social_profiles_updated_at BEFORE UPDATE ON social_profiles
    FOR EACH ROW EXECUTE FUNCTION update_social_updated_at_column();

CREATE TRIGGER update_social_posts_updated_at BEFORE UPDATE ON social_posts
    FOR EACH ROW EXECUTE FUNCTION update_social_updated_at_column();

CREATE TRIGGER update_social_post_comments_updated_at BEFORE UPDATE ON social_post_comments
    FOR EACH ROW EXECUTE FUNCTION update_social_updated_at_column();

CREATE TRIGGER update_community_groups_updated_at BEFORE UPDATE ON community_groups
    FOR EACH ROW EXECUTE FUNCTION update_social_updated_at_column();

CREATE TRIGGER update_community_group_members_updated_at BEFORE UPDATE ON community_group_members
    FOR EACH ROW EXECUTE FUNCTION update_social_updated_at_column();

CREATE TRIGGER update_trending_topics_updated_at BEFORE UPDATE ON trending_topics
    FOR EACH ROW EXECUTE FUNCTION update_social_updated_at_column();

CREATE TRIGGER update_social_content_rewards_updated_at BEFORE UPDATE ON social_content_rewards
    FOR EACH ROW EXECUTE FUNCTION update_social_updated_at_column();

-- 통계 업데이트 트리거 함수들

-- 포스트 좋아요 수 업데이트 트리거
CREATE OR REPLACE FUNCTION update_post_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE social_posts SET likes_count = likes_count + 1 WHERE id = NEW.post_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE social_posts SET likes_count = likes_count - 1 WHERE id = OLD.post_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_post_likes_count
    AFTER INSERT OR DELETE ON social_post_likes
    FOR EACH ROW EXECUTE FUNCTION update_post_likes_count();

-- 포스트 댓글 수 업데이트 트리거
CREATE OR REPLACE FUNCTION update_post_comments_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE social_posts SET comments_count = comments_count + 1 WHERE id = NEW.post_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE social_posts SET comments_count = comments_count - 1 WHERE id = OLD.post_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_post_comments_count
    AFTER INSERT OR DELETE ON social_post_comments
    FOR EACH ROW EXECUTE FUNCTION update_post_comments_count();

-- 팔로우 카운트 업데이트 트리거
CREATE OR REPLACE FUNCTION update_follow_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE social_profiles SET followers_count = followers_count + 1 WHERE user_id = NEW.following_id;
        UPDATE social_profiles SET following_count = following_count + 1 WHERE user_id = NEW.follower_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE social_profiles SET followers_count = followers_count - 1 WHERE user_id = OLD.following_id;
        UPDATE social_profiles SET following_count = following_count - 1 WHERE user_id = OLD.follower_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_follow_counts
    AFTER INSERT OR DELETE ON social_follows
    FOR EACH ROW EXECUTE FUNCTION update_follow_counts();