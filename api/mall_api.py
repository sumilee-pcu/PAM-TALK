#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM MALL REST API
쇼핑몰 및 디지털 쿠폰 관리 API
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.coupon_manager import CouponManager, Product, DigitalCoupon
from api.auth_middleware import require_auth, require_role

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

# Enable CORS
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Global coupon manager instance
coupon_manager = None


def get_coupon_manager():
    """Get or create coupon manager instance"""
    global coupon_manager
    if coupon_manager is None:
        coupon_manager = CouponManager()
    return coupon_manager


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
# 상품 관리 엔드포인트
# =============================================================================

@app.route('/api/mall/products', methods=['GET'])
def get_products():
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
def get_product(product_id):
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


@app.route('/api/mall/products', methods=['POST'])
@require_role('ADMIN', 'SUPPLIER')
def add_product():
    """상품 추가 (관리자 및 공급자만 가능)"""
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

        manager = get_coupon_manager()

        product = Product(
            product_id=data['product_id'],
            name=data['name'],
            category=data['category'],
            price=float(data['price']),
            stock=int(data['stock']),
            description=data.get('description', ''),
            image_url=data.get('image_url', ''),
            farm_id=data.get('farm_id')
        )

        success = manager.add_product(product)

        if success:
            return jsonify(create_success_response(
                product.to_dict(), "상품이 추가되었습니다"
            )), 201
        else:
            return jsonify(create_error_response("이미 존재하는 상품입니다")), 400

    except Exception as e:
        logger.error(f"Add product error: {e}")
        return jsonify(create_error_response(f"상품 추가 실패: {str(e)}")), 500


# =============================================================================
# 쿠폰 관리 엔드포인트
# =============================================================================

@app.route('/api/mall/coupons', methods=['GET'])
def get_all_coupons():
    """모든 쿠폰 조회"""
    try:
        manager = get_coupon_manager()
        coupons = [c.to_dict() for c in manager.coupons.values()]

        return jsonify(create_success_response(coupons))

    except Exception as e:
        logger.error(f"Get coupons error: {e}")
        return jsonify(create_error_response(f"쿠폰 조회 실패: {str(e)}")), 500


@app.route('/api/mall/coupons/<string:coupon_id>', methods=['GET'])
def get_coupon_detail(coupon_id):
    """특정 쿠폰 조회"""
    try:
        manager = get_coupon_manager()
        coupon = manager.get_coupon(coupon_id)

        if not coupon:
            return jsonify(create_error_response("쿠폰을 찾을 수 없습니다")), 404

        return jsonify(create_success_response(coupon.to_dict()))

    except Exception as e:
        logger.error(f"Get coupon error: {e}")
        return jsonify(create_error_response(f"쿠폰 조회 실패: {str(e)}")), 500


@app.route('/api/mall/users/<string:user_address>/coupons', methods=['GET'])
def get_user_coupons(user_address):
    """사용자 쿠폰 목록 조회"""
    try:
        manager = get_coupon_manager()
        coupons = manager.get_user_coupons(user_address)
        coupons_data = [c.to_dict() for c in coupons]

        return jsonify(create_success_response(coupons_data))

    except Exception as e:
        logger.error(f"Get user coupons error: {e}")
        return jsonify(create_error_response(f"사용자 쿠폰 조회 실패: {str(e)}")), 500


@app.route('/api/mall/users/<string:user_address>/coupons/<string:coupon_id>', methods=['POST'])
@require_role('ADMIN', 'COMMITTEE')
def issue_coupon(user_address, coupon_id):
    """사용자에게 쿠폰 발급 (관리자 및 위원회만 가능)"""
    try:
        manager = get_coupon_manager()
        success = manager.issue_coupon_to_user(user_address, coupon_id)

        if success:
            return jsonify(create_success_response(
                {"user_address": user_address, "coupon_id": coupon_id},
                "쿠폰이 발급되었습니다"
            )), 201
        else:
            return jsonify(create_error_response("쿠폰 발급에 실패했습니다")), 400

    except Exception as e:
        logger.error(f"Issue coupon error: {e}")
        return jsonify(create_error_response(f"쿠폰 발급 실패: {str(e)}")), 500


@app.route('/api/mall/coupons/<string:coupon_id>/validate', methods=['POST'])
def validate_coupon(coupon_id):
    """쿠폰 유효성 검증"""
    try:
        data = request.get_json() or {}
        product_id = data.get('product_id')

        manager = get_coupon_manager()
        result = manager.validate_coupon(coupon_id, product_id)

        if result['valid']:
            return jsonify(create_success_response(result, "유효한 쿠폰입니다"))
        else:
            return jsonify(create_error_response(result.get('error', '유효하지 않은 쿠폰입니다'))), 400

    except Exception as e:
        logger.error(f"Validate coupon error: {e}")
        return jsonify(create_error_response(f"쿠폰 검증 실패: {str(e)}")), 500


# =============================================================================
# 주문 관리 엔드포인트
# =============================================================================

@app.route('/api/mall/orders', methods=['POST'])
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


