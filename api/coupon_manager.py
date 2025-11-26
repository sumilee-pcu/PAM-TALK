#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Digital Coupon Manager
디지털 쿠폰 관리 시스템 - Algorand 블록체인 기반
"""

import json
import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DigitalCoupon:
    """디지털 쿠폰 클래스"""

    def __init__(self, coupon_id: str, name: str, discount_type: str,
                 discount_value: float, valid_from: str, valid_until: str,
                 usage_limit: int = 1, product_ids: List[str] = None,
                 used_count: int = 0, created_at: str = None):
        self.coupon_id = coupon_id
        self.name = name
        self.discount_type = discount_type  # "percentage" or "fixed"
        self.discount_value = discount_value
        self.valid_from = valid_from
        self.valid_until = valid_until
        self.usage_limit = usage_limit
        self.product_ids = product_ids or []  # 빈 리스트면 전체 상품 적용
        self.used_count = used_count
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            'coupon_id': self.coupon_id,
            'name': self.name,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'valid_from': self.valid_from,
            'valid_until': self.valid_until,
            'usage_limit': self.usage_limit,
            'product_ids': self.product_ids,
            'used_count': self.used_count,
            'created_at': self.created_at
        }

    def is_valid(self, product_id: str = None) -> bool:
        """쿠폰 유효성 검증"""
        now = datetime.now()
        valid_from = datetime.fromisoformat(self.valid_from)
        valid_until = datetime.fromisoformat(self.valid_until)

        # 날짜 확인
        if not (valid_from <= now <= valid_until):
            return False

        # 사용 횟수 확인
        if self.used_count >= self.usage_limit:
            return False

        # 상품 확인
        if product_id and self.product_ids and product_id not in self.product_ids:
            return False

        return True

    def calculate_discount(self, original_price: float) -> float:
        """할인 금액 계산"""
        if self.discount_type == "percentage":
            return original_price * (self.discount_value / 100)
        elif self.discount_type == "fixed":
            return min(self.discount_value, original_price)
        return 0


class Product:
    """상품 클래스"""

    def __init__(self, product_id: str, name: str, category: str,
                 price: float, stock: int, description: str = "",
                 image_url: str = "", farm_id: str = None, created_at: str = None):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
        self.description = description
        self.image_url = image_url
        self.farm_id = farm_id
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'stock': self.stock,
            'description': self.description,
            'image_url': self.image_url,
            'farm_id': self.farm_id,
            'created_at': self.created_at
        }


class CouponManager:
    """쿠폰 및 상품 관리자"""

    def __init__(self, data_dir: str = None):
        # 기본 경로: PAM-TALK/data/mall (api 디렉토리 기준 상위)
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(os.path.dirname(current_dir), "data", "mall")
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self.coupons_file = os.path.join(data_dir, "coupons.json")
        self.products_file = os.path.join(data_dir, "products.json")
        self.user_coupons_file = os.path.join(data_dir, "user_coupons.json")
        self.orders_file = os.path.join(data_dir, "orders.json")

        self.coupons: Dict[str, DigitalCoupon] = {}
        self.products: Dict[str, Product] = {}
        self.user_coupons: Dict[str, List[str]] = {}  # user_address -> [coupon_ids]
        self.orders: List[Dict] = []

        self._load_data()
        # self._init_default_data()  # 주석 처리: products.json 덮어쓰기 방지

    def _load_data(self):
        """데이터 로드"""
        # 쿠폰 로드
        if os.path.exists(self.coupons_file):
            with open(self.coupons_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for coupon_data in data:
                    coupon = DigitalCoupon(**coupon_data)
                    self.coupons[coupon.coupon_id] = coupon

        # 상품 로드
        logger.info(f"[DEBUG] Products file path: {self.products_file}")
        logger.info(f"[DEBUG] Products file exists: {os.path.exists(self.products_file)}")
        if os.path.exists(self.products_file):
            with open(self.products_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"[DEBUG] Loaded {len(data)} products from JSON")
                for product_data in data:
                    product = Product(**product_data)
                    self.products[product.product_id] = product
                    logger.info(f"[DEBUG] Loaded product: {product.name} - Category: {product.category}")
        logger.info(f"[DEBUG] Total products in memory: {len(self.products)}")

        # 사용자 쿠폰 로드
        if os.path.exists(self.user_coupons_file):
            with open(self.user_coupons_file, 'r', encoding='utf-8') as f:
                self.user_coupons = json.load(f)

        # 주문 로드
        if os.path.exists(self.orders_file):
            with open(self.orders_file, 'r', encoding='utf-8') as f:
                self.orders = json.load(f)

    def _save_data(self):
        """데이터 저장"""
        # 쿠폰 저장
        with open(self.coupons_file, 'w', encoding='utf-8') as f:
            json.dump([c.to_dict() for c in self.coupons.values()], f, indent=2, ensure_ascii=False)

        # 상품 저장
        with open(self.products_file, 'w', encoding='utf-8') as f:
            json.dump([p.to_dict() for p in self.products.values()], f, indent=2, ensure_ascii=False)

        # 사용자 쿠폰 저장
        with open(self.user_coupons_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_coupons, f, indent=2, ensure_ascii=False)

        # 주문 저장
        with open(self.orders_file, 'w', encoding='utf-8') as f:
            json.dump(self.orders, f, indent=2, ensure_ascii=False)

    def _init_default_data(self):
        """기본 데이터 초기화"""
        # 상품이 없으면 기본 상품 추가
        if not self.products:
            default_products = [
                # 과일
                Product(
                    product_id="PRODUCT_APPLE",
                    name="사과",
                    category="과일",
                    price=5000,
                    stock=100,
                    description="신선한 아산 사과 1kg",
                    image_url="/images/apple.jpg",
                    farm_id="FARM_001"
                ),
                # 채소
                Product(
                    product_id="PRODUCT_CARROT",
                    name="당근",
                    category="채소",
                    price=3000,
                    stock=150,
                    description="유기농 당근 500g",
                    image_url="/images/carrot.jpg",
                    farm_id="FARM_002"
                ),
                Product(
                    product_id="PRODUCT_ONION",
                    name="양파",
                    category="채소",
                    price=4000,
                    stock=120,
                    description="국내산 햇양파 1kg",
                    image_url="/images/onion.jpg",
                    farm_id="FARM_003"
                ),
                Product(
                    product_id="PRODUCT_RADISH",
                    name="무",
                    category="채소",
                    price=3500,
                    stock=80,
                    description="국내산 무 1개 (약 1.5kg)",
                    image_url="/images/radish.jpg",
                    farm_id="FARM_004"
                ),
                Product(
                    product_id="PRODUCT_CABBAGE",
                    name="배추",
                    category="채소",
                    price=6000,
                    stock=60,
                    description="절임배추 1포기 (약 3kg)",
                    image_url="/images/cabbage.jpg",
                    farm_id="FARM_004"
                ),
                # 카페 음료
                Product(
                    product_id="PRODUCT_LATTE",
                    name="카페라떼",
                    category="음료",
                    price=4500,
                    stock=999,
                    description="부드러운 우유와 에스프레소의 조화",
                    image_url="/images/latte.jpg",
                    farm_id="CAFE_001"
                ),
                Product(
                    product_id="PRODUCT_AMERICANO",
                    name="아메리카노",
                    category="음료",
                    price=3500,
                    stock=999,
                    description="깔끔한 에스프레소 아메리카노",
                    image_url="/images/americano.jpg",
                    farm_id="CAFE_001"
                )
            ]

            for product in default_products:
                self.products[product.product_id] = product

            self._save_data()

        # 쿠폰이 없으면 기본 쿠폰 추가
        if not self.coupons:
            default_coupons = [
                DigitalCoupon(
                    coupon_id="WELCOME_10",
                    name="신규 회원 10% 할인",
                    discount_type="percentage",
                    discount_value=10,
                    valid_from=datetime.now().isoformat(),
                    valid_until=(datetime.now() + timedelta(days=30)).isoformat(),
                    usage_limit=1
                ),
                DigitalCoupon(
                    coupon_id="FRUIT_5000",
                    name="과일 5000원 할인",
                    discount_type="fixed",
                    discount_value=5000,
                    valid_from=datetime.now().isoformat(),
                    valid_until=(datetime.now() + timedelta(days=15)).isoformat(),
                    usage_limit=1,
                    product_ids=["PRODUCT_APPLE"]
                ),
                DigitalCoupon(
                    coupon_id="VEGGIE_20",
                    name="채소 20% 할인",
                    discount_type="percentage",
                    discount_value=20,
                    valid_from=datetime.now().isoformat(),
                    valid_until=(datetime.now() + timedelta(days=20)).isoformat(),
                    usage_limit=2,
                    product_ids=["PRODUCT_CARROT", "PRODUCT_ONION"]
                ),
                DigitalCoupon(
                    coupon_id="ECOBAG_DISCOUNT",
                    name="에코백 사용 할인 10%",
                    discount_type="percentage",
                    discount_value=10,
                    valid_from=datetime.now().isoformat(),
                    valid_until=(datetime.now() + timedelta(days=90)).isoformat(),
                    usage_limit=999,
                    product_ids=[]  # 모든 상품에 적용
                ),
                DigitalCoupon(
                    coupon_id="TUMBLER_COFFEE",
                    name="텀블러 사용 커피 500원 할인",
                    discount_type="fixed",
                    discount_value=500,
                    valid_from=datetime.now().isoformat(),
                    valid_until=(datetime.now() + timedelta(days=90)).isoformat(),
                    usage_limit=999,
                    product_ids=["PRODUCT_LATTE", "PRODUCT_AMERICANO"]
                ),
                DigitalCoupon(
                    coupon_id="BASKET_VEGGIE",
                    name="바구니 사용 농수산물 15% 할인",
                    discount_type="percentage",
                    discount_value=15,
                    valid_from=datetime.now().isoformat(),
                    valid_until=(datetime.now() + timedelta(days=90)).isoformat(),
                    usage_limit=999,
                    product_ids=["PRODUCT_RADISH", "PRODUCT_CABBAGE", "PRODUCT_CARROT", "PRODUCT_ONION"]
                )
            ]

            for coupon in default_coupons:
                self.coupons[coupon.coupon_id] = coupon

            self._save_data()

    # 상품 관리
    def add_product(self, product: Product) -> bool:
        """상품 추가"""
        if product.product_id in self.products:
            return False
        self.products[product.product_id] = product
        self._save_data()
        return True

    def get_product(self, product_id: str) -> Optional[Product]:
        """상품 조회"""
        return self.products.get(product_id)

    def get_all_products(self, category: str = None) -> List[Product]:
        """모든 상품 조회"""
        logger.info(f"[DEBUG] get_all_products called with category: {category}")
        logger.info(f"[DEBUG] Total products available: {len(self.products)}")
        if category:
            filtered = [p for p in self.products.values() if p.category == category]
            logger.info(f"[DEBUG] Filtered products for category '{category}': {len(filtered)}")
            for p in filtered:
                logger.info(f"[DEBUG]   - {p.name} (category: {p.category})")
            return filtered
        return list(self.products.values())

    def update_stock(self, product_id: str, quantity: int) -> bool:
        """재고 업데이트"""
        product = self.products.get(product_id)
        if not product:
            return False

        new_stock = product.stock + quantity
        if new_stock < 0:
            return False

        product.stock = new_stock
        self._save_data()
        return True

    # 쿠폰 관리
    def add_coupon(self, coupon: DigitalCoupon) -> bool:
        """쿠폰 추가"""
        if coupon.coupon_id in self.coupons:
            return False
        self.coupons[coupon.coupon_id] = coupon
        self._save_data()
        return True

    def get_coupon(self, coupon_id: str) -> Optional[DigitalCoupon]:
        """쿠폰 조회"""
        return self.coupons.get(coupon_id)

    def issue_coupon_to_user(self, user_address: str, coupon_id: str) -> bool:
        """사용자에게 쿠폰 발급"""
        if coupon_id not in self.coupons:
            return False

        if user_address not in self.user_coupons:
            self.user_coupons[user_address] = []

        self.user_coupons[user_address].append(coupon_id)
        self._save_data()
        return True

    def get_user_coupons(self, user_address: str) -> List[DigitalCoupon]:
        """사용자 쿠폰 목록"""
        coupon_ids = self.user_coupons.get(user_address, [])
        return [self.coupons[cid] for cid in coupon_ids if cid in self.coupons]

    def validate_coupon(self, coupon_id: str, product_id: str = None) -> Dict:
        """쿠폰 유효성 검증"""
        coupon = self.get_coupon(coupon_id)
        if not coupon:
            return {"valid": False, "error": "쿠폰을 찾을 수 없습니다"}

        if not coupon.is_valid(product_id):
            return {"valid": False, "error": "쿠폰이 유효하지 않습니다"}

        return {"valid": True, "coupon": coupon.to_dict()}

    # 주문 처리
    def create_order(self, user_address: str, items: List[Dict],
                    coupon_id: str = None, payment_txid: str = None) -> Dict:
        """주문 생성"""
        order_id = f"ORDER_{uuid.uuid4().hex[:12].upper()}"

        # 상품 및 재고 확인
        total_amount = 0
        order_items = []

        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']

            product = self.get_product(product_id)
            if not product:
                return {"success": False, "error": f"상품을 찾을 수 없습니다: {product_id}"}

            if product.stock < quantity:
                return {"success": False, "error": f"재고가 부족합니다: {product.name}"}

            item_total = product.price * quantity
            total_amount += item_total

            order_items.append({
                "product_id": product_id,
                "product_name": product.name,
                "price": product.price,
                "quantity": quantity,
                "subtotal": item_total
            })

        # 쿠폰 적용
        discount_amount = 0
        coupon_info = None

        if coupon_id:
            coupon = self.get_coupon(coupon_id)
            if coupon and coupon.is_valid():
                discount_amount = coupon.calculate_discount(total_amount)
                coupon.used_count += 1
                coupon_info = {
                    "coupon_id": coupon_id,
                    "discount_type": coupon.discount_type,
                    "discount_value": coupon.discount_value,
                    "discount_amount": discount_amount
                }

        final_amount = total_amount - discount_amount

        # 주문 생성
        order = {
            "order_id": order_id,
            "user_address": user_address,
            "items": order_items,
            "total_amount": total_amount,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "coupon": coupon_info,
            "payment_txid": payment_txid,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        # 재고 차감
        for item in items:
            self.update_stock(item['product_id'], -item['quantity'])

        self.orders.append(order)
        self._save_data()

        return {
            "success": True,
            "order": order
        }

    def get_order(self, order_id: str) -> Optional[Dict]:
        """주문 조회"""
        for order in self.orders:
            if order['order_id'] == order_id:
                return order
        return None

    def get_user_orders(self, user_address: str) -> List[Dict]:
        """사용자 주문 목록"""
        return [order for order in self.orders if order['user_address'] == user_address]

    def update_order_status(self, order_id: str, status: str, payment_txid: str = None) -> bool:
        """주문 상태 업데이트"""
        for order in self.orders:
            if order['order_id'] == order_id:
                order['status'] = status
                if payment_txid:
                    order['payment_txid'] = payment_txid
                order['updated_at'] = datetime.now().isoformat()
                self._save_data()
                return True
        return False
