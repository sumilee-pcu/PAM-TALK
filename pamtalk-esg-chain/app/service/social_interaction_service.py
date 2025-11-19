# -*- coding: utf-8 -*-
"""
소셜 인터랙션 서비스
좋아요, 댓글, 공유 등 사용자 상호작용 관리
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from app.utils.db_pool import db_service
from app.service.social_feed_service import social_feed_service


class SocialInteractionService:
    """소셜 인터랙션 관리 서비스"""

    def __init__(self):
        self.db = db_service
        self.feed_service = social_feed_service

    # ========== 좋아요 기능 ==========

    def like_post(self, user_id: str, post_id: int, like_type: str = 'like') -> Dict:
        """포스트 좋아요"""
        try:
            # 이미 좋아요했는지 확인
            existing_like = self._get_existing_like(user_id, post_id)

            if existing_like:
                # 기존 좋아요가 같은 타입이면 취소, 다른 타입이면 변경
                if existing_like['like_type'] == like_type:
                    return self.unlike_post(user_id, post_id)
                else:
                    return self._update_like_type(user_id, post_id, like_type)

            # 새로운 좋아요 추가
            query = """
                INSERT INTO social_post_likes (post_id, user_id, like_type)
                VALUES (%s, %s, %s)
                RETURNING id
            """

            result = self.db.pool.execute_query(
                query, (post_id, user_id, like_type), fetch='one'
            )

            # 포스트 작성자에게 알림 생성 (본인이 아닌 경우)
            post_info = self._get_post_author(post_id)
            if post_info and post_info['user_id'] != user_id:
                self._create_like_notification(user_id, post_id, post_info['user_id'], like_type)

            # 참여도 점수 업데이트
            self._update_post_engagement_score(post_id)

            return {
                'success': True,
                'action': 'liked',
                'like_type': like_type,
                'like_id': result['id']
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'좋아요 실패: {str(e)}'
            }

    def unlike_post(self, user_id: str, post_id: int) -> Dict:
        """포스트 좋아요 취소"""
        try:
            query = """
                DELETE FROM social_post_likes
                WHERE post_id = %s AND user_id = %s
                RETURNING id
            """

            result = self.db.pool.execute_query(
                query, (post_id, user_id), fetch='one'
            )

            if result:
                # 참여도 점수 업데이트
                self._update_post_engagement_score(post_id)

                return {
                    'success': True,
                    'action': 'unliked'
                }
            else:
                return {
                    'success': False,
                    'message': '좋아요가 존재하지 않습니다.'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'좋아요 취소 실패: {str(e)}'
            }

    def get_post_likes(self, post_id: int, page: int = 1, limit: int = 20) -> Dict:
        """포스트 좋아요 목록 조회"""
        offset = (page - 1) * limit

        query = """
            SELECT spl.like_type, spl.created_at,
                   sp.user_id, sp.display_name, sp.avatar_url, sp.is_verified
            FROM social_post_likes spl
            JOIN social_profiles sp ON spl.user_id = sp.user_id
            WHERE spl.post_id = %s
            ORDER BY spl.created_at DESC
            LIMIT %s OFFSET %s
        """

        likes = self.db.pool.execute_query(query, (post_id, limit, offset))

        # 좋아요 타입별 통계
        stats_query = """
            SELECT like_type, COUNT(*) as count
            FROM social_post_likes
            WHERE post_id = %s
            GROUP BY like_type
        """

        like_stats = self.db.pool.execute_query(stats_query, (post_id,))

        return {
            'likes': [dict(like) for like in likes],
            'statistics': {stat['like_type']: stat['count'] for stat in like_stats},
            'total_count': sum(stat['count'] for stat in like_stats),
            'page': page,
            'limit': limit,
            'has_more': len(likes) == limit
        }

    # ========== 댓글 기능 ==========

    def create_comment(self, user_id: str, post_id: int, content: str,
                      parent_comment_id: int = None) -> Dict:
        """댓글 작성"""
        try:
            # 내용 검증
            if not content.strip():
                return {
                    'success': False,
                    'message': '댓글 내용을 입력해주세요.'
                }

            if len(content) > 1000:
                return {
                    'success': False,
                    'message': '댓글은 1000자 이내로 작성해주세요.'
                }

            query = """
                INSERT INTO social_post_comments
                (post_id, user_id, parent_comment_id, content)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """

            result = self.db.pool.execute_query(
                query, (post_id, user_id, parent_comment_id, content), fetch='one'
            )

            comment_id = result['id']

            # 대댓글인 경우 부모 댓글의 답글 수 증가
            if parent_comment_id:
                self._increment_comment_replies_count(parent_comment_id)

                # 부모 댓글 작성자에게 알림
                parent_comment_info = self._get_comment_info(parent_comment_id)
                if parent_comment_info and parent_comment_info['user_id'] != user_id:
                    self._create_reply_notification(
                        user_id, comment_id, parent_comment_info['user_id'], post_id
                    )

            # 포스트 작성자에게 알림 (본인이 아닌 경우)
            post_info = self._get_post_author(post_id)
            if post_info and post_info['user_id'] != user_id:
                self._create_comment_notification(user_id, comment_id, post_info['user_id'], post_id)

            # 참여도 점수 업데이트
            self._update_post_engagement_score(post_id)

            return {
                'success': True,
                'comment_id': comment_id,
                'message': '댓글이 작성되었습니다.'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'댓글 작성 실패: {str(e)}'
            }

    def get_post_comments(self, post_id: int, page: int = 1, limit: int = 20,
                         sort_by: str = 'newest') -> Dict:
        """포스트 댓글 목록 조회"""
        offset = (page - 1) * limit

        # 정렬 옵션
        sort_options = {
            'newest': 'c.created_at DESC',
            'oldest': 'c.created_at ASC',
            'most_liked': 'c.likes_count DESC, c.created_at DESC'
        }

        order_by = sort_options.get(sort_by, 'c.created_at DESC')

        # 최상위 댓글만 조회 (대댓글은 별도 로딩)
        query = f"""
            SELECT c.*, sp.display_name, sp.avatar_url, sp.is_verified
            FROM social_post_comments c
            JOIN social_profiles sp ON c.user_id = sp.user_id
            WHERE c.post_id = %s AND c.parent_comment_id IS NULL
            AND c.status = 'published'
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """

        comments = self.db.pool.execute_query(query, (post_id, limit, offset))

        # 각 댓글의 대댓글 미리보기 (최신 3개)
        processed_comments = []
        for comment in comments:
            comment_dict = dict(comment)

            # 대댓글 미리보기
            if comment_dict['replies_count'] > 0:
                replies_preview = self._get_comment_replies_preview(comment_dict['id'])
                comment_dict['replies_preview'] = replies_preview
            else:
                comment_dict['replies_preview'] = []

            processed_comments.append(comment_dict)

        return {
            'comments': processed_comments,
            'page': page,
            'limit': limit,
            'sort_by': sort_by,
            'has_more': len(comments) == limit
        }

    def get_comment_replies(self, comment_id: int, page: int = 1, limit: int = 10) -> Dict:
        """댓글의 대댓글 목록 조회"""
        offset = (page - 1) * limit

        query = """
            SELECT c.*, sp.display_name, sp.avatar_url, sp.is_verified
            FROM social_post_comments c
            JOIN social_profiles sp ON c.user_id = sp.user_id
            WHERE c.parent_comment_id = %s AND c.status = 'published'
            ORDER BY c.created_at ASC
            LIMIT %s OFFSET %s
        """

        replies = self.db.pool.execute_query(query, (comment_id, limit, offset))

        return {
            'replies': [dict(reply) for reply in replies],
            'page': page,
            'limit': limit,
            'has_more': len(replies) == limit
        }

    def like_comment(self, user_id: str, comment_id: int) -> Dict:
        """댓글 좋아요"""
        try:
            # 중복 확인
            check_query = """
                SELECT id FROM social_comment_likes
                WHERE comment_id = %s AND user_id = %s
            """

            existing = self.db.pool.execute_query(
                check_query, (comment_id, user_id), fetch='one'
            )

            if existing:
                # 이미 좋아요한 경우 취소
                delete_query = """
                    DELETE FROM social_comment_likes
                    WHERE comment_id = %s AND user_id = %s
                """
                self.db.pool.execute_query(delete_query, (comment_id, user_id), fetch=None)

                return {
                    'success': True,
                    'action': 'unliked'
                }
            else:
                # 새로운 좋아요 추가
                insert_query = """
                    INSERT INTO social_comment_likes (comment_id, user_id)
                    VALUES (%s, %s)
                """
                self.db.pool.execute_query(insert_query, (comment_id, user_id), fetch=None)

                return {
                    'success': True,
                    'action': 'liked'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'댓글 좋아요 실패: {str(e)}'
            }

    def delete_comment(self, user_id: str, comment_id: int) -> Dict:
        """댓글 삭제 (본인 댓글만)"""
        try:
            # 댓글 소유자 확인
            comment_info = self._get_comment_info(comment_id)

            if not comment_info:
                return {
                    'success': False,
                    'message': '댓글을 찾을 수 없습니다.'
                }

            if comment_info['user_id'] != user_id:
                return {
                    'success': False,
                    'message': '본인의 댓글만 삭제할 수 있습니다.'
                }

            # 대댓글이 있는 경우 내용만 삭제 (구조 유지)
            if comment_info['replies_count'] > 0:
                update_query = """
                    UPDATE social_post_comments
                    SET content = '[삭제된 댓글입니다]',
                        status = 'deleted',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                self.db.pool.execute_query(update_query, (comment_id,), fetch=None)

                action = 'content_deleted'
            else:
                # 대댓글이 없으면 완전 삭제
                delete_query = """
                    DELETE FROM social_post_comments
                    WHERE id = %s
                """
                self.db.pool.execute_query(delete_query, (comment_id,), fetch=None)

                action = 'deleted'

            return {
                'success': True,
                'action': action
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'댓글 삭제 실패: {str(e)}'
            }

    # ========== 공유 기능 ==========

    def share_post(self, user_id: str, post_id: int, share_type: str = 'repost',
                  additional_comment: str = '') -> Dict:
        """포스트 공유"""
        try:
            # 원본 포스트 정보 조회
            original_post = self._get_post_info(post_id)

            if not original_post:
                return {
                    'success': False,
                    'message': '공유할 포스트를 찾을 수 없습니다.'
                }

            if share_type == 'repost':
                # 리포스트: 새로운 포스트 생성
                repost_content = f"[리포스트] {additional_comment}".strip()

                if not repost_content or repost_content == '[리포스트]':
                    repost_content = f"@{original_post['user_id']}님의 게시물을 공유합니다."

                new_post_query = """
                    INSERT INTO social_posts
                    (user_id, post_type, content, hashtags, categories, status)
                    VALUES (%s, 'repost', %s, %s, %s, 'published')
                    RETURNING id
                """

                result = self.db.pool.execute_query(
                    new_post_query,
                    (user_id, repost_content, original_post.get('hashtags', []),
                     original_post.get('categories', [])),
                    fetch='one'
                )

                share_id = result['id']

            elif share_type == 'quote':
                # 인용 공유: 원본 포스트 참조하여 새 포스트 생성
                quote_content = f"{additional_comment}\n\n--- 원문 ---\n{original_post['content'][:200]}..."

                new_post_query = """
                    INSERT INTO social_posts
                    (user_id, post_type, content, status)
                    VALUES (%s, 'quote', %s, 'published')
                    RETURNING id
                """

                result = self.db.pool.execute_query(
                    new_post_query, (user_id, quote_content), fetch='one'
                )

                share_id = result['id']

            # 원본 포스트 공유 수 증가
            share_count_query = """
                UPDATE social_posts
                SET shares_count = shares_count + 1
                WHERE id = %s
            """
            self.db.pool.execute_query(share_count_query, (post_id,), fetch=None)

            # 원본 작성자에게 알림
            if original_post['user_id'] != user_id:
                self._create_share_notification(
                    user_id, share_id, original_post['user_id'], post_id, share_type
                )

            # 참여도 점수 업데이트
            self._update_post_engagement_score(post_id)

            return {
                'success': True,
                'share_type': share_type,
                'share_id': share_id,
                'message': f'포스트가 {share_type}되었습니다.'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'포스트 공유 실패: {str(e)}'
            }

    # ========== 알림 기능 ==========

    def get_user_notifications(self, user_id: str, page: int = 1, limit: int = 20,
                              unread_only: bool = False) -> Dict:
        """사용자 알림 목록 조회"""
        offset = (page - 1) * limit

        conditions = ["user_id = %s"]
        params = [user_id]

        if unread_only:
            conditions.append("is_read = FALSE")

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT n.*, sp.display_name, sp.avatar_url
            FROM social_notifications n
            LEFT JOIN social_profiles sp ON n.triggered_by_user_id = sp.user_id
            WHERE {where_clause}
            ORDER BY n.created_at DESC
            LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])

        notifications = self.db.pool.execute_query(query, tuple(params))

        return {
            'notifications': [dict(notif) for notif in notifications],
            'page': page,
            'limit': limit,
            'unread_only': unread_only,
            'has_more': len(notifications) == limit
        }

    def mark_notification_read(self, user_id: str, notification_id: int) -> Dict:
        """알림 읽음 처리"""
        try:
            query = """
                UPDATE social_notifications
                SET is_read = TRUE, read_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s AND is_read = FALSE
            """

            self.db.pool.execute_query(query, (notification_id, user_id), fetch=None)

            return {
                'success': True,
                'message': '알림이 읽음 처리되었습니다.'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'알림 읽음 처리 실패: {str(e)}'
            }

    def mark_all_notifications_read(self, user_id: str) -> Dict:
        """모든 알림 읽음 처리"""
        try:
            query = """
                UPDATE social_notifications
                SET is_read = TRUE, read_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND is_read = FALSE
            """

            self.db.pool.execute_query(query, (user_id,), fetch=None)

            return {
                'success': True,
                'message': '모든 알림이 읽음 처리되었습니다.'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'알림 읽음 처리 실패: {str(e)}'
            }

    def get_unread_notifications_count(self, user_id: str) -> int:
        """읽지 않은 알림 개수 조회"""
        query = """
            SELECT COUNT(*) as count
            FROM social_notifications
            WHERE user_id = %s AND is_read = FALSE
        """

        result = self.db.pool.execute_query(query, (user_id,), fetch='one')
        return result['count'] if result else 0

    # ========== Private 메서드들 ==========

    def _get_existing_like(self, user_id: str, post_id: int) -> Optional[Dict]:
        """기존 좋아요 확인"""
        query = """
            SELECT * FROM social_post_likes
            WHERE user_id = %s AND post_id = %s
        """
        result = self.db.pool.execute_query(query, (user_id, post_id), fetch='one')
        return dict(result) if result else None

    def _update_like_type(self, user_id: str, post_id: int, like_type: str) -> Dict:
        """좋아요 타입 변경"""
        query = """
            UPDATE social_post_likes
            SET like_type = %s, created_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND post_id = %s
        """
        self.db.pool.execute_query(query, (like_type, user_id, post_id), fetch=None)

        return {
            'success': True,
            'action': 'updated',
            'like_type': like_type
        }

    def _get_post_author(self, post_id: int) -> Optional[Dict]:
        """포스트 작성자 정보 조회"""
        query = "SELECT user_id FROM social_posts WHERE id = %s"
        result = self.db.pool.execute_query(query, (post_id,), fetch='one')
        return dict(result) if result else None

    def _get_post_info(self, post_id: int) -> Optional[Dict]:
        """포스트 정보 조회"""
        query = "SELECT * FROM social_posts WHERE id = %s"
        result = self.db.pool.execute_query(query, (post_id,), fetch='one')
        return dict(result) if result else None

    def _get_comment_info(self, comment_id: int) -> Optional[Dict]:
        """댓글 정보 조회"""
        query = "SELECT * FROM social_post_comments WHERE id = %s"
        result = self.db.pool.execute_query(query, (comment_id,), fetch='one')
        return dict(result) if result else None

    def _increment_comment_replies_count(self, parent_comment_id: int):
        """부모 댓글의 답글 수 증가"""
        query = """
            UPDATE social_post_comments
            SET replies_count = replies_count + 1
            WHERE id = %s
        """
        self.db.pool.execute_query(query, (parent_comment_id,), fetch=None)

    def _get_comment_replies_preview(self, comment_id: int, limit: int = 3) -> List[Dict]:
        """댓글의 대댓글 미리보기"""
        query = """
            SELECT c.*, sp.display_name, sp.avatar_url
            FROM social_post_comments c
            JOIN social_profiles sp ON c.user_id = sp.user_id
            WHERE c.parent_comment_id = %s AND c.status = 'published'
            ORDER BY c.created_at ASC
            LIMIT %s
        """

        replies = self.db.pool.execute_query(query, (comment_id, limit))
        return [dict(reply) for reply in replies]

    def _update_post_engagement_score(self, post_id: int):
        """포스트 참여도 점수 업데이트"""
        query = """
            UPDATE social_posts
            SET engagement_score = (
                (likes_count * 1.0) +
                (comments_count * 2.0) +
                (shares_count * 3.0) +
                (views_count * 0.1)
            ) / GREATEST(EXTRACT(EPOCH FROM (NOW() - published_at)) / 3600, 1)
            WHERE id = %s
        """
        self.db.pool.execute_query(query, (post_id,), fetch=None)

    def _create_like_notification(self, triggered_by: str, post_id: int,
                                target_user: str, like_type: str):
        """좋아요 알림 생성"""
        like_messages = {
            'like': '회원님의 게시물을 좋아합니다.',
            'love': '회원님의 게시물에 하트를 보냈습니다.',
            'helpful': '회원님의 게시물이 도움이 된다고 했습니다.',
            'inspiring': '회원님의 게시물이 영감을 준다고 했습니다.'
        }

        message = like_messages.get(like_type, '회원님의 게시물에 반응했습니다.')

        self._create_notification(
            user_id=target_user,
            notification_type='like',
            triggered_by_user_id=triggered_by,
            post_id=post_id,
            title='새로운 좋아요',
            message=message
        )

    def _create_comment_notification(self, triggered_by: str, comment_id: int,
                                   target_user: str, post_id: int):
        """댓글 알림 생성"""
        self._create_notification(
            user_id=target_user,
            notification_type='comment',
            triggered_by_user_id=triggered_by,
            post_id=post_id,
            comment_id=comment_id,
            title='새로운 댓글',
            message='회원님의 게시물에 댓글을 달았습니다.'
        )

    def _create_reply_notification(self, triggered_by: str, reply_id: int,
                                 target_user: str, post_id: int):
        """대댓글 알림 생성"""
        self._create_notification(
            user_id=target_user,
            notification_type='reply',
            triggered_by_user_id=triggered_by,
            post_id=post_id,
            comment_id=reply_id,
            title='새로운 답글',
            message='회원님의 댓글에 답글을 달았습니다.'
        )

    def _create_share_notification(self, triggered_by: str, share_id: int,
                                 target_user: str, original_post_id: int, share_type: str):
        """공유 알림 생성"""
        share_messages = {
            'repost': '회원님의 게시물을 리포스트했습니다.',
            'quote': '회원님의 게시물을 인용했습니다.'
        }

        message = share_messages.get(share_type, '회원님의 게시물을 공유했습니다.')

        self._create_notification(
            user_id=target_user,
            notification_type='share',
            triggered_by_user_id=triggered_by,
            post_id=original_post_id,
            title='게시물 공유',
            message=message
        )

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
social_interaction_service = SocialInteractionService()


# 사용 예시
if __name__ == "__main__":
    service = social_interaction_service

    try:
        # 좋아요 테스트
        like_result = service.like_post("user123", 1, "like")
        print(f"좋아요 결과: {like_result}")

        # 댓글 작성 테스트
        comment_result = service.create_comment(
            user_id="user456",
            post_id=1,
            content="정말 좋은 정보네요! 감사합니다. #도움됨"
        )
        print(f"댓글 작성 결과: {comment_result}")

    except Exception as e:
        print(f"테스트 실행 중 오류: {e}")