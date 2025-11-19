/**
 * PAM MALL Marketplace Page
 * 농산물 직거래 마켓플레이스
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import algosdk from 'algosdk';
import './MarketplacePage.css';

function MarketplacePage() {
  const [cart, setCart] = useState([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [filters, setFilters] = useState({
    category: '',
    location: '',
    distance: '',
    search: ''
  });
  const [sortBy, setSortBy] = useState('newest');
  const [wallet, setWallet] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('cash'); // 'cash' or 'token'
  const [paying, setPaying] = useState(false);

  // 판매자 지갑 주소 (데모용 - 실제로는 각 농부마다 다른 주소)
  const SELLER_ADDRESS = 'SELLER6IXVYMV7YDH6TJKQRQZJ3VJKBXSSLV5WFRCEOTN5HQPVWDEMO'; // 데모용 주소

  // 페이지 로드 시 데모 상품 생성
  useEffect(() => {
    const demoProducts = generateDemoProducts();
    setProducts(demoProducts);
    setFilteredProducts(demoProducts);

    // 로컬스토리지에서 장바구니 불러오기
    const savedCart = localStorage.getItem('pamtalk_cart');
    if (savedCart) {
      setCart(JSON.parse(savedCart));
    }

    // 지갑 불러오기
    const savedWallet = localStorage.getItem('algorand_wallet');
    if (savedWallet) {
      setWallet(JSON.parse(savedWallet));
    }
  }, []);

  // 필터 적용
  useEffect(() => {
    let filtered = [...products];

    if (filters.category) {
      filtered = filtered.filter(p => p.category === filters.category);
    }
    if (filters.location) {
      filtered = filtered.filter(p => p.location.includes(filters.location));
    }
    if (filters.distance) {
      filtered = filtered.filter(p => p.distance_km <= parseInt(filters.distance));
    }
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchLower) ||
        p.farmer_name.toLowerCase().includes(searchLower)
      );
    }

    // 정렬 적용
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price_low':
          return a.price_per_kg - b.price_per_kg;
        case 'price_high':
          return b.price_per_kg - a.price_per_kg;
        case 'distance':
          return a.distance_km - b.distance_km;
        case 'eco_friendly':
          return parseFloat(a.carbon_footprint) - parseFloat(b.carbon_footprint);
        case 'popular':
          return b.likes - a.likes;
        default:
          return 0;
      }
    });

    setFilteredProducts(filtered);
  }, [filters, sortBy, products]);

  // 데모 상품 생성
  function generateDemoProducts() {
    const categories = ['채소', '과일', '곡물', '축산물'];
    const locations = ['경기도 용인시', '강원도 춘천시', '충남 아산시', '전북 완주군', '경남 김해시'];
    const farmers = ['김농부', '이농부', '박농부', '최농부', '정농부'];
    const productNames = ['토마토', '오이', '배추', '사과', '배', '쌀', '감자', '양파', '당근', '상추'];
    const emojis = ['🍅', '🥒', '🥬', '🍎', '🍐', '🌾', '🥔', '🧅', '🥕', '🥬'];
    const images = [
      'https://images.unsplash.com/photo-1546470427-227a1e3e0d05?w=400&h=300&fit=crop', // 토마토
      'https://images.unsplash.com/photo-1604977042946-1eecc30f269e?w=400&h=300&fit=crop', // 오이
      'https://images.unsplash.com/photo-1584868826962-1fa50f7e6d3e?w=400&h=300&fit=crop', // 배추
      'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&h=300&fit=crop', // 사과
      'https://images.unsplash.com/photo-1585059895524-72359e06133a?w=400&h=300&fit=crop', // 배
      'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=300&fit=crop', // 쌀
      'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&h=300&fit=crop', // 감자
      'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400&h=300&fit=crop', // 양파
      'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400&h=300&fit=crop', // 당근
      'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400&h=300&fit=crop'  // 상추
    ];

    return Array.from({ length: 20 }, (_, i) => ({
      product_id: `demo_${i + 1}`,
      name: `신선한 ${productNames[i % productNames.length]}`,
      emoji: emojis[i % emojis.length],
      image: images[i % images.length],
      category: categories[i % categories.length],
      farmer_name: farmers[i % farmers.length],
      farmer_id: `farmer_${(i % farmers.length) + 1}`,
      location: locations[i % locations.length],
      price_per_kg: Math.floor(Math.random() * 5000) + 2000,
      available_quantity: Math.floor(Math.random() * 50) + 10,
      carbon_footprint: (Math.random() * 1.5 + 0.3).toFixed(1),
      distance_km: Math.floor(Math.random() * 80) + 5,
      certifications: Math.random() > 0.5 ? '유기농' : '친환경',
      description: `농부가 직접 기른 신선한 ${productNames[i % productNames.length]}입니다.`,
      likes: Math.floor(Math.random() * 50)
    }));
  }

  // 장바구니에 추가
  const addToCart = (product) => {
    const existingItem = cart.find(item => item.product_id === product.product_id);
    let newCart;

    if (existingItem) {
      newCart = cart.map(item =>
        item.product_id === product.product_id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      );
    } else {
      newCart = [...cart, { ...product, quantity: 1 }];
    }

    setCart(newCart);
    localStorage.setItem('pamtalk_cart', JSON.stringify(newCart));
    showNotification('장바구니에 추가되었습니다! 🛒');
  };

  // 좋아요
  const likeProduct = (productId) => {
    setProducts(products.map(p =>
      p.product_id === productId ? { ...p, likes: p.likes + 1 } : p
    ));
    showNotification('좋아요! ❤️');
  };

  // 수량 업데이트
  const updateQuantity = (productId, change) => {
    const newCart = cart.map(item =>
      item.product_id === productId
        ? { ...item, quantity: Math.max(1, item.quantity + change) }
        : item
    ).filter(item => item.quantity > 0);

    setCart(newCart);
    localStorage.setItem('pamtalk_cart', JSON.stringify(newCart));
  };

  // 장바구니 토글
  const toggleCart = () => {
    setCartOpen(!cartOpen);
  };

  // 주문하기
  const checkout = async () => {
    if (cart.length === 0) {
      alert('장바구니가 비어있습니다!');
      return;
    }

    const total = cart.reduce((sum, item) => sum + (item.price_per_kg * item.quantity), 0);
    const totalCarbon = cart.reduce((sum, item) => sum + (parseFloat(item.carbon_footprint) * item.quantity), 0);

    if (paymentMethod === 'token') {
      // ESG-GOLD 토큰 결제
      await checkoutWithToken(total, totalCarbon);
    } else {
      // 현금 결제 (기존)
      alert(`주문 정보:
- 총 금액: ${total.toLocaleString()}원
- 절약할 탄소: ${totalCarbon.toFixed(1)}kg CO₂
- 획득 에코포인트: ${Math.floor(totalCarbon * 10)}pt

실제 결제 시스템은 개발 중입니다! 🚧`);
    }
  };

  // ESG-GOLD 토큰으로 결제
  const checkoutWithToken = async (totalAmount, totalCarbon) => {
    // 지갑 확인
    if (!wallet) {
      alert('❌ 지갑이 없습니다!\n\n지갑 페이지에서 먼저 지갑을 생성하세요.');
      return;
    }

    // ESG-GOLD 자산 ID 확인
    if (!wallet.esgGoldAssetId) {
      alert('❌ ESG-GOLD 토큰이 없습니다!\n\n지갑 페이지에서 먼저 토큰을 생성하세요.');
      return;
    }

    // 토큰 가격 계산 (1 ESGOLD = 100원으로 가정)
    const tokenAmount = Math.ceil(totalAmount / 100);

    // 판매자 주소 입력 받기 (데모용)
    const sellerAddress = prompt(
      `🪙 ESG-GOLD 토큰 결제\n\n` +
      `총 금액: ${totalAmount.toLocaleString()}원\n` +
      `토큰 수량: ${tokenAmount.toLocaleString()} ESGOLD\n` +
      `절약할 탄소: ${totalCarbon.toFixed(1)}kg CO₂\n\n` +
      `판매자의 알고랜드 주소를 입력하세요:\n` +
      `(테스트용으로 자신의 다른 지갑 주소를 입력해도 됩니다)`
    );

    if (!sellerAddress || sellerAddress.length !== 58) {
      alert('❌ 올바른 알고랜드 주소를 입력하세요 (58자).');
      return;
    }

    if (!window.confirm(
      `💳 결제를 진행하시겠습니까?\n\n` +
      `상품: ${cart.map(item => `${item.name} x${item.quantity}kg`).join(', ')}\n` +
      `토큰: ${tokenAmount} ESGOLD\n` +
      `판매자: ${sellerAddress.substring(0, 10)}...${sellerAddress.substring(48)}`
    )) {
      return;
    }

    setPaying(true);

    try {
      const algodClient = new algosdk.Algodv2(
        '',
        'https://testnet-api.algonode.cloud',
        ''
      );

      const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);
      const params = await algodClient.getTransactionParams().do();

      // 토큰 전송 트랜잭션
      const txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
        from: account.addr,
        to: sellerAddress,
        amount: tokenAmount * 100, // 소수점 2자리
        assetIndex: wallet.esgGoldAssetId,
        note: new Uint8Array(Buffer.from(`PAM-TALK 상품 구매: ${cart.length}개 상품`)),
        suggestedParams: params
      });

      const signedTxn = txn.signTxn(account.sk);
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();

      alert('⏳ 결제 처리 중...\n\n트랜잭션 ID: ' + txId);

      await algosdk.waitForConfirmation(algodClient, txId, 4);

      // 주문 완료
      alert(
        `✅ 결제가 완료되었습니다!\n\n` +
        `🪙 전송: ${tokenAmount} ESGOLD\n` +
        `🌱 탄소 절약: ${totalCarbon.toFixed(1)}kg CO₂\n` +
        `⭐ 획득 포인트: ${Math.floor(totalCarbon * 10)}pt\n\n` +
        `트랜잭션 ID:\n${txId.substring(0, 20)}...`
      );

      // 장바구니 비우기
      setCart([]);
      localStorage.removeItem('pamtalk_cart');
      setCartOpen(false);

    } catch (error) {
      console.error('토큰 결제 실패:', error);
      alert('❌ 결제에 실패했습니다.\n\n' + error.message);
    } finally {
      setPaying(false);
    }
  };

  // 알림 표시
  const showNotification = (message) => {
    // 간단한 알림 (실제로는 toast 라이브러리 사용 추천)
    alert(message);
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.price_per_kg * item.quantity), 0);
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="marketplace-page">
      {/* Top Header */}
      <div className="marketplace-top-header">
        <div className="top-header-container">
          <Link to="/login" className="top-header-link">로그인</Link>
          <span className="top-header-link" onClick={toggleCart} style={{ cursor: 'pointer' }}>
            장바구니({cartCount})
          </span>
          <Link to="/profile" className="top-header-link">마이쇼핑</Link>
        </div>
      </div>

      {/* Main Header */}
      <div className="marketplace-header">
        <div className="marketplace-header-container">
          <Link to="/" className="marketplace-logo">
            🛒 PAM MALL
          </Link>
          <div className="marketplace-search">
            <input
              type="text"
              placeholder="검색어를 입력하세요"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
            <button>
              <i className="fas fa-search"></i>
            </button>
          </div>
          <div className="marketplace-cart-icon" onClick={toggleCart}>
            <i className="fas fa-shopping-cart"></i>
            {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="marketplace-nav">
        <div className="marketplace-nav-container">
          <a href="#ai" className="marketplace-nav-link">AI추천</a>
          <a href="#local" className="marketplace-nav-link">지자체(아산시)</a>
          <a href="#birthday" className="marketplace-nav-link">생일쿠폰</a>
          <a href="#hope" className="marketplace-nav-link">희망나눔</a>
          <a href="#best" className="marketplace-nav-link">베스트</a>
          <a href="#special" className="marketplace-nav-link">특가</a>
          <a href="#specialty" className="marketplace-nav-link">특산물</a>
          <a href="#traditional" className="marketplace-nav-link">전통시장</a>
        </div>
      </nav>

      {/* Main Content */}
      <main className="marketplace-main">
        {/* Filters */}
        <section className="marketplace-filters">
          <div className="filters-row">
            <div className="filter-group">
              <label>카테고리</label>
              <select
                className="filter-select"
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              >
                <option value="">전체 카테고리</option>
                <option value="채소">채소</option>
                <option value="과일">과일</option>
                <option value="곡물">곡물</option>
                <option value="축산물">축산물</option>
              </select>
            </div>

            <div className="filter-group">
              <label>지역</label>
              <select
                className="filter-select"
                value={filters.location}
                onChange={(e) => setFilters({ ...filters, location: e.target.value })}
              >
                <option value="">전체 지역</option>
                <option value="경기도">경기도</option>
                <option value="강원도">강원도</option>
                <option value="충청도">충청도</option>
                <option value="전라도">전라도</option>
                <option value="경상도">경상도</option>
              </select>
            </div>

            <div className="filter-group">
              <label>최대 거리</label>
              <select
                className="filter-select"
                value={filters.distance}
                onChange={(e) => setFilters({ ...filters, distance: e.target.value })}
              >
                <option value="">제한 없음</option>
                <option value="10">10km 이내</option>
                <option value="30">30km 이내</option>
                <option value="50">50km 이내</option>
                <option value="100">100km 이내</option>
              </select>
            </div>
          </div>
        </section>

        {/* Products Header */}
        <div className="products-header">
          <div className="products-count">
            총 <strong>{filteredProducts.length}</strong>개 상품
          </div>
          <select
            className="sort-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="newest">최신순</option>
            <option value="price_low">가격 낮은 순</option>
            <option value="price_high">가격 높은 순</option>
            <option value="distance">가까운 거리순</option>
            <option value="eco_friendly">친환경 순</option>
            <option value="popular">인기순</option>
          </select>
        </div>

        {/* Products Grid */}
        <div className="products-grid">
          {filteredProducts.length === 0 ? (
            <div className="loading">조건에 맞는 상품이 없습니다.</div>
          ) : (
            filteredProducts.map(product => (
              <div key={product.product_id} className="product-card">
                <div className="product-image">
                  <img src={product.image} alt={product.name} />
                  <div className="farmer-badge">
                    <i className="fas fa-user"></i> {product.farmer_name}
                  </div>
                  <div className="eco-badge">
                    -{product.carbon_footprint}kg CO₂
                  </div>
                </div>
                <div className="product-info">
                  <h3 className="product-name">{product.name}</h3>
                  <div className="product-farmer">
                    <i className="fas fa-seedling"></i>
                    {product.farmer_name}
                  </div>
                  <div className="product-location">
                    <i className="fas fa-map-marker-alt"></i>
                    {product.location} · {product.distance_km}km
                  </div>

                  <div className="product-price">
                    {product.price_per_kg.toLocaleString()}원
                    <span className="unit">/kg</span>
                  </div>

                  <div className="eco-impact">
                    <div className="eco-stats">
                      <div className="eco-stat">
                        <span className="eco-value">{product.available_quantity}kg</span>
                        <small>재고</small>
                      </div>
                      <div className="eco-stat">
                        <span className="eco-value">{product.certifications}</span>
                        <small>인증</small>
                      </div>
                      <div className="eco-stat">
                        <span className="eco-value">{product.likes}</span>
                        <small>좋아요</small>
                      </div>
                    </div>
                  </div>

                  <div className="product-actions">
                    <button
                      className="btn btn-like"
                      onClick={() => likeProduct(product.product_id)}
                    >
                      <i className="far fa-heart"></i>
                    </button>
                    <button
                      className="btn btn-cart"
                      onClick={() => addToCart(product)}
                    >
                      <i className="fas fa-cart-plus"></i>
                      담기
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </main>

      {/* Cart Overlay */}
      <div
        className={`cart-overlay ${cartOpen ? 'show' : ''}`}
        onClick={toggleCart}
      ></div>

      {/* Cart Sidebar */}
      <div className={`cart-sidebar ${cartOpen ? 'open' : ''}`}>
        <div className="cart-header">
          <h3>장바구니</h3>
          <button className="cart-close" onClick={toggleCart}>
            <i className="fas fa-times"></i>
          </button>
        </div>

        <div className="cart-items">
          {cart.length === 0 ? (
            <div className="loading">장바구니가 비어있습니다</div>
          ) : (
            cart.map(item => (
              <div key={item.product_id} className="cart-item">
                <div className="cart-item-image">
                  <img src={item.image} alt={item.name} />
                </div>
                <div className="cart-item-info">
                  <div className="cart-item-name">{item.name}</div>
                  <div className="cart-item-farmer">
                    <i className="fas fa-seedling"></i> {item.farmer_name}
                  </div>
                  <div className="cart-item-controls">
                    <button
                      className="qty-btn"
                      onClick={() => updateQuantity(item.product_id, -1)}
                    >
                      -
                    </button>
                    <input
                      type="number"
                      className="qty-input"
                      value={item.quantity}
                      readOnly
                    />
                    <button
                      className="qty-btn"
                      onClick={() => updateQuantity(item.product_id, 1)}
                    >
                      +
                    </button>
                    <div style={{ marginLeft: 'auto', fontWeight: 'bold' }}>
                      {(item.price_per_kg * item.quantity).toLocaleString()}원
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="cart-summary">
          <div className="cart-total">
            총 금액: {cartTotal.toLocaleString()}원
          </div>

          {/* 결제 방법 선택 */}
          <div className="payment-method-selector">
            <label className="payment-method-label">결제 수단:</label>
            <div className="payment-methods">
              <label className={`payment-option ${paymentMethod === 'cash' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="payment"
                  value="cash"
                  checked={paymentMethod === 'cash'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                />
                <span>💵 현금</span>
              </label>
              <label className={`payment-option ${paymentMethod === 'token' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="payment"
                  value="token"
                  checked={paymentMethod === 'token'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  disabled={!wallet || !wallet.esgGoldAssetId}
                />
                <span>🪙 ESG-GOLD</span>
              </label>
            </div>
            {paymentMethod === 'token' && (
              <div className="token-price-info">
                약 {Math.ceil(cartTotal / 100).toLocaleString()} ESGOLD 필요
              </div>
            )}
            {!wallet && paymentMethod === 'token' && (
              <div className="payment-warning">
                ⚠️ 지갑이 없습니다. <Link to="/wallet">지갑 생성하기 →</Link>
              </div>
            )}
          </div>

          <button
            className="btn-checkout"
            onClick={checkout}
            disabled={paying}
          >
            {paying ? (
              <>⏳ 결제 중...</>
            ) : paymentMethod === 'token' ? (
              <>🪙 토큰으로 결제</>
            ) : (
              <>💳 주문하기</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default MarketplacePage;
