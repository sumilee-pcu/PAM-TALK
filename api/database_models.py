#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Models for PAM Community
SQLAlchemy ORM models
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Table, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """사용자 테이블"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    role = Column(String(50), nullable=False)  # 'consumer', 'supplier', 'admin'
    profile_image = Column(String(500))
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)
    reputation_score = Column(Integer, default=0)

    # Relationships
    posts = relationship('Post', back_populates='author', cascade='all, delete-orphan')
    comments = relationship('Comment', back_populates='author', cascade='all, delete-orphan')
    likes = relationship('Like', back_populates='user', cascade='all, delete-orphan')
    reports_made = relationship('Report', foreign_keys='Report.reporter_id', back_populates='reporter', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'profile_image': self.profile_image,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'reputation_score': self.reputation_score
        }


class Post(Base):
    """게시글 테이블"""
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(100), ForeignKey('users.user_id'), nullable=False)
    username = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    images = Column(JSON, default=list)  # List of image URLs
    tags = Column(JSON, default=list)  # List of tags
    category = Column(String(50), default='general', index=True)  # 'general', 'esg', 'product', 'question'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_reported = Column(Boolean, default=False)
    status = Column(String(20), default='active')  # 'active', 'hidden', 'deleted'

    # Relationships
    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post', cascade='all, delete-orphan')
    likes = relationship('Like', back_populates='post', cascade='all, delete-orphan')
    reports = relationship('Report', foreign_keys='Report.target_id', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'post_id': self.post_id,
            'user_id': self.user_id,
            'username': self.username,
            'content': self.content,
            'images': self.images or [],
            'tags': self.tags or [],
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'views_count': self.views_count,
            'is_pinned': self.is_pinned,
            'is_reported': self.is_reported,
            'status': self.status
        }


class Comment(Base):
    """댓글 테이블"""
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(String(100), unique=True, nullable=False, index=True)
    post_id = Column(String(100), ForeignKey('posts.post_id'), nullable=False, index=True)
    user_id = Column(String(100), ForeignKey('users.user_id'), nullable=False)
    username = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    parent_comment_id = Column(String(100), ForeignKey('comments.comment_id'))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    likes_count = Column(Integer, default=0)
    is_reported = Column(Boolean, default=False)
    status = Column(String(20), default='active')  # 'active', 'hidden', 'deleted'

    # Relationships
    author = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')
    parent = relationship('Comment', remote_side=[comment_id], backref='replies')
    likes = relationship('Like', back_populates='comment', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'comment_id': self.comment_id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'username': self.username,
            'content': self.content,
            'parent_comment_id': self.parent_comment_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'likes_count': self.likes_count,
            'is_reported': self.is_reported,
            'status': self.status
        }


class Like(Base):
    """좋아요 테이블"""
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    like_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(100), ForeignKey('users.user_id'), nullable=False)
    target_type = Column(String(20), nullable=False)  # 'post', 'comment'
    target_id = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='likes')
    post = relationship('Post', foreign_keys=[target_id], primaryjoin='and_(Like.target_id==Post.post_id, Like.target_type=="post")', back_populates='likes', uselist=False)
    comment = relationship('Comment', foreign_keys=[target_id], primaryjoin='and_(Like.target_id==Comment.comment_id, Like.target_type=="comment")', back_populates='likes', uselist=False)

    def to_dict(self):
        return {
            'like_id': self.like_id,
            'user_id': self.user_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ChatRoom(Base):
    """채팅방 테이블"""
    __tablename__ = 'chat_rooms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(100), unique=True, nullable=False, index=True)
    room_name = Column(String(200), nullable=False)
    room_type = Column(String(20), default='public')  # 'public', 'private', 'group'
    members = Column(JSON, default=list)  # List of user_ids
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_message_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    messages = relationship('ChatMessage', back_populates='room', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'room_name': self.room_name,
            'room_type': self.room_type,
            'members': self.members or [],
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'is_active': self.is_active
        }


class ChatMessage(Base):
    """채팅 메시지 테이블"""
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(100), unique=True, nullable=False, index=True)
    room_id = Column(String(100), ForeignKey('chat_rooms.room_id'), nullable=False, index=True)
    user_id = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default='text')  # 'text', 'image', 'file', 'system'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_read = Column(Boolean, default=False)

    # Relationships
    room = relationship('ChatRoom', back_populates='messages')

    def to_dict(self):
        return {
            'message_id': self.message_id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'username': self.username,
            'content': self.content,
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_read': self.is_read
        }


class Report(Base):
    """신고 테이블"""
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    reporter_id = Column(String(100), ForeignKey('users.user_id'), nullable=False)
    target_type = Column(String(20), nullable=False)  # 'post', 'comment', 'user'
    target_id = Column(String(100), nullable=False, index=True)
    reason = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='pending', index=True)  # 'pending', 'reviewed', 'resolved', 'rejected'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    action_taken = Column(Text)

    # Relationships
    reporter = relationship('User', foreign_keys=[reporter_id], back_populates='reports_made')

    def to_dict(self):
        return {
            'report_id': self.report_id,
            'reporter_id': self.reporter_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'action_taken': self.action_taken
        }


# Database connection and session management
class Database:
    """데이터베이스 연결 및 세션 관리"""

    def __init__(self, database_url='sqlite:///pam_community.db'):
        """
        Initialize database connection

        Args:
            database_url: SQLAlchemy database URL
                         - SQLite: 'sqlite:///pam_community.db'
                         - PostgreSQL: 'postgresql://user:password@localhost/dbname'
        """
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True,  # Verify connections before using
            json_serializer=lambda obj: obj  # Handle JSON serialization
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()


# Global database instance
db = None


def init_database(database_url='sqlite:///pam_community.db'):
    """Initialize the global database instance"""
    global db
    db = Database(database_url)
    db.create_tables()
    return db


def get_db():
    """Get the global database instance"""
    global db
    if db is None:
        db = init_database()
    return db
