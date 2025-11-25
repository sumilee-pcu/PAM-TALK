/**
 * Analytics Page
 * 분석 페이지
 */

import React, { useState } from 'react';
import '../Users/UsersPage.css';

function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('7days');

  const stats = {
    totalUsers: 6234,
    activeUsers: 3456,
    totalESGPoints: 125400,
    totalActivities: 8932,
    couponsIssued: 45000,
    couponsUsed: 32100,
    avgPointsPerUser: 20.1,
    topCategory: '재활용'
  };

  const categories = [
    { name: '재활용', activities: 3421, percentage: 38.3, color: '#51cf66' },
    { name: '친환경 교통', activities: 2134, percentage: 23.9, color: '#4dabf7' },
    { name: '나무심기', activities: 1892, percentage: 21.2, color: '#40c057' },
    { name: '에너지 절약', activities: 1485, percentage: 16.6, color: '#ffd43b' }
  ];

  const recentTrends = [
    { period: '이번 주', users: 450, activities: 1234, points: 18500 },
    { period: '지난 주', users: 420, activities: 1156, points: 17200 },
    { period: '2주 전', users: 380, activities: 1089, points: 16100 },
    { period: '3주 전', users: 350, activities: 998, points: 14800 }
  ];

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>📈 분석 페이지</h1>
        <p>플랫폼 사용 현황 및 통계 분석</p>
      </div>

      {/* 기간 선택 */}
      <div className="controls-section" style={{marginBottom: '2rem'}}>
        <div className="filters">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="filter-select"
          >
            <option value="7days">최근 7일</option>
            <option value="30days">최근 30일</option>
            <option value="3months">최근 3개월</option>
            <option value="1year">최근 1년</option>
          </select>
        </div>
      </div>

      {/* 주요 지표 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-label">총 사용자</div>
            <div className="stat-value">{stats.totalUsers.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">활성 사용자</div>
            <div className="stat-value">{stats.activeUsers.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🌟</div>
          <div className="stat-content">
            <div className="stat-label">총 ESG 포인트</div>
            <div className="stat-value">{stats.totalESGPoints.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <div className="stat-label">총 활동 수</div>
            <div className="stat-value">{stats.totalActivities.toLocaleString()}</div>
          </div>
        </div>
      </div>

      {/* 카테고리별 활동 */}
      <div className="users-table-container" style={{marginTop: '2rem'}}>
        <h2 style={{marginBottom: '1.5rem'}}>카테고리별 활동 현황</h2>
        {categories.map(category => (
          <div key={category.name} style={{marginBottom: '1.5rem'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
              <span style={{fontWeight: 600}}>{category.name}</span>
              <span>{category.activities.toLocaleString()}건 ({category.percentage}%)</span>
            </div>
            <div style={{background: '#f0f0f0', borderRadius: '8px', height: '12px', overflow: 'hidden'}}>
              <div
                style={{
                  background: category.color,
                  height: '100%',
                  width: `${category.percentage}%`,
                  transition: 'width 0.3s ease'
                }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* 추세 분석 */}
      <div className="users-table-container" style={{marginTop: '2rem'}}>
        <h2 style={{marginBottom: '1rem'}}>주간 추세 분석</h2>
        <table className="users-table">
          <thead>
            <tr>
              <th>기간</th>
              <th>신규 사용자</th>
              <th>활동 수</th>
              <th>포인트 적립</th>
              <th>증감율</th>
            </tr>
          </thead>
          <tbody>
            {recentTrends.map((trend, index) => {
              const prevTrend = recentTrends[index + 1];
              const growth = prevTrend
                ? ((trend.activities - prevTrend.activities) / prevTrend.activities * 100).toFixed(1)
                : 0;

              return (
                <tr key={trend.period}>
                  <td className="user-name">{trend.period}</td>
                  <td>{trend.users.toLocaleString()}</td>
                  <td>{trend.activities.toLocaleString()}</td>
                  <td className="points">{trend.points.toLocaleString()}</td>
                  <td style={{color: growth >= 0 ? '#51cf66' : '#ff6b6b', fontWeight: 600}}>
                    {growth > 0 ? '+' : ''}{growth}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* 쿠폰 통계 */}
      <div className="stats-grid" style={{marginTop: '2rem'}}>
        <div className="stat-card">
          <div className="stat-icon">🎟️</div>
          <div className="stat-content">
            <div className="stat-label">발행된 쿠폰</div>
            <div className="stat-value">{stats.couponsIssued.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">사용된 쿠폰</div>
            <div className="stat-value">{stats.couponsUsed.toLocaleString()}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">사용률</div>
            <div className="stat-value">{((stats.couponsUsed / stats.couponsIssued) * 100).toFixed(1)}%</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">💎</div>
          <div className="stat-content">
            <div className="stat-label">평균 포인트/사용자</div>
            <div className="stat-value">{stats.avgPointsPerUser}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsPage;
