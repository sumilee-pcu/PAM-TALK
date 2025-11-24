#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM Community Manager
커뮤니티 기능 데이터 관리 클래스
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
import uuid


@dataclass
class User:
    """사용자 정보"""
    user_id: str
    username: str
    email: str
    role: str  # 'consumer', 'supplier', 'admin'
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True
    reputation_score: int = 0  # 신뢰도 점수

    def to_dict(self):
        return asdict(self)


@dataclass
class Post:
    """커뮤니티 게시글"""
    post_id: str
    user_id: str
    username: str
    content: str
    images: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    category: str = 'general'  # 'general', 'esg', 'product', 'question'
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    is_pinned: bool = False
    is_reported: bool = False
    status: str = 'active'  # 'active', 'hidden', 'deleted'

    def to_dict(self):
        return asdict(self)


@dataclass
class Comment:
    """댓글"""
    comment_id: str
    post_id: str
    user_id: str
    username: str
    content: str
    parent_comment_id: Optional[str] = None  # 대댓글용
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    likes_count: int = 0
    is_reported: bool = False
    status: str = 'active'  # 'active', 'hidden', 'deleted'

    def to_dict(self):
        return asdict(self)


@dataclass
class Like:
    """좋아요"""
    like_id: str
    user_id: str
    target_type: str  # 'post', 'comment'
    target_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)


@dataclass
class ChatMessage:
    """실시간 채팅 메시지"""
    message_id: str
    room_id: str
    user_id: str
    username: str
    content: str
    message_type: str = 'text'  # 'text', 'image', 'file', 'system'
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_read: bool = False

    def to_dict(self):
        return asdict(self)


@dataclass
class ChatRoom:
    """채팅방"""
    room_id: str
    room_name: str
    room_type: str = 'public'  # 'public', 'private', 'group'
    members: List[str] = field(default_factory=list)
    created_by: str = ''
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_message_at: Optional[str] = None
    is_active: bool = True

    def to_dict(self):
        return asdict(self)


