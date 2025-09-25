#!/usr/bin/env python3
"""
PAM-TALK: Platform for Active Meta
지역 농수축산물 유통 혁신 SNS 플랫폼

핵심 기능:
- 탄소발자국 추적 및 개인 참여 시스템
- 농촌-도시 직접 연결 SNS
- 지역 기반 유통 활성화
- 이윤 창출 구조
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from advanced_cache import global_cache

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# ===============================
# 데이터 모델 정의
# ===============================

@dataclass
class User:
    user_id: str
    username: str
    user_type: str  # "farmer", "consumer", "distributor", "restaurant"
    location: Dict[str, str]  # {"region": "경기도", "city": "용인시"}
    profile: Dict[str, any]
    carbon_footprint: float = 0.0
    eco_points: int = 0
    followers: int = 0
    following: int = 0
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class Product:
    product_id: str
    farmer_id: str
    name: str
    category: str  # "채소", "과일", "곡물", "축산물", "수산물"
    description: str
    price_per_kg: float
    available_quantity: int
    harvest_date: str
    location: Dict[str, str]
    carbon_footprint: float  # kg CO2 per kg product
    certifications: List[str]  # ["유기농", "무농약", "친환경"]
    images: List[str]
    likes: int = 0
    views: int = 0
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class SocialPost:
    post_id: str
    user_id: str
    content: str
    post_type: str  # "farm_story", "recipe", "review", "tip", "carbon_challenge"
    images: List[str]
    tags: List[str]
    location: Dict[str, str]
    likes: int = 0
    comments: int = 0
    shares: int = 0
    eco_impact: Dict[str, float] = None  # {"carbon_saved": 1.2, "local_distance": 5.0}
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class Transaction:
    transaction_id: str
    buyer_id: str
    seller_id: str
    product_id: str
    quantity: int
    total_price: float
    delivery_method: str  # "pickup", "local_delivery", "shipping"
    carbon_saved: float  # vs 기존 유통구조
    distance_km: float
    status: str  # "pending", "confirmed", "delivered", "completed"
    eco_points_earned: int
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class CarbonChallenge:
    challenge_id: str
    title: str
    description: str
    target_reduction: float  # kg CO2
    duration_days: int
    reward_points: int
    participants: int = 0
    status: str = "active"  # "active", "completed", "expired"
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

# ===============================
# 데이터 스토어
# ===============================

class PAMTalkDataStore:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.products: Dict[str, Product] = {}
        self.social_posts: Dict[str, SocialPost] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.challenges: Dict[str, CarbonChallenge] = {}
        self._lock = threading.RLock()

        # 초기 데이터 생성
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """샘플 데이터 초기화"""

        # 샘플 사용자들
        sample_users = [
            User("farmer001", "김농부", "farmer",
                 {"region": "경기도", "city": "용인시"},
                 {"description": "30년 경력의 유기농 농부", "specialty": "토마토, 오이"},
                 carbon_footprint=-50.2, eco_points=1250, followers=234),

            User("consumer001", "박도시", "consumer",
                 {"region": "서울시", "city": "강남구"},
                 {"description": "건강한 먹거리를 찾는 직장인", "interests": ["유기농", "로컬푸드"]},
                 carbon_footprint=12.5, eco_points=890, followers=145),

            User("restaurant001", "맛집사장", "restaurant",
                 {"region": "서울시", "city": "홍대"},
                 {"description": "로컬 식재료 전문 레스토랑", "cuisine": "한식"},
                 carbon_footprint=8.3, eco_points=2100, followers=567),
        ]

        for user in sample_users:
            self.users[user.user_id] = user

        # 샘플 상품들
        sample_products = [
            Product("prod001", "farmer001", "친환경 토마토", "채소",
                   "햇살 가득한 유기농 토마토입니다", 3.5, 50,
                   "2024-01-15", {"region": "경기도", "city": "용인시"},
                   0.8, ["유기농", "무농약"], ["tomato1.jpg"], likes=23, views=156),

            Product("prod002", "farmer001", "신선한 오이", "채소",
                   "아침에 딴 싱싱한 오이", 2.8, 30,
                   "2024-01-16", {"region": "경기도", "city": "용인시"},
                   0.6, ["친환경"], ["cucumber1.jpg"], likes=18, views=89),
        ]

        for product in sample_products:
            self.products[product.product_id] = product

        # 샘플 소셜 포스트들
        sample_posts = [
            SocialPost("post001", "farmer001",
                      "오늘 아침 수확한 토마토들! 🍅 30년간 키워온 노하우로 당도 최고예요",
                      "farm_story", ["tomato_harvest.jpg"], ["토마토", "수확", "유기농"],
                      {"region": "경기도", "city": "용인시"},
                      likes=45, comments=12, shares=8,
                      eco_impact={"carbon_saved": 2.1, "local_distance": 0}),

            SocialPost("post002", "consumer001",
                      "김농부님 토마토로 만든 파스타 🍝 정말 맛있어요! #로컬푸드",
                      "review", ["pasta.jpg"], ["리뷰", "로컬푸드", "파스타"],
                      {"region": "서울시", "city": "강남구"},
                      likes=28, comments=5, shares=3,
                      eco_impact={"carbon_saved": 1.5, "local_distance": 35.2}),
        ]

        for post in sample_posts:
            self.social_posts[post.post_id] = post

        # 샘플 탄소 챌린지
        sample_challenges = [
            CarbonChallenge("ch001", "로컬푸드 한 달 챌린지",
                           "한 달간 50km 이내 농산물만 구매하기",
                           15.0, 30, 500, participants=156),

            CarbonChallenge("ch002", "제로웨이스트 요리",
                           "음식 쓰레기 없는 요리 도전",
                           8.0, 14, 300, participants=89),
        ]

        for challenge in sample_challenges:
            self.challenges[challenge.challenge_id] = challenge

# 전역 데이터 스토어
data_store = PAMTalkDataStore()

# ===============================
# 성능 미들웨어
# ===============================

@app.before_request
def before_request():
    g.start_time = time.time()
    g.request_id = f"req_{int(time.time() * 1000)}"

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        response.headers['X-Platform'] = 'PAM-TALK-Social'
    return response

# ===============================
# API 엔드포인트들
# ===============================

@app.route('/api/health', methods=['GET'])
def health_check():
    return {
        "status": "healthy",
        "platform": "PAM-TALK: Platform for Active Meta",
        "version": "3.0.0-social",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "social_networking",
            "carbon_tracking",
            "local_trading",
            "rural_urban_bridge"
        ]
    }

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    with data_store._lock:
        stats = {
            "platform_stats": {
                "total_users": len(data_store.users),
                "active_farmers": len([u for u in data_store.users.values() if u.user_type == "farmer"]),
                "active_consumers": len([u for u in data_store.users.values() if u.user_type == "consumer"]),
                "available_products": len([p for p in data_store.products.values() if p.available_quantity > 0]),
                "total_posts": len(data_store.social_posts),
                "active_challenges": len([c for c in data_store.challenges.values() if c.status == "active"])
            },
            "carbon_impact": {
                "total_carbon_saved": sum(p.eco_impact.get("carbon_saved", 0) for p in data_store.social_posts.values() if p.eco_impact),
                "average_delivery_distance": 25.3,  # km
                "eco_points_distributed": sum(u.eco_points for u in data_store.users.values()),
                "challenges_completed": 45
            },
            "community_engagement": {
                "total_likes": sum(p.likes for p in data_store.social_posts.values()),
                "total_shares": sum(p.shares for p in data_store.social_posts.values()),
                "total_followers": sum(u.followers for u in data_store.users.values()),
                "local_connections": 156  # 지역 내 연결 수
            },
            "economic_impact": {
                "direct_trades_value": 2580000,  # 원
                "farmer_earnings": 1850000,
                "carbon_credits_earned": 125,
                "platform_commission": 258000
            }
        }

    return {
        "success": True,
        "data": stats,
        "generated_at": datetime.now().isoformat()
    }

@app.route('/api/users', methods=['GET'])
def get_users():
    user_type = request.args.get('type')
    location = request.args.get('location')

    with data_store._lock:
        users = list(data_store.users.values())

        if user_type:
            users = [u for u in users if u.user_type == user_type]

        if location:
            users = [u for u in users if location.lower() in u.location.get("region", "").lower()]

    return {
        "success": True,
        "users": [asdict(u) for u in users],
        "total": len(users)
    }

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    location = request.args.get('location')
    max_distance = request.args.get('max_distance', type=int)

    with data_store._lock:
        products = list(data_store.products.values())

        if category:
            products = [p for p in products if p.category == category]

        if location:
            products = [p for p in products if location.lower() in p.location.get("region", "").lower()]

        # 거리 필터링 (실제 구현시 GPS 좌표 사용)
        if max_distance:
            # 간단한 거리 시뮬레이션
            products = [p for p in products if hash(p.product_id) % 100 < max_distance]

    return {
        "success": True,
        "products": [asdict(p) for p in products],
        "total": len(products),
        "filters": {
            "category": category,
            "location": location,
            "max_distance": max_distance
        }
    }

@app.route('/api/social/feed', methods=['GET'])
def get_social_feed():
    user_id = request.args.get('user_id')
    post_type = request.args.get('type')
    limit = request.args.get('limit', 20, type=int)

    with data_store._lock:
        posts = list(data_store.social_posts.values())

        if post_type:
            posts = [p for p in posts if p.post_type == post_type]

        # 최신순 정렬
        posts.sort(key=lambda x: x.created_at, reverse=True)

        # 사용자 정보 추가
        enriched_posts = []
        for post in posts[:limit]:
            post_dict = asdict(post)
            if post.user_id in data_store.users:
                post_dict['user_info'] = {
                    "username": data_store.users[post.user_id].username,
                    "user_type": data_store.users[post.user_id].user_type,
                    "location": data_store.users[post.user_id].location
                }
            enriched_posts.append(post_dict)

    return {
        "success": True,
        "posts": enriched_posts,
        "total": len(enriched_posts)
    }

@app.route('/api/carbon/challenges', methods=['GET'])
def get_carbon_challenges():
    status = request.args.get('status', 'active')

    with data_store._lock:
        challenges = [c for c in data_store.challenges.values() if c.status == status]
        challenges.sort(key=lambda x: x.participants, reverse=True)

    return {
        "success": True,
        "challenges": [asdict(c) for c in challenges],
        "total": len(challenges)
    }

@app.route('/api/carbon/footprint/<user_id>', methods=['GET'])
def get_user_carbon_footprint(user_id):
    if user_id not in data_store.users:
        return {"success": False, "error": "User not found"}, 404

    user = data_store.users[user_id]

    # 탄소발자국 상세 분석
    footprint_analysis = {
        "total_footprint": user.carbon_footprint,
        "footprint_category": "carbon_positive" if user.carbon_footprint < 0 else "carbon_neutral" if user.carbon_footprint < 5 else "needs_improvement",
        "monthly_trend": [-2.1, -1.8, -2.5, -3.2],  # 최근 4개월
        "breakdown": {
            "local_purchases": -15.2,
            "transportation": 8.1,
            "packaging": 2.3,
            "food_waste": -1.8
        },
        "achievements": [
            "로컬푸드 챔피언 (30km 이내 구매 90%)",
            "제로웨이스트 달성자"
        ],
        "next_goals": [
            "탄소 발자국 -10kg 달성",
            "로컬 농부 5명 이상 직거래"
        ]
    }

    return {
        "success": True,
        "user_id": user_id,
        "footprint_analysis": footprint_analysis,
        "eco_points": user.eco_points
    }

@app.route('/api/trading/create', methods=['POST'])
def create_trading_post():
    data = request.get_json()

    # 상품 등록 (농부) 또는 구매 요청 (소비자)
    if data.get('type') == 'sell':
        # 판매 상품 등록
        product_id = f"prod_{int(time.time())}"
        product = Product(
            product_id=product_id,
            farmer_id=data.get('user_id'),
            name=data.get('name'),
            category=data.get('category'),
            description=data.get('description', ''),
            price_per_kg=data.get('price_per_kg'),
            available_quantity=data.get('quantity'),
            harvest_date=data.get('harvest_date', datetime.now().strftime('%Y-%m-%d')),
            location=data.get('location', {}),
            carbon_footprint=data.get('carbon_footprint', 1.0),
            certifications=data.get('certifications', []),
            images=data.get('images', [])
        )

        data_store.products[product_id] = product

        return {
            "success": True,
            "product_id": product_id,
            "message": "상품이 등록되었습니다"
        }, 201

    elif data.get('type') == 'buy':
        # 구매 요청 처리
        # 실제로는 매칭 알고리즘 실행
        return {
            "success": True,
            "matches": 5,
            "message": "구매 요청이 등록되었습니다. 5개의 매칭 상품을 찾았습니다."
        }

@app.route('/api/social/post', methods=['POST'])
def create_social_post():
    data = request.get_json()

    post_id = f"post_{int(time.time())}"
    post = SocialPost(
        post_id=post_id,
        user_id=data.get('user_id'),
        content=data.get('content'),
        post_type=data.get('post_type', 'farm_story'),
        images=data.get('images', []),
        tags=data.get('tags', []),
        location=data.get('location', {}),
        eco_impact=data.get('eco_impact')
    )

    data_store.social_posts[post_id] = post

    # 에코 포인트 지급
    if data.get('user_id') in data_store.users:
        user = data_store.users[data.get('user_id')]
        if post.post_type == 'carbon_challenge':
            user.eco_points += 50
        else:
            user.eco_points += 10

    return {
        "success": True,
        "post_id": post_id,
        "eco_points_earned": 50 if post.post_type == 'carbon_challenge' else 10,
        "message": "포스트가 등록되었습니다"
    }, 201

@app.route('/')
def index():
    """메인 페이지"""
    return app.send_static_file('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """정적 파일 서빙"""
    return app.send_static_file(filename)

if __name__ == '__main__':
    print("PAM-TALK Social Platform Server")
    print("Platform for Active Meta - 지역 농수축산물 유통 혁신 SNS")
    app.run(host='127.0.0.1', port=5003, debug=False, threaded=True)