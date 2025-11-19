/**
 * Features Section
 * 주요 기능 섹션
 */

import React from 'react';

function FeaturesSection() {
  const features = [
    {
      icon: '🛒',
      title: '신선한 로컬푸드',
      description: '우리 동네 농부가 직접 기른 신선한 농산물을 만나보세요.',
      image: 'https://images.unsplash.com/photo-1488459716781-31db52582fe9?w=600&h=400&fit=crop',
      features: ['신선한 농산물', '농가 직거래', '합리적인 가격']
    },
    {
      icon: '🎯',
      title: '재미있는 챌린지',
      description: '친환경 챌린지에 참여하고 포인트를 모아보세요.',
      image: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop',
      features: ['다양한 챌린지', '포인트 적립', '리더보드 경쟁']
    },
    {
      icon: '💰',
      title: '즉시 리워드 지급',
      description: '활동 후 즉시 디지털 포인트를 받아보세요.',
      image: 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=600&h=400&fit=crop',
      features: ['즉시 지급', '투명한 거래', '실시간 확인']
    },
    {
      icon: '🎫',
      title: '다양한 혜택',
      description: '포인트로 친환경 제품 구매, 쿠폰 교환 등 다양한 혜택을 누리세요.',
      image: 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=600&h=400&fit=crop',
      features: ['쿠폰 교환', '제품 구매', '특별 할인']
    }
  ];

  return (
    <section className="features-section">
      <div className="features-container">
        <div className="section-header">
          <h2 className="section-title">
            왜 <span className="gradient-text">PAM-TALK</span>인가요?
          </h2>
          <p className="section-description">
            신선한 로컬푸드부터 재미있는 챌린지까지, 지속 가능한 라이프스타일을 시작하세요
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className={`feature-card ${index % 2 === 0 ? 'left' : 'right'}`}>
              <div className="feature-image">
                <img src={feature.image} alt={feature.title} />
                <div className="feature-overlay">
                  <div className="feature-icon">{feature.icon}</div>
                </div>
              </div>
              <div className="feature-content">
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
                <ul className="feature-list">
                  {feature.features.map((item, i) => (
                    <li key={i}>
                      <span className="check-icon">✓</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FeaturesSection;
