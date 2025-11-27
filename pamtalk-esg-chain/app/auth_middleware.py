#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK ESG Chain Authentication and Authorization Middleware
인증 및 권한 관리 미들웨어
"""

import logging
import sys
import os
from functools import wraps
from flask import request, jsonify
from datetime import datetime

# shared_auth 모듈 import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import shared_auth

logger = logging.getLogger(__name__)


def register_token(token: str, user_id: int, email: str, role: str):
    """토큰 등록"""
    shared_auth.register_token(token, user_id, email, role)


def validate_token(token: str) -> dict:
    """
    토큰 유효성 검증
    Returns: 사용자 정보 dict 또는 None
    """
    return shared_auth.validate_token(token)


def get_current_user():
    """현재 요청의 사용자 정보 가져오기"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    return validate_token(auth_header)


def require_auth(f):
    """
    인증 필수 데코레이터
    로그인된 사용자만 접근 가능
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'message': '인증이 필요합니다. 로그인 후 다시 시도하세요.'
            }), 401

        user = validate_token(auth_header)
        if not user:
            logger.warning(f"Invalid token for {request.path}")
            return jsonify({
                'success': False,
                'error': 'Invalid token',
                'message': '유효하지 않거나 만료된 토큰입니다.'
            }), 401

        # 요청 객체에 사용자 정보 추가
        request.current_user = user
        logger.info(f"Authenticated request: {user['email']} -> {request.path}")

        return f(*args, **kwargs)

    return decorated_function


def require_role(*allowed_roles):
    """
    역할 기반 접근 제어 데코레이터
    지정된 역할을 가진 사용자만 접근 가능

    Usage:
        @require_role('ADMIN')
        @require_role('ADMIN', 'COMMITTEE')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                logger.warning(f"Unauthorized access attempt to {request.path}")
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'message': '인증이 필요합니다. 로그인 후 다시 시도하세요.'
                }), 401

            user = validate_token(auth_header)
            if not user:
                logger.warning(f"Invalid token for {request.path}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid token',
                    'message': '유효하지 않거나 만료된 토큰입니다.'
                }), 401

            # 역할 확인
            user_role = user.get('role', '').upper()
            if user_role not in [role.upper() for role in allowed_roles]:
                logger.warning(
                    f"Access denied for {user['email']} (role: {user_role}) "
                    f"to {request.path} (required: {allowed_roles})"
                )
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': f'접근 권한이 없습니다. 필요한 권한: {", ".join(allowed_roles)}',
                    'user_role': user_role,
                    'required_roles': list(allowed_roles)
                }), 403

            # 요청 객체에 사용자 정보 추가
            request.current_user = user
            logger.info(
                f"Authorized request: {user['email']} ({user_role}) -> {request.path}"
            )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_admin(f):
    """관리자 전용 데코레이터 (간편 버전)"""
    return require_role('ADMIN')(f)


def require_admin_or_committee(f):
    """관리자 또는 위원회 전용 데코레이터 (간편 버전)"""
    return require_role('ADMIN', 'COMMITTEE')(f)


# 로깅 헬퍼
def log_security_event(event_type: str, user_email: str = None, details: str = ""):
    """보안 이벤트 로깅"""
    logger.warning(
        f"[SECURITY] {event_type} | User: {user_email or 'Unknown'} | {details}"
    )
