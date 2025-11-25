/**
 * User Dashboard
 * 사용자 대시보드
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import './UserDashboard.css';

function UserDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    esgPoints: 0,
    totalActivities: 0,
    coupons: 0,
    rank: 0
  });
  const [recentActivities, setRecentActivities] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = () => {
    // ESG 활동 히스토리 로드
    const activityHistory = JSON.parse(localStorage.getItem('esg_activity_history') || '[]');
    const totalPoints = activityHistory.reduce((sum, activity) => sum + (activity.reward || 0), 0);

    // 쿠폰 개수 (임시)
    const coupons = Math.floor(totalPoints / 100);

    setStats({
      esgPoints: totalPoints,
      totalActivities: activityHistory.length,
      coupons: coupons,
      rank: Math.max(1, Math.floor(totalPoints / 500) + 1)
    });

    // 최근 활동 3개
    setRecentActivities(activityHistory.slice(0, 3));

    // 추천 활동
    setRecommendations([
      {
        id: 1,
        name: '플라스틱 재활용',
        category: '재활용',
        icon: '♻️',
        reward: 50,
        difficulty: '쉬움'
      },
      {
        id: 2,
        name: '자전거 출퇴근',
        category: '친환경 교통',
        icon: '🚲',
        reward: 100,
        difficulty: '보통'
      },
      {
        id: 3,
        name: '나무 심기',
        category: '환경 보호',
        icon: '🌳',
        reward: 200,
        difficulty: '어려움'
      }
    ]);
  };

  const handleStartActivity = (activityId) => {
    navigate('/esg');
  };

  const getRankBadge = (rank) => {
    if (rank <= 10) return { emoji: '🏆', label: '골드', color: '#FFD700' };
    if (rank <= 50) return { emoji: '🥈', label: '실버', color: '#C0C0C0' };
    if (rank <= 100) return { emoji: '🥉', label: '브론즈', color: '#CD7F32' };
    return { emoji: '🌱', label: '새싹', color: '#51cf66' };
  };

  const rankBadge = getRankBadge(stats.rank);

  return (
    <div className="user-dashboard">
      {/* 헤더 */}
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>안녕하세요, {user?.name || '사용자'}님! 👋</h1>
          <p>오늘도 지구를 위한 작은 실천을 시작해보세요</p>
        </div>
        <div className="rank-badge-large">
          <div className="rank-emoji">{rankBadge.emoji}</div>
          <div className="rank-info">
            <div className="rank-label">{rankBadge.label} 등급</div>
            <div className="rank-number">#{stats.rank}</div>
          </div>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">🌟</div>
          <div className="stat-content">
            <div className="stat-label">ESG 포인트</div>
            <div className="stat-value">{stats.esgPoints.toLocaleString()}</div>
            <div className="stat-change">+50 (이번 주)</div>
          </div>
        </div>

        <div className="stat-card success">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">완료한 활동</div>
            <div className="stat-value">{stats.totalActivities}</div>
            <div className="stat-change">총 {stats.totalActivities}개 활동</div>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">🎟️</div>
          <div className="stat-content">
            <div className="stat-label">보유 쿠폰</div>
            <div className="stat-value">{stats.coupons}</div>
            <div className="stat-change">사용 가능</div>
          </div>
        </div>

        <div className="stat-card info">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">이번 달 순위</div>
            <div className="stat-value">#{stats.rank}</div>
            <div className="stat-change">상위 {Math.round(stats.rank / 100 * 100)}%</div>
          </div>
        </div>
      </div>

      {/* 빠른 액션 */}
      <div className="quick-actions">
        <h2>빠른 실행</h2>
        <div className="action-buttons">
          <button className="action-btn primary" onClick={() => navigate('/esg')}>
            <div className="action-icon">📸</div>
            <div className="action-text">
              <div className="action-title">활동 인증</div>
              <div className="action-desc">ESG 활동 시작하기</div>
            </div>
          </button>

          <button className="action-btn success" onClick={() => navigate('/coupons')}>
            <div className="action-icon">🎟️</div>
            <div className="action-text">
              <div className="action-title">쿠폰 사용</div>
              <div className="action-desc">{stats.coupons}개 사용 가능</div>
            </div>
          </button>

          <button className="action-btn warning" onClick={() => navigate('/marketplace')}>
            <div className="action-icon">🏪</div>
            <div className="action-text">
              <div className="action-title">마켓플레이스</div>
              <div className="action-desc">친환경 제품 구매</div>
            </div>
          </button>

          <button className="action-btn info" onClick={() => navigate('/wallet')}>
            <div className="action-icon">💳</div>
            <div className="action-text">
              <div className="action-title">디지털 쿠폰함</div>
              <div className="action-desc">내 포인트 확인</div>
            </div>
          </button>
        </div>
      </div>

      {/* 최근 활동 */}
      <div className="recent-section">
        <div className="section-header">
          <h2>최근 활동</h2>
          <button className="btn-view-all" onClick={() => navigate('/activities')}>
            전체보기 →
          </button>
        </div>

        {recentActivities.length > 0 ? (
          <div className="activity-list">
            {recentActivities.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">✅</div>
                <div className="activity-content">
                  <div className="activity-title">{activity.activityName}</div>
                  <div className="activity-meta">
                    <span>{activity.category}</span>
                    <span>•</span>
                    <span>{new Date(activity.timestamp).toLocaleDateString('ko-KR')}</span>
                  </div>
                </div>
                <div className="activity-reward">+{activity.reward} P</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>아직 완료한 활동이 없습니다</p>
            <button className="btn-start" onClick={() => navigate('/esg')}>
              첫 활동 시작하기
            </button>
          </div>
        )}
      </div>

      {/* 추천 활동 */}
      <div className="recommendations-section">
        <h2>오늘의 추천 활동</h2>
        <div className="recommendations-grid">
          {recommendations.map(activity => (
            <div key={activity.id} className="recommendation-card">
              <div className="rec-icon">{activity.icon}</div>
              <div className="rec-content">
                <div className="rec-title">{activity.name}</div>
                <div className="rec-category">{activity.category}</div>
                <div className="rec-footer">
                  <div className="rec-reward">+{activity.reward} P</div>
                  <div className="rec-difficulty">{activity.difficulty}</div>
                </div>
              </div>
              <button
                className="btn-rec-start"
                onClick={() => handleStartActivity(activity.id)}
              >
                시작하기
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 진행 상황 */}
      <div className="progress-section">
        <h2>이번 달 목표</h2>
        <div className="progress-card">
          <div className="progress-header">
            <span>월간 활동 목표</span>
            <span>{stats.totalActivities} / 20</span>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${Math.min(stats.totalActivities / 20 * 100, 100)}%` }}
            />
          </div>
          <div className="progress-footer">
            {stats.totalActivities >= 20 ? (
              <span className="progress-complete">🎉 목표 달성!</span>
            ) : (
              <span className="progress-remaining">
                {20 - stats.totalActivities}개 더 필요해요
              </span>
            )}
          </div>
        </div>

        <div className="progress-card">
          <div className="progress-header">
            <span>월간 포인트 목표</span>
            <span>{stats.esgPoints} / 1000</span>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill success"
              style={{ width: `${Math.min(stats.esgPoints / 1000 * 100, 100)}%` }}
            />
          </div>
          <div className="progress-footer">
            {stats.esgPoints >= 1000 ? (
              <span className="progress-complete">🎉 목표 달성!</span>
            ) : (
              <span className="progress-remaining">
                {1000 - stats.esgPoints}P 더 필요해요
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserDashboard;
