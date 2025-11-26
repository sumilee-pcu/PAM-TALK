/**
 * Farmer Dashboard - Production Management & Sales Overview
 * 농부 대시보드 - 생산 관리 및 판매 현황
 */

import React, { useState, useEffect } from 'react';
import './FarmerDashboard.css';

function FarmerDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalRevenue: 0,
    activeCrops: 0,
    pendingOrders: 0,
    esgReward: 0
  });
  const [crops, setCrops] = useState([]);
  const [sales, setSales] = useState([]);
  const [orders, setOrders] = useState([]);
  const [esgActivities, setEsgActivities] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = () => {
    // 데모 데이터 생성
    const demoCrops = generateDemoCrops();
    const demoSales = generateDemoSales();
    const demoOrders = generateDemoOrders();
    const demoEsgActivities = generateDemoEsgActivities();

    setCrops(demoCrops);
    setSales(demoSales);
    setOrders(demoOrders);
    setEsgActivities(demoEsgActivities);

    // 통계 계산
    const totalRevenue = demoSales.reduce((sum, sale) => sum + sale.revenue, 0);
    const pendingOrders = demoOrders.filter(o => o.status === 'pending').length;
    const esgReward = demoEsgActivities
      .filter(a => a.status === 'approved')
      .reduce((sum, a) => sum + a.reward, 0);

    setStats({
      totalRevenue,
      activeCrops: demoCrops.filter(c => c.status === 'growing').length,
      pendingOrders,
      esgReward
    });
  };

  // 작물 수확 기록
  const recordHarvest = (cropId, amount) => {
    const crop = crops.find(c => c.id === cropId);
    if (!crop) return;

    alert(`${crop.name} ${amount}kg 수확 기록 완료!`);
    const updated = crops.map(c =>
      c.id === cropId
        ? { ...c, harvestedAmount: c.harvestedAmount + amount }
        : c
    );
    setCrops(updated);
  };

  // 주문 확인
  const confirmOrder = (orderId) => {
    if (!window.confirm('이 주문을 확인하시겠습니까?')) return;

    const updated = orders.map(o =>
      o.id === orderId ? { ...o, status: 'confirmed' } : o
    );
    setOrders(updated);
    alert('✅ 주문이 확인되었습니다.');
  };

  // ESG 활동 등록
  const registerEsgActivity = () => {
    alert('🌱 ESG 활동 등록 기능 (준비중)\n\n친환경 농법, 재생에너지 사용 등을 등록할 수 있습니다.');
  };

  // 작물 상세 모달
  const openCropDetail = (crop) => {
    setSelectedCrop(crop);
  };

  const closeCropDetail = () => {
    setSelectedCrop(null);
  };

  return (
    <div className="farmer-dashboard">
      <div className="farmer-header">
        <h1>🌾 농부 대시보드</h1>
        <p>생산 관리 및 판매 현황</p>
      </div>

      {/* 통계 카드 */}
      <div className="farmer-stats-grid">
        <div className="farmer-stat-card revenue">
          <div className="farmer-stat-icon">💰</div>
          <div className="farmer-stat-content">
            <div className="farmer-stat-label">총 매출</div>
            <div className="farmer-stat-value">₩{stats.totalRevenue.toLocaleString()}</div>
            <div className="farmer-stat-subtitle">이번 달</div>
          </div>
        </div>
        <div className="farmer-stat-card crops">
          <div className="farmer-stat-icon">🌱</div>
          <div className="farmer-stat-content">
            <div className="farmer-stat-label">재배중인 작물</div>
            <div className="farmer-stat-value">{stats.activeCrops}</div>
            <div className="farmer-stat-subtitle">종류</div>
          </div>
        </div>
        <div className="farmer-stat-card orders">
          <div className="farmer-stat-icon">📦</div>
          <div className="farmer-stat-content">
            <div className="farmer-stat-label">대기중인 주문</div>
            <div className="farmer-stat-value">{stats.pendingOrders}</div>
            <div className="farmer-stat-subtitle">건</div>
          </div>
        </div>
        <div className="farmer-stat-card esg">
          <div className="farmer-stat-icon">🏆</div>
          <div className="farmer-stat-content">
            <div className="farmer-stat-label">ESG 보상</div>
            <div className="farmer-stat-value">{stats.esgReward}</div>
            <div className="farmer-stat-subtitle">DC</div>
          </div>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="farmer-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          📊 대시보드
        </button>
        <button
          className={activeTab === 'crops' ? 'active' : ''}
          onClick={() => setActiveTab('crops')}
        >
          🌱 작물 관리
        </button>
        <button
          className={activeTab === 'orders' ? 'active' : ''}
          onClick={() => setActiveTab('orders')}
        >
          📦 주문 현황
        </button>
        <button
          className={activeTab === 'sales' ? 'active' : ''}
          onClick={() => setActiveTab('sales')}
        >
          📈 판매 분석
        </button>
        <button
          className={activeTab === 'esg' ? 'active' : ''}
          onClick={() => setActiveTab('esg')}
        >
          🌿 ESG 활동
        </button>
      </div>

      {/* 탭 컨텐츠 */}
      <div className="farmer-content">
        {/* 대시보드 탭 */}
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="overview-section">
              <h2>🌱 재배 현황</h2>
              <div className="crops-overview">
                {crops.filter(c => c.status === 'growing').map(crop => (
                  <div key={crop.id} className="crop-overview-card">
                    <div className="crop-image-small">
                      <img src={crop.imageUrl} alt={crop.name} />
                    </div>
                    <div className="crop-info-small">
                      <h4>{crop.name}</h4>
                      <div className="crop-progress">
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{ width: `${crop.growthProgress}%` }}
                          ></div>
                        </div>
                        <span className="progress-text">{crop.growthProgress}%</span>
                      </div>
                      <div className="crop-days">
                        수확까지 {crop.daysUntilHarvest}일
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="overview-section">
              <h2>📦 최근 주문</h2>
              <div className="recent-orders">
                {orders.slice(0, 5).map(order => (
                  <div key={order.id} className="recent-order-item">
                    <div className="order-icon">📦</div>
                    <div className="order-details">
                      <div className="order-title">주문 #{order.id}</div>
                      <div className="order-meta">
                        {order.buyerName} • {order.productName} {order.quantity}kg
                      </div>
                    </div>
                    <div className="order-amount">₩{order.totalAmount.toLocaleString()}</div>
                    <div className={`order-status status-${order.status}`}>
                      {order.status === 'pending' && '⏳ 대기'}
                      {order.status === 'confirmed' && '✅ 확인'}
                      {order.status === 'shipped' && '🚚 배송중'}
                      {order.status === 'completed' && '✅ 완료'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="overview-section">
              <h2>🌿 최근 ESG 활동</h2>
              <div className="esg-activities-quick">
                {esgActivities.slice(0, 3).map(activity => (
                  <div key={activity.id} className="esg-activity-quick-card">
                    <div className="activity-icon">🌱</div>
                    <div className="activity-details">
                      <div className="activity-title">{activity.type}</div>
                      <div className="activity-date">
                        {new Date(activity.date).toLocaleDateString('ko-KR')}
                      </div>
                    </div>
                    <div className="activity-reward">+{activity.reward} DC</div>
                    <div className={`activity-status status-${activity.status}`}>
                      {activity.status === 'pending' && '⏳ 심사중'}
                      {activity.status === 'approved' && '✅ 승인'}
                      {activity.status === 'rejected' && '❌ 거부'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 작물 관리 탭 */}
        {activeTab === 'crops' && (
          <div className="crops-tab">
            <div className="crops-header">
              <h2>🌱 작물 목록</h2>
              <button className="btn-add-crop">+ 새 작물 등록</button>
            </div>
            <div className="crops-grid">
              {crops.map(crop => (
                <div key={crop.id} className="crop-card">
                  <div className="crop-image">
                    <img src={crop.imageUrl} alt={crop.name} />
                    <div className={`crop-status-badge ${crop.status}`}>
                      {crop.status === 'growing' && '🌱 재배중'}
                      {crop.status === 'harvested' && '✅ 수확완료'}
                      {crop.status === 'planning' && '📋 계획중'}
                    </div>
                  </div>
                  <div className="crop-info">
                    <h3>{crop.name}</h3>
                    <p className="crop-variety">{crop.variety}</p>
                    <div className="crop-area">재배면적: {crop.area}평</div>
                    {crop.status === 'growing' && (
                      <>
                        <div className="crop-progress-section">
                          <div className="progress-label">
                            생육도: {crop.growthProgress}%
                          </div>
                          <div className="progress-bar">
                            <div
                              className="progress-fill"
                              style={{ width: `${crop.growthProgress}%` }}
                            ></div>
                          </div>
                        </div>
                        <div className="crop-harvest-date">
                          수확예정: {new Date(crop.harvestDate).toLocaleDateString('ko-KR')}
                        </div>
                      </>
                    )}
                    {crop.status === 'harvested' && (
                      <div className="crop-harvest-info">
                        <div>수확량: {crop.harvestedAmount}kg</div>
                        <div>목표: {crop.expectedYield}kg</div>
                      </div>
                    )}
                  </div>
                  <div className="crop-actions">
                    <button
                      className="btn-crop-detail"
                      onClick={() => openCropDetail(crop)}
                    >
                      상세보기
                    </button>
                    {crop.status === 'growing' && (
                      <button
                        className="btn-record-harvest"
                        onClick={() => recordHarvest(crop.id, 100)}
                      >
                        수확기록
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 주문 현황 탭 */}
        {activeTab === 'orders' && (
          <div className="orders-tab">
            <h2>📦 주문 목록</h2>
            <div className="orders-table">
              <table>
                <thead>
                  <tr>
                    <th>주문번호</th>
                    <th>구매자</th>
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
                      <td>{order.buyerName}</td>
                      <td>{order.productName}</td>
                      <td>{order.quantity}kg</td>
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
                        </span>
                      </td>
                      <td>
                        {order.status === 'pending' && (
                          <button
                            className="btn-confirm-order"
                            onClick={() => confirmOrder(order.id)}
                          >
                            확인
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
            <h2>📈 판매 실적</h2>

            <div className="sales-chart-section">
              <h3>월별 매출 추이</h3>
              <div className="sales-chart">
                <div className="chart-bars">
                  {sales.map((data, index) => (
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
              <h3>제품별 판매량</h3>
              <div className="product-sales-list">
                {crops
                  .filter(c => c.harvestedAmount > 0)
                  .sort((a, b) => b.harvestedAmount - a.harvestedAmount)
                  .map(crop => {
                    const maxAmount = Math.max(...crops.map(c => c.harvestedAmount));
                    const percentage = (crop.harvestedAmount / maxAmount) * 100;

                    return (
                      <div key={crop.id} className="product-sales-item">
                        <div className="product-sales-info">
                          <span className="product-name">{crop.name}</span>
                          <span className="product-sales-value">
                            {crop.harvestedAmount}kg
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

        {/* ESG 활동 탭 */}
        {activeTab === 'esg' && (
          <div className="esg-tab">
            <div className="esg-header">
              <h2>🌿 ESG 활동 관리</h2>
              <button className="btn-register-esg" onClick={registerEsgActivity}>
                + 새 활동 등록
              </button>
            </div>

            <div className="esg-summary">
              <div className="esg-summary-card">
                <div className="esg-summary-icon">🏆</div>
                <div className="esg-summary-content">
                  <div className="esg-summary-label">총 보상</div>
                  <div className="esg-summary-value">{stats.esgReward} DC</div>
                </div>
              </div>
              <div className="esg-summary-card">
                <div className="esg-summary-icon">✅</div>
                <div className="esg-summary-content">
                  <div className="esg-summary-label">승인된 활동</div>
                  <div className="esg-summary-value">
                    {esgActivities.filter(a => a.status === 'approved').length}건
                  </div>
                </div>
              </div>
              <div className="esg-summary-card">
                <div className="esg-summary-icon">⏳</div>
                <div className="esg-summary-content">
                  <div className="esg-summary-label">심사 대기</div>
                  <div className="esg-summary-value">
                    {esgActivities.filter(a => a.status === 'pending').length}건
                  </div>
                </div>
              </div>
            </div>

            <div className="esg-activities-list">
              {esgActivities.map(activity => (
                <div key={activity.id} className={`esg-activity-card status-${activity.status}`}>
                  <div className="esg-activity-header">
                    <h3>{activity.type}</h3>
                    <span className={`status-badge ${activity.status}`}>
                      {activity.status === 'pending' && '⏳ 심사중'}
                      {activity.status === 'approved' && '✅ 승인'}
                      {activity.status === 'rejected' && '❌ 거부'}
                    </span>
                  </div>
                  <div className="esg-activity-body">
                    <p className="activity-description">{activity.description}</p>
                    <div className="activity-details-grid">
                      <div className="detail-item">
                        <span className="detail-label">날짜:</span>
                        <span>{new Date(activity.date).toLocaleDateString('ko-KR')}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">보상:</span>
                        <span className="detail-value">+{activity.reward} DC</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">탄소 절감:</span>
                        <span>{activity.carbonReduction} kg CO₂</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">위치:</span>
                        <span>{activity.location}</span>
                      </div>
                    </div>
                    {activity.imageUrl && (
                      <div className="activity-image">
                        <img src={activity.imageUrl} alt="활동 증거" />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 작물 상세 모달 */}
      {selectedCrop && (
        <div className="crop-modal-overlay" onClick={closeCropDetail}>
          <div className="crop-modal" onClick={(e) => e.stopPropagation()}>
            <div className="crop-modal-header">
              <h2>{selectedCrop.name}</h2>
              <button className="modal-close" onClick={closeCropDetail}>✕</button>
            </div>
            <div className="crop-modal-body">
              <div className="crop-modal-image">
                <img src={selectedCrop.imageUrl} alt={selectedCrop.name} />
              </div>
              <div className="crop-modal-details">
                <div className="detail-row">
                  <span className="detail-label">품종:</span>
                  <span>{selectedCrop.variety}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">재배면적:</span>
                  <span>{selectedCrop.area}평</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">파종일:</span>
                  <span>{new Date(selectedCrop.plantingDate).toLocaleDateString('ko-KR')}</span>
                </div>
                {selectedCrop.status === 'growing' && (
                  <>
                    <div className="detail-row">
                      <span className="detail-label">수확예정일:</span>
                      <span>{new Date(selectedCrop.harvestDate).toLocaleDateString('ko-KR')}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">생육도:</span>
                      <span>{selectedCrop.growthProgress}%</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">예상수확량:</span>
                      <span>{selectedCrop.expectedYield}kg</span>
                    </div>
                  </>
                )}
                {selectedCrop.status === 'harvested' && (
                  <>
                    <div className="detail-row">
                      <span className="detail-label">실제수확량:</span>
                      <span>{selectedCrop.harvestedAmount}kg</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">수확일:</span>
                      <span>{new Date(selectedCrop.harvestDate).toLocaleDateString('ko-KR')}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// 데모 데이터 생성 함수들
function generateDemoCrops() {
  return [
    {
      id: 'CROP001',
      name: '유기농 토마토',
      variety: '완숙 토마토',
      area: 500,
      plantingDate: new Date(Date.now() - 86400000 * 60).toISOString(),
      harvestDate: new Date(Date.now() + 86400000 * 30).toISOString(),
      daysUntilHarvest: 30,
      growthProgress: 67,
      expectedYield: 2500,
      harvestedAmount: 0,
      status: 'growing',
      imageUrl: 'https://images.unsplash.com/photo-1546470427-e26264592e6f?w=300&h=300&fit=crop'
    },
    {
      id: 'CROP002',
      name: '친환경 상추',
      variety: '로메인 상추',
      area: 300,
      plantingDate: new Date(Date.now() - 86400000 * 45).toISOString(),
      harvestDate: new Date(Date.now() + 86400000 * 15).toISOString(),
      daysUntilHarvest: 15,
      growthProgress: 75,
      expectedYield: 1200,
      harvestedAmount: 0,
      status: 'growing',
      imageUrl: 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=300&h=300&fit=crop'
    },
    {
      id: 'CROP003',
      name: '유기농 당근',
      variety: '미니 당근',
      area: 400,
      plantingDate: new Date(Date.now() - 86400000 * 120).toISOString(),
      harvestDate: new Date(Date.now() - 86400000 * 30).toISOString(),
      daysUntilHarvest: 0,
      growthProgress: 100,
      expectedYield: 1800,
      harvestedAmount: 1750,
      status: 'harvested',
      imageUrl: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=300&h=300&fit=crop'
    },
    {
      id: 'CROP004',
      name: '친환경 배추',
      variety: '김장 배추',
      area: 600,
      plantingDate: new Date(Date.now() - 86400000 * 30).toISOString(),
      harvestDate: new Date(Date.now() + 86400000 * 60).toISOString(),
      daysUntilHarvest: 60,
      growthProgress: 33,
      expectedYield: 3000,
      harvestedAmount: 0,
      status: 'growing',
      imageUrl: 'https://images.unsplash.com/photo-1597362925123-77861d3fbac7?w=300&h=300&fit=crop'
    }
  ];
}

function generateDemoSales() {
  return [
    { month: '1월', revenue: 2800000 },
    { month: '2월', revenue: 3200000 },
    { month: '3월', revenue: 3600000 },
    { month: '4월', revenue: 3400000 },
    { month: '5월', revenue: 4000000 },
    { month: '6월', revenue: 4200000 }
  ];
}

function generateDemoOrders() {
  return [
    {
      id: 'FO1001',
      buyerName: '그린마트',
      productName: '유기농 토마토',
      quantity: 50,
      totalAmount: 425000,
      orderDate: new Date(Date.now() - 86400000).toISOString(),
      deliveryDate: new Date(Date.now() + 86400000 * 2).toISOString(),
      status: 'pending'
    },
    {
      id: 'FO1002',
      buyerName: '프레시마켓',
      productName: '친환경 상추',
      quantity: 30,
      totalAmount: 150000,
      orderDate: new Date(Date.now() - 86400000 * 2).toISOString(),
      deliveryDate: new Date(Date.now() + 86400000).toISOString(),
      status: 'confirmed'
    },
    {
      id: 'FO1003',
      buyerName: '에코스토어',
      productName: '유기농 당근',
      quantity: 40,
      totalAmount: 180000,
      orderDate: new Date(Date.now() - 86400000 * 5).toISOString(),
      deliveryDate: new Date(Date.now() - 86400000 * 2).toISOString(),
      status: 'shipped'
    },
    {
      id: 'FO1004',
      buyerName: '바이오마켓',
      productName: '친환경 배추',
      quantity: 60,
      totalAmount: 360000,
      orderDate: new Date(Date.now() - 86400000 * 10).toISOString(),
      deliveryDate: new Date(Date.now() - 86400000 * 7).toISOString(),
      status: 'completed'
    }
  ];
}

function generateDemoEsgActivities() {
  return [
    {
      id: 'ESG001',
      type: '친환경 농법 실천',
      description: '무농약 유기농법으로 토마토 재배',
      date: new Date(Date.now() - 86400000 * 5).toISOString(),
      reward: 500,
      carbonReduction: 15.5,
      location: '경기도 여주시',
      imageUrl: 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=400&h=300&fit=crop',
      status: 'approved'
    },
    {
      id: 'ESG002',
      type: '재생에너지 사용',
      description: '태양광 패널 설치 및 운영',
      date: new Date(Date.now() - 86400000 * 3).toISOString(),
      reward: 1000,
      carbonReduction: 45.0,
      location: '경기도 여주시',
      imageUrl: 'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400&h=300&fit=crop',
      status: 'pending'
    },
    {
      id: 'ESG003',
      type: '음식물 쓰레기 퇴비화',
      description: '농장 내 음식물 쓰레기를 퇴비로 재활용',
      date: new Date(Date.now() - 86400000 * 7).toISOString(),
      reward: 300,
      carbonReduction: 8.2,
      location: '경기도 여주시',
      imageUrl: 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=400&h=300&fit=crop',
      status: 'approved'
    },
    {
      id: 'ESG004',
      type: '빗물 재활용',
      description: '빗물 저장 시스템으로 농업용수 절약',
      date: new Date(Date.now() - 86400000 * 1).toISOString(),
      reward: 400,
      carbonReduction: 12.0,
      location: '경기도 여주시',
      status: 'pending'
    }
  ];
}

export default FarmerDashboard;
