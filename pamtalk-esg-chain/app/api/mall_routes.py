# -*- coding: utf-8 -*-
"""
PAM MALL Routes
마켓플레이스 상품 관리 API
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

mall_routes = Blueprint('mall_routes', __name__)

# 초기 상품 데이터
INITIAL_PRODUCTS = [
    {
        "product_id": "PRODUCT_APPLE",
        "name": "사과",
        "category": "과일",
        "price": 5000,
        "stock": 100,
        "description": "신선한 아산 사과 1kg",
        "image_url": "/images/apple.jpg",
        "farm_id": "FARM_001",
        "created_at": datetime.now().isoformat()
    },
    {
        "product_id": "PRODUCT_CARROT",
        "name": "당근",
        "category": "채소",
        "price": 3000,
        "stock": 150,
        "description": "유기농 당근 500g",
        "image_url": "/images/carrot.jpg",
        "farm_id": "FARM_002",
        "created_at": datetime.now().isoformat()
    },
    {
        "product_id": "PRODUCT_ONION",
        "name": "양파",
        "category": "채소",
        "price": 4000,
        "stock": 120,
        "description": "국내산 햇양파 1kg",
        "image_url": "/images/onion.jpg",
        "farm_id": "FARM_003",
        "created_at": datetime.now().isoformat()
    },
    {
        "product_id": "PRODUCT_RADISH",
        "name": "무",
        "category": "채소",
        "price": 3500,
        "stock": 80,
        "description": "국내산 무 1개 (약 1.5kg)",
        "image_url": "/images/radish.jpg",
        "farm_id": "FARM_004",
        "created_at": datetime.now().isoformat()
    },
    {
        "product_id": "PRODUCT_CABBAGE",
        "name": "배추",
        "category": "채소",
        "price": 6000,
        "stock": 60,
        "description": "절임배추 1포기 (약 3kg)",
        "image_url": "/images/cabbage.jpg",
        "farm_id": "FARM_004",
        "created_at": datetime.now().isoformat()
    },
    {
        "product_id": "PRODUCT_LATTE",
        "name": "카페라떼",
        "category": "음료",
        "price": 4500,
        "stock": 999,
        "description": "부드러운 우유와 에스프레소의 조화",
        "image_url": "/images/latte.jpg",
        "farm_id": "CAFE_001",
        "created_at": datetime.now().isoformat()
    },
    {
        "product_id": "PRODUCT_AMERICANO",
        "name": "아메리카노",
        "category": "음료",
        "price": 3500,
        "stock": 999,
        "description": "깔끔한 에스프레소 아메리카노",
        "image_url": "/images/americano.jpg",
        "farm_id": "CAFE_001",
        "created_at": datetime.now().isoformat()
    }
]

# 메모리 저장소 (실제 배포시에는 데이터베이스 사용)
products_db = {product["product_id"]: product for product in INITIAL_PRODUCTS}
orders_db = {}


def create_success_response(data: any, message: str = None):
    """표준 성공 응답 생성"""
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    if message:
        response["message"] = message
    return response


def create_error_response(message: str, status_code: int = 400):
    """표준 에러 응답 생성"""
    return {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
    }


@mall_routes.route('/products', methods=['GET'])
def get_products():
    """상품 목록 조회"""
    try:
        category = request.args.get('category')

        products = list(products_db.values())

        # 카테고리 필터링
        if category:
            products = [p for p in products if p['category'] == category]

        return jsonify(create_success_response(products)), 200

    except Exception as e:
        logger.error(f"Get products error: {e}")
        return jsonify(create_error_response(f"상품 조회 실패: {str(e)}")), 500


@mall_routes.route('/products/<string:product_id>', methods=['GET'])
def get_product(product_id):
    """특정 상품 조회"""
    try:
        product = products_db.get(product_id)

        if not product:
            return jsonify(create_error_response("상품을 찾을 수 없습니다")), 404

        return jsonify(create_success_response(product)), 200

    except Exception as e:
        logger.error(f"Get product error: {e}")
        return jsonify(create_error_response(f"상품 조회 실패: {str(e)}")), 500


@mall_routes.route('/products', methods=['POST'])
def add_product():
    """상품 추가 (관리자용)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        # 필수 필드 확인
        required_fields = ['product_id', 'name', 'category', 'price', 'stock']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            )), 400

        product_id = data['product_id']

        # 중복 확인
        if product_id in products_db:
            return jsonify(create_error_response("이미 존재하는 상품입니다")), 400

        # 상품 생성
        product = {
            'product_id': product_id,
            'name': data['name'],
            'category': data['category'],
            'price': float(data['price']),
            'stock': int(data['stock']),
            'description': data.get('description', ''),
            'image_url': data.get('image_url', ''),
            'farm_id': data.get('farm_id'),
            'created_at': datetime.now().isoformat()
        }

        products_db[product_id] = product

        return jsonify(create_success_response(product, "상품이 추가되었습니다")), 201

    except Exception as e:
        logger.error(f"Add product error: {e}")
        return jsonify(create_error_response(f"상품 추가 실패: {str(e)}")), 500


@mall_routes.route('/orders', methods=['POST'])
def create_order():
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

        # 주문 생성
        import uuid
        order_id = f"ORDER_{uuid.uuid4().hex[:8].upper()}"

        order = {
            'order_id': order_id,
            'user_address': data['user_address'],
            'items': data['items'],
            'coupon_id': data.get('coupon_id'),
            'payment_txid': data.get('payment_txid'),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }

        orders_db[order_id] = order

        return jsonify(create_success_response(order, "주문이 생성되었습니다")), 201

    except Exception as e:
        logger.error(f"Create order error: {e}")
        return jsonify(create_error_response(f"주문 생성 실패: {str(e)}")), 500


@mall_routes.route('/orders/<string:order_id>', methods=['GET'])
def get_order(order_id):
    """주문 조회"""
    try:
        order = orders_db.get(order_id)

        if not order:
            return jsonify(create_error_response("주문을 찾을 수 없습니다")), 404

        return jsonify(create_success_response(order)), 200

    except Exception as e:
        logger.error(f"Get order error: {e}")
        return jsonify(create_error_response(f"주문 조회 실패: {str(e)}")), 500


@mall_routes.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    try:
        return jsonify(create_success_response({
            "status": "healthy",
            "total_products": len(products_db),
            "total_orders": len(orders_db)
        })), 200

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify(create_error_response("서비스 상태 확인 실패")), 500
