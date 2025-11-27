#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공유 인증 토큰 저장소
여러 Flask 앱 간 토큰을 공유하기 위한 모듈
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 전역 토큰 저장소 (데모용 - 실제로는 Redis 사용 권장)
SHARED_TOKEN_STORE = {}


def register_token(token: str, user_id: int, email: str, role: str):
    """토큰 등록"""
    SHARED_TOKEN_STORE[token] = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'created_at': datetime.now().isoformat()
    }
    logger.info(f"[SHARED_AUTH] Token registered: {email} (role: {role})")


def revoke_token(token: str):
    """토큰 무효화"""
    if token in SHARED_TOKEN_STORE:
        user_info = SHARED_TOKEN_STORE[token]
        del SHARED_TOKEN_STORE[token]
        logger.info(f"[SHARED_AUTH] Token revoked: {user_info.get('email')}")


def validate_token(token: str) -> dict:
    """
    토큰 유효성 검증
    Returns: 사용자 정보 dict 또는 None
    """
    if not token:
        return None

    # Bearer 토큰 형식 처리
    if token.startswith('Bearer '):
        token = token[7:]

    # 활성 토큰 확인
    token_data = SHARED_TOKEN_STORE.get(token)
    if not token_data:
        return None

    return token_data


def get_token_store():
    """토큰 저장소 참조 반환"""
    return SHARED_TOKEN_STORE


def get_active_tokens_count():
    """활성 토큰 개수"""
    return len(SHARED_TOKEN_STORE)
