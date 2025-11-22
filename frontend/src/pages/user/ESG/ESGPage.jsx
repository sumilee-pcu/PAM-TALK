import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ESGPage.css';

/**
 * ESG Activity Certification Page
 * - Users select ESG activities to earn ESG-GOLD tokens
 * - Activities: Recycling, Green Transport, Tree Planting, Clean Energy
 * - 30-second target completion time (논문 기준)
 */

// ESG Activity Categories and Rewards
const ESG_ACTIVITIES = {
  recycling: {
    id: 'recycling',
    name: '재활용',
    icon: '♻️',
    description: '재활용품을 분리수거하고 인증받으세요',
    types: [
      { id: 'plastic', name: '플라스틱', reward: 30 },
      { id: 'paper', name: '종이', reward: 40 },
      { id: 'glass', name: '유리', reward: 50 },
      { id: 'metal', name: '금속', reward: 60 }
    ],
    color: '#3498db'
  },
  green_transport: {
    id: 'green_transport',
    name: '친환경 교통',
    icon: '🚲',
    description: '대중교통 또는 자전거 이용을 인증받으세요',
    types: [
      { id: 'public_transport', name: '대중교통', reward: 50 },
      { id: 'bicycle', name: '자전거', reward: 80 },
      { id: 'walking', name: '도보', reward: 100 }
    ],
    color: '#2ecc71'
  },
  tree_planting: {
    id: 'tree_planting',
    name: '나무 심기',
    icon: '🌳',
    description: '나무를 심거나 화분을 가꾸고 인증받으세요',
    types: [
      { id: 'tree', name: '나무 심기', reward: 200 },
      { id: 'plant', name: '화분 가꾸기', reward: 100 }
    ],
    color: '#27ae60'
  },
  clean_energy: {
    id: 'clean_energy',
    name: '청정 에너지',
    icon: '⚡',
    description: '태양광 패널이나 LED 사용을 인증받으세요',
    types: [
      { id: 'solar', name: '태양광', reward: 150 },
      { id: 'led', name: 'LED 전구', reward: 100 }
    ],
    color: '#f39c12'
  }
};

function ESGPage() {
  const navigate = useNavigate();
  const [wallet, setWallet] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [activityHistory, setActivityHistory] = useState([]);

  // Load wallet and activity history
  useEffect(() => {
    const savedWallet = localStorage.getItem('algorand_wallet');
    if (savedWallet) {
      setWallet(JSON.parse(savedWallet));
    }

    const savedHistory = localStorage.getItem('esg_activity_history');
    if (savedHistory) {
      setActivityHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Calculate total rewards earned
  const totalRewards = activityHistory.reduce((sum, activity) => sum + activity.reward, 0);

  // Handle category selection
  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId);
    setSelectedActivity(null);
  };

  // Handle activity type selection
  const handleActivitySelect = (activity) => {
    setSelectedActivity(activity);
  };

  // Start activity certification (will redirect to prepare page)
  const startCertification = () => {
    if (!selectedActivity) {
      alert('❌ 활동을 선택해주세요!');
      return;
    }

    // Store selected activity for prepare page
    localStorage.setItem('esg_current_activity', JSON.stringify({
      category: selectedCategory,
      activity: selectedActivity,
      timestamp: new Date().toISOString()
    }));

    // Navigate to prepare page (wallet check, points view, etc.)
    navigate('/esg/prepare');
  };

  // Back to category selection
  const backToCategories = () => {
    setSelectedCategory(null);
    setSelectedActivity(null);
  };

  return (
    <div className="esg-page">
      <div className="esg-container">
        {/* Header */}
        <div className="esg-header">
          <h1>🌱 ESG 활동 인증</h1>
          <p>환경을 지키고 ESG-GOLD 토큰을 받으세요!</p>
        </div>

        {/* Rewards Summary */}
        <div className="esg-summary">
          <div className="summary-card">
            <div className="summary-label">누적 보상</div>
            <div className="summary-value">
              <span className="amount">{totalRewards}</span>
              <span className="currency">포인트</span>
            </div>
          </div>
          <div className="summary-card">
            <div className="summary-label">완료한 활동</div>
            <div className="summary-value">
              <span className="amount">{activityHistory.length}</span>
              <span className="currency">회</span>
            </div>
          </div>
        </div>

        {!wallet && (
          <div className="wallet-warning">
            <p>💡 활동을 시작하면 자동으로 디지털 지갑이 생성됩니다!</p>
            <p style={{fontSize: '0.9rem', marginTop: '0.5rem', opacity: 0.8}}>
              지갑 없이도 활동을 선택할 수 있습니다
            </p>
          </div>
        )}

        {/* Category Selection */}
        {!selectedCategory && (
          <div className="esg-content">
            <h2 className="section-title">활동 카테고리를 선택하세요</h2>
            <p style={{textAlign: 'center', color: '#666', marginBottom: '1rem'}}>
              카테고리 개수: {Object.values(ESG_ACTIVITIES).length}개
            </p>
            <div className="category-grid">
              {Object.values(ESG_ACTIVITIES).map((category) => (
                <div
                  key={category.id}
                  className="category-card"
                  onClick={() => handleCategorySelect(category.id)}
                  style={{ borderColor: category.color }}
                >
                  <div className="category-icon" style={{ background: category.color }}>
                    {category.icon}
                  </div>
                  <h3 className="category-name">{category.name}</h3>
                  <p className="category-description">{category.description}</p>
                  <div className="category-reward-range">
                    {Math.min(...category.types.map(t => t.reward))} - {Math.max(...category.types.map(t => t.reward))} ESG-GOLD
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Activity Type Selection */}
        {selectedCategory && (
          <div className="esg-content">
            <button className="btn-back" onClick={backToCategories}>
              ← 카테고리로 돌아가기
            </button>
            <h2 className="section-title">
              {ESG_ACTIVITIES[selectedCategory].icon} {ESG_ACTIVITIES[selectedCategory].name}
            </h2>
            <div className="activity-grid">
              {ESG_ACTIVITIES[selectedCategory].types.map((activity) => (
                <div
                  key={activity.id}
                  className={`activity-card ${selectedActivity?.id === activity.id ? 'selected' : ''}`}
                  onClick={() => handleActivitySelect(activity)}
                >
                  <div className="activity-name">{activity.name}</div>
                  <div className="activity-reward">
                    <span className="reward-amount">{activity.reward}</span>
                    <span className="reward-unit">ESG-GOLD</span>
                  </div>
                </div>
              ))}
            </div>
            <button
              className="btn-start-certification"
              onClick={startCertification}
              disabled={!selectedActivity}
            >
              📸 인증 시작하기
            </button>
          </div>
        )}

        {/* Activity History */}
        {activityHistory.length > 0 && !selectedCategory && (
          <div className="esg-history">
            <h2 className="section-title">최근 활동</h2>
            <div className="history-list">
              {activityHistory.slice(0, 5).map((activity, index) => (
                <div key={index} className="history-item">
                  <div className="history-icon">
                    {ESG_ACTIVITIES[activity.category]?.icon || '🌱'}
                  </div>
                  <div className="history-info">
                    <div className="history-name">{activity.activityName}</div>
                    <div className="history-date">
                      {new Date(activity.timestamp).toLocaleDateString('ko-KR')}
                    </div>
                  </div>
                  <div className="history-reward">
                    +{activity.reward} ESG-GOLD
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ESGPage;
