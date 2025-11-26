/**
 * Company Dashboard - Order Management & Supply Chain Analytics
 * 기업 대시보드 - 주문 관리 및 공급망 분석
 */

import React, { useState, useEffect } from 'react';
import './CompanyDashboard.css';

function CompanyDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalOrders: 0,
    totalSpending: 0,
    activeSuppliers: 0,
    avgDeliveryTime: 0
  });
  const [orders, setOrders] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = () => {
    // 데모 데이터 생성
    const demoOrders = generateDemoOrders();
    const demoSuppliers = generateDemoSuppliers();
    const demoInventory = generateDemoInventory();
    const demoPredictions = generateDemoPredictions();

    setOrders(demoOrders);
    setSuppliers(demoSuppliers);
    setInventory(demoInventory);
    setPredictions(demoPredictions);

    // 통계 계산
    const totalSpending = demoOrders
      .filter(o => o.status === 'completed')
      .reduce((sum, order) => sum + order.totalAmount, 0);

    const completedOrders = demoOrders.filter(o => o.status === 'completed');
    const avgDeliveryTime = completedOrders.length > 0
      ? completedOrders.reduce((sum, o) => sum + o.deliveryDays, 0) / completedOrders.length
      : 0;

    setStats({
      totalOrders: demoOrders.length,
      totalSpending,
      activeSuppliers: demoSuppliers.filter(s => s.status === 'active').length,
      avgDeliveryTime: avgDeliveryTime.toFixed(1)
    });
  };

  // 주문 생성
  const createOrder = () => {
    alert('📦 새 주문 생성 기능 (준비중)\n\n공급자 선택 → 제품 선택 → 수량 입력 → 주문 확정');
  };

  // 주문 취소
  const cancelOrder = (orderId) => {
    const order = orders.find(o => o.id === orderId);
    if (!order) return;

    if (!window.confirm(`주문 #${orderId}를 취소하시겠습니까?`)) return;

    const updated = orders.map(o =>
      o.id === orderId ? { ...o, status: 'cancelled' } : o
    );
    setOrders(updated);
    alert('✅ 주문이 취소되었습니다.');
  };

  // 주문 상세 모달
  const openOrderDetail = (order) => {
    setSelectedOrder(order);
  };

  const closeOrderDetail = () => {
    setSelectedOrder(null);
  };

  // 공급자 평가
  const rateSupplier = (supplierId, rating) => {
    alert(`공급자에게 ${rating}점을 평가했습니다.`);
  };

  return (
    <div className="company-dashboard">
      <div className="company-header">
        <h1>🏢 기업 대시보드</h1>
        <p>주문 관리 및 공급망 분석</p>
      </div>

      {/* 통계 카드 */}
      <div className="company-stats-grid">
        <div className="company-stat-card orders">
          <div className="company-stat-icon">📦</div>
          <div className="company-stat-content">
            <div className="company-stat-label">총 주문</div>
            <div className="company-stat-value">{stats.totalOrders}</div>
            <div className="company-stat-subtitle">건</div>
          </div>
        </div>
        <div className="company-stat-card spending">
          <div className="company-stat-icon">💰</div>
          <div className="company-stat-content">
            <div className="company-stat-label">총 구매금액</div>
            <div className="company-stat-value">₩{stats.totalSpending.toLocaleString()}</div>
            <div className="company-stat-subtitle">누적</div>
          </div>
        </div>
        <div className="company-stat-card suppliers">
          <div className="company-stat-icon">🤝</div>
          <div className="company-stat-content">
            <div className="company-stat-label">협력 공급자</div>
            <div className="company-stat-value">{stats.activeSuppliers}</div>
            <div className="company-stat-subtitle">개</div>
          </div>
        </div>
        <div className="company-stat-card delivery">
          <div className="company-stat-icon">🚚</div>
          <div className="company-stat-content">
            <div className="company-stat-label">평균 배송시간</div>
            <div className="company-stat-value">{stats.avgDeliveryTime}</div>
            <div className="company-stat-subtitle">일</div>
          </div>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="company-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          📊 대시보드
        </button>
        <button
          className={activeTab === 'orders' ? 'active' : ''}
          onClick={() => setActiveTab('orders')}
        >
          📦 주문 관리
        </button>
        <button
          className={activeTab === 'suppliers' ? 'active' : ''}
          onClick={() => setActiveTab('suppliers')}
        >
          🤝 공급자 관리
        </button>
        <button
          className={activeTab === 'inventory' ? 'active' : ''}
          onClick={() => setActiveTab('inventory')}
        >
          📋 재고 현황
        </button>
        <button
          className={activeTab === 'predictions' ? 'active' : ''}
          onClick={() => setActiveTab('predictions')}
        >
          🤖 수요 예측
        </button>
      </div>

      {/* 탭 컨텐츠 */}
      <div className="company-content">
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
                        {order.supplierName} • {order.items.length}개 제품
                      </div>
                    </div>
                    <div className="order-amount">₩{order.totalAmount.toLocaleString()}</div>
                    <div className={`order-status status-${order.status}`}>
                      {order.status === 'pending' && '⏳ 대기'}
                      {order.status === 'confirmed' && '✅ 확인'}
                      {order.status === 'shipped' && '🚚 배송중'}
                      {order.status === 'completed' && '✅ 완료'}
                      {order.status === 'cancelled' && '❌ 취소'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="overview-section">
              <h2>🏆 우수 공급자</h2>
              <div className="top-suppliers-grid">
                {suppliers
                  .sort((a, b) => b.rating - a.rating)
                  .slice(0, 3)
                  .map((supplier, index) => (
                    <div key={supplier.id} className="top-supplier-card">
                      <div className="supplier-rank">#{index + 1}</div>
                      <div className="supplier-image">
                        <img src={supplier.imageUrl} alt={supplier.name} />
                      </div>
                      <h3>{supplier.name}</h3>
                      <div className="supplier-rating">⭐ {supplier.rating}</div>
                      <div className="supplier-stats">
                        <div className="supplier-stat">
                          <span className="stat-label">총 거래</span>
                          <span className="stat-value">{supplier.totalOrders}건</span>
                        </div>
                        <div className="supplier-stat">
                          <span className="stat-label">배송 준수율</span>
                          <span className="stat-value">{supplier.onTimeRate}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            <div className="overview-section">
              <h2>📊 수요 예측 요약</h2>
              <div className="predictions-summary">
                {predictions.slice(0, 4).map(pred => (
                  <div key={pred.product} className="prediction-card">
                    <div className="prediction-product">{pred.product}</div>
                    <div className="prediction-value">
                      {pred.predictedDemand}kg
                      {pred.trend === 'up' && <span className="trend-up">📈 +{pred.change}%</span>}
                      {pred.trend === 'down' && <span className="trend-down">📉 -{pred.change}%</span>}
                      {pred.trend === 'stable' && <span className="trend-stable">➡️ 유지</span>}
                    </div>
                    <div className="prediction-recommendation">{pred.recommendation}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 주문 관리 탭 */}
        {activeTab === 'orders' && (
          <div className="orders-tab">
            <div className="orders-header">
              <h2>📦 주문 목록</h2>
              <button className="btn-create-order" onClick={createOrder}>
                + 새 주문 생성
              </button>
            </div>
            <div className="orders-table">
              <table>
                <thead>
                  <tr>
                    <th>주문번호</th>
                    <th>공급자</th>
                    <th>제품</th>
                    <th>수량</th>
                    <th>금액</th>
                    <th>주문일</th>
                    <th>배송예정</th>
                    <th>상태</th>
                    <th>작업</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(order => (
                    <tr key={order.id}>
                      <td className="order-id">#{order.id}</td>
                      <td>{order.supplierName}</td>
                      <td>
                        {order.items.map(item => item.productName).join(', ')}
                      </td>
                      <td>
                        {order.items.reduce((sum, item) => sum + item.quantity, 0)}kg
                      </td>
                      <td className="amount">₩{order.totalAmount.toLocaleString()}</td>
                      <td>{new Date(order.orderDate).toLocaleDateString('ko-KR')}</td>
                      <td>
                        {order.deliveryDate
                          ? new Date(order.deliveryDate).toLocaleDateString('ko-KR')
                          : '-'}
                      </td>
                      <td>
                        <span className={`status-badge ${order.status}`}>
                          {order.status === 'pending' && '⏳ 대기'}
                          {order.status === 'confirmed' && '✅ 확인'}
                          {order.status === 'shipped' && '🚚 배송중'}
                          {order.status === 'completed' && '✅ 완료'}
                          {order.status === 'cancelled' && '❌ 취소'}
                        </span>
                      </td>
                      <td>
                        <button
                          className="btn-view-order"
                          onClick={() => openOrderDetail(order)}
                        >
                          보기
                        </button>
                        {order.status === 'pending' && (
                          <button
                            className="btn-cancel-order"
                            onClick={() => cancelOrder(order.id)}
                          >
                            취소
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

        {/* 공급자 관리 탭 */}
        {activeTab === 'suppliers' && (
          <div className="suppliers-tab">
            <h2>🤝 공급자 목록</h2>
            <div className="suppliers-grid">
              {suppliers.map(supplier => (
                <div key={supplier.id} className="supplier-card">
                  <div className="supplier-card-header">
                    <img src={supplier.imageUrl} alt={supplier.name} />
                    <div className="supplier-badge-container">
                      <span className={`supplier-status ${supplier.status}`}>
                        {supplier.status === 'active' ? '🟢 활성' : '🔴 비활성'}
                      </span>
                    </div>
                  </div>
                  <div className="supplier-card-body">
                    <h3>{supplier.name}</h3>
                    <p className="supplier-category">{supplier.category}</p>
                    <div className="supplier-rating-display">
                      ⭐ {supplier.rating} / 5.0
                    </div>
                    <div className="supplier-info-grid">
                      <div className="info-item">
                        <span className="info-label">총 거래</span>
                        <span className="info-value">{supplier.totalOrders}건</span>
                      </div>
                      <div className="info-item">
                        <span className="info-label">배송 준수율</span>
                        <span className="info-value">{supplier.onTimeRate}%</span>
                      </div>
                      <div className="info-item">
                        <span className="info-label">제품 종류</span>
                        <span className="info-value">{supplier.productCount}개</span>
                      </div>
                      <div className="info-item">
                        <span className="info-label">평균 배송</span>
                        <span className="info-value">{supplier.avgDelivery}일</span>
                      </div>
                    </div>
                  </div>
                  <div className="supplier-card-actions">
                    <button
                      className="btn-supplier-order"
                      onClick={() => alert(`${supplier.name}에게 주문하기 (준비중)`)}
                    >
                      주문하기
                    </button>
                    <button
                      className="btn-supplier-rate"
                      onClick={() => rateSupplier(supplier.id, 5)}
                    >
                      평가하기
                    </button>
                  </div>
                </div>
              ))}
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
                    <th>안전 재고</th>
                    <th>상태</th>
                    <th>다음 입고 예정</th>
                    <th>공급자</th>
                  </tr>
                </thead>
                <tbody>
                  {inventory.map(item => {
                    const stockStatus = item.currentStock < item.safetyStock
                      ? 'critical'
                      : item.currentStock < item.safetyStock * 1.5
                      ? 'warning'
                      : 'good';

                    return (
                      <tr key={item.id}>
                        <td>
                          <div className="product-cell">
                            <img
                              src={item.imageUrl}
                              alt={item.productName}
                              className="product-thumb"
                            />
                            <span>{item.productName}</span>
                          </div>
                        </td>
                        <td>{item.category}</td>
                        <td className="stock-value">{item.currentStock}kg</td>
                        <td>{item.safetyStock}kg</td>
                        <td>
                          <span className={`stock-status ${stockStatus}`}>
                            {stockStatus === 'critical' && '🔴 긴급'}
                            {stockStatus === 'warning' && '🟡 주의'}
                            {stockStatus === 'good' && '🟢 정상'}
                          </span>
                        </td>
                        <td>
                          {item.nextDelivery
                            ? new Date(item.nextDelivery).toLocaleDateString('ko-KR')
                            : '미정'}
                        </td>
                        <td>{item.supplierName}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 수요 예측 탭 */}
        {activeTab === 'predictions' && (
          <div className="predictions-tab">
            <div className="predictions-header">
              <h2>🤖 AI 수요 예측</h2>
              <div className="predictions-info">
                <span className="info-badge">📊 LSTM 모델 사용</span>
                <span className="info-badge">🎯 평균 정확도 85%</span>
              </div>
            </div>

            <div className="predictions-list">
              {predictions.map(pred => (
                <div key={pred.product} className="prediction-detail-card">
                  <div className="prediction-header">
                    <h3>{pred.product}</h3>
                    <span className={`trend-badge trend-${pred.trend}`}>
                      {pred.trend === 'up' && '📈 상승'}
                      {pred.trend === 'down' && '📉 하락'}
                      {pred.trend === 'stable' && '➡️ 안정'}
                    </span>
                  </div>
                  <div className="prediction-body">
                    <div className="prediction-metrics">
                      <div className="metric">
                        <span className="metric-label">예측 수요</span>
                        <span className="metric-value">{pred.predictedDemand}kg</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">현재 재고</span>
                        <span className="metric-value">{pred.currentStock}kg</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">변동률</span>
                        <span className={`metric-value ${pred.trend === 'up' ? 'increase' : 'decrease'}`}>
                          {pred.trend === 'up' ? '+' : pred.trend === 'down' ? '-' : ''}
                          {pred.change}%
                        </span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">권장 주문량</span>
                        <span className="metric-value highlight">{pred.recommendedOrder}kg</span>
                      </div>
                    </div>
                    <div className="prediction-recommendation-box">
                      <div className="recommendation-icon">💡</div>
                      <div className="recommendation-text">{pred.recommendation}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="predictions-footer">
              <button className="btn-run-prediction">
                🔄 예측 모델 재실행
              </button>
              <button className="btn-export-predictions">
                📥 예측 결과 내보내기
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 주문 상세 모달 */}
      {selectedOrder && (
        <div className="order-modal-overlay" onClick={closeOrderDetail}>
          <div className="order-modal" onClick={(e) => e.stopPropagation()}>
            <div className="order-modal-header">
              <h2>주문 상세 정보 #{selectedOrder.id}</h2>
              <button className="modal-close" onClick={closeOrderDetail}>✕</button>
            </div>
            <div className="order-modal-body">
              <div className="order-section">
                <h3>주문 정보</h3>
                <div className="order-info-grid">
                  <div className="info-row">
                    <span className="info-label">공급자:</span>
                    <span>{selectedOrder.supplierName}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">주문일:</span>
                    <span>{new Date(selectedOrder.orderDate).toLocaleString('ko-KR')}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">배송예정일:</span>
                    <span>
                      {selectedOrder.deliveryDate
                        ? new Date(selectedOrder.deliveryDate).toLocaleDateString('ko-KR')
                        : '미정'}
                    </span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">상태:</span>
                    <span className={`status-badge ${selectedOrder.status}`}>
                      {selectedOrder.status === 'pending' && '⏳ 대기'}
                      {selectedOrder.status === 'confirmed' && '✅ 확인'}
                      {selectedOrder.status === 'shipped' && '🚚 배송중'}
                      {selectedOrder.status === 'completed' && '✅ 완료'}
                      {selectedOrder.status === 'cancelled' && '❌ 취소'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="order-section">
                <h3>주문 상품</h3>
                <div className="order-items">
                  {selectedOrder.items.map((item, index) => (
                    <div key={index} className="order-item">
                      <span className="item-name">{item.productName}</span>
                      <span className="item-quantity">{item.quantity}kg</span>
                      <span className="item-price">₩{item.price.toLocaleString()}</span>
                      <span className="item-total">
                        ₩{(item.quantity * item.price).toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="order-section">
                <h3>결제 정보</h3>
                <div className="payment-summary">
                  <div className="payment-row">
                    <span>상품 금액:</span>
                    <span>₩{selectedOrder.totalAmount.toLocaleString()}</span>
                  </div>
                  <div className="payment-row">
                    <span>배송비:</span>
                    <span>₩0</span>
                  </div>
                  <div className="payment-row total">
                    <span>총 결제 금액:</span>
                    <span>₩{selectedOrder.totalAmount.toLocaleString()}</span>
                  </div>
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
function generateDemoOrders() {
  return [
    {
      id: 'CO1001',
      supplierName: '그린팜',
      items: [
        { productName: '유기농 토마토', quantity: 50, price: 8500 }
      ],
      totalAmount: 425000,
      orderDate: new Date(Date.now() - 86400000 * 2).toISOString(),
      deliveryDate: new Date(Date.now() + 86400000 * 1).toISOString(),
      deliveryDays: 3,
      status: 'shipped'
    },
    {
      id: 'CO1002',
      supplierName: '에코팜',
      items: [
        { productName: '친환경 상추', quantity: 30, price: 5000 },
        { productName: '유기농 당근', quantity: 40, price: 4500 }
      ],
      totalAmount: 330000,
      orderDate: new Date(Date.now() - 86400000 * 1).toISOString(),
      deliveryDate: new Date(Date.now() + 86400000 * 2).toISOString(),
      deliveryDays: 3,
      status: 'confirmed'
    },
    {
      id: 'CO1003',
      supplierName: '바이오농장',
      items: [
        { productName: '유기농 쌀', quantity: 100, price: 45000 }
      ],
      totalAmount: 4500000,
      orderDate: new Date(Date.now() - 86400000 * 10).toISOString(),
      deliveryDate: new Date(Date.now() - 86400000 * 5).toISOString(),
      deliveryDays: 5,
      status: 'completed'
    },
    {
      id: 'CO1004',
      supplierName: '그린팜',
      items: [
        { productName: '친환경 배추', quantity: 60, price: 6000 }
      ],
      totalAmount: 360000,
      orderDate: new Date(Date.now() - 86400000).toISOString(),
      deliveryDate: null,
      deliveryDays: 0,
      status: 'pending'
    }
  ];
}

function generateDemoSuppliers() {
  return [
    {
      id: 'SUP001',
      name: '그린팜',
      category: '과채류 전문',
      rating: 4.9,
      totalOrders: 156,
      onTimeRate: 98,
      productCount: 12,
      avgDelivery: 2,
      status: 'active',
      imageUrl: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=300&h=300&fit=crop'
    },
    {
      id: 'SUP002',
      name: '에코팜',
      category: '엽채류 전문',
      rating: 4.8,
      totalOrders: 203,
      onTimeRate: 95,
      productCount: 18,
      avgDelivery: 3,
      status: 'active',
      imageUrl: 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=300&h=300&fit=crop'
    },
    {
      id: 'SUP003',
      name: '바이오농장',
      category: '곡물 전문',
      rating: 5.0,
      totalOrders: 89,
      onTimeRate: 100,
      productCount: 6,
      avgDelivery: 5,
      status: 'active',
      imageUrl: 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=300&h=300&fit=crop'
    },
    {
      id: 'SUP004',
      name: '프레시마켓',
      category: '종합',
      rating: 4.6,
      totalOrders: 312,
      onTimeRate: 92,
      productCount: 25,
      avgDelivery: 2,
      status: 'active',
      imageUrl: 'https://images.unsplash.com/photo-1488459716781-31db52582fe9?w=300&h=300&fit=crop'
    }
  ];
}

function generateDemoInventory() {
  return [
    {
      id: 'INV001',
      productName: '유기농 토마토',
      category: '과채류',
      currentStock: 45,
      safetyStock: 80,
      nextDelivery: new Date(Date.now() + 86400000).toISOString(),
      supplierName: '그린팜',
      imageUrl: 'https://images.unsplash.com/photo-1546470427-e26264592e6f?w=100&h=100&fit=crop'
    },
    {
      id: 'INV002',
      productName: '친환경 상추',
      category: '엽채류',
      currentStock: 120,
      safetyStock: 100,
      nextDelivery: new Date(Date.now() + 86400000 * 2).toISOString(),
      supplierName: '에코팜',
      imageUrl: 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=100&h=100&fit=crop'
    },
    {
      id: 'INV003',
      productName: '유기농 당근',
      category: '근채류',
      currentStock: 200,
      safetyStock: 150,
      nextDelivery: new Date(Date.now() + 86400000 * 2).toISOString(),
      supplierName: '에코팜',
      imageUrl: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=100&h=100&fit=crop'
    },
    {
      id: 'INV004',
      productName: '유기농 쌀',
      category: '곡물',
      currentStock: 800,
      safetyStock: 500,
      nextDelivery: new Date(Date.now() + 86400000 * 7).toISOString(),
      supplierName: '바이오농장',
      imageUrl: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=100&h=100&fit=crop'
    }
  ];
}

function generateDemoPredictions() {
  return [
    {
      product: '유기농 토마토',
      predictedDemand: 350,
      currentStock: 45,
      change: 15,
      trend: 'up',
      recommendedOrder: 300,
      recommendation: '여름철 수요 증가 예상. 재고 부족이 예상되므로 조기 발주를 권장합니다.'
    },
    {
      product: '친환경 상추',
      predictedDemand: 280,
      currentStock: 120,
      change: 8,
      trend: 'up',
      recommendedOrder: 200,
      recommendation: '안정적인 수요 증가 추세. 현재 재고 수준을 고려하여 적정량 발주가 필요합니다.'
    },
    {
      product: '유기농 당근',
      predictedDemand: 250,
      currentStock: 200,
      change: 5,
      trend: 'down',
      recommendedOrder: 100,
      recommendation: '소폭 수요 감소 예상. 과다 재고 방지를 위해 발주량 조정이 필요합니다.'
    },
    {
      product: '유기농 쌀',
      predictedDemand: 1200,
      currentStock: 800,
      change: 2,
      trend: 'stable',
      recommendedOrder: 500,
      recommendation: '안정적인 수요 유지. 정기 발주 패턴을 유지하시면 됩니다.'
    },
    {
      product: '친환경 배추',
      predictedDemand: 420,
      currentStock: 180,
      change: 22,
      trend: 'up',
      recommendedOrder: 400,
      recommendation: '김장철 수요 급증 예상. 대량 발주 및 추가 공급자 확보를 검토하세요.'
    }
  ];
}

export default CompanyDashboard;
