#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM Community REST API
커뮤니티 기능 API
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.community_manager import CommunityManager
from api.coupon_manager import CouponManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = 'pam-community-secret-key'

# Enable CORS
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Socket.IO for real-time chat
socketio = SocketIO(app, cors_allowed_origins="*")

# Global community manager instance
community_manager = None
coupon_manager = None


def get_community_manager():
    """Get or create community manager instance"""
    global community_manager
    if community_manager is None:
        community_manager = CommunityManager()
        # 초기 데이터 생성
        _initialize_sample_data()
    return community_manager


def get_coupon_manager():
    """Get or create coupon manager instance"""
    global coupon_manager
    if coupon_manager is None:
        coupon_manager = CouponManager()
    return coupon_manager


def _initialize_sample_data():
    """샘플 데이터 초기화"""
    manager = community_manager

    # 샘플 사용자
    try:
        manager.create_user('USER_001', 'eco_farmer', 'farmer@pam.com', 'supplier',
                          bio='친환경 농산물을 생산하는 농부입니다', reputation_score=95)
        manager.create_user('USER_002', 'green_consumer', 'consumer@pam.com', 'consumer',
                          bio='환경을 생각하는 소비자', reputation_score=80)
        manager.create_user('USER_003', 'admin', 'admin@pam.com', 'admin',
                          bio='PAM MALL 관리자', reputation_score=100)
    except ValueError:
        pass  # Already initialized

    # 샘플 채팅방
    if not manager.chat_rooms:
        manager.create_chat_room('전체 커뮤니티', 'USER_003', 'public')
        manager.create_chat_room('ESG 활동 공유', 'USER_001', 'public')


def create_error_response(message: str, status_code: int = 400, details: dict = None):
    """Create standardized error response"""
    response = {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
    }
    if details:
        response["error"]["details"] = details
    return response


def create_success_response(data: any, message: str = None):
    """Create standardized success response"""
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    if message:
        response["message"] = message
    return response


# =============================================================================
# 사용자 관리 엔드포인트
# =============================================================================

