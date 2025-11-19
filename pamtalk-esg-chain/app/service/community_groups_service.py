# -*- coding: utf-8 -*-
"""
커뮤니티 그룹 관리 서비스
그룹 생성, 멤버 관리, 그룹 포스트, 지역별 그룹 추천
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

from ..utils.db_pool import get_db_connection

logger = logging.getLogger(__name__)

class CommunityGroupsService:
    def __init__(self):
        self.max_groups_per_user = 10
        self.default_group_categories = [
            'vegetables', 'fruits', 'livestock', 'organic', 'conventional',
            'greenhouse', 'field_crop', 'herb', 'flower', 'rice'
        ]

    async def create_group(
        self,
        creator_user_id: str,
        name: str,
        description: str,
        group_type: str,
        category: str = None,
        region: str = None,
        is_private: bool = False,
        require_approval: bool = False,
        avatar_url: str = None,
        cover_image_url: str = None
    ) -> Optional[Dict[str, Any]]:
        """새 커뮤니티 그룹 생성"""
        try:
            # 사용자의 그룹 생성 제한 확인
            if not await self._can_create_group(creator_user_id):
                raise ValueError("그룹 생성 한도를 초과했습니다")

            conn = get_db_connection()
            cursor = conn.cursor()

            # 그룹 생성
            cursor.execute("""
                INSERT INTO community_groups (
                    name, description, avatar_url, cover_image_url,
                    group_type, category, region, is_private, require_approval,
                    allow_member_posts, created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                name, description, avatar_url, cover_image_url,
                group_type, category, region, is_private, require_approval,
                True, creator_user_id
            ))

            group_id = cursor.fetchone()[0]

            # 생성자를 관리자로 멤버 추가
            cursor.execute("""
                INSERT INTO community_group_members (
                    group_id, user_id, role, status, last_activity_at
                ) VALUES (%s, %s, 'admin', 'active', %s)
            """, (group_id, creator_user_id, datetime.now()))

            # 그룹 멤버 수 업데이트
            cursor.execute("""
                UPDATE community_groups SET members_count = 1 WHERE id = %s
            """, (group_id,))

            conn.commit()

            # 생성된 그룹 정보 조회
            group_info = await self.get_group_info(group_id)

            cursor.close()
            conn.close()

            return group_info

        except Exception as e:
            logger.error(f"그룹 생성 오류: {e}")
            return None

    async def _can_create_group(self, user_id: str) -> bool:
        """사용자가 그룹을 생성할 수 있는지 확인"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM community_groups
                WHERE created_by = %s AND status = 'active'
            """, (user_id,))

            count = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return count < self.max_groups_per_user

        except Exception as e:
            logger.error(f"그룹 생성 권한 확인 오류: {e}")
            return False

    async def get_group_info(self, group_id: int) -> Optional[Dict[str, Any]]:
        """그룹 상세 정보 조회"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    cg.id, cg.name, cg.description, cg.avatar_url, cg.cover_image_url,
                    cg.group_type, cg.category, cg.region, cg.is_private,
                    cg.require_approval, cg.allow_member_posts, cg.members_count,
                    cg.posts_count, cg.created_by, cg.status, cg.created_at,
                    sp.display_name as creator_name, sp.avatar_url as creator_avatar
                FROM community_groups cg
                JOIN social_profiles sp ON cg.created_by = sp.user_id
                WHERE cg.id = %s
            """, (group_id,))

            row = cursor.fetchone()
            if not row:
                return None

            group_info = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'avatar_url': row[3],
                'cover_image_url': row[4],
                'group_type': row[5],
                'category': row[6],
                'region': row[7],
                'is_private': row[8],
                'require_approval': row[9],
                'allow_member_posts': row[10],
                'members_count': row[11],
                'posts_count': row[12],
                'created_by': row[13],
                'status': row[14],
                'created_at': row[15],
                'creator_name': row[16],
                'creator_avatar': row[17]
            }

            # 최근 활동 멤버들 조회
            group_info['recent_members'] = await self._get_recent_members(group_id)

            # 최근 포스트들 조회
            group_info['recent_posts'] = await self._get_recent_group_posts(group_id, limit=3)

            cursor.close()
            conn.close()

            return group_info

        except Exception as e:
            logger.error(f"그룹 정보 조회 오류: {e}")
            return None

    async def _get_recent_members(self, group_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 활동한 그룹 멤버들 조회"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    cgm.user_id, cgm.role, cgm.posts_count, cgm.last_activity_at,
                    sp.display_name, sp.avatar_url
                FROM community_group_members cgm
                JOIN social_profiles sp ON cgm.user_id = sp.user_id
                WHERE cgm.group_id = %s AND cgm.status = 'active'
                ORDER BY cgm.last_activity_at DESC NULLS LAST, cgm.joined_at DESC
                LIMIT %s
            """, (group_id, limit))

            members = []
            for row in cursor.fetchall():
                members.append({
                    'user_id': row[0],
                    'role': row[1],
                    'posts_count': row[2],
                    'last_activity_at': row[3],
                    'display_name': row[4],
                    'avatar_url': row[5]
                })

            cursor.close()
            conn.close()

            return members

        except Exception as e:
            logger.error(f"최근 멤버 조회 오류: {e}")
            return []

    async def _get_recent_group_posts(self, group_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """그룹의 최근 포스트들 조회"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    sp.id, sp.user_id, sp.title, sp.content, sp.post_type,
                    sp.images, sp.likes_count, sp.comments_count,
                    sp.published_at, spr.display_name, spr.avatar_url,
                    cgp.is_pinned, cgp.is_announcement
                FROM social_posts sp
                JOIN community_group_posts cgp ON sp.id = cgp.post_id
                JOIN social_profiles spr ON sp.user_id = spr.user_id
                WHERE cgp.group_id = %s AND sp.status = 'published'
                ORDER BY cgp.is_pinned DESC, cgp.is_announcement DESC,
                         sp.published_at DESC
                LIMIT %s
            """, (group_id, limit))

            posts = []
            for row in cursor.fetchall():
                posts.append({
                    'id': row[0],
                    'user_id': row[1],
                    'title': row[2],
                    'content': row[3][:200] + '...' if len(row[3]) > 200 else row[3],
                    'post_type': row[4],
                    'images': row[5],
                    'likes_count': row[6],
                    'comments_count': row[7],
                    'published_at': row[8],
                    'user_display_name': row[9],
                    'user_avatar_url': row[10],
                    'is_pinned': row[11],
                    'is_announcement': row[12]
                })

            cursor.close()
            conn.close()

            return posts

        except Exception as e:
            logger.error(f"그룹 포스트 조회 오류: {e}")
            return []

    async def join_group(self, group_id: int, user_id: str) -> bool:
        """그룹 가입"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 그룹 정보 확인
            cursor.execute("""
                SELECT is_private, require_approval FROM community_groups
                WHERE id = %s AND status = 'active'
            """, (group_id,))

            group_info = cursor.fetchone()
            if not group_info:
                return False

            is_private, require_approval = group_info

            # 이미 가입했는지 확인
            cursor.execute("""
                SELECT status FROM community_group_members
                WHERE group_id = %s AND user_id = %s
            """, (group_id, user_id))

            existing = cursor.fetchone()
            if existing:
                if existing[0] == 'active':
                    return True  # 이미 활성 멤버
                elif existing[0] == 'banned':
                    return False  # 차단된 사용자

            # 가입 상태 결정
            status = 'pending' if require_approval else 'active'

            # 멤버 추가 또는 업데이트
            cursor.execute("""
                INSERT INTO community_group_members (
                    group_id, user_id, role, status, last_activity_at
                ) VALUES (%s, %s, 'member', %s, %s)
                ON CONFLICT (group_id, user_id)
                DO UPDATE SET status = %s, updated_at = %s
            """, (group_id, user_id, status, datetime.now(), status, datetime.now()))

            # 승인된 가입인 경우 멤버 수 업데이트
            if status == 'active':
                cursor.execute("""
                    UPDATE community_groups
                    SET members_count = (
                        SELECT COUNT(*) FROM community_group_members
                        WHERE group_id = %s AND status = 'active'
                    )
                    WHERE id = %s
                """, (group_id, group_id))

            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"그룹 가입 오류: {e}")
            return False

    async def leave_group(self, group_id: int, user_id: str) -> bool:
        """그룹 탈퇴"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 그룹 생성자인지 확인
            cursor.execute("""
                SELECT created_by FROM community_groups WHERE id = %s
            """, (group_id,))

            creator = cursor.fetchone()
            if creator and creator[0] == user_id:
                # 생성자는 다른 관리자가 있을 때만 탈퇴 가능
                cursor.execute("""
                    SELECT COUNT(*) FROM community_group_members
                    WHERE group_id = %s AND role = 'admin' AND user_id != %s AND status = 'active'
                """, (group_id, user_id))

                other_admins = cursor.fetchone()[0]
                if other_admins == 0:
                    return False  # 다른 관리자가 없으면 탈퇴 불가

            # 멤버 삭제
            cursor.execute("""
                DELETE FROM community_group_members
                WHERE group_id = %s AND user_id = %s
            """, (group_id, user_id))

            # 멤버 수 업데이트
            cursor.execute("""
                UPDATE community_groups
                SET members_count = (
                    SELECT COUNT(*) FROM community_group_members
                    WHERE group_id = %s AND status = 'active'
                )
                WHERE id = %s
            """, (group_id, group_id))

            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"그룹 탈퇴 오류: {e}")
            return False

    async def get_user_groups(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자가 가입한 그룹 목록"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    cg.id, cg.name, cg.description, cg.avatar_url,
                    cg.group_type, cg.category, cg.region, cg.members_count,
                    cg.posts_count, cgm.role, cgm.status, cgm.last_activity_at
                FROM community_groups cg
                JOIN community_group_members cgm ON cg.id = cgm.group_id
                WHERE cgm.user_id = %s AND cg.status = 'active'
                ORDER BY cgm.last_activity_at DESC NULLS LAST, cgm.joined_at DESC
            """, (user_id,))

            groups = []
            for row in cursor.fetchall():
                groups.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'avatar_url': row[3],
                    'group_type': row[4],
                    'category': row[5],
                    'region': row[6],
                    'members_count': row[7],
                    'posts_count': row[8],
                    'user_role': row[9],
                    'user_status': row[10],
                    'last_activity_at': row[11]
                })

            cursor.close()
            conn.close()

            return groups

        except Exception as e:
            logger.error(f"사용자 그룹 조회 오류: {e}")
            return []

    async def search_groups(
        self,
        query: str = None,
        group_type: str = None,
        category: str = None,
        region: str = None,
        user_id: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """그룹 검색"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            base_query = """
                SELECT
                    cg.id, cg.name, cg.description, cg.avatar_url,
                    cg.group_type, cg.category, cg.region, cg.is_private,
                    cg.members_count, cg.posts_count, cg.created_at
                FROM community_groups cg
                WHERE cg.status = 'active'
            """

            params = []
            conditions = []

            if query:
                conditions.append("(cg.name ILIKE %s OR cg.description ILIKE %s)")
                params.extend([f"%{query}%", f"%{query}%"])

            if group_type:
                conditions.append("cg.group_type = %s")
                params.append(group_type)

            if category:
                conditions.append("cg.category = %s")
                params.append(category)

            if region:
                conditions.append("cg.region ILIKE %s")
                params.append(f"%{region}%")

            # 비공개 그룹 제외 (사용자가 멤버가 아닌 경우)
            if user_id:
                conditions.append("""
                    (cg.is_private = FALSE OR EXISTS (
                        SELECT 1 FROM community_group_members cgm
                        WHERE cgm.group_id = cg.id AND cgm.user_id = %s
                        AND cgm.status = 'active'
                    ))
                """)
                params.append(user_id)
            else:
                conditions.append("cg.is_private = FALSE")

            if conditions:
                base_query += " AND " + " AND ".join(conditions)

            base_query += " ORDER BY cg.members_count DESC, cg.created_at DESC LIMIT %s"
            params.append(limit)

            cursor.execute(base_query, params)

            groups = []
            for row in cursor.fetchall():
                groups.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'avatar_url': row[3],
                    'group_type': row[4],
                    'category': row[5],
                    'region': row[6],
                    'is_private': row[7],
                    'members_count': row[8],
                    'posts_count': row[9],
                    'created_at': row[10]
                })

            cursor.close()
            conn.close()

            return groups

        except Exception as e:
            logger.error(f"그룹 검색 오류: {e}")
            return []

    async def get_recommended_groups(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """사용자 맞춤 그룹 추천"""
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
                        specialty_groups = await self.search_groups(
                            category=specialty, user_id=user_id, limit=3
                        )
                        recommendations.extend(specialty_groups)

                # 지역 기반 추천
                if location:
                    regional_groups = await self.search_groups(
                        region=location, user_id=user_id, limit=5
                    )
                    recommendations.extend(regional_groups)

                # 농업 유형 기반 추천
                if farmer_type:
                    type_groups = await self.search_groups(
                        group_type=farmer_type, user_id=user_id, limit=3
                    )
                    recommendations.extend(type_groups)

            # 인기 그룹 추천 (멤버 수 기반)
            popular_groups = await self.search_groups(user_id=user_id, limit=5)
            recommendations.extend(popular_groups)

            # 중복 제거 및 제한
            seen_ids = set()
            unique_recommendations = []

            for group in recommendations:
                if group['id'] not in seen_ids:
                    seen_ids.add(group['id'])
                    unique_recommendations.append(group)

                if len(unique_recommendations) >= limit:
                    break

            cursor.close()
            conn.close()

            return unique_recommendations

        except Exception as e:
            logger.error(f"그룹 추천 오류: {e}")
            return []

    async def update_member_activity(self, group_id: int, user_id: str) -> None:
        """멤버의 그룹 활동 시간 업데이트"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE community_group_members
                SET last_activity_at = %s, updated_at = %s
                WHERE group_id = %s AND user_id = %s
            """, (datetime.now(), datetime.now(), group_id, user_id))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"멤버 활동 업데이트 오류: {e}")

    async def add_post_to_group(
        self, group_id: int, post_id: int, is_pinned: bool = False, is_announcement: bool = False
    ) -> bool:
        """그룹에 포스트 추가"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO community_group_posts (
                    group_id, post_id, is_pinned, is_announcement
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (group_id, post_id) DO UPDATE SET
                    is_pinned = %s, is_announcement = %s
            """, (group_id, post_id, is_pinned, is_announcement, is_pinned, is_announcement))

            # 그룹 포스트 수 업데이트
            cursor.execute("""
                UPDATE community_groups
                SET posts_count = (
                    SELECT COUNT(*) FROM community_group_posts WHERE group_id = %s
                )
                WHERE id = %s
            """, (group_id, group_id))

            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"그룹 포스트 추가 오류: {e}")
            return False