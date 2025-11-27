-- ================================================
-- 009_marketplace_tables.sql
-- 로컬푸드 직거래 마켓플레이스 테이블 생성
-- ================================================

-- 상품 테이블
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    image_url TEXT,
    farm_id VARCHAR(50),
    farmer_name VARCHAR(100),
    farmer_address VARCHAR(100),
    location VARCHAR(200),
    certifications VARCHAR(200),
    carbon_footprint DECIMAL(10, 2),
    unit VARCHAR(20) DEFAULT 'kg',
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, out_of_stock
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 장바구니 테이블
CREATE TABLE IF NOT EXISTS cart (
    cart_id SERIAL PRIMARY KEY,
    user_address VARCHAR(100) NOT NULL,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_address, product_id)
);

-- 주문 테이블
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) PRIMARY KEY,
    user_address VARCHAR(100) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    total_carbon_saved DECIMAL(10, 2) DEFAULT 0,
    payment_method VARCHAR(20) NOT NULL, -- token, cash, card
    payment_txid TEXT, -- Algorand 트랜잭션 ID
    coupon_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, shipping, delivered, cancelled
    delivery_address TEXT,
    delivery_phone VARCHAR(20),
    delivery_request TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 주문 상품 테이블
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    product_name VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    carbon_footprint DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 결제 정보 테이블
CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    user_address VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    payment_txid TEXT, -- Algorand 트랜잭션 ID
    token_amount INTEGER, -- 토큰 수량 (PAM)
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed, refunded
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 상품 리뷰 테이블
CREATE TABLE IF NOT EXISTS product_reviews (
    review_id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    user_address VARCHAR(100) NOT NULL,
    order_id VARCHAR(50) REFERENCES orders(order_id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    images TEXT[], -- 리뷰 이미지 URL 배열
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 농가 정보 테이블
CREATE TABLE IF NOT EXISTS farms (
    farm_id VARCHAR(50) PRIMARY KEY,
    farm_name VARCHAR(200) NOT NULL,
    owner_name VARCHAR(100),
    owner_address VARCHAR(100), -- Algorand 주소
    location VARCHAR(200),
    description TEXT,
    certifications TEXT[],
    profile_image TEXT,
    cover_image TEXT,
    rating DECIMAL(3, 2) DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_farm_id ON products(farm_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_cart_user_address ON cart(user_address);
CREATE INDEX IF NOT EXISTS idx_orders_user_address ON orders(user_address);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_product_reviews_product_id ON product_reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_farms_owner_address ON farms(owner_address);

-- 초기 데이터 삽입 (샘플 농가)
INSERT INTO farms (farm_id, farm_name, owner_name, location, description, certifications) VALUES
('FARM_001', '아산 친환경농장', '김철수', '충남 아산시', '친환경 농법으로 재배하는 신선한 농산물', ARRAY['유기농', '무농약']),
('FARM_002', '용인 행복농장', '이영희', '경기 용인시', '행복한 농부가 키운 건강한 채소', ARRAY['친환경', 'GAP인증']),
('FARM_003', '제주 감귤농장', '박민수', '제주시', '제주 청정 지역의 맛있는 감귤', ARRAY['무농약'])
ON CONFLICT (farm_id) DO NOTHING;

-- 초기 상품 데이터 삽입 (런칭 특가 상품들)
INSERT INTO products (product_id, name, category, price, stock, description, image_url, farm_id, farmer_name, location, certifications, carbon_footprint) VALUES
('LAUNCH_SPECIAL_APPLE', '사과 3개', '런칭특가', 100, 80, '🎉 런칭특가! 달콤한 국내산 사과 3개 - 원가 4,500원', 'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&h=400&fit=crop', 'FARM_001', '김철수', '충남 아산시', '유기농', 1.2),
('LAUNCH_SPECIAL_ORANGE', '귤 1kg', '런칭특가', 100, 70, '🎉 런칭특가! 제주 감귤 1kg - 원가 5,000원', 'https://images.unsplash.com/photo-1547514701-42782101795e?w=400&h=400&fit=crop', 'FARM_002', '이영희', '경기 용인시', '무농약', 1.0),
('LAUNCH_SPECIAL_STRAWBERRY', '딸기 1팩', '런칭특가', 100, 50, '🎉 런칭특가! 설향 딸기 1팩 (500g) - 원가 8,000원', 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400&h=400&fit=crop', 'FARM_001', '김철수', '충남 아산시', '친환경', 1.5),
('LAUNCH_SPECIAL_GRAPE', '샤인머스캣 1송이', '런칭특가', 100, 30, '🎉 런칭특가! 프리미엄 샤인머스캣 1송이 - 원가 12,000원', 'https://images.unsplash.com/photo-1596363505729-4190a9506133?w=400&h=400&fit=crop', 'FARM_003', '박민수', '제주시', '무농약', 2.0),
('PRODUCT_CARROT', '당근', '채소', 3000, 150, '유기농 당근 500g', 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400&h=400&fit=crop', 'FARM_002', '이영희', '경기 용인시', '유기농', 0.8),
('PRODUCT_ONION', '양파', '채소', 4000, 120, '국내산 햇양파 1kg', 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400&h=400&fit=crop', 'FARM_003', '박민수', '제주시', '친환경', 0.9)
ON CONFLICT (product_id) DO NOTHING;

COMMENT ON TABLE products IS '상품 정보 테이블';
COMMENT ON TABLE cart IS '장바구니 테이블';
COMMENT ON TABLE orders IS '주문 정보 테이블';
COMMENT ON TABLE order_items IS '주문 상품 상세 테이블';
COMMENT ON TABLE payments IS '결제 정보 테이블';
COMMENT ON TABLE product_reviews IS '상품 리뷰 테이블';
COMMENT ON TABLE farms IS '농가 정보 테이블';
