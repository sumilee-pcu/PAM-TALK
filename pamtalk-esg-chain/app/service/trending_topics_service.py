# -*- coding: utf-8 -*-
"""
트렌딩 토픽 관리 서비스
실시간 해시태그 분석, 지역별 트렌딩, 토픽 추천 기능
"""
import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
import logging

from ..utils.db_pool import get_db_connection

logger = logging.getLogger(__name__)

class TrendingTopicsService:
    def __init__(self):
        self.hashtag_pattern = re.compile(r'#[\w가-힣]+')
        self.min_mentions_for_trend = 5
        self.trend_decay_hours = 24

    async def extract_hashtags_from_text(self, text: str) -> List[str]:
        """텍스트에서 해시태그 추출"""
        hashtags = self.hashtag_pattern.findall(text)
        return [tag.lower() for tag in hashtags if len(tag) > 2]

    async def process_new_post_hashtags(self, post_id: int, content: str, user_region: str = None) -> None:
        """새 포스트의 해시태그 처리"""
        try:
            hashtags = await self.extract_hashtags_from_text(content)
            if not hashtags:
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            for hashtag in hashtags:
                # 기존 토픽 업데이트 또는 신규 생성
                await self._update_or_create_trending_topic(
                    cursor, hashtag, user_region
                )

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"해시태그 처리 오류: {e}")

    async def _update_or_create_trending_topic(
        self, cursor, hashtag: str, region: str = None
    ) -> None:
        """트렌딩 토픽 업데이트 또는 생성"""

        # 기존 토픽 확인
        cursor.execute("""
            SELECT id, posts_count, mentions_count, daily_mentions, weekly_mentions, monthly_mentions
            FROM trending_topics
            WHERE hashtag = %s AND (region = %s OR (region IS NULL AND %s IS NULL))
        """, (hashtag, region, region))

        existing = cursor.fetchone()

        now = datetime.now()

        if existing:
            # 기존 토픽 업데이트
            topic_id = existing[0]
            cursor.execute("""
                UPDATE trending_topics SET
                    mentions_count = mentions_count + 1,
                    daily_mentions = daily_mentions + 1,
                    weekly_mentions = weekly_mentions + 1,
                    monthly_mentions = monthly_mentions + 1,
                    last_mention_at = %s,
                    updated_at = %s
                WHERE id = %s
            """, (now, now, topic_id))

        else:
            # 새 토픽 생성
            topic_name = hashtag[1:] if hashtag.startswith('#') else hashtag
            cursor.execute("""
                INSERT INTO trending_topics (
                    topic_name, hashtag, region, mentions_count,
                    daily_mentions, weekly_mentions, monthly_mentions,
                    trend_started_at, last_mention_at
                ) VALUES (%s, %s, %s, 1, 1, 1, 1, %s, %s)
            """, (topic_name, hashtag, region, now, now))

    async def get_trending_topics(
        self,
        region: str = None,
        limit: int = 20,
        time_range: str = 'daily'
    ) -> List[Dict[str, Any]]:
        """트렌딩 토픽 조회"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 시간 범위에 따른 정렬 기준
            order_field = {
                'daily': 'daily_mentions',
                'weekly': 'weekly_mentions',
                'monthly': 'monthly_mentions'
            }.get(time_range, 'daily_mentions')

            query = f"""
                SELECT
                    id, topic_name, hashtag, region, category,
                    posts_count, mentions_count, engagement_score, trend_score,
                    {order_field} as current_mentions,
                    is_promoted, trend_started_at, peak_time, last_mention_at
                FROM trending_topics
                WHERE is_active = TRUE
                AND (region = %s OR (region IS NULL AND %s IS NULL))
                AND {order_field} >= %s
                ORDER BY is_promoted DESC, {order_field} DESC, trend_score DESC
                LIMIT %s
            """

            min_mentions = self.min_mentions_for_trend
            cursor.execute(query, (region, region, min_mentions, limit))

            topics = []
            for row in cursor.fetchall():
                topics.append({
                    'id': row[0],
                    'topic_name': row[1],
                    'hashtag': row[2],
                    'region': row[3],
                    'category': row[4],
                    'posts_count': row[5],
                    'mentions_count': row[6],
                    'engagement_score': float(row[7]) if row[7] else 0,
                    'trend_score': float(row[8]) if row[8] else 0,
                    'current_mentions': row[9],
                    'is_promoted': row[10],
                    'trend_started_at': row[11],
                    'peak_time': row[12],
                    'last_mention_at': row[13]
                })

            cursor.close()
            conn.close()

            return topics

        except Exception as e:
            logger.error(f"트렌딩 토픽 조회 오류: {e}")
            return []

    async def calculate_trend_scores(self) -> None:
        """트렌드 점수 계산 (백그라운드 작업)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 활성 토픽들 조회
            cursor.execute("""
                SELECT id, hashtag, region, daily_mentions, weekly_mentions,
                       monthly_mentions, engagement_score, trend_started_at, last_mention_at
                FROM trending_topics
                WHERE is_active = TRUE
                AND last_mention_at >= %s
            """, (datetime.now() - timedelta(hours=self.trend_decay_hours),))

            topics = cursor.fetchall()

            for topic in topics:
                topic_id = topic[0]
                daily = topic[3]
                weekly = topic[4]
                monthly = topic[5]
                engagement = float(topic[6]) if topic[6] else 0
                started = topic[7]
                last_mention = topic[8]

                # 트렌드 점수 계산 로직
                trend_score = await self._calculate_trend_score(
                    daily, weekly, monthly, engagement, started, last_mention
                )

                cursor.execute("""
                    UPDATE trending_topics
                    SET trend_score = %s, updated_at = %s
                    WHERE id = %s
                """, (trend_score, datetime.now(), topic_id))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"트렌드 점수 계산 오류: {e}")

    async def _calculate_trend_score(
        self, daily: int, weekly: int, monthly: int,
        engagement: float, started: datetime, last_mention: datetime
    ) -> float:
        """트렌드 점수 계산 알고리즘"""

        # 기본 점수 (일일 언급 수 기반)
        base_score = daily * 10

        # 성장률 보너스 (주간 vs 일간)
        growth_bonus = 0
        if weekly > 0:
            growth_rate = daily / (weekly / 7)  # 평균 일일 대비 오늘 비율
            if growth_rate > 1:
                growth_bonus = (growth_rate - 1) * 50

        # 참여도 보너스
        engagement_bonus = engagement * 2

        # 신선도 보너스 (최근 언급일수록 높음)
        hours_since_mention = (datetime.now() - last_mention).total_seconds() / 3600
        freshness_bonus = max(0, 100 - hours_since_mention * 2)

        # 지속성 보너스 (오래 지속되는 토픽)
        hours_since_start = (datetime.now() - started).total_seconds() / 3600
        if hours_since_start > 24:
            persistence_bonus = min(50, hours_since_start / 24 * 5)
        else:
            persistence_bonus = 0

        total_score = (
            base_score + growth_bonus + engagement_bonus +
            freshness_bonus + persistence_bonus
        )

        return round(total_score, 2)

    async def get_topic_posts(
        self, hashtag: str, region: str = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """특정 토픽의 포스트들 조회"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 해시태그를 포함한 포스트 검색
            query = """
                SELECT
                    sp.id, sp.user_id, sp.title, sp.content, sp.post_type,
                    sp.images, sp.video_url, sp.location, sp.hashtags,
                    sp.likes_count, sp.comments_count, sp.shares_count,
                    sp.published_at, spr.display_name, spr.avatar_url
                FROM social_posts sp
                JOIN social_profiles spr ON sp.user_id = spr.user_id
                WHERE sp.status = 'published'
                AND %s = ANY(sp.hashtags)
            """

            params = [hashtag]

            if region:
                query += " AND (sp.location LIKE %s OR spr.farm_location LIKE %s)"
                params.extend([f"%{region}%", f"%{region}%"])

            query += " ORDER BY sp.published_at DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)

            posts = []
            for row in cursor.fetchall():
                posts.append({
                    'id': row[0],
                    'user_id': row[1],
                    'title': row[2],
                    'content': row[3],
                    'post_type': row[4],
                    'images': row[5],
                    'video_url': row[6],
                    'location': row[7],
                    'hashtags': row[8],
                    'likes_count': row[9],
                    'comments_count': row[10],
                    'shares_count': row[11],
                    'published_at': row[12],
                    'user_display_name': row[13],
                    'user_avatar_url': row[14]
                })

            cursor.close()
            conn.close()

            return posts

        except Exception as e:
            logger.error(f"토픽 포스트 조회 오류: {e}")
            return []

    async def get_recommended_hashtags(
        self, user_id: str, content: str, limit: int = 10
    ) -> List[str]:
        """사용자에게 추천할 해시태그"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 사용자 프로필 정보 조회
            cursor.execute("""
                SELECT specialties, farm_location, farmer_type
                FROM social_profiles WHERE user_id = %s
            """, (user_id,))

            profile = cursor.fetchone()
            recommendations = []

            if profile:
                specialties = profile[0] or []
                location = profile[1]
                farmer_type = profile[2]

                # 전문 분야 기반 추천
                if specialties:
                    for specialty in specialties:
                        recommendations.append(f"#{specialty}")

                # 지역 기반 추천
                if location:
                    recommendations.append(f"#{location}")

                # 농업 유형 기반 추천
                if farmer_type:
                    recommendations.append(f"#{farmer_type}")

            # 콘텐츠 기반 키워드 추천
            content_keywords = await self._extract_keywords_from_content(content)
            recommendations.extend([f"#{kw}" for kw in content_keywords[:3]])

            # 현재 트렌딩 토픽 추천
            trending = await self.get_trending_topics(limit=5)
            recommendations.extend([topic['hashtag'] for topic in trending])

            # 중복 제거 및 제한
            unique_recommendations = list(dict.fromkeys(recommendations))[:limit]

            cursor.close()
            conn.close()

            return unique_recommendations

        except Exception as e:
            logger.error(f"해시태그 추천 오류: {e}")
            return []

    async def _extract_keywords_from_content(self, content: str) -> List[str]:
        """콘텐츠에서 키워드 추출 (간단한 구현)"""
        # 농업/환경 관련 키워드 사전
        agriculture_keywords = [
            '유기농', '친환경', '재배', '수확', '농장', '텃밭', '작물',
            '씨앗', '모종', '퇴비', '토양', '물주기', '농약', '비료',
            '온실', '하우스', '트랙터', '농기구', '농산물', '로컬푸드',
            '탄소발자국', '지속가능', '재생에너지', '태양광', '풍력',
            '바이오가스', '순환농업', '스마트팜', '드론', 'IoT'
        ]

        found_keywords = []
        content_lower = content.lower()

        for keyword in agriculture_keywords:
            if keyword in content or keyword.lower() in content_lower:
                found_keywords.append(keyword)

        return found_keywords[:5]

    async def cleanup_old_trends(self) -> None:
        """오래된 트렌드 데이터 정리"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 30일 이상 언급이 없는 토픽 비활성화
            cutoff_date = datetime.now() - timedelta(days=30)

            cursor.execute("""
                UPDATE trending_topics
                SET is_active = FALSE
                WHERE last_mention_at < %s AND is_active = TRUE
            """, (cutoff_date,))

            # 일일/주간/월간 카운터 리셋 (매일 자정 실행 가정)
            if datetime.now().hour == 0:
                # 일일 리셋
                cursor.execute("UPDATE trending_topics SET daily_mentions = 0")

                # 주간 리셋 (월요일)
                if datetime.now().weekday() == 0:
                    cursor.execute("UPDATE trending_topics SET weekly_mentions = 0")

                # 월간 리셋 (1일)
                if datetime.now().day == 1:
                    cursor.execute("UPDATE trending_topics SET monthly_mentions = 0")

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"오래된 트렌드 정리 오류: {e}")