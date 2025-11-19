/**
 * Challenge Page
 * 탄소 챌린지 페이지
 */

import React, { useState } from 'react';
import './ChallengePage.css';

function ChallengePage() {
  const [challenges] = useState([
    {
      id: 1,
      title: '로컬푸드 30일 챌린지',
      description: '한 달 동안 50km 이내에서 생산된 농산물만 구매하기',
      difficulty: '중급',
      carbonSaved: 15,
      points: 500,
      duration: '30일',
      progress: 65,
      participants: 234
    },
    {
      id: 2,
      title: '제로웨이스트 요리',
      description: '음식물 쓰레기 없이 식재료를 100% 활용하는 요리 도전',
      difficulty: '고급',
      carbonSaved: 8,
      points: 300,
      duration: '7일',
      progress: 40,
      participants: 156
    },
    {
      id: 3,
      title: '유기농 생활',
      description: '유기농 인증 제품으로 장보기 실천',
      difficulty: '초급',
      carbonSaved: 12,
      points: 450,
      duration: '14일',
      progress: 80,
      participants: 312
    },
    {
      id: 4,
      title: '식물성 식단 일주일',
      description: '일주일 동안 채식 중심의 식단 유지하기',
      difficulty: '중급',
      carbonSaved: 20,
      points: 200,
      duration: '7일',
      progress: 55,
      participants: 189
    },
    {
      id: 5,
      title: '제철 음식 챌린지',
      description: '제철 농산물로만 식단 구성하기',
      difficulty: '초급',
      carbonSaved: 6,
      points: 350,
      duration: '21일',
      progress: 30,
      participants: 267
    },
    {
      id: 6,
      title: '자전거 배송 선택',
      description: '친환경 배송 옵션 우선 선택하기',
      difficulty: '초급',
      carbonSaved: 4.5,
      points: 250,
      duration: '30일',
      progress: 90,
      participants: 401
    }
  ]);

  const [leaderboard] = useState([
    { rank: 1, name: '김에코', score: 2847, avatar: '🌟' },
    { rank: 2, name: '이그린', score: 2456, avatar: '🌱' },
    { rank: 3, name: '박친환', score: 2103, avatar: '♻️' },
    { rank: 4, name: '최자연', score: 1892, avatar: '🌿' },
    { rank: 5, name: '정초록', score: 1654, avatar: '🍀' }
  ]);

  const joinChallenge = (challengeId) => {
    alert(`챌린지 #${challengeId}에 참여하셨습니다! 🎯`);
  };

  const updateProgress = (challengeId) => {
    alert(`챌린지 #${challengeId} 진행률을 업데이트하세요! 📊`);
  };

  const shareChallenge = (challengeId) => {
    alert(`챌린지 #${challengeId}를 공유했습니다! 📢`);
  };

  const totalCarbonSaved = challenges.reduce((sum, c) => sum + (c.carbonSaved * c.progress / 100), 0);
  const totalParticipants = challenges.reduce((sum, c) => sum + c.participants, 0);

  return (
    <div className="challenge-page">
      <div className="challenge-container">
        {/* Hero Section */}
        <section className="challenge-hero">
          <h1>🌍 탄소 챌린지</h1>
          <p>일상 속 작은 실천으로 지구를 지키고 리워드를 받으세요</p>

          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat-number">-{totalCarbonSaved.toFixed(1)}kg</div>
              <div className="hero-stat-label">CO₂ 절약</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-number">{totalParticipants.toLocaleString()}</div>
              <div className="hero-stat-label">참여자</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-number">{challenges.length}</div>
              <div className="hero-stat-label">활성 챌린지</div>
            </div>
          </div>
        </section>

        {/* User Dashboard */}
        <section className="user-dashboard">
          <div className="dashboard-header">
            <div className="user-info">
              <div className="user-avatar">👤</div>
              <div className="user-details">
                <h3>나의 에코 여정</h3>
                <div className="user-level">🏆 에코 워리어 레벨 5</div>
              </div>
            </div>
          </div>

          <div className="dashboard-stats">
            <div className="dashboard-stat">
              <div className="dashboard-stat-value">-42.5kg</div>
              <div className="dashboard-stat-label">이번 달 CO₂ 절약</div>
            </div>
            <div className="dashboard-stat">
              <div className="dashboard-stat-value">1,850</div>
              <div className="dashboard-stat-label">에코 포인트</div>
            </div>
            <div className="dashboard-stat">
              <div className="dashboard-stat-value">12</div>
              <div className="dashboard-stat-label">완료한 챌린지</div>
            </div>
          </div>
        </section>

        {/* Challenges Section */}
        <section className="challenges-section">
          <h2>활성 챌린지</h2>

          <div className="challenges-grid">
            {challenges.map(challenge => (
              <div key={challenge.id} className="challenge-card">
                <div className="challenge-header">
                  <h3 className="challenge-title">{challenge.title}</h3>
                  <span className="challenge-difficulty">{challenge.difficulty}</span>
                </div>

                <div className="challenge-body">
                  <p className="challenge-description">{challenge.description}</p>

                  <div className="challenge-rewards">
                    <div className="reward-item">
                      <span className="reward-value">{challenge.carbonSaved}kg</span>
                      <span className="reward-label">CO₂ 절약</span>
                    </div>
                    <div className="reward-item">
                      <span className="reward-value">{challenge.points}</span>
                      <span className="reward-label">포인트</span>
                    </div>
                    <div className="reward-item">
                      <span className="reward-value">{challenge.duration}</span>
                      <span className="reward-label">기간</span>
                    </div>
                  </div>

                  <div className="challenge-progress">
                    <div className="progress-header">
                      <span>진행률</span>
                      <span>{challenge.progress}%</span>
                    </div>
                    <div className="progress-bar-container">
                      <div
                        className="progress-bar"
                        style={{ width: `${challenge.progress}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="challenge-participants">
                    <div className="participants-avatars">
                      {[1, 2, 3].map(i => (
                        <div key={i} className="participant-avatar">
                          {['👤', '👩', '👨'][i - 1]}
                        </div>
                      ))}
                    </div>
                    <span className="participants-count">
                      {challenge.participants}명 참여 중
                    </span>
                  </div>

                  <div className="challenge-actions">
                    <button
                      className="btn-challenge btn-primary"
                      onClick={() => joinChallenge(challenge.id)}
                    >
                      도전하기
                    </button>
                    <button
                      className="btn-challenge btn-secondary"
                      onClick={() => updateProgress(challenge.id)}
                    >
                      진행 업데이트
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Leaderboard */}
        <section className="leaderboard">
          <h2>🏆 에코 리더보드</h2>

          <ul className="leaderboard-list">
            {leaderboard.map(user => (
              <li key={user.rank} className="leaderboard-item">
                <div className={`leaderboard-rank ${user.rank <= 3 ? 'top' : ''}`}>
                  #{user.rank}
                </div>
                <div className="leaderboard-user">
                  <div className="leaderboard-avatar">{user.avatar}</div>
                  <div className="leaderboard-name">{user.name}</div>
                </div>
                <div className="leaderboard-score">
                  {user.score.toLocaleString()} pt
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

export default ChallengePage;
