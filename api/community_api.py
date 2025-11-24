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


def get_community_manager():
    """Get or create community manager instance"""
    global community_manager
    if community_manager is None:
        community_manager = CommunityManager()
        # 초기 데이터 생성
        _initialize_sample_data()
    return community_manager


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
