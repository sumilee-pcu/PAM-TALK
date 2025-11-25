/**
 * Blockchain Management Page
 * 블록체인 관리 페이지
 */

import React, { useState, useEffect } from 'react';
import '../Users/UsersPage.css';

function BlockchainPage() {
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState({
    totalTransactions: 0,
    totalVolume: 0,
    avgBlockTime: 4.5,
    networkStatus: 'ONLINE'
  });

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = () => {
    const demoTransactions = [
      {
        id: 1,
        txHash: '0x1a2b3c4d5e6f7890abcdef1234567890',
        type: 'ESG_REWARD',
        from: 'System',
        to: 'consumer@pamtalk.com',
        amount: 50,
        timestamp: '2024-11-22 10:30:25',
        block: 12345,
        status: 'CONFIRMED'
      },
      {
        id: 2,
        txHash: '0x2b3c4d5e6f7890abcdef1234567890ab',
        type: 'COUPON_ISSUE',
        from: 'admin@pamtalk.com',
        to: 'Smart Contract',
        amount: 1000,
        timestamp: '2024-11-22 09:15:10',
        block: 12340,
        status: 'CONFIRMED'
      },
      {
        id: 3,
        txHash: '0x3c4d5e6f7890abcdef1234567890abcd',
        type: 'TOKEN_TRANSFER',
        from: 'farmer@pamtalk.com',
        to: 'consumer@pamtalk.com',
        amount: 200,
        timestamp: '2024-11-22 08:45:33',
        block: 12335,
        status: 'CONFIRMED'
      },
      {
        id: 4,
        txHash: '0x4d5e6f7890abcdef1234567890abcdef',
        type: 'ESG_REWARD',
        from: 'System',
        to: 'farmer@pamtalk.com',
        amount: 100,
        timestamp: '2024-11-22 07:20:15',
        block: 12330,
        status: 'PENDING'
      }
    ];

    setTransactions(demoTransactions);
    setStats({
      totalTransactions: demoTransactions.length,
      totalVolume: demoTransactions.reduce((sum, tx) => sum + tx.amount, 0),
      avgBlockTime: 4.5,
      networkStatus: 'ONLINE'
    });
  };

  const getTypeLabel = (type) => {
    const labels = {
      'ESG_REWARD': 'ESG 보상',
      'COUPON_ISSUE': '쿠폰 발행',
      'TOKEN_TRANSFER': '토큰 전송'
    };
    return labels[type] || type;
  };

  const getTypeBadge = (type) => {
    const classes = {
      'ESG_REWARD': 'role-badge farmer',
      'COUPON_ISSUE': 'role-badge admin',
      'TOKEN_TRANSFER': 'role-badge consumer'
    };
    return classes[type] || 'role-badge';
  };

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>⛓️ 블록체인 관리</h1>
        <p>트랜잭션 모니터링 및 네트워크 상태</p>
      </div>

      {/* 통계 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">총 트랜잭션</div>
            <div className="stat-value">{stats.totalTransactions.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <div className="stat-label">총 거래량</div>
            <div className="stat-value">{stats.totalVolume.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <div className="stat-label">평균 블록 시간</div>
            <div className="stat-value">{stats.avgBlockTime}s</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🟢</div>
          <div className="stat-content">
            <div className="stat-label">네트워크 상태</div>
            <div className="stat-value" style={{color: '#51cf66'}}>{stats.networkStatus}</div>
          </div>
        </div>
      </div>

      {/* 트랜잭션 테이블 */}
      <div className="users-table-container">
        <h2 style={{marginBottom: '1rem'}}>최근 트랜잭션</h2>
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>트랜잭션 해시</th>
              <th>유형</th>
              <th>발신자</th>
              <th>수신자</th>
              <th>금액</th>
              <th>블록</th>
              <th>시간</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map(tx => (
              <tr key={tx.id}>
                <td>{tx.id}</td>
                <td style={{fontFamily: 'monospace', fontSize: '0.85rem'}}>
                  {tx.txHash.substring(0, 20)}...
                </td>
                <td>
                  <span className={getTypeBadge(tx.type)}>
                    {getTypeLabel(tx.type)}
                  </span>
                </td>
                <td>{tx.from}</td>
                <td>{tx.to}</td>
                <td className="points">{tx.amount.toLocaleString()}</td>
                <td>{tx.block}</td>
                <td style={{fontSize: '0.85rem'}}>{tx.timestamp}</td>
                <td>
                  <span className={`status-badge ${tx.status === 'CONFIRMED' ? 'active' : 'suspended'}`}>
                    {tx.status === 'CONFIRMED' ? '완료' : '대기'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 네트워크 정보 */}
      <div className="users-table-container" style={{marginTop: '2rem'}}>
        <h2 style={{marginBottom: '1rem'}}>네트워크 정보</h2>
        <div className="user-detail-grid">
          <div className="detail-item">
            <label>네트워크</label>
            <div>Algorand TestNet</div>
          </div>
          <div className="detail-item">
            <label>체인 ID</label>
            <div>416001</div>
          </div>
          <div className="detail-item">
            <label>현재 블록</label>
            <div className="points-large">12,345</div>
          </div>
          <div className="detail-item">
            <label>가스 가격</label>
            <div>0.001 ALGO</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BlockchainPage;