@dataclass
class Report:
    """신고"""
    report_id: str
    reporter_id: str
    target_type: str  # 'post', 'comment', 'user'
    target_id: str
    reason: str
    description: Optional[str] = None
    status: str = 'pending'  # 'pending', 'reviewed', 'resolved', 'rejected'
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    action_taken: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class CommunityManager:
    """커뮤니티 데이터 관리자"""

    def __init__(self):
        # 데이터 저장소 (실제 환경에서는 데이터베이스 사용)
        self.users: Dict[str, User] = {}
        self.posts: Dict[str, Post] = {}
        self.comments: Dict[str, Comment] = {}
        self.likes: Dict[str, Like] = {}
        self.chat_messages: Dict[str, List[ChatMessage]] = {}
        self.chat_rooms: Dict[str, ChatRoom] = {}
        self.reports: Dict[str, Report] = {}

        # 인덱스 (빠른 조회용)
        self.user_posts: Dict[str, List[str]] = {}  # user_id -> [post_ids]
        self.post_comments: Dict[str, List[str]] = {}  # post_id -> [comment_ids]
        self.user_likes: Dict[str, List[str]] = {}  # user_id -> [like_ids]

    # =========================================================================
    # 사용자 관리
    # =========================================================================

    def create_user(self, user_id: str, username: str, email: str, role: str, **kwargs) -> User:
        """사용자 생성"""
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            **kwargs
        )
        self.users[user_id] = user
        self.user_posts[user_id] = []
        self.user_likes[user_id] = []
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """사용자 조회"""
        return self.users.get(user_id)

    def update_user(self, user_id: str, **kwargs) -> bool:
        """사용자 정보 업데이트"""
        user = self.users.get(user_id)
        if not user:
            return False

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return True

    # =========================================================================
    # 게시글 관리
    # =========================================================================

    def create_post(self, user_id: str, username: str, content: str, **kwargs) -> Post:
        """게시글 생성"""
        post_id = f"POST_{uuid.uuid4().hex[:12].upper()}"

        post = Post(
            post_id=post_id,
            user_id=user_id,
            username=username,
            content=content,
            **kwargs
        )

        self.posts[post_id] = post
        self.post_comments[post_id] = []

        if user_id not in self.user_posts:
            self.user_posts[user_id] = []
        self.user_posts[user_id].append(post_id)

        return post

    def get_post(self, post_id: str) -> Optional[Post]:
        """게시글 조회"""
        post = self.posts.get(post_id)
        if post:
            # 조회수 증가
            post.views_count += 1
        return post

    def get_all_posts(self, category: Optional[str] = None,
                     status: str = 'active',
                     limit: int = 50,
                     offset: int = 0) -> List[Post]:
        """게시글 목록 조회"""
        posts = list(self.posts.values())

        # 필터링
        if category:
            posts = [p for p in posts if p.category == category]
        if status:
            posts = [p for p in posts if p.status == status]

        # 정렬 (최신순, 고정된 글 우선)
        posts.sort(key=lambda p: (not p.is_pinned, p.created_at), reverse=True)

        # 페이지네이션
        return posts[offset:offset + limit]

    def update_post(self, post_id: str, **kwargs) -> bool:
        """게시글 업데이트"""
        post = self.posts.get(post_id)
        if not post:
            return False

        for key, value in kwargs.items():
            if hasattr(post, key):
                setattr(post, key, value)

        post.updated_at = datetime.now().isoformat()
        return True

    def delete_post(self, post_id: str) -> bool:
        """게시글 삭제 (소프트 삭제)"""
        post = self.posts.get(post_id)
        if not post:
            return False

        post.status = 'deleted'
        return True

    # =========================================================================
    # 댓글 관리
    # =========================================================================

    def create_comment(self, post_id: str, user_id: str, username: str,
                      content: str, parent_comment_id: Optional[str] = None) -> Optional[Comment]:
        """댓글 생성"""
        if post_id not in self.posts:
            return None

        comment_id = f"COMMENT_{uuid.uuid4().hex[:12].upper()}"

        comment = Comment(
            comment_id=comment_id,
            post_id=post_id,
            user_id=user_id,
            username=username,
            content=content,
            parent_comment_id=parent_comment_id
        )

        self.comments[comment_id] = comment

        if post_id not in self.post_comments:
            self.post_comments[post_id] = []
        self.post_comments[post_id].append(comment_id)

        # 게시글 댓글 수 증가
        self.posts[post_id].comments_count += 1

        return comment

    def get_post_comments(self, post_id: str) -> List[Comment]:
        """게시글의 댓글 목록 조회"""
        comment_ids = self.post_comments.get(post_id, [])
        comments = [self.comments[cid] for cid in comment_ids if cid in self.comments]

        # 상태가 active인 것만 반환
        comments = [c for c in comments if c.status == 'active']

        # 시간순 정렬
        comments.sort(key=lambda c: c.created_at)
        return comments

    def delete_comment(self, comment_id: str) -> bool:
        """댓글 삭제 (소프트 삭제)"""
        comment = self.comments.get(comment_id)
        if not comment:
            return False

        comment.status = 'deleted'

        # 게시글 댓글 수 감소
        post = self.posts.get(comment.post_id)
        if post:
            post.comments_count = max(0, post.comments_count - 1)

        return True

    # =========================================================================
    # 좋아요 관리
    # =========================================================================

    def add_like(self, user_id: str, target_type: str, target_id: str) -> Optional[Like]:
        """좋아요 추가"""
        # 중복 체크
        existing_likes = [
            like for like in self.likes.values()
            if like.user_id == user_id and like.target_type == target_type and like.target_id == target_id
        ]

        if existing_likes:
            return None  # 이미 좋아요 했음

        like_id = f"LIKE_{uuid.uuid4().hex[:12].upper()}"

        like = Like(
            like_id=like_id,
            user_id=user_id,
            target_type=target_type,
            target_id=target_id
        )

        self.likes[like_id] = like

        if user_id not in self.user_likes:
            self.user_likes[user_id] = []
        self.user_likes[user_id].append(like_id)

        # 타겟의 좋아요 수 증가
        if target_type == 'post' and target_id in self.posts:
            self.posts[target_id].likes_count += 1
        elif target_type == 'comment' and target_id in self.comments:
            self.comments[target_id].likes_count += 1

        return like

    def remove_like(self, user_id: str, target_type: str, target_id: str) -> bool:
        """좋아요 취소"""
        like_to_remove = None

        for like in self.likes.values():
            if (like.user_id == user_id and
                like.target_type == target_type and
                like.target_id == target_id):
                like_to_remove = like
                break

        if not like_to_remove:
            return False

        # 좋아요 삭제
        del self.likes[like_to_remove.like_id]

        if user_id in self.user_likes:
            self.user_likes[user_id] = [
                lid for lid in self.user_likes[user_id]
                if lid != like_to_remove.like_id
            ]

        # 타겟의 좋아요 수 감소
        if target_type == 'post' and target_id in self.posts:
            self.posts[target_id].likes_count = max(0, self.posts[target_id].likes_count - 1)
        elif target_type == 'comment' and target_id in self.comments:
            self.comments[target_id].likes_count = max(0, self.comments[target_id].likes_count - 1)

        return True

    def check_user_liked(self, user_id: str, target_type: str, target_id: str) -> bool:
        """사용자가 좋아요 했는지 확인"""
        for like in self.likes.values():
            if (like.user_id == user_id and
                like.target_type == target_type and
                like.target_id == target_id):
                return True
        return False

    # =========================================================================
    # 채팅방 관리
    # =========================================================================

    def create_chat_room(self, room_name: str, created_by: str,
                        room_type: str = 'public', members: List[str] = None) -> ChatRoom:
        """채팅방 생성"""
        room_id = f"ROOM_{uuid.uuid4().hex[:12].upper()}"

        room = ChatRoom(
            room_id=room_id,
            room_name=room_name,
            room_type=room_type,
            created_by=created_by,
            members=members or []
        )

        self.chat_rooms[room_id] = room
        self.chat_messages[room_id] = []

        return room

    def get_chat_room(self, room_id: str) -> Optional[ChatRoom]:
        """채팅방 조회"""
        return self.chat_rooms.get(room_id)

    def get_all_chat_rooms(self, user_id: Optional[str] = None) -> List[ChatRoom]:
        """채팅방 목록 조회"""
        rooms = list(self.chat_rooms.values())

        # 사용자별 필터링 (사용자가 속한 방만)
        if user_id:
            rooms = [r for r in rooms if r.room_type == 'public' or user_id in r.members]

        # 최근 메시지 시간순 정렬
        rooms.sort(key=lambda r: r.last_message_at or r.created_at, reverse=True)

        return rooms

    # =========================================================================
    # 채팅 메시지 관리
    # =========================================================================

    def send_message(self, room_id: str, user_id: str, username: str,
                    content: str, message_type: str = 'text') -> Optional[ChatMessage]:
        """메시지 전송"""
        if room_id not in self.chat_rooms:
            return None

        message_id = f"MSG_{uuid.uuid4().hex[:12].upper()}"

        message = ChatMessage(
            message_id=message_id,
            room_id=room_id,
            user_id=user_id,
            username=username,
            content=content,
            message_type=message_type
        )

        if room_id not in self.chat_messages:
            self.chat_messages[room_id] = []
        self.chat_messages[room_id].append(message)

        # 채팅방의 마지막 메시지 시간 업데이트
        self.chat_rooms[room_id].last_message_at = message.created_at

        return message

    def get_room_messages(self, room_id: str, limit: int = 100) -> List[ChatMessage]:
        """채팅방 메시지 조회"""
        messages = self.chat_messages.get(room_id, [])

        # 최신 메시지부터 limit개 반환
        return messages[-limit:]

    # =========================================================================
    # 신고 관리
    # =========================================================================

    def create_report(self, reporter_id: str, target_type: str, target_id: str,
                     reason: str, description: Optional[str] = None) -> Report:
        """신고 생성"""
        report_id = f"REPORT_{uuid.uuid4().hex[:12].upper()}"

        report = Report(
            report_id=report_id,
            reporter_id=reporter_id,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            description=description
        )

        self.reports[report_id] = report

        # 타겟을 신고됨으로 표시
        if target_type == 'post' and target_id in self.posts:
            self.posts[target_id].is_reported = True
        elif target_type == 'comment' and target_id in self.comments:
            self.comments[target_id].is_reported = True

        return report

    def get_pending_reports(self) -> List[Report]:
        """처리 대기 중인 신고 조회"""
        reports = [r for r in self.reports.values() if r.status == 'pending']
        reports.sort(key=lambda r: r.created_at)
        return reports

    def resolve_report(self, report_id: str, resolved_by: str,
                      action_taken: str, new_status: str = 'resolved') -> bool:
        """신고 처리"""
        report = self.reports.get(report_id)
        if not report:
            return False

        report.status = new_status
        report.resolved_at = datetime.now().isoformat()
        report.resolved_by = resolved_by
        report.action_taken = action_taken

        return True

    # =========================================================================
    # 통계
    # =========================================================================

    def get_statistics(self) -> Dict:
        """커뮤니티 통계"""
        active_posts = [p for p in self.posts.values() if p.status == 'active']
        active_users = [u for u in self.users.values() if u.is_active]
        pending_reports = [r for r in self.reports.values() if r.status == 'pending']

        # 24시간 내 반응 계산
        recent_posts = [p for p in active_posts
                       if (datetime.now() - datetime.fromisoformat(p.created_at)).days < 1]
        posts_with_reactions = [p for p in recent_posts
                               if p.likes_count > 0 or p.comments_count > 0]

        reaction_rate = (len(posts_with_reactions) / len(recent_posts) * 100) if recent_posts else 0

        return {
            'total_users': len(self.users),
            'active_users': len(active_users),
            'total_posts': len(active_posts),
            'total_comments': len([c for c in self.comments.values() if c.status == 'active']),
            'total_likes': len(self.likes),
            'active_chat_rooms': len([r for r in self.chat_rooms.values() if r.is_active]),
            'pending_reports': len(pending_reports),
            'reaction_rate_24h': round(reaction_rate, 2),
            'report_rate': round(len(pending_reports) / max(len(active_posts), 1) * 100, 2)
        }
