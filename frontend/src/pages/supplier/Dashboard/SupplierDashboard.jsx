/**
 * Supplier Dashboard - Product Management & Sales Analytics
 * 공급자 대시보드 - 제품 관리 및 판매 분석
 */

import React, { useState, useEffect } from 'react';
import './SupplierDashboard.css';

function SupplierDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalRevenue: 0,
    totalOrders: 0,
    activeProducts: 0,
    avgRating: 0
  });
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [salesData, setSalesData] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = () => {
    // 데모 데이터 생성
    const demoProducts = generateDemoProducts();
    const demoOrders = generateDemoOrders();
    const demoSalesData = generateDemoSalesData();

    setProducts(demoProducts);
    setOrders(demoOrders);
    setSalesData(demoSalesData);

    // 통계 계산
    const totalRevenue = demoOrders
      .filter(o => o.status === 'completed')
      .reduce((sum, order) => sum + order.totalAmount, 0);

    const avgRating = demoProducts.reduce((sum, p) => sum + p.rating, 0) / demoProducts.length;

    setStats({
      totalRevenue,
      totalOrders: demoOrders.length,
      activeProducts: demoProducts.filter(p => p.stock > 0).length,
      avgRating: avgRating.toFixed(1)
    });
  };

  // 제품 재고 업데이트
  const updateStock = (productId, newStock) => {
    if (!window.confirm('재고를 업데이트하시겠습니까?')) return;

    const updated = products.map(p =>
      p.id === productId ? { ...p, stock: parseInt(newStock) } : p
    );
    setProducts(updated);
    alert('✅ 재고가 업데이트되었습니다.');
  };

  // 주문 상태 변경
  const updateOrderStatus = (orderId, newStatus) => {
    const order = orders.find(o => o.id === orderId);
    if (!order) return;

    if (!window.confirm(`주문 상태를 "${newStatus}"로 변경하시겠습니까?`)) return;

    const updated = orders.map(o =>
      o.id === orderId ? { ...o, status: newStatus } : o
    );
    setOrders(updated);
    alert('✅ 주문 상태가 업데이트되었습니다.');
  };

  // 제품 상세 모달 열기
  const openProductDetail = (product) => {
    setSelectedProduct(product);
  };

  const closeProductDetail = () => {
    setSelectedProduct(null);
  };

  return (
    <div className="supplier-dashboard">
      <div className="supplier-header">
        <h1>🌾 공급자 대시보드</h1>
        <p>제품 관리 및 판매 분석</p>
      </div>

      {/* 통계 카드 */}
      <div className="supplier-stats-grid">
        <div className="supplier-stat-card revenue">
          <div className="supplier-stat-icon">💰</div>
          <div className="supplier-stat-content">
            <div className="supplier-stat-label">총 매출</div>
            <div className="supplier-stat-value">₩{stats.totalRevenue.toLocaleString()}</div>
            <div className="supplier-stat-subtitle">누적</div>
          </div>
        </div>
        <div className="supplier-stat-card orders">
          <div className="supplier-stat-icon">📦</div>
          <div className="supplier-stat-content">
            <div className="supplier-stat-label">총 주문</div>
            <div className="supplier-stat-value">{stats.totalOrders}</div>
            <div className="supplier-stat-subtitle">건</div>
          </div>
        </div>
        <div className="supplier-stat-card products">
          <div className="supplier-stat-icon">🥬</div>
          <div className="supplier-stat-content">
            <div className="supplier-stat-label">판매중인 제품</div>
            <div className="supplier-stat-value">{stats.activeProducts}</div>
            <div className="supplier-stat-subtitle">개</div>
          </div>
        </div>
        <div className="supplier-stat-card rating">
          <div className="supplier-stat-icon">⭐</div>
          <div className="supplier-stat-content">
            <div className="supplier-stat-label">평균 평점</div>
            <div className="supplier-stat-value">{stats.avgRating}</div>
            <div className="supplier-stat-subtitle">/ 5.0</div>
          </div>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="supplier-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          📊 대시보드
        </button>
        <button
          className={activeTab === 'products' ? 'active' : ''}
          onClick={() => setActiveTab('products')}
        >
          🥬 제품 관리
        </button>
        <button
          className={activeTab === 'orders' ? 'active' : ''}
          onClick={() => setActiveTab('orders')}
        >
          📦 주문 관리
        </button>
        <button
          className={activeTab === 'sales' ? 'active' : ''}
          onClick={() => setActiveTab('sales')}
        >
          📈 판매 분석
        </button>
        <button
          className={activeTab === 'inventory' ? 'active' : ''}
          onClick={() => setActiveTab('inventory')}
        >
          📋 재고 현황
        </button>
      </div>

      {/* 탭 컨텐츠 */}
      <div className="supplier-content">
        {/* 대시보드 탭 */}
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="overview-section">
              <h2>📦 최근 주문</h2>
              <div className="recent-orders">
                {orders.slice(0, 5).map(order => (
                  <div key={order.id} className="recent-order-item">
                    <div className="order-icon">📦</div>
                    <div className="order-details">
                      <div className="order-title">주문 #{order.id}</div>
                      <div className="order-meta">
                        {order.customerName} • {order.items.length}개 제품
                      </div>
                    </div>
                    <div className="order-amount">₩{order.totalAmount.toLocaleString()}</div>
                    <div className={`order-status status-${order.status}`}>
                      {order.status === 'pending' && '⏳ 대기'}
                      {order.status === 'processing' && '🔄 처리중'}
                      {order.status === 'shipped' && '🚚 배송중'}
                      {order.status === 'completed' && '✅ 완료'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="overview-section">
              <h2>⚠️ 재고 알림</h2>
              {products.filter(p => p.stock < p.minStock).length === 0 ? (
                <p className="empty-message">재고 부족 제품이 없습니다.</p>
              ) : (
                <div className="low-stock-alerts">
                  {products.filter(p => p.stock < p.minStock).map(product => (
                    <div key={product.id} className="low-stock-alert">
                      <div className="alert-icon">⚠️</div>
                      <div className="alert-details">
                        <div className="alert-title">{product.name}</div>
                        <div className="alert-meta">
                          현재 재고: {product.stock}kg / 최소 재고: {product.minStock}kg
                        </div>
                      </div>
                      <button
                        className="btn-restock"
                        onClick={() => updateStock(product.id, product.minStock * 2)}
                      >
                        재입고
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="overview-section">
              <h2>🏆 베스트셀러</h2>
              <div className="bestseller-grid">
                {products
                  .sort((a, b) => b.soldCount - a.soldCount)
                  .slice(0, 3)
                  .map((product, index) => (
                    <div key={product.id} className="bestseller-card">
                      <div className="bestseller-rank">#{index + 1}</div>
                      <div className="bestseller-image">
                        <img src={product.imageUrl} alt={product.name} />
                      </div>
                      <h3>{product.name}</h3>
                      <div className="bestseller-stats">
                        <div className="stat">
                          <span className="stat-label">판매량</span>
                          <span className="stat-value">{product.soldCount}kg</span>
                        </div>
                        <div className="stat">
                          <span className="stat-label">평점</span>
                          <span className="stat-value">⭐ {product.rating}</span>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* 제품 관리 탭 */}
        {activeTab === 'products' && (
          <div className="products-tab">
            <div className="products-header">
              <h2>🥬 제품 목록</h2>
              <button className="btn-add-product">+ 새 제품 추가</button>
            </div>
            <div className="products-grid">
              {products.map(product => (
                <div key={product.id} className="product-card">
                  <div className="product-image">
                    <img src={product.imageUrl} alt={product.name} />
                    {product.stock < product.minStock && (
                      <div className="low-stock-badge">재고부족</div>
                    )}
                  </div>
                  <div className="product-info">
                    <h3>{product.name}</h3>
                    <p className="product-category">{product.category}</p>
                    <div className="product-price">₩{product.price.toLocaleString()}/kg</div>
                    <div className="product-rating">
                      ⭐ {product.rating} ({product.reviewCount}개 리뷰)
                    </div>
                  </div>
                  <div className="product-stock-info">
                    <div className="stock-row">
                      <span>재고:</span>
                      <span className={product.stock < product.minStock ? 'low-stock' : ''}>
                        {product.stock}kg
                      </span>
                    </div>
                    <div className="stock-row">
                      <span>판매:</span>
                      <span>{product.soldCount}kg</span>
                    </div>
                  </div>
                  <div className="product-actions">
                    <button
                      className="btn-product-detail"
                      onClick={() => openProductDetail(product)}
                    >
                      상세보기
                    </button>
                    <button
                      className="btn-product-edit"
                      onClick={() => alert('제품 수정 기능 (준비중)')}
                    >
                      수정
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 주문 관리 탭 */}
        {activeTab === 'orders' && (
          <div className="orders-tab">
            <h2>📦 주문 관리</h2>
            <div className="orders-table">
              <table>
                <thead>
                  <tr>
                    <th>주문번호</th>
                    <th>고객명</th>
                    <th>제품</th>
                    <th>수량</th>
                    <th>금액</th>
                    <th>주문일시</th>
                    <th>상태</th>
                    <th>작업</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(order => (
                    <tr key={order.id}>
                      <td className="order-id">#{order.id}</td>
                      <td>{order.customerName}</td>
                      <td>
                        {order.items.map(item => item.productName).join(', ')}
                      </td>
                      <td>
                        {order.items.reduce((sum, item) => sum + item.quantity, 0)}kg
                      </td>
                      <td className="amount">₩{order.totalAmount.toLocaleString()}</td>
                      <td>{new Date(order.orderDate).toLocaleString('ko-KR')}</td>
                      <td>
                        <span className={`status-badge ${order.status}`}>
                          {order.status === 'pending' && '⏳ 대기'}
                          {order.status === 'processing' && '🔄 처리중'}
                          {order.status === 'shipped' && '🚚 배송중'}
                          {order.status === 'completed' && '✅ 완료'}
                        </span>
                      </td>
                      <td>
                        {order.status === 'pending' && (
                          <button
                            className="btn-process"
                            onClick={() => updateOrderStatus(order.id, 'processing')}
                          >
                            처리
                          </button>
                        )}
                        {order.status === 'processing' && (
                          <button
                            className="btn-ship"
                            onClick={() => updateOrderStatus(order.id, 'shipped')}
                          >
                            배송
                          </button>
                        )}
                        {order.status === 'shipped' && (
                          <button
                            className="btn-complete"
                            onClick={() => updateOrderStatus(order.id, 'completed')}
                          >
                            완료
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 판매 분석 탭 */}
        {activeTab === 'sales' && (
          <div className="sales-tab">
            <h2>📈 판매 분석</h2>

            <div className="sales-chart-section">
              <h3>월별 매출 추이</h3>
              <div className="sales-chart">
                <div className="chart-bars">
                  {salesData.map((data, index) => (
                    <div key={index} className="chart-bar-wrapper">
                      <div
                        className="chart-bar"
                        style={{ height: `${(data.revenue / 5000000) * 100}%` }}
                      >
                        <span className="bar-value">
                          ₩{(data.revenue / 1000000).toFixed(1)}M
                        </span>
                      </div>
                      <span className="bar-label">{data.month}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="sales-breakdown">
              <h3>제품별 매출</h3>
              <div className="product-sales-list">
                {products
                  .sort((a, b) => (b.soldCount * b.price) - (a.soldCount * a.price))
                  .map(product => {
                    const revenue = product.soldCount * product.price;
                    const maxRevenue = Math.max(
                      ...products.map(p => p.soldCount * p.price)
                    );
                    const percentage = (revenue / maxRevenue) * 100;

                    return (
                      <div key={product.id} className="product-sales-item">
                        <div className="product-sales-info">
                          <span className="product-name">{product.name}</span>
                          <span className="product-sales-value">
                            ₩{revenue.toLocaleString()}
                          </span>
                        </div>
                        <div className="product-sales-bar">
                          <div
                            className="product-sales-fill"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        )}

        {/* 재고 현황 탭 */}
        {activeTab === 'inventory' && (
          <div className="inventory-tab">
            <h2>📋 재고 현황</h2>
            <div className="inventory-table">
              <table>
                <thead>
                  <tr>
                    <th>제품명</th>
                    <th>카테고리</th>
                    <th>현재 재고</th>
                    <th>최소 재고</th>
                    <th>상태</th>
                    <th>판매량</th>
                    <th>작업</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(product => {
                    const stockStatus = product.stock < product.minStock
                      ? 'critical'
                      : product.stock < product.minStock * 1.5
                      ? 'warning'
                      : 'good';

                    return (
                      <tr key={product.id}>
                        <td>
                          <div className="product-cell">
                            <img
                              src={product.imageUrl}
                              alt={product.name}
                              className="product-thumb"
                            />
                            <span>{product.name}</span>
                          </div>
                        </td>
                        <td>{product.category}</td>
                        <td className="stock-cell">
                          <input
                            type="number"
                            value={product.stock}
                            onChange={(e) =>
                              setProducts(
                                products.map(p =>
                                  p.id === product.id
                                    ? { ...p, stock: parseInt(e.target.value) || 0 }
                                    : p
                                )
                              )
                            }
                            className="stock-input"
                          />
                          kg
                        </td>
                        <td>{product.minStock}kg</td>
                        <td>
                          <span className={`stock-status ${stockStatus}`}>
                            {stockStatus === 'critical' && '🔴 부족'}
                            {stockStatus === 'warning' && '🟡 주의'}
                            {stockStatus === 'good' && '🟢 정상'}
                          </span>
                        </td>
                        <td>{product.soldCount}kg</td>
                        <td>
                          <button
                            className="btn-update-stock"
                            onClick={() => updateStock(product.id, product.stock)}
                          >
                            업데이트
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* 제품 상세 모달 */}
      {selectedProduct && (
        <div className="product-modal-overlay" onClick={closeProductDetail}>
          <div className="product-modal" onClick={(e) => e.stopPropagation()}>
            <div className="product-modal-header">
              <h2>{selectedProduct.name}</h2>
              <button className="modal-close" onClick={closeProductDetail}>✕</button>
            </div>
            <div className="product-modal-body">
              <div className="product-modal-image">
                <img src={selectedProduct.imageUrl} alt={selectedProduct.name} />
              </div>
              <div className="product-modal-details">
                <div className="detail-row">
                  <span className="detail-label">카테고리:</span>
                  <span>{selectedProduct.category}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">가격:</span>
                  <span>₩{selectedProduct.price.toLocaleString()}/kg</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">재고:</span>
                  <span>{selectedProduct.stock}kg</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">최소 재고:</span>
                  <span>{selectedProduct.minStock}kg</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">총 판매량:</span>
                  <span>{selectedProduct.soldCount}kg</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">평점:</span>
                  <span>⭐ {selectedProduct.rating} ({selectedProduct.reviewCount}개 리뷰)</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">총 매출:</span>
                  <span>
                    ₩{(selectedProduct.soldCount * selectedProduct.price).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// 데모 데이터 생성 함수들
function generateDemoProducts() {
  return [
    {
      id: 'PRD001',
      name: '유기농 토마토',
      category: '과채류',
      price: 8500,
      stock: 150,
      minStock: 100,
      soldCount: 1250,
      rating: 4.8,
      reviewCount: 234,
      imageUrl: 'https://images.unsplash.com/photo-1546470427-e26264592e6f?w=300&h=300&fit=crop'
    },
    {
      id: 'PRD002',
      name: '친환경 상추',
      category: '엽채류',
      price: 5000,
      stock: 45,
      minStock: 80,
      soldCount: 2100,
      rating: 4.9,
      reviewCount: 412,
      imageUrl: 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=300&h=300&fit=crop'
    },
    {
      id: 'PRD003',
      name: '유기농 당근',
      category: '근채류',
      price: 4500,
      stock: 200,
      minStock: 100,
      soldCount: 1800,
      rating: 4.7,
      reviewCount: 156,
      imageUrl: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=300&h=300&fit=crop'
    },
    {
      id: 'PRD004',
      name: '친환경 배추',
      category: '엽채류',
      price: 6000,
      stock: 120,
      minStock: 100,
      soldCount: 980,
      rating: 4.6,
      reviewCount: 89,
      imageUrl: 'https://images.unsplash.com/photo-1597362925123-77861d3fbac7?w=300&h=300&fit=crop'
    },
    {
      id: 'PRD005',
      name: '유기농 쌀',
      category: '곡물',
      price: 45000,
      stock: 500,
      minStock: 300,
      soldCount: 3200,
      rating: 5.0,
      reviewCount: 678,
      imageUrl: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=300&h=300&fit=crop'
    },
    {
      id: 'PRD006',
      name: '친환경 오이',
      category: '과채류',
      price: 3500,
      stock: 80,
      minStock: 100,
      soldCount: 1450,
      rating: 4.5,
      reviewCount: 203,
      imageUrl: 'https://images.unsplash.com/photo-1568584711271-e25956f4f4ae?w=300&h=300&fit=crop'
    }
  ];
}

function generateDemoOrders() {
  const products = generateDemoProducts();
  return [
    {
      id: 'ORD1001',
      customerName: '김철수',
      items: [
        { productName: products[0].name, quantity: 10, price: products[0].price }
      ],
      totalAmount: 85000,
      orderDate: new Date(Date.now() - 1800000).toISOString(),
      status: 'pending'
    },
    {
      id: 'ORD1002',
      customerName: '이영희',
      items: [
        { productName: products[1].name, quantity: 5, price: products[1].price },
        { productName: products[2].name, quantity: 8, price: products[2].price }
      ],
      totalAmount: 61000,
      orderDate: new Date(Date.now() - 3600000).toISOString(),
      status: 'processing'
    },
    {
      id: 'ORD1003',
      customerName: '박민수',
      items: [
        { productName: products[4].name, quantity: 20, price: products[4].price }
      ],
      totalAmount: 900000,
      orderDate: new Date(Date.now() - 7200000).toISOString(),
      status: 'shipped'
    },
    {
      id: 'ORD1004',
      customerName: '정수연',
      items: [
        { productName: products[0].name, quantity: 5, price: products[0].price },
        { productName: products[3].name, quantity: 10, price: products[3].price }
      ],
      totalAmount: 102500,
      orderDate: new Date(Date.now() - 10800000).toISOString(),
      status: 'completed'
    },
    {
      id: 'ORD1005',
      customerName: '최동욱',
      items: [
        { productName: products[5].name, quantity: 15, price: products[5].price }
      ],
      totalAmount: 52500,
      orderDate: new Date(Date.now() - 14400000).toISOString(),
      status: 'completed'
    }
  ];
}

function generateDemoSalesData() {
  return [
    { month: '1월', revenue: 3200000 },
    { month: '2월', revenue: 3800000 },
    { month: '3월', revenue: 4200000 },
    { month: '4월', revenue: 3900000 },
    { month: '5월', revenue: 4500000 },
    { month: '6월', revenue: 4800000 }
  ];
}

export default SupplierDashboard;
