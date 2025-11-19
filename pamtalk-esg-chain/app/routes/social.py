# -*- coding: utf-8 -*-
"""
SNS/커뮤니티 API 라우트
소셜 피드, 인터랙션, 트렌딩 토픽, 커뮤니티 그룹, 콘텐츠 보상 기능
"""
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from datetime import datetime
import asyncio
import json
import logging

from ..service.social_feed_service import SocialFeedService
from ..service.social_interaction_service import SocialInteractionService
from ..service.social_content_rewards_service import SocialContentRewardsService
from ..service.trending_topics_service import TrendingTopicsService
from ..service.community_groups_service import CommunityGroupsService
from ..utils.auth import verify_jwt_token

social_bp = Blueprint('social', __name__)
logger = logging.getLogger(__name__)

# 서비스 인스턴스 생성
feed_service = SocialFeedService()
interaction_service = SocialInteractionService()
rewards_service = SocialContentRewardsService()
trending_service = TrendingTopicsService()
groups_service = CommunityGroupsService()

def async_route(f):
    """비동기 라우트 데코레이터"""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    wrapper.__name__ = f.__name__
    return wrapper

# ========== 소셜 피드 API ==========

@social_bp.route('/feed/timeline/<user_id>', methods=['GET'])
@cross_origin()
@async_route
async def get_user_timeline(user_id):
    """사용자 타임라인 피드 조회"""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 50)

        posts = await feed_service.get_timeline_feed(user_id, page, limit)

        return jsonify({
            'success': True,
            'data': {
                'posts': posts,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'has_more': len(posts) == limit
                }
            }
        })

    except Exception as e:
        logger.error(f"타임라인 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/feed/discover', methods=['GET'])
@cross_origin()
@async_route
async def get_discover_feed():
    """발견 피드 조회"""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 50)
        region = request.args.get('region')
        category = request.args.get('category')

        posts = await feed_service.get_discover_feed(page, limit, region, category)

        return jsonify({
            'success': True,
            'data': {
                'posts': posts,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'has_more': len(posts) == limit
                }
            }
        })

    except Exception as e:
        logger.error(f"발견 피드 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/feed/carbon', methods=['GET'])
@cross_origin()
@async_route
async def get_carbon_feed():
    """탄소 활동 피드 조회"""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 50)
        activity_type = request.args.get('activity_type')

        posts = await feed_service.get_carbon_activity_feed(page, limit, activity_type)

        return jsonify({
            'success': True,
            'data': {
                'posts': posts,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'has_more': len(posts) == limit
                }
            }
        })

    except Exception as e:
        logger.error(f"탄소 피드 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/posts', methods=['POST'])
@cross_origin()
@async_route
async def create_post():
    """새 포스트 생성"""
    try:
        data = request.get_json()

        # JWT 토큰 확인 (실제 환경에서)
        user_id = data.get('user_id')  # 실제로는 JWT에서 추출

        required_fields = ['user_id', 'content', 'post_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400

        post = await feed_service.create_post(
            user_id=data['user_id'],
            post_type=data['post_type'],
            title=data.get('title'),
            content=data['content'],
            images=data.get('images'),
            video_url=data.get('video_url'),
            location=data.get('location'),
            carbon_activity_id=data.get('carbon_activity_id'),
            hashtags=data.get('hashtags'),
            categories=data.get('categories')
        )

        if post:
            return jsonify({'success': True, 'data': post})
        else:
            return jsonify({'success': False, 'error': 'Failed to create post'}), 500

    except Exception as e:
        logger.error(f"포스트 생성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 소셜 인터랙션 API ==========

@social_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@cross_origin()
@async_route
async def like_post(post_id):
    """포스트 좋아요"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        like_type = data.get('like_type', 'like')

        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400

        success = await interaction_service.like_post(user_id, post_id, like_type)

        return jsonify({'success': success})

    except Exception as e:
        logger.error(f"포스트 좋아요 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/posts/<int:post_id>/unlike', methods=['DELETE'])
@cross_origin()
@async_route
async def unlike_post(post_id):
    """포스트 좋아요 취소"""
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400

        success = await interaction_service.unlike_post(user_id, post_id)

        return jsonify({'success': success})

    except Exception as e:
        logger.error(f"포스트 좋아요 취소 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
@cross_origin()
@async_route
async def get_post_comments(post_id):
    """포스트 댓글 조회"""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 50)

        comments = await interaction_service.get_post_comments(post_id, page, limit)

        return jsonify({
            'success': True,
            'data': {
                'comments': comments,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'has_more': len(comments) == limit
                }
            }
        })

    except Exception as e:
        logger.error(f"댓글 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@cross_origin()
@async_route
async def add_comment(post_id):
    """댓글 추가"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        content = data.get('content')
        parent_comment_id = data.get('parent_comment_id')

        if not user_id or not content:
            return jsonify({'success': False, 'error': 'user_id and content are required'}), 400

        comment = await interaction_service.add_comment(
            user_id, post_id, content, parent_comment_id
        )

        if comment:
            return jsonify({'success': True, 'data': comment})
        else:
            return jsonify({'success': False, 'error': 'Failed to add comment'}), 500

    except Exception as e:
        logger.error(f"댓글 추가 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/posts/<int:post_id>/share', methods=['POST'])
@cross_origin()
@async_route
async def share_post(post_id):
    """포스트 공유"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        share_type = data.get('share_type', 'repost')
        share_comment = data.get('share_comment')

        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400

        success = await interaction_service.share_post(
            user_id, post_id, share_type, share_comment
        )

        return jsonify({'success': success})

    except Exception as e:
        logger.error(f"포스트 공유 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 트렌딩 토픽 API ==========

@social_bp.route('/trending', methods=['GET'])
@cross_origin()
@async_route
async def get_trending_topics():
    """트렌딩 토픽 조회"""
    try:
        region = request.args.get('region')
        time_range = request.args.get('time_range', 'daily')
        limit = min(int(request.args.get('limit', 20)), 50)

        topics = await trending_service.get_trending_topics(region, limit, time_range)

        return jsonify({'success': True, 'data': topics})

    except Exception as e:
        logger.error(f"트렌딩 토픽 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/trending/<hashtag>/posts', methods=['GET'])
@cross_origin()
@async_route
async def get_topic_posts(hashtag):
    """특정 토픽의 포스트들 조회"""
    try:
        region = request.args.get('region')
        limit = min(int(request.args.get('limit', 50)), 100)

        # 해시태그 정규화
        if not hashtag.startswith('#'):
            hashtag = f'#{hashtag}'

        posts = await trending_service.get_topic_posts(hashtag, region, limit)

        return jsonify({'success': True, 'data': posts})

    except Exception as e:
        logger.error(f"토픽 포스트 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/hashtags/recommend/<user_id>', methods=['POST'])
@cross_origin()
@async_route
async def recommend_hashtags(user_id):
    """해시태그 추천"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        limit = min(int(data.get('limit', 10)), 20)

        hashtags = await trending_service.get_recommended_hashtags(user_id, content, limit)

        return jsonify({'success': True, 'data': hashtags})

    except Exception as e:
        logger.error(f"해시태그 추천 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 커뮤니티 그룹 API ==========

@social_bp.route('/groups', methods=['POST'])
@cross_origin()
@async_route
async def create_group():
    """새 그룹 생성"""
    try:
        data = request.get_json()

        required_fields = ['creator_user_id', 'name', 'group_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400

        group = await groups_service.create_group(
            creator_user_id=data['creator_user_id'],
            name=data['name'],
            description=data.get('description', ''),
            group_type=data['group_type'],
            category=data.get('category'),
            region=data.get('region'),
            is_private=data.get('is_private', False),
            require_approval=data.get('require_approval', False),
            avatar_url=data.get('avatar_url'),
            cover_image_url=data.get('cover_image_url')
        )

        if group:
            return jsonify({'success': True, 'data': group})
        else:
            return jsonify({'success': False, 'error': 'Failed to create group'}), 500

    except Exception as e:
        logger.error(f"그룹 생성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/groups/<int:group_id>', methods=['GET'])
@cross_origin()
@async_route
async def get_group_info(group_id):
    """그룹 정보 조회"""
    try:
        group = await groups_service.get_group_info(group_id)

        if group:
            return jsonify({'success': True, 'data': group})
        else:
            return jsonify({'success': False, 'error': 'Group not found'}), 404

    except Exception as e:
        logger.error(f"그룹 정보 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/groups/<int:group_id>/join', methods=['POST'])
@cross_origin()
@async_route
async def join_group(group_id):
    """그룹 가입"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400

        success = await groups_service.join_group(group_id, user_id)

        return jsonify({'success': success})

    except Exception as e:
        logger.error(f"그룹 가입 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/groups/<int:group_id>/leave', methods=['DELETE'])
@cross_origin()
@async_route
async def leave_group(group_id):
    """그룹 탈퇴"""
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400

        success = await groups_service.leave_group(group_id, user_id)

        return jsonify({'success': success})

    except Exception as e:
        logger.error(f"그룹 탈퇴 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/groups/search', methods=['GET'])
@cross_origin()
@async_route
async def search_groups():
    """그룹 검색"""
    try:
        query = request.args.get('query')
        group_type = request.args.get('group_type')
        category = request.args.get('category')
        region = request.args.get('region')
        user_id = request.args.get('user_id')
        limit = min(int(request.args.get('limit', 20)), 50)

        groups = await groups_service.search_groups(
            query, group_type, category, region, user_id, limit
        )

        return jsonify({'success': True, 'data': groups})

    except Exception as e:
        logger.error(f"그룹 검색 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/groups/recommend/<user_id>', methods=['GET'])
@cross_origin()
@async_route
async def recommend_groups(user_id):
    """그룹 추천"""
    try:
        limit = min(int(request.args.get('limit', 10)), 20)

        groups = await groups_service.get_recommended_groups(user_id, limit)

        return jsonify({'success': True, 'data': groups})

    except Exception as e:
        logger.error(f"그룹 추천 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/users/<user_id>/groups', methods=['GET'])
@cross_origin()
@async_route
async def get_user_groups(user_id):
    """사용자 그룹 목록"""
    try:
        groups = await groups_service.get_user_groups(user_id)

        return jsonify({'success': True, 'data': groups})

    except Exception as e:
        logger.error(f"사용자 그룹 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 콘텐츠 보상 API ==========

@social_bp.route('/rewards/eligible-content', methods=['GET'])
@cross_origin()
@async_route
async def get_eligible_content():
    """보상 대상 콘텐츠 조회"""
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 50)

        content = await rewards_service.get_eligible_content_for_rewards(page, limit)

        return jsonify({
            'success': True,
            'data': {
                'content': content,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'has_more': len(content) == limit
                }
            }
        })

    except Exception as e:
        logger.error(f"보상 대상 콘텐츠 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/rewards/user/<user_id>', methods=['GET'])
@cross_origin()
@async_route
async def get_user_rewards(user_id):
    """사용자 보상 내역 조회"""
    try:
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 50)

        rewards = await rewards_service.get_user_rewards(user_id, status, page, limit)

        return jsonify({
            'success': True,
            'data': {
                'rewards': rewards,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'has_more': len(rewards) == limit
                }
            }
        })

    except Exception as e:
        logger.error(f"사용자 보상 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@social_bp.route('/rewards/stats/<user_id>', methods=['GET'])
@cross_origin()
@async_route
async def get_user_reward_stats(user_id):
    """사용자 보상 통계 조회"""
    try:
        stats = await rewards_service.get_user_reward_stats(user_id)

        return jsonify({'success': True, 'data': stats})

    except Exception as e:
        logger.error(f"사용자 보상 통계 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500