@app.route('/api/community/users', methods=['POST'])
def create_user():
    """사용자 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        required_fields = ['user_id', 'username', 'email', 'role']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_community_manager()

        user = manager.create_user(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            role=data['role'],
            profile_image=data.get('profile_image'),
            bio=data.get('bio')
        )

        return jsonify(create_success_response(user.to_dict(), "사용자가 생성되었습니다")), 201

    except ValueError as e:
        return jsonify(create_error_response(str(e))), 400
    except Exception as e:
        logger.error(f"Create user error: {e}")
        return jsonify(create_error_response(f"사용자 생성 실패: {str(e)}")), 500


@app.route('/api/community/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    """사용자 조회"""
    try:
        manager = get_community_manager()
        user = manager.get_user(user_id)

        if not user:
            return jsonify(create_error_response("사용자를 찾을 수 없습니다")), 404

        return jsonify(create_success_response(user.to_dict()))

    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify(create_error_response(f"사용자 조회 실패: {str(e)}")), 500


# =============================================================================
# 게시글 관리 엔드포인트
# =============================================================================

@app.route('/api/community/posts', methods=['GET'])
def get_posts():
    """게시글 목록 조회"""
    try:
        manager = get_community_manager()

        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        posts = manager.get_all_posts(category=category, limit=limit, offset=offset)
        posts_data = [p.to_dict() for p in posts]

        return jsonify(create_success_response(posts_data))

    except Exception as e:
        logger.error(f"Get posts error: {e}")
        return jsonify(create_error_response(f"게시글 조회 실패: {str(e)}")), 500


@app.route('/api/community/posts/<string:post_id>', methods=['GET'])
def get_post(post_id):
    """특정 게시글 조회"""
    try:
        manager = get_community_manager()
        post = manager.get_post(post_id)

        if not post:
            return jsonify(create_error_response("게시글을 찾을 수 없습니다")), 404

        # 댓글도 함께 반환
        comments = manager.get_post_comments(post_id)
        comments_data = [c.to_dict() for c in comments]

        response_data = post.to_dict()
        response_data['comments'] = comments_data

        return jsonify(create_success_response(response_data))

    except Exception as e:
        logger.error(f"Get post error: {e}")
        return jsonify(create_error_response(f"게시글 조회 실패: {str(e)}")), 500


@app.route('/api/community/posts', methods=['POST'])
def create_post():
    """게시글 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        required_fields = ['user_id', 'username', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_community_manager()

        post = manager.create_post(
            user_id=data['user_id'],
            username=data['username'],
            content=data['content'],
            images=data.get('images', []),
            tags=data.get('tags', []),
            category=data.get('category', 'general')
        )

        return jsonify(create_success_response(post.to_dict(), "게시글이 생성되었습니다")), 201

    except Exception as e:
        logger.error(f"Create post error: {e}")
        return jsonify(create_error_response(f"게시글 생성 실패: {str(e)}")), 500


@app.route('/api/community/posts/<string:post_id>', methods=['PUT'])
def update_post(post_id):
    """게시글 수정"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        manager = get_community_manager()
        success = manager.update_post(post_id, **data)

        if success:
            post = manager.get_post(post_id)
            return jsonify(create_success_response(post.to_dict(), "게시글이 수정되었습니다"))
        else:
            return jsonify(create_error_response("게시글을 찾을 수 없습니다")), 404

    except Exception as e:
        logger.error(f"Update post error: {e}")
        return jsonify(create_error_response(f"게시글 수정 실패: {str(e)}")), 500


@app.route('/api/community/posts/<string:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """게시글 삭제"""
    try:
        manager = get_community_manager()
        success = manager.delete_post(post_id)

        if success:
            return jsonify(create_success_response(
                {"post_id": post_id}, "게시글이 삭제되었습니다"
            ))
        else:
            return jsonify(create_error_response("게시글을 찾을 수 없습니다")), 404

    except Exception as e:
        logger.error(f"Delete post error: {e}")
        return jsonify(create_error_response(f"게시글 삭제 실패: {str(e)}")), 500


# =============================================================================
# 댓글 관리 엔드포인트
# =============================================================================

@app.route('/api/community/posts/<string:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    """댓글 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        required_fields = ['user_id', 'username', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_community_manager()

        comment = manager.create_comment(
            post_id=post_id,
            user_id=data['user_id'],
            username=data['username'],
            content=data['content'],
            parent_comment_id=data.get('parent_comment_id')
        )

        if comment:
            return jsonify(create_success_response(comment.to_dict(), "댓글이 생성되었습니다")), 201
        else:
            return jsonify(create_error_response("게시글을 찾을 수 없습니다")), 404

    except Exception as e:
        logger.error(f"Create comment error: {e}")
        return jsonify(create_error_response(f"댓글 생성 실패: {str(e)}")), 500


@app.route('/api/community/posts/<string:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """게시글의 댓글 목록 조회"""
    try:
        manager = get_community_manager()
        comments = manager.get_post_comments(post_id)
        comments_data = [c.to_dict() for c in comments]

        return jsonify(create_success_response(comments_data))

    except Exception as e:
        logger.error(f"Get comments error: {e}")
        return jsonify(create_error_response(f"댓글 조회 실패: {str(e)}")), 500


@app.route('/api/community/comments/<string:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """댓글 삭제"""
    try:
        manager = get_community_manager()
        success = manager.delete_comment(comment_id)

        if success:
            return jsonify(create_success_response(
                {"comment_id": comment_id}, "댓글이 삭제되었습니다"
            ))
        else:
            return jsonify(create_error_response("댓글을 찾을 수 없습니다")), 404

    except Exception as e:
        logger.error(f"Delete comment error: {e}")
        return jsonify(create_error_response(f"댓글 삭제 실패: {str(e)}")), 500


# =============================================================================
# 좋아요 관리 엔드포인트
# =============================================================================

@app.route('/api/community/likes', methods=['POST'])
def add_like():
    """좋아요 추가"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        required_fields = ['user_id', 'target_type', 'target_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_community_manager()

        like = manager.add_like(
            user_id=data['user_id'],
            target_type=data['target_type'],
            target_id=data['target_id']
        )

        if like:
            return jsonify(create_success_response(like.to_dict(), "좋아요가 추가되었습니다")), 201
        else:
            return jsonify(create_error_response("이미 좋아요를 했습니다")), 400

    except Exception as e:
        logger.error(f"Add like error: {e}")
        return jsonify(create_error_response(f"좋아요 추가 실패: {str(e)}")), 500


@app.route('/api/community/likes', methods=['DELETE'])
def remove_like():
    """좋아요 취소"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        required_fields = ['user_id', 'target_type', 'target_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_community_manager()

        success = manager.remove_like(
            user_id=data['user_id'],
            target_type=data['target_type'],
            target_id=data['target_id']
        )

        if success:
            return jsonify(create_success_response({}, "좋아요가 취소되었습니다"))
        else:
            return jsonify(create_error_response("좋아요를 찾을 수 없습니다")), 404

    except Exception as e:
        logger.error(f"Remove like error: {e}")
        return jsonify(create_error_response(f"좋아요 취소 실패: {str(e)}")), 500


@app.route('/api/community/likes/check', methods=['POST'])
def check_like():
    """좋아요 여부 확인"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        manager = get_community_manager()

        liked = manager.check_user_liked(
            user_id=data['user_id'],
            target_type=data['target_type'],
            target_id=data['target_id']
        )

        return jsonify(create_success_response({"liked": liked}))

    except Exception as e:
        logger.error(f"Check like error: {e}")
        return jsonify(create_error_response(f"좋아요 확인 실패: {str(e)}")), 500


# =============================================================================
# 채팅방 관리 엔드포인트
# =============================================================================

@app.route('/api/community/chat/rooms', methods=['GET'])
def get_chat_rooms():
    """채팅방 목록 조회"""
    try:
        manager = get_community_manager()
        user_id = request.args.get('user_id')

        rooms = manager.get_all_chat_rooms(user_id)
        rooms_data = [r.to_dict() for r in rooms]

        return jsonify(create_success_response(rooms_data))

    except Exception as e:
        logger.error(f"Get chat rooms error: {e}")
        return jsonify(create_error_response(f"채팅방 조회 실패: {str(e)}")), 500


@app.route('/api/community/chat/rooms', methods=['POST'])
def create_chat_room():
    """채팅방 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        required_fields = ['room_name', 'created_by']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_community_manager()

        room = manager.create_chat_room(
            room_name=data['room_name'],
            created_by=data['created_by'],
            room_type=data.get('room_type', 'public'),
            members=data.get('members', [])
        )

        return jsonify(create_success_response(room.to_dict(), "채팅방이 생성되었습니다")), 201

    except Exception as e:
        logger.error(f"Create chat room error: {e}")
        return jsonify(create_error_response(f"채팅방 생성 실패: {str(e)}")), 500


@app.route('/api/community/chat/rooms/<string:room_id>/messages', methods=['GET'])
def get_chat_messages(room_id):
    """채팅방 메시지 조회"""
    try:
        manager = get_community_manager()
        limit = int(request.args.get('limit', 100))

        messages = manager.get_room_messages(room_id, limit)
        messages_data = [m.to_dict() for m in messages]

        return jsonify(create_success_response(messages_data))

    except Exception as e:
        logger.error(f"Get chat messages error: {e}")
        return jsonify(create_error_response(f"메시지 조회 실패: {str(e)}")), 500


@app.route('/api/community/chat/private', methods=['POST'])
def get_or_create_private_chat():
    """1:1 채팅방 가져오기 또는 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        required_fields = ['user1_email', 'user2_email', 'user1_name', 'user2_name']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_community_manager()

        # Generate consistent room ID for 1:1 chat
        users = sorted([data['user1_email'], data['user2_email']])
        room_id = f"private_{users[0]}_{users[1]}".replace('@', '_').replace('.', '_')

        # Check if room exists
        existing_rooms = manager.get_all_chat_rooms()
        room = None
        for r in existing_rooms:
            if r.room_id == room_id:
                room = r
                break

        # Create room if it doesn't exist
        if not room:
            room_name = f"{data['user1_name']} & {data['user2_name']}"
            room = manager.create_chat_room(
                room_name=room_name,
                created_by=data['user1_email'],
                room_type='private',
                members=[data['user1_email'], data['user2_email']]
            )
            # Override room_id to be consistent
            room.room_id = room_id

        # Get messages for this room
        messages = manager.get_room_messages(room_id, limit=100)
        messages_data = [m.to_dict() for m in messages]

        response_data = {
            'room': room.to_dict(),
            'messages': messages_data
        }

        return jsonify(create_success_response(response_data))

    except Exception as e:
        logger.error(f"Get or create private chat error: {e}")
        return jsonify(create_error_response(f"1:1 채팅방 생성 실패: {str(e)}")), 500


# =============================================================================
# 신고 관리 엔드포인트
# =============================================================================

@app.route('/api/community/reports', methods=['POST'])
def create_report():
    """신고 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        required_fields = ['reporter_id', 'target_type', 'target_id', 'reason']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_community_manager()

        report = manager.create_report(
            reporter_id=data['reporter_id'],
            target_type=data['target_type'],
            target_id=data['target_id'],
            reason=data['reason'],
            description=data.get('description')
        )

        return jsonify(create_success_response(report.to_dict(), "신고가 접수되었습니다")), 201

    except Exception as e:
        logger.error(f"Create report error: {e}")
        return jsonify(create_error_response(f"신고 생성 실패: {str(e)}")), 500


@app.route('/api/community/reports/pending', methods=['GET'])
def get_pending_reports():
    """처리 대기 중인 신고 조회"""
    try:
        manager = get_community_manager()
        reports = manager.get_pending_reports()
        reports_data = [r.to_dict() for r in reports]

        return jsonify(create_success_response(reports_data))

    except Exception as e:
        logger.error(f"Get pending reports error: {e}")
        return jsonify(create_error_response(f"신고 조회 실패: {str(e)}")), 500


@app.route('/api/community/reports/<string:report_id>/resolve', methods=['PUT'])
def resolve_report(report_id):
    """신고 처리"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        required_fields = ['resolved_by', 'action_taken']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_community_manager()

        success = manager.resolve_report(
            report_id=report_id,
            resolved_by=data['resolved_by'],
            action_taken=data['action_taken'],
            new_status=data.get('new_status', 'resolved')
        )

        if success:
            return jsonify(create_success_response(
                {"report_id": report_id}, "신고가 처리되었습니다"
            ))
        else:
            return jsonify(create_error_response("신고를 찾을 수 없습니다")), 404

    except Exception as e:
        logger.error(f"Resolve report error: {e}")
        return jsonify(create_error_response(f"신고 처리 실패: {str(e)}")), 500


# =============================================================================
# 통계 엔드포인트
# =============================================================================

@app.route('/api/community/statistics', methods=['GET'])
def get_statistics():
    """커뮤니티 통계"""
    try:
        manager = get_community_manager()
        stats = manager.get_statistics()

        return jsonify(create_success_response(stats))

    except Exception as e:
        logger.error(f"Get statistics error: {e}")
        return jsonify(create_error_response(f"통계 조회 실패: {str(e)}")), 500


# =============================================================================
# WebSocket 이벤트 (실시간 채팅)
# =============================================================================

@socketio.on('join')
def on_join(data):
    """채팅방 입장"""
    room_id = data.get('room_id')
    username = data.get('username')

    if room_id:
        join_room(room_id)
        emit('user_joined', {
            'username': username,
            'message': f'{username}님이 입장했습니다.',
            'timestamp': datetime.now().isoformat()
        }, room=room_id)


@socketio.on('leave')
def on_leave(data):
    """채팅방 퇴장"""
    room_id = data.get('room_id')
    username = data.get('username')

    if room_id:
        leave_room(room_id)
        emit('user_left', {
            'username': username,
            'message': f'{username}님이 퇴장했습니다.',
            'timestamp': datetime.now().isoformat()
        }, room=room_id)


@socketio.on('send_message')
def on_send_message(data):
    """메시지 전송"""
    try:
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        username = data.get('username')
        content = data.get('content')
        message_type = data.get('message_type', 'text')

        manager = get_community_manager()

        message = manager.send_message(
            room_id=room_id,
            user_id=user_id,
            username=username,
            content=content,
            message_type=message_type
        )

        if message:
            emit('new_message', message.to_dict(), room=room_id)
        else:
            emit('error', {'message': '메시지 전송 실패'})

    except Exception as e:
        logger.error(f"Send message error: {e}")
        emit('error', {'message': str(e)})


@socketio.on('typing')
def on_typing(data):
    """타이핑 중 알림"""
    room_id = data.get('room_id')
    username = data.get('username')

    if room_id:
        emit('user_typing', {
            'username': username,
            'timestamp': datetime.now().isoformat()
        }, room=room_id, include_self=False)


# =============================================================================
# Health Check
# =============================================================================

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "name": "PAM Community API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "POST /api/auth/login",
            "POST /api/auth/signup",
            "POST /api/auth/logout",
            "GET /api/auth/me",
            "POST /api/community/users",
            "GET /api/community/users/{id}",
            "GET /api/community/posts",
            "GET /api/community/posts/{id}",
            "POST /api/community/posts",
            "PUT /api/community/posts/{id}",
            "DELETE /api/community/posts/{id}",
            "POST /api/community/posts/{id}/comments",
            "GET /api/community/posts/{id}/comments",
            "DELETE /api/community/comments/{id}",
            "POST /api/community/likes",
            "DELETE /api/community/likes",
            "POST /api/community/likes/check",
            "GET /api/community/chat/rooms",
            "POST /api/community/chat/rooms",
            "GET /api/community/chat/rooms/{id}/messages",
            "POST /api/community/reports",
            "GET /api/community/reports/pending",
            "PUT /api/community/reports/{id}/resolve",
            "GET /api/community/statistics"
        ]
    })


# ========================================
# Authentication Endpoints (데모용)
# ========================================

# 데모 사용자 데이터
DEMO_USERS = {
    'consumer@pamtalk.com': {
        'id': 1,
        'email': 'consumer@pamtalk.com',
        'name': '소비자',
        'role': 'CONSUMER',
        'password': 'Consumer123!'
    },
    'supplier@pamtalk.com': {
        'id': 2,
        'email': 'supplier@pamtalk.com',
        'name': '공급자',
        'role': 'SUPPLIER',
        'password': 'Supplier123!'
    },
    'company@pamtalk.com': {
        'id': 3,
        'email': 'company@pamtalk.com',
        'name': '기업담당자',
        'role': 'COMPANY',
        'password': 'Company123!'
    },
    'farmer@pamtalk.com': {
        'id': 4,
        'email': 'farmer@pamtalk.com',
        'name': '농부',
        'role': 'FARMER',
        'password': 'Farmer123!'
    },
    'committee@pamtalk.com': {
        'id': 5,
        'email': 'committee@pamtalk.com',
        'name': '위원회',
        'role': 'COMMITTEE',
        'password': 'Committee123!'
    },
    'admin@pamtalk.com': {
        'id': 6,
        'email': 'admin@pamtalk.com',
        'name': '관리자',
        'role': 'ADMIN',
        'password': 'Admin123!'
    }
}

@app.route('/api/auth/login', methods=['POST'])
def login():
    """사용자 로그인"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        logger.info(f"Login attempt: {email}")

        if not email or not password:
            return jsonify({'error': '이메일과 비밀번호를 입력하세요.'}), 400

        # 데모 사용자 확인
        user_data = DEMO_USERS.get(email)
        if not user_data:
            logger.warning(f"Unknown email: {email}")
            return jsonify({'error': '등록되지 않은 이메일입니다.'}), 401

        # 비밀번호 확인
        if user_data['password'] != password:
            logger.warning(f"Invalid password for: {email}")
            return jsonify({'error': '비밀번호가 일치하지 않습니다.'}), 401

        # 비밀번호를 제외한 사용자 정보 반환
        user = {
            'id': user_data['id'],
            'email': user_data['email'],
            'name': user_data['name'],
            'role': user_data['role']
        }

        # 토큰 생성 (데모용)
        access_token = f"demo_token_{user['id']}_{datetime.now().timestamp()}"
        refresh_token = f"demo_refresh_{user['id']}_{datetime.now().timestamp()}"

        logger.info(f"Login successful: {email} ({user['role']})")

        return jsonify({
            'user': user,
            'tokens': {
                'accessToken': access_token,
                'refreshToken': refresh_token
            }
        })

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': '로그인 중 오류가 발생했습니다.'}), 500

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """사용자 회원가입"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        role = data.get('role', 'CONSUMER')

        if not name or not email or not password:
            return jsonify({'error': '필수 정보를 입력하세요.'}), 400

        # 이메일 중복 확인
        if email in DEMO_USERS:
            return jsonify({'error': '이미 등록된 이메일입니다.'}), 400

        # 새 사용자 생성 (데모용 - 실제로는 DB에 저장)
        user = {
            'id': len(DEMO_USERS) + 1,
            'email': email,
            'name': name,
            'phone': phone,
            'role': role,
            'createdAt': datetime.now().isoformat()
        }

        # 토큰 생성 (데모용)
        access_token = f"demo_token_{user['id']}_{datetime.now().timestamp()}"
        refresh_token = f"demo_refresh_{user['id']}_{datetime.now().timestamp()}"

        logger.info(f"User registered: {email}")

        return jsonify({
            'user': user,
            'tokens': {
                'accessToken': access_token,
                'refreshToken': refresh_token
            }
        }), 201

    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({'error': '회원가입 중 오류가 발생했습니다.'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """사용자 로그아웃"""
    return jsonify({'message': '로그아웃되었습니다.'})

@app.route('/api/auth/me', methods=['GET'])
def get_profile():
    """사용자 프로필 조회"""
    # 데모용 - 실제로는 토큰에서 사용자 정보를 가져옴
    return jsonify({'error': 'Not implemented'}), 501

# ========================================
# LSTM Demand Prediction
# ========================================

@app.route('/api/lstm/predict', methods=['POST'])
def lstm_predict():
    """LSTM 수요 예측 실행"""
    try:
        data = request.get_json()
        product_name = data.get('product', 'tomatoes')
        days_ahead = data.get('days_ahead', 7)

        # LSTM predictor import
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from ai_models.lstm_demand_predictor import LSTMDemandPredictor
        except ImportError as e:
            logger.error(f"LSTM import error: {e}")
            return jsonify(create_error_response("LSTM 모델을 불러올 수 없습니다.")), 500

        # 예측 실행
        predictor = LSTMDemandPredictor()
        predictions = predictor.predict(product_name, days_ahead=days_ahead)

        # DataFrame을 dict로 변환
        predictions_dict = predictions.to_dict(orient='records')

        return jsonify(create_success_response({
            "product": product_name,
            "days_ahead": days_ahead,
            "predictions": predictions_dict
        }))

    except Exception as e:
        logger.error(f"LSTM prediction error: {e}")
        return jsonify(create_error_response(f"예측 실패: {str(e)}")), 500


@app.route('/api/lstm/train', methods=['POST'])
def lstm_train():
    """LSTM 모델 학습 실행"""
    try:
        data = request.get_json()
        product_name = data.get('product', 'tomatoes')
        epochs = data.get('epochs', 20)
        training_days = data.get('training_days', 90)

        # LSTM predictor import
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from ai_models.lstm_demand_predictor import LSTMDemandPredictor
        except ImportError as e:
            logger.error(f"LSTM import error: {e}")
            return jsonify(create_error_response("LSTM 모델을 불러올 수 없습니다.")), 500

        # 모델 학습
        predictor = LSTMDemandPredictor()
        predictor.config['training_parameters']['epochs'] = epochs
        predictor.config['data_parameters']['training_days'] = training_days

        results = predictor.train(product_name, save_model=True)

        return jsonify(create_success_response({
            "product": product_name,
            "training_results": {
                "test_loss": float(results['test_loss']),
                "test_mae": float(results['test_mae']),
                "test_mape": float(results['test_mape']),
                "epochs_trained": int(results['epochs_trained']),
                "training_time": float(results['training_time'])
            }
        }))

    except Exception as e:
        logger.error(f"LSTM training error: {e}")
        return jsonify(create_error_response(f"학습 실패: {str(e)}")), 500


@app.route('/api/lstm/products', methods=['GET'])
def lstm_products():
    """사용 가능한 제품 목록 조회"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ai_models.lstm_demand_predictor import LSTMDemandPredictor

        predictor = LSTMDemandPredictor()
        products = predictor.config['products']

        product_list = []
        for name, config in products.items():
            product_list.append({
                "name": name,
                "description": config.get('description', ''),
                "base_demand": config.get('base_demand', 0)
            })

        return jsonify(create_success_response({
            "products": product_list
        }))

    except Exception as e:
        logger.error(f"LSTM products error: {e}")
        return jsonify(create_error_response(f"제품 목록 조회 실패: {str(e)}")), 500


# ========================================
# Mall API Endpoints
# ========================================

@app.route('/api/mall/products', methods=['GET'])
def get_mall_products():
    """상품 목록 조회"""
    try:
        manager = get_coupon_manager()
        category = request.args.get('category')

        products = manager.get_all_products(category)
        products_data = [p.to_dict() for p in products]

        return jsonify(create_success_response(products_data))

    except Exception as e:
        logger.error(f"Get products error: {e}")
        return jsonify(create_error_response(f"상품 조회 실패: {str(e)}")), 500


@app.route('/api/mall/products/<string:product_id>', methods=['GET'])
def get_mall_product(product_id):
    """특정 상품 조회"""
    try:
        manager = get_coupon_manager()
        product = manager.get_product(product_id)

        if not product:
            return jsonify(create_error_response("상품을 찾을 수 없습니다")), 404

        return jsonify(create_success_response(product.to_dict()))

    except Exception as e:
        logger.error(f"Get product error: {e}")
        return jsonify(create_error_response(f"상품 조회 실패: {str(e)}")), 500


@app.route('/api/mall/orders', methods=['POST'])
def create_mall_order():
    """주문 생성"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        # 필수 필드 확인
        required_fields = ['user_address', 'items']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        manager = get_coupon_manager()

        result = manager.create_order(
            user_address=data['user_address'],
            items=data['items'],
            coupon_id=data.get('coupon_id'),
            payment_txid=data.get('payment_txid')
        )

        if result['success']:
            return jsonify(create_success_response(
                result['order'], "주문이 생성되었습니다"
            )), 201
        else:
            return jsonify(create_error_response(result.get('error', '주문 생성 실패'))), 400

    except Exception as e:
        logger.error(f"Create order error: {e}")
        return jsonify(create_error_response(f"주문 생성 실패: {str(e)}")), 500


@app.route('/api/mall/health', methods=['GET'])
def mall_health_check():
    """Mall API 헬스 체크"""
    try:
        manager = get_coupon_manager()
        products_count = len(manager.products)

        return jsonify(create_success_response({
            "status": "healthy",
            "total_products": products_count
        }))

    except Exception as e:
        logger.error(f"Mall health check error: {e}")
        return jsonify(create_error_response("서비스 상태 확인 실패")), 500


# ========================================
# Simulation APIs
# ========================================

@app.route('/api/simulation/run', methods=['POST'])
def run_simulation():
    """통합 시뮬레이션 실행"""
    try:
        data = request.get_json()
        population = data.get('population', 100000)

        # 시뮬레이터 import
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from ai_models.integrated_simulator import IntegratedSimulator
        except ImportError as e:
            logger.error(f"Simulator import error: {e}")
            return jsonify(create_error_response("시뮬레이터를 불러올 수 없습니다.")), 500

        # 시뮬레이션 실행
        simulator = IntegratedSimulator(population=population)
        results = simulator.run_full_simulation()

        return jsonify(create_success_response({
            "simulation_results": results
        }))

    except Exception as e:
        logger.error(f"Simulation error: {e}")
        return jsonify(create_error_response(f"시뮬레이션 실패: {str(e)}")), 500


@app.route('/api/simulation/distribution', methods=['POST'])
def run_distribution_simulation():
    """유통 구조 시뮬레이션"""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ai_models.distribution_simulator import DistributionSimulator

        simulator = DistributionSimulator()
        results = simulator.run_simulation()

        return jsonify(create_success_response({
            "distribution_results": results
        }))

    except Exception as e:
        logger.error(f"Distribution simulation error: {e}")
        return jsonify(create_error_response(f"유통 시뮬레이션 실패: {str(e)}")), 500


@app.route('/api/simulation/carbon', methods=['POST'])
def calculate_carbon():
    """탄소 절감 계산"""
    try:
        data = request.get_json()
        population = data.get('population', 100000)

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ai_models.carbon_calculator import CarbonCalculator

        calculator = CarbonCalculator(population=population)
        results = calculator.run_calculation()

        return jsonify(create_success_response({
            "carbon_results": results
        }))

    except Exception as e:
        logger.error(f"Carbon calculation error: {e}")
        return jsonify(create_error_response(f"탄소 계산 실패: {str(e)}")), 500


@app.route('/api/simulation/economic', methods=['POST'])
def analyze_economic():
    """경제 효과 분석"""
    try:
        data = request.get_json()
        population = data.get('population', 100000)

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ai_models.economic_analyzer import EconomicAnalyzer

        analyzer = EconomicAnalyzer(population=population)
        results = analyzer.run_analysis()

        return jsonify(create_success_response({
            "economic_results": results
        }))

    except Exception as e:
        logger.error(f"Economic analysis error: {e}")
        return jsonify(create_error_response(f"경제 분석 실패: {str(e)}")), 500


# ========================================
# Health Check
# ========================================

@app.route('/api/community/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        manager = get_community_manager()
        stats = manager.get_statistics()

        return jsonify(create_success_response({
            "status": "healthy",
            "statistics": stats
        }))

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify(create_error_response("서비스 상태 확인 실패")), 500


if __name__ == '__main__':
    import sys
    import io

    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(">> PAM Community API Server starting...")
    print(">> Server: http://localhost:5002")
    print(">> WebSocket enabled for real-time chat")
    print(">> API Documentation: See endpoints above")

    # Run with SocketIO support
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)
