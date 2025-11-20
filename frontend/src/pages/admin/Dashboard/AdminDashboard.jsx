/**
 * Admin Dashboard - DC Distribution & User Management
 * 관리자 대시보드 - 디지털쿠폰 배포 및 사용자 관리
 */

import React, { useState, useEffect } from 'react';
import algosdk from 'algosdk';
import './AdminDashboard.css';

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [users, setUsers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [esgActivities, setEsgActivities] = useState([]);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalDCDistributed: 0,
    pendingActivities: 0,
    totalCarbonSaved: 0
  });
  const [dcAmount, setDcAmount] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const [distributionNote, setDistributionNote] = useState('');
  const [distributing, setDistributing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  // 데이터 로드 (실제로는 백엔드 API 호출)
  const loadData = () => {
    // 데모 데이터 생성
    const demoUsers = generateDemoUsers();
    const demoTransactions = generateDemoTransactions();
    const demoActivities = generateDemoEsgActivities();

    setUsers(demoUsers);
    setTransactions(demoTransactions);
    setEsgActivities(demoActivities);

    // 통계 계산
    setStats({
      totalUsers: demoUsers.length,
      totalDCDistributed: demoTransactions.reduce((sum, tx) => sum + tx.amount, 0),
      pendingActivities: demoActivities.filter(a => a.status === 'pending').length,
      totalCarbonSaved: demoActivities.reduce((sum, a) => sum + (a.carbonSaved || 0), 0)
    });
  };

  // DC 배포
  const distributeDC = async () => {
    if (!selectedUser || !dcAmount || parseFloat(dcAmount) <= 0) {
      alert('사용자와 금액을 올바르게 입력해주세요.');
      return;
    }

    if (!window.confirm(`${selectedUser}에게 ${dcAmount} DC를 배포하시겠습니까?`)) {
      return;
    }

    setDistributing(true);

    try {
      // 실제로는 백엔드 API 호출하여 블록체인 트랜잭션 실행
      await new Promise(resolve => setTimeout(resolve, 1500)); // 시뮬레이션

      alert(`✅ ${dcAmount} DC가 성공적으로 배포되었습니다!`);

      // 거래 내역에 추가
      const newTransaction = {
        id: `TX${Date.now()}`,
        timestamp: new Date().toISOString(),
        userAddress: selectedUser,
        amount: parseFloat(dcAmount),
        type: '관리자 배포',
        note: distributionNote,
        status: 'completed'
      };
      setTransactions([newTransaction, ...transactions]);

      // 폼 초기화
      setDcAmount('');
      setSelectedUser('');
      setDistributionNote('');

      loadData();
    } catch (error) {
      alert('❌ DC 배포 실패: ' + error.message);
    } finally {
      setDistributing(false);
    }
  };

  // ESG 활동 승인/거부
  const handleActivityApproval = async (activityId, approved) => {
    const activity = esgActivities.find(a => a.id === activityId);
    if (!activity) return;

    const action = approved ? '승인' : '거부';
    if (!window.confirm(`이 ESG 활동을 ${action}하시겠습니까?\n\n활동: ${activity.type}\n보상: ${activity.reward} ESG-GOLD`)) {
      return;
    }

    try {
      // 실제로는 백엔드 API 호출
      await new Promise(resolve => setTimeout(resolve, 1000));

      // 상태 업데이트
      const updated = esgActivities.map(a =>
        a.id === activityId
          ? { ...a, status: approved ? 'approved' : 'rejected' }
          : a
      );
      setEsgActivities(updated);

      alert(`✅ ${action} 완료되었습니다.`);
      loadData();
    } catch (error) {
      alert('❌ 처리 실패: ' + error.message);
    }
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>🛠️ 관리자 대시보드</h1>
        <p>디지털쿠폰 배포 및 시스템 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-label">총 사용자</div>
            <div className="stat-value">{stats.totalUsers.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🪙</div>
          <div className="stat-content">
            <div className="stat-label">총 DC 배포량</div>
            <div className="stat-value">{stats.totalDCDistributed.toLocaleString()} DC</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <div className="stat-label">대기중인 활동</div>
            <div className="stat-value">{stats.pendingActivities}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🌱</div>
          <div className="stat-content">
            <div className="stat-label">누적 탄소 절감</div>
            <div className="stat-value">{stats.totalCarbonSaved.toFixed(1)} kg</div>
          </div>
        </div>
      </div>

      {/* 탭 네비게이션 */}
      <div className="admin-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          📊 개요
        </button>
        <button
          className={activeTab === 'distribute' ? 'active' : ''}
          onClick={() => setActiveTab('distribute')}
        >
          🪙 DC 배포
        </button>
        <button
          className={activeTab === 'users' ? 'active' : ''}
          onClick={() => setActiveTab('users')}
        >
          👥 사용자 관리
        </button>
        <button
          className={activeTab === 'activities' ? 'active' : ''}
          onClick={() => setActiveTab('activities')}
        >
          🌱 ESG 활동 관리
        </button>
        <button
          className={activeTab === 'transactions' ? 'active' : ''}
          onClick={() => setActiveTab('transactions')}
        >
          📜 거래 내역
        </button>
      </div>

      {/* 탭 컨텐츠 */}
      <div className="admin-content">
        {/* 개요 탭 */}
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="section">
              <h2>최근 활동</h2>
              <div className="recent-activities">
                {transactions.slice(0, 5).map(tx => (
                  <div key={tx.id} className="activity-item">
                    <div className="activity-icon">💳</div>
                    <div className="activity-details">
                      <div className="activity-title">{tx.type}</div>
                      <div className="activity-meta">{new Date(tx.timestamp).toLocaleString('ko-KR')}</div>
                    </div>
                    <div className="activity-amount">+{tx.amount} DC</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="section">
              <h2>대기중인 ESG 활동 승인</h2>
              {esgActivities.filter(a => a.status === 'pending').length === 0 ? (
                <p className="empty-message">대기중인 활동이 없습니다.</p>
              ) : (
                <div className="pending-activities">
                  {esgActivities.filter(a => a.status === 'pending').slice(0, 3).map(activity => (
                    <div key={activity.id} className="pending-activity-card">
                      <div className="activity-header">
                        <span className="activity-type">{activity.type}</span>
                        <span className="activity-reward">+{activity.reward} ESG-GOLD</span>
                      </div>
                      <div className="activity-user">사용자: {activity.userName}</div>
                      <div className="activity-time">{new Date(activity.timestamp).toLocaleString('ko-KR')}</div>
                      <div className="activity-actions">
                        <button
                          className="btn-approve"
                          onClick={() => handleActivityApproval(activity.id, true)}
                        >
                          ✓ 승인
                        </button>
                        <button
                          className="btn-reject"
                          onClick={() => handleActivityApproval(activity.id, false)}
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

        {/* DC 배포 탭 */}
        {activeTab === 'distribute' && (
          <div className="distribute-tab">
            <div className="distribution-form">
              <h2>💰 디지털쿠폰 (DC) 배포</h2>
              <p className="form-description">사용자에게 직접 DC를 배포할 수 있습니다.</p>

              <div className="form-group">
                <label>사용자 주소 선택</label>
                <select
                  value={selectedUser}
                  onChange={(e) => setSelectedUser(e.target.value)}
                  className="form-input"
                >
                  <option value="">사용자를 선택하세요</option>
                  {users.map(user => (
                    <option key={user.address} value={user.address}>
                      {user.name} ({user.address.substring(0, 8)}...)
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>배포 금액 (DC)</label>
                <input
                  type="number"
                  value={dcAmount}
                  onChange={(e) => setDcAmount(e.target.value)}
                  placeholder="배포할 DC 금액"
                  className="form-input"
                  min="0"
                  step="0.01"
                />
              </div>

              <div className="form-group">
                <label>메모 (선택사항)</label>
                <textarea
                  value={distributionNote}
                  onChange={(e) => setDistributionNote(e.target.value)}
                  placeholder="배포 사유나 메모를 입력하세요"
                  className="form-input"
                  rows="3"
                />
              </div>

              <button
                className="btn-distribute"
                onClick={distributeDC}
                disabled={distributing || !selectedUser || !dcAmount}
              >
                {distributing ? '배포 중...' : '🪙 DC 배포하기'}
              </button>
            </div>
          </div>
        )}

        {/* 사용자 관리 탭 */}
        {activeTab === 'users' && (
          <div className="users-tab">
            <h2>👥 사용자 목록</h2>
            <div className="users-table">
              <table>
                <thead>
                  <tr>
                    <th>이름</th>
                    <th>지갑 주소</th>
                    <th>DC 잔액</th>
                    <th>ESG-GOLD</th>
                    <th>가입일</th>
                    <th>상태</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.address}>
                      <td>{user.name}</td>
                      <td className="address-cell">{user.address.substring(0, 12)}...{user.address.substring(user.address.length - 6)}</td>
                      <td>{user.dcBalance.toFixed(2)} DC</td>
                      <td>{user.esgBalance.toLocaleString()} ESG-GOLD</td>
                      <td>{new Date(user.joinDate).toLocaleDateString('ko-KR')}</td>
                      <td>
                        <span className={`status-badge ${user.status}`}>
                          {user.status === 'active' ? '🟢 활성' : '🔴 비활성'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ESG 활동 관리 탭 */}
        {activeTab === 'activities' && (
          <div className="activities-tab">
            <h2>🌱 ESG 활동 관리</h2>
            <div className="activities-list">
              {esgActivities.map(activity => (
                <div key={activity.id} className={`activity-card status-${activity.status}`}>
                  <div className="activity-card-header">
                    <div className="activity-card-type">
                      <span className="type-badge">{activity.type}</span>
                      <span className="reward-badge">+{activity.reward} ESG-GOLD</span>
                    </div>
                    <div className={`status-badge ${activity.status}`}>
                      {activity.status === 'pending' && '⏳ 대기'}
                      {activity.status === 'approved' && '✅ 승인'}
                      {activity.status === 'rejected' && '❌ 거부'}
                    </div>
                  </div>
                  <div className="activity-card-body">
                    <div className="activity-info">
                      <div><strong>사용자:</strong> {activity.userName}</div>
                      <div><strong>위치:</strong> {activity.location || 'N/A'}</div>
                      <div><strong>탄소 절감:</strong> {activity.carbonSaved} kg CO₂</div>
                      <div><strong>시간:</strong> {new Date(activity.timestamp).toLocaleString('ko-KR')}</div>
                    </div>
                    {activity.imageUrl && (
                      <div className="activity-image">
                        <img src={activity.imageUrl} alt="활동 사진" />
                      </div>
                    )}
                  </div>
                  {activity.status === 'pending' && (
                    <div className="activity-card-actions">
                      <button
                        className="btn-approve"
                        onClick={() => handleActivityApproval(activity.id, true)}
                      >
                        ✓ 승인
                      </button>
                      <button
                        className="btn-reject"
                        onClick={() => handleActivityApproval(activity.id, false)}
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

        {/* 거래 내역 탭 */}
        {activeTab === 'transactions' && (
          <div className="transactions-tab">
            <h2>📜 거래 내역</h2>
            <div className="transactions-table">
              <table>
                <thead>
                  <tr>
                    <th>거래 ID</th>
                    <th>시간</th>
                    <th>사용자</th>
                    <th>유형</th>
                    <th>금액</th>
                    <th>메모</th>
                    <th>상태</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map(tx => (
                    <tr key={tx.id}>
                      <td className="tx-id">{tx.id}</td>
                      <td>{new Date(tx.timestamp).toLocaleString('ko-KR')}</td>
                      <td className="address-cell">{tx.userAddress.substring(0, 10)}...</td>
                      <td>{tx.type}</td>
                      <td className="amount-cell">+{tx.amount} DC</td>
                      <td>{tx.note || '-'}</td>
                      <td>
                        <span className="status-badge completed">✅ 완료</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// 데모 데이터 생성 함수들
function generateDemoUsers() {
  return [
    {
      name: '김철수',
      address: 'USER1ABCDEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFGHIJKLMNO',
      dcBalance: 50.25,
      esgBalance: 1200,
      joinDate: '2024-01-15',
      status: 'active'
    },
    {
      name: '이영희',
      address: 'USER2BCDEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFGHIJKLMNOP',
      dcBalance: 123.50,
      esgBalance: 3400,
      joinDate: '2024-02-20',
      status: 'active'
    },
    {
      name: '박민수',
      address: 'USER3CDEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFGHIJKLMNOPQ',
      dcBalance: 75.00,
      esgBalance: 2100,
      joinDate: '2024-03-10',
      status: 'active'
    },
    {
      name: '정수연',
      address: 'USER4DEFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFGHIJKLMNOPQR',
      dcBalance: 200.75,
      esgBalance: 5600,
      joinDate: '2024-01-25',
      status: 'active'
    },
    {
      name: '최동욱',
      address: 'USER5EFGHIJKLMNOPQRSTUVWXYZ234567890ABCDEFGHIJKLMNOPQRS',
      dcBalance: 45.30,
      esgBalance: 890,
      joinDate: '2024-04-05',
      status: 'active'
    }
  ];
}

function generateDemoTransactions() {
  const users = generateDemoUsers();
  return [
    {
      id: 'TX1001',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      userAddress: users[0].address,
      amount: 10.00,
      type: '관리자 배포',
      note: '이벤트 참여 보상',
      status: 'completed'
    },
    {
      id: 'TX1002',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      userAddress: users[1].address,
      amount: 25.50,
      type: '관리자 배포',
      note: 'ESG 활동 장려금',
      status: 'completed'
    },
    {
      id: 'TX1003',
      timestamp: new Date(Date.now() - 10800000).toISOString(),
      userAddress: users[2].address,
      amount: 15.00,
      type: '관리자 배포',
      note: '신규 가입 환영',
      status: 'completed'
    },
    {
      id: 'TX1004',
      timestamp: new Date(Date.now() - 14400000).toISOString(),
      userAddress: users[3].address,
      amount: 50.00,
      type: '관리자 배포',
      note: '우수 활동 보상',
      status: 'completed'
    }
  ];
}

function generateDemoEsgActivities() {
  const users = generateDemoUsers();
  return [
    {
      id: 'ACT1001',
      userName: users[0].name,
      userAddress: users[0].address,
      type: '대중교통 이용',
      reward: 100,
      carbonSaved: 2.5,
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      location: '서울시 강남구',
      imageUrl: 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=300&h=200&fit=crop',
      status: 'pending'
    },
    {
      id: 'ACT1002',
      userName: users[1].name,
      userAddress: users[1].address,
      type: '재활용 분리수거',
      reward: 50,
      carbonSaved: 1.2,
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      location: '서울시 서초구',
      imageUrl: 'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=300&h=200&fit=crop',
      status: 'pending'
    },
    {
      id: 'ACT1003',
      userName: users[2].name,
      userAddress: users[2].address,
      type: '친환경 제품 구매',
      reward: 150,
      carbonSaved: 3.0,
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      location: '경기도 성남시',
      imageUrl: 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=300&h=200&fit=crop',
      status: 'approved'
    },
    {
      id: 'ACT1004',
      userName: users[3].name,
      userAddress: users[3].address,
      type: '텀블러 사용',
      reward: 30,
      carbonSaved: 0.5,
      timestamp: new Date(Date.now() - 10800000).toISOString(),
      location: '서울시 종로구',
      status: 'rejected'
    }
  ];
}

export default AdminDashboard;