@app.route('/api/mall/orders/<string:order_id>', methods=['GET'])
def get_order(order_id):
    """주문 조회"""
    try:
        manager = get_coupon_manager()
        order = manager.get_order(order_id)

        if not order:
            return jsonify(create_error_response("주문을 찾을 수 없습니다")), 404

        return jsonify(create_success_response(order))

    except Exception as e:
        logger.error(f"Get order error: {e}")
        return jsonify(create_error_response(f"주문 조회 실패: {str(e)}")), 500


@app.route('/api/mall/users/<string:user_address>/orders', methods=['GET'])
def get_user_orders(user_address):
    """사용자 주문 목록 조회"""
    try:
        manager = get_coupon_manager()
        orders = manager.get_user_orders(user_address)

        return jsonify(create_success_response(orders))

    except Exception as e:
        logger.error(f"Get user orders error: {e}")
        return jsonify(create_error_response(f"주문 목록 조회 실패: {str(e)}")), 500


@app.route('/api/mall/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """주문 상태 업데이트"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify(create_error_response("상태 정보가 없습니다")), 400

        manager = get_coupon_manager()
        success = manager.update_order_status(
            order_id,
            data['status'],
            data.get('payment_txid')
        )

        if success:
            return jsonify(create_success_response(
                {"order_id": order_id, "status": data['status']},
                "주문 상태가 업데이트되었습니다"
            ))
        else:
            return jsonify(create_error_response("주문을 찾을 수 없습니다")), 404

    except Exception as e:
        logger.error(f"Update order status error: {e}")
        return jsonify(create_error_response(f"상태 업데이트 실패: {str(e)}")), 500


# =============================================================================
# 사용자 관리 엔드포인트
# =============================================================================

@app.route('/api/mall/users/register', methods=['POST'])
def register_user():
    """신규 사용자 가입 및 100DC 지급"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("요청 데이터가 없습니다")), 400

        # 필수 필드 확인
        user_address = data.get('user_address')
        if not user_address:
            return jsonify(create_error_response("사용자 주소가 필요합니다")), 400

        manager = get_coupon_manager()

        # 이미 가입된 사용자인지 확인
        if user_address in manager.user_coupons:
            return jsonify(create_error_response("이미 가입된 사용자입니다")), 400

        # 신규 가입자에게 100DC 웰컴 쿠폰 발급
        welcome_coupon_id = "WELCOME_100DC"

        # 웰컴 쿠폰이 없으면 생성
        if welcome_coupon_id not in manager.coupons:
            welcome_coupon = DigitalCoupon(
                coupon_id=welcome_coupon_id,
                name="신규 가입 웰컴 쿠폰",
                discount_type="fixed",
                discount_value=100,
                valid_from=datetime.now().isoformat(),
                valid_until="2099-12-31T23:59:59",
                usage_limit=999999,
                used_count=0,
                product_ids=[]  # 모든 상품에 사용 가능
            )
            manager.coupons[welcome_coupon_id] = welcome_coupon
            manager._save_coupons()

        # 사용자에게 쿠폰 발급
        success = manager.issue_coupon_to_user(user_address, welcome_coupon_id)

        if success:
            logger.info(f"New user registered: {user_address}, 100DC issued")
            return jsonify(create_success_response(
                {
                    "user_address": user_address,
                    "welcome_bonus": 100,
                    "coupon_id": welcome_coupon_id,
                    "message": "가입을 환영합니다! 100DC가 지급되었습니다."
                },
                "회원가입이 완료되었습니다"
            )), 201
        else:
            return jsonify(create_error_response("쿠폰 발급에 실패했습니다")), 500

    except Exception as e:
        logger.error(f"Register user error: {e}")
        return jsonify(create_error_response(f"회원가입 실패: {str(e)}")), 500


@app.route('/api/mall/users/<string:user_address>/check', methods=['GET'])
def check_user_exists(user_address):
    """사용자 가입 여부 확인"""
    try:
        manager = get_coupon_manager()
        exists = user_address in manager.user_coupons

        return jsonify(create_success_response({
            "user_address": user_address,
            "is_registered": exists
        }))

    except Exception as e:
        logger.error(f"Check user exists error: {e}")
        return jsonify(create_error_response(f"사용자 확인 실패: {str(e)}")), 500


# =============================================================================
# Health Check
# =============================================================================

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "name": "PAM MALL API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "GET /api/mall/products",
            "GET /api/mall/products/{id}",
            "POST /api/mall/products",
            "GET /api/mall/coupons",
            "GET /api/mall/coupons/{id}",
            "GET /api/mall/users/{address}/coupons",
            "POST /api/mall/users/{address}/coupons/{id}",
            "POST /api/mall/coupons/{id}/validate",
            "POST /api/mall/orders",
            "GET /api/mall/orders/{id}",
            "GET /api/mall/users/{address}/orders",
            "PUT /api/mall/orders/{id}/status"
        ]
    })


@app.route('/api/mall/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        manager = get_coupon_manager()
        products_count = len(manager.products)
        coupons_count = len(manager.coupons)
        orders_count = len(manager.orders)

        return jsonify(create_success_response({
            "status": "healthy",
            "statistics": {
                "total_products": products_count,
                "total_coupons": coupons_count,
                "total_orders": orders_count
            }
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

    print(">> PAM MALL API Server starting...")
    print(">> Server: http://localhost:5001")
    print(">> API Documentation: See README.md")
    app.run(host='0.0.0.0', port=5001, debug=True)
