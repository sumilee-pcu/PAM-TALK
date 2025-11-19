# -*- coding: utf-8 -*-
"""
소셜 피드 서비스
실시간 탄소 활동 공유 및 커뮤니티 피드 관리
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.utils.db_pool import db_service
from app.service.carbon_tracking_service import carbon_tracking_service


@dataclass
class FeedPost:
    """피드 포스트 데이터 클래스"""
    id: int
    user_id: str
    post_type: str
    title: str
    content: str
    images: List[str]
    carbon_activity_id: Optional[int]
    hashtags: List[str]
    categories: List[str]
    likes_count: int
    comments_count: int
    shares_count: int
    engagement_score: float
    created_at: str


class SocialFeedService:
    """소셜 피드 관리 서비스"""

    def __init__(self):
        self.db = db_service
        self.carbon_service = carbon_tracking_service

    def create_social_profile(self, user_id: str, profile_data: Dict) -> int:
        """소셜 프로필 생성"""
        query = """
            INSERT INTO social_profiles
            (user_id, display_name, bio, farmer_type, specialties,
             farm_location, farm_size_ha, is_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        params = (
            user_id,
            profile_data['display_name'],
            profile_data.get('bio', ''),
            profile_data.get('farmer_type', ''),
            profile_data.get('specialties', []),
            profile_data.get('farm_location', ''),
            profile_data.get('farm_size_ha'),
            profile_data.get('is_verified', False)
        )

        result = self.db.pool.execute_query(query, params, fetch='one')
        return result['id']

    def get_social_profile(self, user_id: str) -> Optional[Dict]:
        """소셜 프로필 조회"""
        query = "SELECT * FROM social_profiles WHERE user_id = %s"
        result = self.db.pool.execute_query(query, (user_id,), fetch='one')
        return dict(result) if result else None

    def create_post(self, user_id: str, post_data: Dict) -> int:
        """포스트 생성"""

        # 해시태그 추출
        hashtags = self._extract_hashtags(post_data.get('content', ''))

        # 카테고리 자동 분류
        categories = self._classify_post_categories(post_data)

        query = """
            INSERT INTO social_posts
            (user_id, post_type, title, content, images, carbon_activity_id,
             location, hashtags, categories, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        params = (
            user_id,
            post_data.get('post_type', 'text'),
            post_data.get('title', ''),
            post_data['content'],
            json.dumps(post_data.get('images', [])),
            post_data.get('carbon_activity_id'),
            post_data.get('location', ''),
            hashtags,
            categories,
            post_data.get('status', 'published')
        )

        result = self.db.pool.execute_query(query, params, fetch='one')
        post_id = result['id']

        # 포스트 생성 시 관련 처리
        self._post_creation_tasks(user_id, post_id, post_data)

        return post_id

    def create_carbon_activity_post(self, user_id: str, activity_id: int,
                                   additional_content: str = '') -> int:
        """탄소 활동 기반 자동 포스트 생성"""

        # 탄소 활동 정보 조회
        activity = carbon_tracking_service.get_user_activities(
            user_id=user_id, limit=1
        )

        if not activity:
            raise Exception("탄소 활동을 찾을 수 없습니다.")

        activity_data = activity[0]
        carbon_savings = float(activity_data['carbon_savings'])
        reduction_percentage = float(activity_data['reduction_percentage'])
        token_reward = int(activity_data['token_reward_amount'])

        # 자동 포스트 내용 생성
        post_content = self._generate_carbon_activity_content(
            activity_data, additional_content
        )

        post_data = {
            'post_type': 'carbon_activity',
            'content': post_content,
            'carbon_activity_id': activity_id,
            'categories': ['탄소절약', '친환경', activity_data['activity_type']]
        }

        return self.create_post(user_id, post_data)

    def get_user_feed(self, user_id: str, page: int = 1, limit: int = 20,
                      feed_type: str = 'timeline') -> Dict:
        """사용자 개인화 피드 조회"""

        offset = (page - 1) * limit

        if feed_type == 'timeline':
            # 팔로우한 사용자들의 포스트 + 본인 포스트
            query = """
                SELECT p.*, sp.display_name, sp.avatar_url, sp.is_verified
                FROM social_posts p
                JOIN social_profiles sp ON p.user_id = sp.user_id
                WHERE (p.user_id = %s
                       OR p.user_id IN (
                           SELECT following_id FROM social_follows WHERE follower_id = %s
                       ))
                AND p.status = 'published'
                ORDER BY p.published_at DESC
                LIMIT %s OFFSET %s
            """
            params = (user_id, user_id, limit, offset)

        elif feed_type == 'discover':
            # 트렌딩 포스트 (높은 참여도)
            query = """
                SELECT p.*, sp.display_name, sp.avatar_url, sp.is_verified
                FROM social_posts p
                JOIN social_profiles sp ON p.user_id = sp.user_id
                WHERE p.status = 'published'
                AND p.engagement_score > 5.0
                AND p.published_at >= NOW() - INTERVAL '7 days'
                ORDER BY p.engagement_score DESC, p.published_at DESC
                LIMIT %s OFFSET %s
            """
            params = (limit, offset)

        elif feed_type == 'carbon':
            # 탄소 활동 관련 포스트만
            query = """
                SELECT p.*, sp.display_name, sp.avatar_url, sp.is_verified,
                       ca.carbon_savings, ca.token_reward_amount
                FROM social_posts p
                JOIN social_profiles sp ON p.user_id = sp.user_id
                LEFT JOIN carbon_activities ca ON p.carbon_activity_id = ca.id
                WHERE p.post_type = 'carbon_activity'
                AND p.status = 'published'
                ORDER BY p.published_at DESC
                LIMIT %s OFFSET %s
            """
            params = (limit, offset)

        else:
            # 전체 공개 피드
            query = """
                SELECT p.*, sp.display_name, sp.avatar_url, sp.is_verified
                FROM social_posts p
                JOIN social_profiles sp ON p.user_id = sp.user_id
                WHERE p.status = 'published'
                ORDER BY p.published_at DESC
                LIMIT %s OFFSET %s
            """
            params = (limit, offset)

        posts = self.db.pool.execute_query(query, params)

        # 포스트 데이터 가공
        processed_posts = []
        for post in posts:
            processed_post = self._process_post_data(dict(post))
            processed_posts.append(processed_post)

        return {
            'posts': processed_posts,
            'page': page,
            'limit': limit,
            'feed_type': feed_type,
            'has_more': len(processed_posts) == limit
        }

    def get_regional_feed(self, region: str, page: int = 1, limit: int = 20) -> Dict:
        """지역별 피드 조회"""
        offset = (page - 1) * limit

        query = """
            SELECT p.*, sp.display_name, sp.avatar_url, sp.is_verified, sp.farm_location
            FROM social_posts p
            JOIN social_profiles sp ON p.user_id = sp.user_id
            WHERE (p.location = %s OR sp.farm_location = %s)
            AND p.status = 'published'
            ORDER BY p.published_at DESC
            LIMIT %s OFFSET %s
        """

        posts = self.db.pool.execute_query(query, (region, region, limit, offset))

        return {
            'posts': [self._process_post_data(dict(post)) for post in posts],
            'region': region,
            'page': page,
            'limit': limit,
            'has_more': len(posts) == limit
        }

    def get_hashtag_feed(self, hashtag: str, page: int = 1, limit: int = 20) -> Dict:
        """해시태그별 피드 조회"""
        offset = (page - 1) * limit

        # 해시태그 앞에 # 추가 (없는 경우)
        if not hashtag.startswith('#'):
            hashtag = f'#{hashtag}'

        query = """
            SELECT p.*, sp.display_name, sp.avatar_url, sp.is_verified
            FROM social_posts p
            JOIN social_profiles sp ON p.user_id = sp.user_id
            WHERE %s = ANY(p.hashtags)
            AND p.status = 'published'
            ORDER BY p.engagement_score DESC, p.published_at DESC
            LIMIT %s OFFSET %s
        """

        posts = self.db.pool.execute_query(query, (hashtag, limit, offset))

        return {
            'posts': [self._process_post_data(dict(post)) for post in posts],
            'hashtag': hashtag,
            'page': page,
            'limit': limit,
            'has_more': len(posts) == limit
        }

    def get_post_detail(self, post_id: int, viewer_user_id: str = None) -> Optional[Dict]:
        """포스트 상세 정보 조회"""

        # 조회수 증가
        if viewer_user_id:
            self._increment_post_views(post_id, viewer_user_id)

        query = """
            SELECT p.*, sp.display_name, sp.avatar_url, sp.is_verified,
                   sp.farmer_type, sp.farm_location
            FROM social_posts p
            JOIN social_profiles sp ON p.user_id = sp.user_id
            WHERE p.id = %s AND p.status = 'published'
        """

        result = self.db.pool.execute_query(query, (post_id,), fetch='one')

        if not result:
            return None

        post = self._process_post_data(dict(result))

        # 탄소 활동 정보 추가 (있는 경우)
        if post['carbon_activity_id']:
            carbon_info = self._get_carbon_activity_info(post['carbon_activity_id'])
            post['carbon_info'] = carbon_info

        return post

    def search_posts(self, query_text: str, filters: Dict = None,
                    page: int = 1, limit: int = 20) -> Dict:
        """포스트 검색"""
        offset = (page - 1) * limit

        # 기본 검색 쿼리
        search_conditions = ["p.status = 'published'"]
        params = []

        # 텍스트 검색
        if query_text.strip():
            search_conditions.append("""
                (p.content ILIKE %s OR p.title ILIKE %s
                 OR sp.display_name ILIKE %s)
            """)
            search_term = f'%{query_text}%'
            params.extend([search_term, search_term, search_term])

        # 필터 적용
        if filters:
            if filters.get('post_type'):
                search_conditions.append("p.post_type = %s")
                params.append(filters['post_type'])

            if filters.get('region'):
                search_conditions.append("""
                    (p.location = %s OR sp.farm_location = %s)
                """)
                params.extend([filters['region'], filters['region']])

            if filters.get('category'):
                search_conditions.append("%s = ANY(p.categories)")
                params.append(filters['category'])

            if filters.get('date_from'):
                search_conditions.append("p.published_at >= %s")
                params.append(filters['date_from'])

            if filters.get('date_to'):
                search_conditions.append("p.published_at <= %s")
                params.append(filters['date_to'])

        where_clause = " AND ".join(search_conditions)

        query = f"""
            SELECT p.*, sp.display_name, sp.avatar_url, sp.is_verified
            FROM social_posts p
            JOIN social_profiles sp ON p.user_id = sp.user_id
            WHERE {where_clause}
            ORDER BY p.engagement_score DESC, p.published_at DESC
            LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])
        posts = self.db.pool.execute_query(query, tuple(params))

        return {
            'posts': [self._process_post_data(dict(post)) for post in posts],
            'query': query_text,
            'filters': filters,
            'page': page,
            'limit': limit,
            'has_more': len(posts) == limit
        }

    def follow_user(self, follower_id: str, following_id: str) -> bool:
        """사용자 팔로우"""
        if follower_id == following_id:
            return False

        try:
            query = """
                INSERT INTO social_follows (follower_id, following_id)
                VALUES (%s, %s)
                ON CONFLICT (follower_id, following_id) DO NOTHING
            """

            self.db.pool.execute_query(query, (follower_id, following_id), fetch=None)

            # 팔로우 알림 생성
            self._create_notification(
                user_id=following_id,
                notification_type='follow',
                triggered_by_user_id=follower_id,
                title='새로운 팔로워',
                message=f'{follower_id}님이 회원님을 팔로우했습니다.'
            )

            return True

        except Exception:
            return False

    def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """사용자 언팔로우"""
        try:
            query = """
                DELETE FROM social_follows
                WHERE follower_id = %s AND following_id = %s
            """

            self.db.pool.execute_query(query, (follower_id, following_id), fetch=None)
            return True

        except Exception:
            return False

    def get_user_followers(self, user_id: str, page: int = 1, limit: int = 20) -> Dict:
        """사용자 팔로워 목록"""
        offset = (page - 1) * limit

        query = """
            SELECT sp.user_id, sp.display_name, sp.avatar_url, sp.is_verified,
                   sf.followed_at
            FROM social_follows sf
            JOIN social_profiles sp ON sf.follower_id = sp.user_id
            WHERE sf.following_id = %s
            ORDER BY sf.followed_at DESC
            LIMIT %s OFFSET %s
        """

        followers = self.db.pool.execute_query(query, (user_id, limit, offset))

        return {
            'followers': [dict(follower) for follower in followers],
            'page': page,
            'limit': limit,
            'has_more': len(followers) == limit
        }

    def get_user_following(self, user_id: str, page: int = 1, limit: int = 20) -> Dict:
        """사용자 팔로잉 목록"""
        offset = (page - 1) * limit

        query = """
            SELECT sp.user_id, sp.display_name, sp.avatar_url, sp.is_verified,
                   sf.followed_at
            FROM social_follows sf
            JOIN social_profiles sp ON sf.following_id = sp.user_id
            WHERE sf.follower_id = %s
            ORDER BY sf.followed_at DESC
            LIMIT %s OFFSET %s
        """

        following = self.db.pool.execute_query(query, (user_id, limit, offset))

        return {
            'following': [dict(user) for user in following],
            'page': page,
            'limit': limit,
            'has_more': len(following) == limit
        }

    # Private 메서드들

    def _extract_hashtags(self, content: str) -> List[str]:
        """텍스트에서 해시태그 추출"""
        hashtag_pattern = r'#[가-힣\w]+'
        hashtags = re.findall(hashtag_pattern, content)
        return list(set(hashtags))  # 중복 제거

    def _classify_post_categories(self, post_data: Dict) -> List[str]:
        """포스트 카테고리 자동 분류"""
        categories = []
        content = post_data.get('content', '').lower()

        # 농업 관련 키워드
        if any(keyword in content for keyword in ['유기농', '친환경', '무농약']):
            categories.append('친환경농업')

        if any(keyword in content for keyword in ['지역', '로컬', '직거래']):
            categories.append('지역농업')

        if any(keyword in content for keyword in ['탄소', '온실가스', '배출']):
            categories.append('탄소절약')

        # 포스트 타입에 따른 기본 카테고리
        if post_data.get('post_type') == 'carbon_activity':
            categories.append('탄소활동')

        return list(set(categories))

    def _generate_carbon_activity_content(self, activity_data: Dict,
                                        additional_content: str) -> str:
        """탄소 활동 기반 포스트 내용 자동 생성"""

        product_name = activity_data.get('product_name', '농산물')
        carbon_savings = float(activity_data['carbon_savings'])
        reduction_percentage = float(activity_data['reduction_percentage'])
        token_reward = int(activity_data['token_reward_amount'])
        farming_method = activity_data.get('farming_method', '').replace('organic', '유기농')

        base_content = f"""
🌱 오늘의 친환경 농업 활동을 공유합니다!

📦 구매한 농산물: {product_name} ({farming_method})
🌍 탄소 절약량: {carbon_savings:.1f}kg CO2
📈 절약 비율: {reduction_percentage:.1f}%
🪙 보상 토큰: {token_reward}개

지구를 위한 작은 실천이 모여 큰 변화를 만들어갑니다!
함께 친환경 농업을 응원해주세요.

#친환경 #로컬푸드 #탄소절약 #지속가능농업
        """

        if additional_content.strip():
            base_content += f"\n\n{additional_content.strip()}"

        return base_content.strip()

    def _process_post_data(self, post: Dict) -> Dict:
        """포스트 데이터 가공"""
        # JSON 필드 파싱
        if isinstance(post.get('images'), str):
            post['images'] = json.loads(post['images'])

        if isinstance(post.get('hashtags'), str):
            post['hashtags'] = json.loads(post['hashtags']) if post['hashtags'] else []

        if isinstance(post.get('categories'), str):
            post['categories'] = json.loads(post['categories']) if post['categories'] else []

        # 시간 포맷팅
        if post.get('published_at'):
            post['published_at_formatted'] = self._format_relative_time(post['published_at'])

        return post

    def _format_relative_time(self, timestamp) -> str:
        """상대적 시간 포맷 (예: 2시간 전, 3일 전)"""
        now = datetime.now()
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

        diff = now - timestamp

        if diff.days > 0:
            return f"{diff.days}일 전"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}시간 전"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}분 전"
        else:
            return "방금 전"

    def _post_creation_tasks(self, user_id: str, post_id: int, post_data: Dict):
        """포스트 생성 후 처리 작업"""

        # 해시태그 트렌딩 업데이트
        hashtags = post_data.get('hashtags', [])
        for hashtag in hashtags:
            self._update_hashtag_trending(hashtag)

        # 사용자 포스트 카운트 증가
        self._increment_user_posts_count(user_id)

    def _increment_post_views(self, post_id: int, viewer_user_id: str):
        """포스트 조회수 증가 (중복 방지)"""
        # 간단한 중복 방지: 24시간 내 같은 사용자 조회 제한
        query = """
            UPDATE social_posts
            SET views_count = views_count + 1
            WHERE id = %s
        """
        self.db.pool.execute_query(query, (post_id,), fetch=None)

    def _get_carbon_activity_info(self, activity_id: int) -> Optional[Dict]:
        """탄소 활동 정보 조회"""
        query = "SELECT * FROM carbon_activities WHERE id = %s"
        result = self.db.pool.execute_query(query, (activity_id,), fetch='one')
        return dict(result) if result else None

    def _update_hashtag_trending(self, hashtag: str):
        """해시태그 트렌딩 점수 업데이트"""
        query = """
            INSERT INTO trending_topics (topic_name, hashtag, daily_mentions, trend_score)
            VALUES (%s, %s, 1, 1.0)
            ON CONFLICT (hashtag) DO UPDATE SET
                daily_mentions = trending_topics.daily_mentions + 1,
                trend_score = trending_topics.trend_score + 0.1,
                last_mention_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
        """

        topic_name = hashtag.replace('#', '')
        self.db.pool.execute_query(query, (topic_name, hashtag), fetch=None)

    def _increment_user_posts_count(self, user_id: str):
        """사용자 포스트 카운트 증가"""
        query = """
            UPDATE social_profiles
            SET posts_count = posts_count + 1
            WHERE user_id = %s
        """
        self.db.pool.execute_query(query, (user_id,), fetch=None)

    def _create_notification(self, user_id: str, notification_type: str,
                           triggered_by_user_id: str, title: str, message: str,
                           **kwargs):
        """알림 생성"""
        query = """
            INSERT INTO social_notifications
            (user_id, notification_type, triggered_by_user_id, title, message,
             post_id, comment_id, group_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            user_id, notification_type, triggered_by_user_id, title, message,
            kwargs.get('post_id'), kwargs.get('comment_id'), kwargs.get('group_id')
        )

        self.db.pool.execute_query(query, params, fetch=None)


# 서비스 인스턴스
social_feed_service = SocialFeedService()


# 사용 예시
if __name__ == "__main__":
    service = social_feed_service

    # 테스트 소셜 프로필 생성
    try:
        profile_id = service.create_social_profile(
            user_id="farmer123",
            profile_data={
                'display_name': '친환경 농부 김씨',
                'bio': '30년간 유기농업을 해온 농부입니다.',
                'farmer_type': 'organic',
                'specialties': ['채소', '과일'],
                'farm_location': '경기도 양평',
                'farm_size_ha': 5.2
            }
        )
        print(f"프로필 생성: {profile_id}")

        # 테스트 포스트 생성
        post_id = service.create_post(
            user_id="farmer123",
            post_data={
                'post_type': 'text',
                'content': '오늘 #유기농 토마토를 수확했습니다! #친환경농업 #로컬푸드',
                'location': '경기도 양평'
            }
        )
        print(f"포스트 생성: {post_id}")

    except Exception as e:
        print(f"테스트 실행 중 오류: {e}")