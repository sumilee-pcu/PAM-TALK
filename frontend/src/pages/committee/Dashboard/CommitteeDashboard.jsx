/**
 * Committee Dashboard - Carbon Tracking & ESG Verification
 * 위원회 대시보드 - 탄소 배출량 추적 및 ESG 검증
 */

import React, { useState, useEffect } from 'react';
import './CommitteeDashboard.css';

function CommitteeDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [carbonData, setCarbonData] = useState({
    totalReduced: 0,
    thisMonth: 0,
    activitiesCount: 0,
    participantsCount: 0
  });
  const [dcRequests, setDcRequests] = useState([]);
  const [esgActivities, setEsgActivities] = useState([]);
  const [reports, setReports] = useState([]);
  const [selectedActivity, setSelectedActivity] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = () => {
    // 데모 데이터 로드
    const demoCarbon = {
      totalReduced: 2547.8,
      thisMonth: 342.5,
      activitiesCount: 1248,
      participantsCount: 356
    };

    const demoDcRequests = generateDemoDcRequests();
    const demoActivities = generateDemoActivities();
    const demoReports = generateDemoReports();

    setCarbonData(demoCarbon);
    setDcRequests(demoDcRequests);
    setEsgActivities(demoActivities);
    setReports(demoReports);
  };

  // DC 배포 요청 승인/거부
  const handleDcRequestAction = async (requestId, approved) => {
    const request = dcRequests.find(r => r.id === requestId);
    if (!request) return;

    const action = approved ? '승인' : '거부';
    if (!window.confirm(`이 DC 배포 요청을 ${action}하시겠습니까?\n\n사용자: ${request.userName}\n금액: ${request.amount} DC`)) {
      return;
    }

    try {
      await new Promise(resolve => setTimeout(resolve, 1000));

      const updated = dcRequests.map(r =>
        r.id === requestId
          ? { ...r, status: approved ? 'approved' : 'rejected' }
          : r
      );
      setDcRequests(updated);

      alert(`✅ ${action} 완료되었습니다.`);
    } catch (error) {
      alert('❌ 처리 실패: ' + error.message);
    }
  };

  // ESG 활동 검증
  const verifyActivity = (activity) => {
    setSelectedActivity(activity);
  };

  const closeActivityModal = () => {
    setSelectedActivity(null);
  };

  const submitVerification = async (activityId, verified, comments) => {
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));

      const updated = esgActivities.map(a =>
        a.id === activityId
          ? { ...a, status: verified ? 'verified' : 'rejected', verificationComments: comments }
          : a
      );
      setEsgActivities(updated);

      alert(`✅ 검증이 완료되었습니다.`);
      closeActivityModal();
    } catch (error) {
      alert('❌ 검증 실패: ' + error.message);
    }
  };

  // 리포트 생성
  const generateReport = () => {
    alert('📊 환경 영향 리포트가 생성되었습니다!\n\n리포트는 다운로드 섹션에서 확인할 수 있습니다.');
  };

  return (
    <div className="committee-dashboard">
      <div className="committee-header">
        <h1>🏛️ 위원회 대시보드</h1>
        <p>탄소 배출량 추적 및 ESG 활동 검증</p>
      </div>

      {/* 탄소 통계 카드 */}
      <div className="carbon-stats-grid">
        <div className="carbon-stat-card total">
          <div className="carbon-stat-icon">🌍</div>
          <div className="carbon-stat-content">
            <div className="carbon-stat-label">총 탄소 절감량</div>
            <div className="carbon-stat-value">{carbonData.totalReduced.toLocaleString()} kg</div>
            <div className="carbon-stat-subtitle">CO₂ 누적</div>
          </div>
        </div>
        <div className="carbon-stat-card month">
          <div className="carbon-stat-icon">📅</div>
          <div className="carbon-stat-content">
            <div className="carbon-stat-label">이번 달 절감량</div>
            <div className="carbon-stat-value">{carbonData.thisMonth.toLocaleString()} kg</div>
            <div className="carbon-stat-subtitle">CO₂ 월간</div>
          </div>
        </div>
        <div className="carbon-stat-card activities">
          <div className="carbon-stat-icon">🌱</div>
          <div className="carbon-stat-content">
            <div className="carbon-stat-label">누적 ESG 활동</div>
            <div className="carbon-stat-value">{carbonData.activitiesCount.toLocaleString()}</div>
            <div className="carbon-stat-subtitle">건</div>
          </div>
        </div>
        <div className="carbon-stat-card participants">
          <div className="carbon-stat-icon">👥</div>
          <div className="carbon-stat-content">
            <div className="carbon-stat-label">참여자 수</div>
            <div className="carbon-stat-value">{carbonData.participantsCount.toLocaleString()}</div>
            <div className="carbon-stat-subtitle">명</div>
          </div>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="committee-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          📊 대시보드
        </button>
        <button
          className={activeTab === 'carbon' ? 'active' : ''}
          onClick={() => setActiveTab('carbon')}
        >
          🌍 탄소 추적
        </button>
        <button
          className={activeTab === 'dc-requests' ? 'active' : ''}
          onClick={() => setActiveTab('dc-requests')}
        >
          💰 DC 배포 승인
        </button>
        <button
          className={activeTab === 'verification' ? 'active' : ''}
          onClick={() => setActiveTab('verification')}
        >
          ✅ ESG 검증
        </button>
        <button
          className={activeTab === 'reports' ? 'active' : ''}
          onClick={() => setActiveTab('reports')}
        >
          📄 리포트
        </button>
      </div>

      {/* 탭 컨텐츠 */}
      <div className="committee-content">
        {/* 대시보드 탭 */}
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="overview-section">
              <h2>🔥 최근 활동</h2>
              <div className="recent-items">
                {esgActivities.slice(0, 5).map(activity => (
                  <div key={activity.id} className="recent-item">
                    <div className="recent-icon">🌱</div>
                    <div className="recent-details">
                      <div className="recent-title">{activity.type}</div>
                      <div className="recent-meta">
                        {activity.userName} • {activity.carbonSaved} kg CO₂
                      </div>
                    </div>
                    <div className={`recent-status status-${activity.status}`}>
                      {activity.status === 'pending' && '⏳'}
                      {activity.status === 'verified' && '✅'}
                      {activity.status === 'rejected' && '❌'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="overview-section">
              <h2>💰 대기중인 DC 배포 요청</h2>
              {dcRequests.filter(r => r.status === 'pending').length === 0 ? (
                <p className="empty-message">대기중인 요청이 없습니다.</p>
              ) : (
                <div className="dc-requests-quick">
                  {dcRequests.filter(r => r.status === 'pending').slice(0, 3).map(request => (
                    <div key={request.id} className="dc-request-quick-card">
                      <div className="dc-request-header">
                        <span className="dc-request-user">{request.userName}</span>
                        <span className="dc-request-amount">{request.amount} DC</span>
                      </div>
                      <div className="dc-request-reason">{request.reason}</div>
                      <div className="dc-request-actions">
                        <button
                          className="btn-approve-small"
                          onClick={() => handleDcRequestAction(request.id, true)}
                        >
                          ✓ 승인
                        </button>
                        <button
                          className="btn-reject-small"
                          onClick={() => handleDcRequestAction(request.id, false)}
                        >
                          ✕ 거부
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* 탄소 추적 탭 */}
        {activeTab === 'carbon' && (
          <div className="carbon-tab">
            <h2>🌍 탄소 배출량 모니터링</h2>

            <div className="carbon-chart-section">
              <div className="chart-placeholder">
                <div className="chart-icon">📊</div>
                <p>탄소 절감량 트렌드</p>
                <div className="chart-bars">
                  <div className="chart-bar" style={{height: '60%'}}><span>1월</span></div>
                  <div className="chart-bar" style={{height: '75%'}}><span>2월</span></div>
                  <div className="chart-bar" style={{height: '90%'}}><span>3월</span></div>
                  <div className="chart-bar" style={{height: '85%'}}><span>4월</span></div>
                  <div className="chart-bar" style={{height: '95%'}}><span>5월</span></div>
                  <div className="chart-bar" style={{height: '100%'}}><span>6월</span></div>
                </div>
              </div>
            </div>

            <div className="carbon-breakdown">
              <h3>활동별 탄소 절감량</h3>
              <div className="carbon-categories">
                <div className="carbon-category-item">
                  <div className="category-label">
                    <span className="category-icon">🚇</span>
                    <span>대중교통 이용</span>
                  </div>
                  <div className="category-bar">
                    <div className="category-fill" style={{width: '85%'}}></div>
                  </div>
                  <div className="category-value">1,246 kg CO₂</div>
                </div>
                <div className="carbon-category-item">
                  <div className="category-label">
                    <span className="category-icon">♻️</span>
                    <span>재활용 분리수거</span>
                  </div>
                  <div className="category-bar">
                    <div className="category-fill" style={{width: '65%'}}></div>
                  </div>
                  <div className="category-value">654 kg CO₂</div>
                </div>
                <div className="carbon-category-item">
                  <div className="category-label">
                    <span className="category-icon">🌿</span>
                    <span>친환경 제품 구매</span>
                  </div>
                  <div className="category-bar">
                    <div className="category-fill" style={{width: '45%'}}></div>
                  </div>
                  <div className="category-value">342 kg CO₂</div>
                </div>
                <div className="carbon-category-item">
                  <div className="category-label">
                    <span className="category-icon">🥤</span>
                    <span>텀블러 사용</span>
                  </div>
                  <div className="category-bar">
                    <div className="category-fill" style={{width: '30%'}}></div>
                  </div>
                  <div className="category-value">305 kg CO₂</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* DC 배포 승인 탭 */}
        {activeTab === 'dc-requests' && (
          <div className="dc-requests-tab">
            <h2>💰 DC 배포 요청 관리</h2>
            <div className="dc-requests-list">
              {dcRequests.map(request => (
                <div key={request.id} className={`dc-request-card status-${request.status}`}>
                  <div className="dc-request-card-header">
                    <div className="dc-request-info">
                      <h3>{request.userName}</h3>
                      <p className="dc-request-date">{new Date(request.timestamp).toLocaleString('ko-KR')}</p>
                    </div>
                    <div className="dc-request-amount-large">{request.amount} DC</div>
                  </div>
                  <div className="dc-request-card-body">
                    <div className="dc-request-field">
                      <strong>요청 사유:</strong>
                      <p>{request.reason}</p>
                    </div>
                    <div className="dc-request-field">
                      <strong>지갑 주소:</strong>
                      <p className="address-mono">{request.userAddress.substring(0, 20)}...</p>
                    </div>
                    <div className="dc-request-field">
                      <strong>상태:</strong>
                      <span className={`status-badge ${request.status}`}>
                        {request.status === 'pending' && '⏳ 대기중'}
                        {request.status === 'approved' && '✅ 승인됨'}
                        {request.status === 'rejected' && '❌ 거부됨'}
                      </span>
                    </div>
                  </div>
                  {request.status === 'pending' && (
                    <div className="dc-request-card-actions">
                      <button
                        className="btn-approve"
                        onClick={() => handleDcRequestAction(request.id, true)}
                      >
                        ✓ 승인
                      </button>
                      <button
                        className="btn-reject"
                        onClick={() => handleDcRequestAction(request.id, false)}
                      >
                        ✕ 거부
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ESG 검증 탭 */}
        {activeTab === 'verification' && (
          <div className="verification-tab">
            <h2>✅ ESG 활동 검증</h2>
            <div className="verification-list">
              {esgActivities.map(activity => (
                <div key={activity.id} className={`verification-card status-${activity.status}`}>
                  <div className="verification-card-header">
                    <div>
                      <h3>{activity.type}</h3>
                      <p className="verification-user">{activity.userName}</p>
                    </div>
                    <span className={`status-badge ${activity.status}`}>
                      {activity.status === 'pending' && '⏳ 검증 대기'}
                      {activity.status === 'verified' && '✅ 검증 완료'}
                      {activity.status === 'rejected' && '❌ 거부됨'}
                    </span>
                  </div>
                  <div className="verification-card-body">
                    <div className="verification-details">
                      <div className="verification-row">
                        <span className="verification-label">🌱 탄소 절감:</span>
                        <span className="verification-value">{activity.carbonSaved} kg CO₂</span>
                      </div>
                      <div className="verification-row">
                        <span className="verification-label">🪙 보상:</span>
                        <span className="verification-value">{activity.reward} ESG-GOLD</span>
                      </div>
                      <div className="verification-row">
                        <span className="verification-label">📍 위치:</span>
                        <span className="verification-value">{activity.location}</span>
                      </div>
                      <div className="verification-row">
                        <span className="verification-label">🕐 시간:</span>
                        <span className="verification-value">{new Date(activity.timestamp).toLocaleString('ko-KR')}</span>
                      </div>
                      <div className="verification-row">
                        <span className="verification-label">🤖 AI 검증:</span>
                        <span className={`verification-value ${activity.aiVerified ? 'verified' : 'pending'}`}>
                          {activity.aiVerified ? '✅ 통과' : '⏳ 대기'}
                        </span>
                      </div>
                      <div className="verification-row">
                        <span className="verification-label">📍 GPS 검증:</span>
                        <span className={`verification-value ${activity.gpsVerified ? 'verified' : 'pending'}`}>
                          {activity.gpsVerified ? '✅ 통과' : '⏳ 대기'}
                        </span>
                      </div>
                    </div>
                    {activity.imageUrl && (
                      <div className="verification-image">
                        <img src={activity.imageUrl} alt="활동 증거" />
                      </div>
                    )}
                  </div>
                  {activity.status === 'pending' && (
                    <div className="verification-card-actions">
                      <button
                        className="btn-verify"
                        onClick={() => verifyActivity(activity)}
                      >
                        🔍 상세 검증
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 리포트 탭 */}
        {activeTab === 'reports' && (
          <div className="reports-tab">
            <h2>📄 환경 영향 리포트</h2>

            <div className="report-generator">
              <h3>새 리포트 생성</h3>
              <p>현재 데이터를 기반으로 환경 영향 리포트를 생성합니다.</p>
              <button className="btn-generate-report" onClick={generateReport}>
                📊 리포트 생성
              </button>
            </div>

            <div className="reports-list">
              <h3>생성된 리포트</h3>
              {reports.map(report => (
                <div key={report.id} className="report-card">
                  <div className="report-icon">📄</div>
                  <div className="report-details">
                    <h4>{report.title}</h4>
                    <p>{report.description}</p>
                    <p className="report-date">생성일: {new Date(report.createdAt).toLocaleDateString('ko-KR')}</p>
                  </div>
                  <button className="btn-download-report">
                    📥 다운로드
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 검증 모달 */}
      {selectedActivity && (
        <div className="verification-modal-overlay" onClick={closeActivityModal}>
          <div className="verification-modal" onClick={(e) => e.stopPropagation()}>
            <div className="verification-modal-header">
              <h2>🔍 ESG 활동 상세 검증</h2>
              <button className="modal-close" onClick={closeActivityModal}>✕</button>
            </div>
            <div className="verification-modal-body">
              <div className="verification-modal-section">
                <h3>활동 정보</h3>
                <div className="verification-modal-info">
                  <p><strong>유형:</strong> {selectedActivity.type}</p>
                  <p><strong>사용자:</strong> {selectedActivity.userName}</p>
                  <p><strong>탄소 절감:</strong> {selectedActivity.carbonSaved} kg CO₂</p>
                  <p><strong>보상:</strong> {selectedActivity.reward} ESG-GOLD</p>
                  <p><strong>위치:</strong> {selectedActivity.location}</p>
                  <p><strong>시간:</strong> {new Date(selectedActivity.timestamp).toLocaleString('ko-KR')}</p>
                </div>
              </div>

              {selectedActivity.imageUrl && (
                <div className="verification-modal-section">
                  <h3>증거 사진</h3>
                  <img src={selectedActivity.imageUrl} alt="활동 증거" className="verification-modal-image" />
                </div>
              )}

              <div className="verification-modal-section">
                <h3>자동 검증 결과</h3>
                <div className="auto-verification-results">
                  <div className={`auto-verify-item ${selectedActivity.aiVerified ? 'verified' : 'pending'}`}>
                    <span className="auto-verify-label">🤖 AI 이미지 분석:</span>
                    <span className="auto-verify-status">
                      {selectedActivity.aiVerified ? '✅ 통과' : '❌ 실패'}
                    </span>
                  </div>
                  <div className={`auto-verify-item ${selectedActivity.gpsVerified ? 'verified' : 'pending'}`}>
                    <span className="auto-verify-label">📍 GPS 위치 확인:</span>
                    <span className="auto-verify-status">
                      {selectedActivity.gpsVerified ? '✅ 통과' : '❌ 실패'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="verification-modal-section">
                <h3>검증 의견</h3>
                <textarea
                  className="verification-comments"
                  placeholder="검증 의견을 입력하세요..."
                  rows="4"
                ></textarea>
              </div>
            </div>
            <div className="verification-modal-actions">
              <button
                className="btn-verify-approve"
                onClick={() => submitVerification(selectedActivity.id, true, '')}
              >
                ✅ 검증 승인
              </button>
              <button
                className="btn-verify-reject"
                onClick={() => submitVerification(selectedActivity.id, false, '')}
              >
                ❌ 검증 거부
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// 데모 데이터 생성 함수들
function generateDemoDcRequests() {
  return [
    {
      id: 'DCR1001',
      userName: '김철수',
      userAddress: 'USER1ABCDEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFGHIJKLMNO',
      amount: 50,
      reason: 'ESG 활동 참여 장려를 위한 초기 지원금 요청',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      status: 'pending'
    },
    {
      id: 'DCR1002',
      userName: '이영희',
      userAddress: 'USER2BCDEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFGHIJKLMNOP',
      amount: 100,
      reason: '지역 환경 개선 프로젝트 참여자 보상',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      status: 'pending'
    },
    {
      id: 'DCR1003',
      userName: '박민수',
      userAddress: 'USER3CDEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFGHIJKLMNOPQ',
      amount: 75,
      reason: '우수 ESG 활동가 포상',
      timestamp: new Date(Date.now() - 86400000).toISOString(),
      status: 'approved'
    }
  ];
}

function generateDemoActivities() {
  return [
    {
      id: 'ACT2001',
      userName: '김철수',
      type: '대중교통 이용',
      carbonSaved: 3.2,
      reward: 150,
      location: '서울시 강남구',
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      imageUrl: 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=400&h=300&fit=crop',
      aiVerified: true,
      gpsVerified: true,
      status: 'pending'
    },
    {
      id: 'ACT2002',
      userName: '이영희',
      type: '재활용 분리수거',
      carbonSaved: 1.8,
      reward: 80,
      location: '서울시 서초구',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      imageUrl: 'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=400&h=300&fit=crop',
      aiVerified: true,
      gpsVerified: false,
      status: 'pending'
    },
    {
      id: 'ACT2003',
      userName: '박민수',
      type: '친환경 제품 구매',
      carbonSaved: 2.5,
      reward: 120,
      location: '경기도 성남시',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      imageUrl: 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=400&h=300&fit=crop',
      aiVerified: true,
      gpsVerified: true,
      status: 'verified'
    },
    {
      id: 'ACT2004',
      userName: '정수연',
      type: '텀블러 사용',
      carbonSaved: 0.3,
      reward: 30,
      location: '서울시 종로구',
      timestamp: new Date(Date.now() - 10800000).toISOString(),
      aiVerified: false,
      gpsVerified: true,
      status: 'rejected'
    }
  ];
}

function generateDemoReports() {
  return [
    {
      id: 'REP1001',
      title: '2024년 6월 환경 영향 보고서',
      description: '월간 탄소 절감량 및 ESG 활동 통계',
      createdAt: new Date(Date.now() - 86400000 * 15).toISOString()
    },
    {
      id: 'REP1002',
      title: '2024년 5월 환경 영향 보고서',
      description: '월간 탄소 절감량 및 ESG 활동 통계',
      createdAt: new Date(Date.now() - 86400000 * 45).toISOString()
    },
    {
      id: 'REP1003',
      title: '2024년 2분기 종합 보고서',
      description: '분기별 환경 영향 분석 및 트렌드',
      createdAt: new Date(Date.now() - 86400000 * 60).toISOString()
    }
  ];
}

export default CommitteeDashboard;
