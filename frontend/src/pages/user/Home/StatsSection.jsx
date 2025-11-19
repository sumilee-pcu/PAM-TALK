/**
 * Stats Section
 * 통계 섹션
 */

import React from 'react';

function StatsSection() {
  const stats = [
    {
      icon: '👥',
      number: '12,500+',
      label: '참여자',
      description: '매월 증가 중'
    },
    {
      icon: '🌍',
      number: '285톤',
      label: 'CO₂ 감축',
      description: '지난 6개월간'
    },
    {
      icon: '🎁',
      number: '₩8.5M',
      label: '리워드 지급',
      description: '누적 금액'
    },
    {
      icon: '🏪',
      number: '150+',
      label: '파트너사',
      description: '전국 친환경 매장'
    }
  ];

  return (
    <section className="stats-section">
      <div className="stats-container">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-number" data-number={stat.number}>
              {stat.number}
            </div>
            <div className="stat-label">{stat.label}</div>
            <div className="stat-description">{stat.description}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default StatsSection;
