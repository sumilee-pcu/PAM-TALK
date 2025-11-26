import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ESGPage.css';

/**
 * ESG Activity Certification Page
 * - Users select ESG activities to earn Digital Coupons (DC)
 * - Activities: Recycling, Green Transport, Tree Planting, Clean Energy
 * - 30-second target completion time (논문 기준)
 */

// ESG Activity Categories and Rewards
const ESG_ACTIVITIES = {
  environment: {
    id: 'environment',
    name: '환경 (Environment)',
    icon: '🌍',
    description: '환경 보호 활동으로 DC를 받으세요',
    types: [
      {
        id: 'local_food',
        name: '로컬푸드 구매',
        reward: 0, // 거래액의 5-10%
        rewardType: 'percentage',
        rewardRange: '5-10%',
        verification: '블록체인 거래 내역',
        icon: '🛒'
      },
      {
        id: 'low_carbon_product',
        name: '저탄소 제품 선택',
        reward: 0, // 추가 3-5%
        rewardType: 'percentage',
        rewardRange: '3-5%',
        verification: '블록체인 거래 내역',
        icon: '🌿'
      },
      {
        id: 'public_transport',
        name: '대중교통 이용 (버스/지하철)',
        reward: 0.5,
        rewardType: 'fixed',
        verification: '외부 API 연동',
        icon: '🚇'
      },
      {
        id: 'bike_sharing',
        name: '공유자전거 이용',
        reward: 0.7,
        rewardType: 'fixed',
        verification: '외부 API 연동',
        icon: '🚲'
      },
      {
        id: 'recycling',
        name: '재활용 참여',
        reward: 0.3,
        rewardType: 'fixed',
        verification: 'AI 이미지 인식',
        icon: '♻️'
      },
      {
        id: 'reusable_tumbler',
        name: '텀블러 사용 (일회용 컵 대신)',
        reward: 0.3,
        rewardType: 'fixed',
        verification: 'AI 이미지 인식, 카페 영수증',
        icon: '☕'
      },
      {
        id: 'reusable_basket',
        name: '재사용 바구니/장바구니 사용',
        reward: 0.2,
        rewardType: 'fixed',
        verification: 'AI 이미지 인식',
        icon: '🧺'
      },
      {
        id: 'ecobag_use',
        name: '에코백 사용 (비닐봉투 대신)',
        reward: 0.2,
        rewardType: 'fixed',
        verification: 'AI 이미지 인식',
        icon: '👜'
      }
    ],
    color: '#27ae60'
  },
  social: {
    id: 'social',
    name: '사회 (Social)',
    icon: '👥',
    description: '사회 공헌 활동으로 DC를 받으세요',
    types: [
      {
        id: 'public_facility',
        name: '공공시설 방문 (도서관/문화센터/체육시설)',
        reward: 1,
        rewardType: 'fixed',
        verification: '외부 API, GPS 위치검증, AI 이미지 인식',
        icon: '🏛️'
      },
      {
        id: 'volunteer',
        name: '자원봉사 활동',
        reward: 5,
        rewardType: 'hourly',
        rewardUnit: '시간당',
        verification: '수동 검증',
        icon: '🤝'
      },
      {
        id: 'local_event',
        name: '지역행사 참여',
        reward: 2,
        rewardType: 'fixed',
        verification: '수동 검증',
        icon: '🎉'
      }
    ],
    color: '#3498db'
  },
  governance: {
    id: 'governance',
    name: '거버넌스 (Governance)',
    icon: '⚖️',
    description: '플랫폼 참여로 DC를 받으세요',
    types: [
      {
        id: 'platform_voting',
        name: '플랫폼 투표 참여',
        reward: 0.5,
        rewardType: 'fixed',
        verification: '블록체인 거래 내역',
        icon: '🗳️'
      },
      {
        id: 'review_writing',
        name: '우수 후기 작성',
        reward: 1,
        rewardType: 'conditional',
        rewardCondition: '채택 시',
        verification: '수동 검증',
        icon: '✍️'
      },
      {
        id: 'policy_proposal',
        name: '정책 제안',
        reward: 10,
        rewardType: 'conditional',
        rewardCondition: '채택 시',
        verification: '수동 검증',
        icon: '💡'
      }
    ],
    color: '#9b59b6'
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
          <p>환경을 지키고 디지털 쿠폰(DC)을 받으세요!</p>
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
                    {Math.min(...category.types.map(t => t.reward))} - {Math.max(...category.types.map(t => t.reward))} DC
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
                  <div className="activity-icon-small">{activity.icon}</div>
                  <div className="activity-name">{activity.name}</div>
                  <div className="activity-reward">
                    {activity.rewardType === 'percentage' ? (
                      <>
                        <span className="reward-amount">{activity.rewardRange}</span>
                        <span className="reward-unit">보상</span>
                      </>
                    ) : activity.rewardType === 'hourly' ? (
                      <>
                        <span className="reward-amount">{activity.reward}</span>
                        <span className="reward-unit">DC/{activity.rewardUnit}</span>
                      </>
                    ) : activity.rewardType === 'conditional' ? (
                      <>
                        <span className="reward-amount">{activity.reward}</span>
                        <span className="reward-unit">DC</span>
                        <div className="reward-condition">({activity.rewardCondition})</div>
                      </>
                    ) : (
                      <>
                        <span className="reward-amount">{activity.reward}</span>
                        <span className="reward-unit">DC</span>
                      </>
                    )}
                  </div>
                  <div className="activity-verification">
                    <small>✓ {activity.verification}</small>
                  </div>
                </div>
              ))}
            </div>
            <button
              type="button"
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
                    +{activity.reward} DC
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
