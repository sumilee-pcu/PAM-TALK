# -*- coding: utf-8 -*-
"""
소셜 콘텐츠 보상 시스템
고품질 콘텐츠 및 참여 활동에 대한 토큰 보상 자동화
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from app.utils.db_pool import db_service
from app.service.social_interaction_service import social_interaction_service
from app.service.batch_service import batch_service


class RewardType(Enum):
    """보상 타입 정의"""
    QUALITY_CONTENT = "quality_content"      # 고품질 콘텐츠
    VIRAL_POST = "viral_post"                # 바이럴 포스트
    HELPFUL_COMMENT = "helpful_comment"       # 도움되는 댓글
    ENGAGEMENT_BOOST = "engagement_boost"     # 참여 촉진
    CARBON_INFLUENCE = "carbon_influence"     # 탄소 영향력
    COMMUNITY_BUILDER = "community_builder"   # 커뮤니티 빌더
    KNOWLEDGE_SHARING = "knowledge_sharing"   # 지식 공유


@dataclass
class ContentRewardConfig:
    """콘텐츠 보상 설정"""
    min_engagement_score: float = 5.0
    min_likes_for_viral: int = 50
    min_comments_for_quality: int = 10
    min_carbon_impact: float = 1.0
    daily_max_rewards_per_user: int = 100
    quality_multiplier: float = 1.5
    viral_multiplier: float = 2.0
    carbon_multiplier: float = 3.0


class SocialContentRewardsService:
    """소셜 콘텐츠 보상 관리 서비스"""

    def __init__(self):
        self.db = db_service
        self.interaction_service = social_interaction_service
        self.batch_service = batch_service
        self.config = ContentRewardConfig()

    def evaluate_and_reward_content(self, content_type: str, content_id: int,
                                  force_evaluation: bool = False) -> Dict:
        """콘텐츠 평가 및 보상 지급"""

        try:
            # 이미 보상이 지급된 콘텐츠인지 확인
            if not force_evaluation and self._is_already_rewarded(content_type, content_id):
                return {
                    'success': False,
                    'message': '이미 보상이 지급된 콘텐츠입니다.'
                }

            # 콘텐츠 정보 조회
            content_info = self._get_content_info(content_type, content_id)
            if not content_info:
                return {
                    'success': False,
                    'message': '콘텐츠를 찾을 수 없습니다.'
                }

            # 보상 기준 평가
            evaluation_result = self._evaluate_content_quality(content_type, content_info)

            if not evaluation_result['eligible']:
                return {
                    'success': False,
                    'message': f'보상 기준 미달: {evaluation_result["reason"]}'
                }

            # 보상 계산
            reward_calculation = self._calculate_content_rewards(
                content_type, content_info, evaluation_result
            )

            # 일일 보상 한도 확인
            user_id = content_info['user_id']
            if not self._check_daily_reward_limit(user_id, reward_calculation['total_tokens']):
                return {
                    'success': False,
                    'message': '일일 보상 한도를 초과했습니다.'
                }

            # 보상 기록 생성
            reward_records = []
            for reward in reward_calculation['rewards']:
                reward_id = self._create_reward_record(
                    user_id=user_id,
                    content_type=content_type,
                    content_id=content_id,
                    reward_info=reward
                )
                reward_records.append(reward_id)

            return {
                'success': True,
                'evaluation': evaluation_result,
                'rewards': reward_calculation['rewards'],
                'total_tokens': reward_calculation['total_tokens'],
                'reward_records': reward_records
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'콘텐츠 보상 평가 실패: {str(e)}'
            }

    def process_daily_content_rewards(self) -> Dict:
        """일일 콘텐츠 보상 배치 처리"""

        try:
            # 어제 생성된 미평가 콘텐츠 조회
            yesterday = datetime.now() - timedelta(days=1)
            pending_contents = self._get_pending_reward_contents(yesterday)

            processed_count = 0
            rewarded_count = 0
            total_rewards = 0

            for content in pending_contents:
                try:
                    result = self.evaluate_and_reward_content(
                        content['content_type'], content['content_id']
                    )

                    processed_count += 1

                    if result['success']:
                        rewarded_count += 1
                        total_rewards += result['total_tokens']

                except Exception as e:
                    print(f"콘텐츠 {content['content_id']} 보상 처리 중 오류: {str(e)}")

            # 승인된 보상들 토큰 발행 처리
            if total_rewards > 0:
                self._process_approved_rewards()

            return {
                'success': True,
                'processed_count': processed_count,
                'rewarded_count': rewarded_count,
                'total_rewards': total_rewards
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'일일 보상 처리 실패: {str(e)}'
            }

    def get_content_reward_analytics(self, user_id: str = None,
                                   period_days: int = 30) -> Dict:
        """콘텐츠 보상 분석 데이터"""

        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)

        conditions = ["created_at >= %s", "created_at <= %s"]
        params = [start_date, end_date]

        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)

        where_clause = " AND ".join(conditions)

        # 보상 타입별 통계
        type_stats_query = f"""
            SELECT
                reward_type,
                COUNT(*) as count,
                SUM(token_amount) as total_tokens,
                AVG(engagement_score) as avg_engagement,
                AVG(quality_score) as avg_quality
            FROM social_content_rewards
            WHERE {where_clause}
            AND status = 'approved'
            GROUP BY reward_type
            ORDER BY total_tokens DESC
        """

        type_stats = self.db.pool.execute_query(type_stats_query, tuple(params))

        # 일별 보상 트렌드
        daily_trend_query = f"""
            SELECT
                DATE(created_at) as reward_date,
                COUNT(*) as rewards_count,
                SUM(token_amount) as daily_tokens,
                COUNT(DISTINCT user_id) as unique_users
            FROM social_content_rewards
            WHERE {where_clause}
            AND status = 'approved'
            GROUP BY DATE(created_at)
            ORDER BY reward_date DESC
        """

        daily_trend = self.db.pool.execute_query(daily_trend_query, tuple(params))

        # 상위 보상 수령자 (user_id 지정되지 않은 경우)
        top_earners = []
        if not user_id:
            top_earners_query = f"""
                SELECT
                    scr.user_id,
                    sp.display_name,
                    sp.avatar_url,
                    COUNT(*) as rewards_count,
                    SUM(scr.token_amount) as total_tokens,
                    AVG(scr.engagement_score) as avg_engagement
                FROM social_content_rewards scr
                JOIN social_profiles sp ON scr.user_id = sp.user_id
                WHERE {where_clause}
                AND scr.status = 'approved'
                GROUP BY scr.user_id, sp.display_name, sp.avatar_url
                ORDER BY total_tokens DESC
                LIMIT 10
            """

            top_earners = self.db.pool.execute_query(top_earners_query, tuple(params))

        return {
            'period_days': period_days,
            'type_statistics': [dict(stat) for stat in type_stats],
            'daily_trend': [dict(day) for day in daily_trend],
            'top_earners': [dict(earner) for earner in top_earners],
            'total_rewards': sum(stat['total_tokens'] for stat in type_stats),
            'total_recipients': len(top_earners) if not user_id else (1 if type_stats else 0)
        }

    def get_user_reward_history(self, user_id: str, page: int = 1,
                               limit: int = 20) -> Dict:
        """사용자 보상 히스토리"""

        offset = (page - 1) * limit

        query = """
            SELECT scr.*, sp.title as post_title, sp.content as post_content
            FROM social_content_rewards scr
            LEFT JOIN social_posts sp ON scr.content_type = 'post' AND scr.content_id = sp.id
            WHERE scr.user_id = %s
            ORDER BY scr.created_at DESC
            LIMIT %s OFFSET %s
        """

        rewards = self.db.pool.execute_query(query, (user_id, limit, offset))

        # 사용자 보상 요약
        summary_query = """
            SELECT
                COUNT(*) as total_rewards,
                SUM(token_amount) as total_tokens,
                SUM(CASE WHEN status = 'pending' THEN token_amount ELSE 0 END) as pending_tokens,
                SUM(CASE WHEN status = 'approved' THEN token_amount ELSE 0 END) as approved_tokens,
                SUM(CASE WHEN status = 'paid' THEN token_amount ELSE 0 END) as paid_tokens
            FROM social_content_rewards
            WHERE user_id = %s
        """

        summary = self.db.pool.execute_query(summary_query, (user_id,), fetch='one')

        return {
            'rewards': [dict(reward) for reward in rewards],
            'summary': dict(summary) if summary else {},
            'page': page,
            'limit': limit,
            'has_more': len(rewards) == limit
        }

    def approve_reward(self, reward_id: int, approver_id: str) -> Dict:
        """보상 승인"""

        try:
            # 보상 정보 조회
            reward_info = self._get_reward_info(reward_id)

            if not reward_info:
                return {
                    'success': False,
                    'message': '보상 정보를 찾을 수 없습니다.'
                }

            if reward_info['status'] != 'pending':
                return {
                    'success': False,
                    'message': f'승인할 수 없는 상태입니다: {reward_info["status"]}'
                }

            # 승인 처리
            update_query = """
                UPDATE social_content_rewards
                SET status = 'approved',
                    approved_by = %s,
                    approved_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            self.db.pool.execute_query(update_query, (approver_id, reward_id), fetch=None)

            return {
                'success': True,
                'message': '보상이 승인되었습니다.',
                'reward_id': reward_id,
                'token_amount': reward_info['token_amount']
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'보상 승인 실패: {str(e)}'
            }

    def reject_reward(self, reward_id: int, approver_id: str, reason: str) -> Dict:
        """보상 거부"""

        try:
            update_query = """
                UPDATE social_content_rewards
                SET status = 'rejected',
                    approved_by = %s,
                    approved_at = CURRENT_TIMESTAMP
                WHERE id = %s AND status = 'pending'
            """

            result = self.db.pool.execute_query(
                update_query, (approver_id, reward_id), fetch=None
            )

            return {
                'success': True,
                'message': f'보상이 거부되었습니다. 사유: {reason}'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'보상 거부 실패: {str(e)}'
            }

    # ========== Private 메서드들 ==========

    def _is_already_rewarded(self, content_type: str, content_id: int) -> bool:
        """이미 보상된 콘텐츠인지 확인"""
        query = """
            SELECT id FROM social_content_rewards
            WHERE content_type = %s AND content_id = %s
            AND status IN ('approved', 'paid')
        """
        result = self.db.pool.execute_query(query, (content_type, content_id), fetch='one')
        return result is not None

    def _get_content_info(self, content_type: str, content_id: int) -> Optional[Dict]:
        """콘텐츠 정보 조회"""
        if content_type == 'post':
            query = """
                SELECT sp.*, spr.display_name, spr.followers_count,
                       ca.carbon_savings, ca.token_reward_amount as carbon_tokens
                FROM social_posts sp
                JOIN social_profiles spr ON sp.user_id = spr.user_id
                LEFT JOIN carbon_activities ca ON sp.carbon_activity_id = ca.id
                WHERE sp.id = %s AND sp.status = 'published'
            """
        elif content_type == 'comment':
            query = """
                SELECT spc.*, spr.display_name, spr.followers_count
                FROM social_post_comments spc
                JOIN social_profiles spr ON spc.user_id = spr.user_id
                WHERE spc.id = %s AND spc.status = 'published'
            """
        else:
            return None

        result = self.db.pool.execute_query(query, (content_id,), fetch='one')
        return dict(result) if result else None

    def _evaluate_content_quality(self, content_type: str, content_info: Dict) -> Dict:
        """콘텐츠 품질 평가"""

        evaluation = {
            'eligible': False,
            'quality_score': 0.0,
            'engagement_score': 0.0,
            'reasons': []
        }

        if content_type == 'post':
            return self._evaluate_post_quality(content_info, evaluation)
        elif content_type == 'comment':
            return self._evaluate_comment_quality(content_info, evaluation)

        return evaluation

    def _evaluate_post_quality(self, post_info: Dict, evaluation: Dict) -> Dict:
        """포스트 품질 평가"""

        likes_count = int(post_info.get('likes_count', 0))
        comments_count = int(post_info.get('comments_count', 0))
        shares_count = int(post_info.get('shares_count', 0))
        views_count = int(post_info.get('views_count', 0))
        engagement_score = float(post_info.get('engagement_score', 0))
        content_length = len(post_info.get('content', ''))

        # 기본 품질 점수 계산
        quality_score = 0.0

        # 콘텐츠 길이 점수 (적절한 길이 선호)
        if 100 <= content_length <= 1000:
            quality_score += 2.0
        elif content_length > 50:
            quality_score += 1.0

        # 참여도 점수
        if engagement_score >= self.config.min_engagement_score:
            quality_score += min(engagement_score / 5, 5.0)
            evaluation['reasons'].append('높은 참여도')

        # 댓글 품질 (토론 유발)
        if comments_count >= self.config.min_comments_for_quality:
            quality_score += 3.0
            evaluation['reasons'].append('활발한 토론 유발')

        # 바이럴 성과
        if likes_count >= self.config.min_likes_for_viral:
            quality_score += 5.0
            evaluation['reasons'].append('바이럴 성과')

        # 탄소 임팩트 (탄소 활동 포스트인 경우)
        carbon_savings = post_info.get('carbon_savings')
        if carbon_savings and float(carbon_savings) >= self.config.min_carbon_impact:
            quality_score += float(carbon_savings) * 2
            evaluation['reasons'].append('탄소 임팩트')

        # 해시태그 적절 사용
        hashtags = post_info.get('hashtags', [])
        if isinstance(hashtags, str):
            hashtags = json.loads(hashtags) if hashtags else []

        if 1 <= len(hashtags) <= 5:
            quality_score += 1.0
            evaluation['reasons'].append('적절한 해시태그 사용')

        # 이미지/미디어 포함
        images = post_info.get('images', [])
        if isinstance(images, str):
            images = json.loads(images) if images else []

        if len(images) > 0:
            quality_score += 1.5
            evaluation['reasons'].append('멀티미디어 콘텐츠')

        evaluation['quality_score'] = quality_score
        evaluation['engagement_score'] = engagement_score

        # 보상 자격 판정 (최소 3점 이상)
        evaluation['eligible'] = quality_score >= 3.0

        if not evaluation['eligible']:
            evaluation['reason'] = '품질 점수 부족 (최소 3.0점 필요)'

        return evaluation

    def _evaluate_comment_quality(self, comment_info: Dict, evaluation: Dict) -> Dict:
        """댓글 품질 평가"""

        likes_count = int(comment_info.get('likes_count', 0))
        replies_count = int(comment_info.get('replies_count', 0))
        content_length = len(comment_info.get('content', ''))

        quality_score = 0.0

        # 댓글 길이 (적절한 설명)
        if content_length >= 50:
            quality_score += 2.0
        elif content_length >= 20:
            quality_score += 1.0

        # 좋아요 수
        if likes_count >= 5:
            quality_score += min(likes_count / 2, 3.0)

        # 답글 유발 (토론 촉진)
        if replies_count > 0:
            quality_score += min(replies_count, 2.0)

        evaluation['quality_score'] = quality_score
        evaluation['engagement_score'] = likes_count + replies_count * 2

        # 댓글 보상 자격 (최소 2점)
        evaluation['eligible'] = quality_score >= 2.0

        if not evaluation['eligible']:
            evaluation['reason'] = '댓글 품질 점수 부족 (최소 2.0점 필요)'

        return evaluation

    def _calculate_content_rewards(self, content_type: str, content_info: Dict,
                                 evaluation: Dict) -> Dict:
        """콘텐츠 보상 계산"""

        rewards = []
        base_tokens = 5  # 기본 토큰

        quality_score = evaluation['quality_score']
        engagement_score = evaluation['engagement_score']

        # 1. 기본 품질 보상
        if quality_score >= 3.0:
            quality_tokens = int(quality_score * 2)
            rewards.append({
                'reward_type': RewardType.QUALITY_CONTENT.value,
                'token_amount': quality_tokens,
                'engagement_score': engagement_score,
                'quality_score': quality_score,
                'description': '고품질 콘텐츠 보상'
            })

        # 2. 바이럴 보상 (포스트만)
        if content_type == 'post':
            likes_count = int(content_info.get('likes_count', 0))
            if likes_count >= self.config.min_likes_for_viral:
                viral_tokens = int(likes_count / 10 * self.config.viral_multiplier)
                rewards.append({
                    'reward_type': RewardType.VIRAL_POST.value,
                    'token_amount': viral_tokens,
                    'engagement_score': engagement_score,
                    'quality_score': quality_score,
                    'reach_count': likes_count,
                    'description': '바이럴 포스트 보상'
                })

        # 3. 탄소 영향력 보상
        carbon_savings = content_info.get('carbon_savings')
        if carbon_savings and float(carbon_savings) >= self.config.min_carbon_impact:
            carbon_tokens = int(float(carbon_savings) * self.config.carbon_multiplier)
            rewards.append({
                'reward_type': RewardType.CARBON_INFLUENCE.value,
                'token_amount': carbon_tokens,
                'engagement_score': engagement_score,
                'quality_score': quality_score,
                'carbon_impact': float(carbon_savings),
                'description': '탄소 영향력 보상'
            })

        # 4. 지식 공유 보상 (교육적 콘텐츠)
        content = content_info.get('content', '').lower()
        educational_keywords = ['방법', '팁', '노하우', '경험', '배웠', '추천', '정보']
        if any(keyword in content for keyword in educational_keywords):
            knowledge_tokens = int(quality_score * 1.5)
            rewards.append({
                'reward_type': RewardType.KNOWLEDGE_SHARING.value,
                'token_amount': knowledge_tokens,
                'engagement_score': engagement_score,
                'quality_score': quality_score,
                'description': '지식 공유 보상'
            })

        total_tokens = sum(reward['token_amount'] for reward in rewards)

        return {
            'rewards': rewards,
            'total_tokens': total_tokens
        }

    def _check_daily_reward_limit(self, user_id: str, additional_tokens: int) -> bool:
        """일일 보상 한도 확인"""
        today = datetime.now().date()

        query = """
            SELECT COALESCE(SUM(token_amount), 0) as daily_total
            FROM social_content_rewards
            WHERE user_id = %s
            AND DATE(created_at) = %s
            AND status != 'rejected'
        """

        result = self.db.pool.execute_query(query, (user_id, today), fetch='one')
        daily_total = int(result['daily_total']) if result else 0

        return (daily_total + additional_tokens) <= self.config.daily_max_rewards_per_user

    def _create_reward_record(self, user_id: str, content_type: str, content_id: int,
                            reward_info: Dict) -> int:
        """보상 기록 생성"""

        query = """
            INSERT INTO social_content_rewards
            (user_id, content_type, content_id, reward_type, token_amount,
             engagement_score, quality_score, reach_count, carbon_impact, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            RETURNING id
        """

        params = (
            user_id, content_type, content_id,
            reward_info['reward_type'], reward_info['token_amount'],
            reward_info.get('engagement_score', 0),
            reward_info.get('quality_score', 0),
            reward_info.get('reach_count'),
            reward_info.get('carbon_impact'),
        )

        result = self.db.pool.execute_query(query, params, fetch='one')
        return result['id']

    def _get_pending_reward_contents(self, since_date: datetime) -> List[Dict]:
        """보상 대기 중인 콘텐츠 조회"""

        # 포스트 조회
        posts_query = """
            SELECT 'post' as content_type, id as content_id, user_id, published_at as created_at
            FROM social_posts
            WHERE published_at >= %s
            AND engagement_score >= %s
            AND id NOT IN (
                SELECT content_id FROM social_content_rewards
                WHERE content_type = 'post' AND status IN ('approved', 'paid')
            )
        """

        # 댓글 조회
        comments_query = """
            SELECT 'comment' as content_type, id as content_id, user_id, created_at
            FROM social_post_comments
            WHERE created_at >= %s
            AND likes_count >= 3
            AND id NOT IN (
                SELECT content_id FROM social_content_rewards
                WHERE content_type = 'comment' AND status IN ('approved', 'paid')
            )
        """

        posts = self.db.pool.execute_query(
            posts_query, (since_date, self.config.min_engagement_score)
        )

        comments = self.db.pool.execute_query(comments_query, (since_date,))

        # 결합 및 정렬
        all_contents = list(posts) + list(comments)
        return [dict(content) for content in all_contents]

    def _get_reward_info(self, reward_id: int) -> Optional[Dict]:
        """보상 정보 조회"""
        query = "SELECT * FROM social_content_rewards WHERE id = %s"
        result = self.db.pool.execute_query(query, (reward_id,), fetch='one')
        return dict(result) if result else None

    def _process_approved_rewards(self):
        """승인된 보상들 토큰 발행 처리"""

        # 승인되었지만 아직 지급되지 않은 보상들 조회
        query = """
            SELECT user_id, SUM(token_amount) as total_tokens, COUNT(*) as reward_count
            FROM social_content_rewards
            WHERE status = 'approved' AND tx_hash IS NULL
            GROUP BY user_id
            HAVING SUM(token_amount) >= 10  -- 최소 10토큰 이상
        """

        pending_rewards = self.db.pool.execute_query(query)

        for reward in pending_rewards:
            try:
                # 배치 토큰 발행 작업 생성
                job_id = self.batch_service.create_mass_mint_job(
                    amount=int(reward['total_tokens']),
                    description=f"소셜 콘텐츠 보상 ({reward['user_id']})",
                    issued_by="social_content_system",
                    asset_id=int(os.getenv("ASA_ID")),
                    asset_name=os.getenv("ASA_NAME", "PAM Token"),
                    unit_name="SOCIAL"
                )

                # 보상 기록 업데이트
                update_query = """
                    UPDATE social_content_rewards
                    SET status = 'processing', tx_hash = %s, paid_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND status = 'approved' AND tx_hash IS NULL
                """

                self.db.pool.execute_query(
                    update_query, (job_id, reward['user_id']), fetch=None
                )

                print(f"사용자 {reward['user_id']} 콘텐츠 보상 토큰 발행 시작: {job_id}")

            except Exception as e:
                print(f"보상 토큰 발행 실패 (사용자: {reward['user_id']}): {str(e)}")


# 서비스 인스턴스
social_content_rewards_service = SocialContentRewardsService()


# 사용 예시
if __name__ == "__main__":
    service = social_content_rewards_service

    try:
        # 포스트 보상 평가 테스트
        result = service.evaluate_and_reward_content("post", 1)
        print(f"포스트 보상 평가: {result}")

        # 일일 보상 처리 테스트
        daily_result = service.process_daily_content_rewards()
        print(f"일일 보상 처리: {daily_result}")

        # 분석 데이터 조회 테스트
        analytics = service.get_content_reward_analytics(period_days=7)
        print(f"보상 분석 데이터: {analytics}")

    except Exception as e:
        print(f"테스트 실행 중 오류: {e}")