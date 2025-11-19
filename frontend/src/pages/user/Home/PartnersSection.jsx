/**
 * Partners Section
 * 파트너사 섹션
 */

import React from 'react';

function PartnersSection() {
  const partners = [
    { name: '환경부', logo: '🏛️' },
    { name: '한국환경공단', logo: '🌿' },
    { name: '탄소중립위원회', logo: '🌍' },
    { name: '그린피스', logo: '☮️' },
    { name: 'WWF Korea', logo: '🐼' },
    { name: '기후행동네트워크', logo: '🌡️' },
    { name: '로컬푸드협회', logo: '🥬' },
    { name: '친환경유통협회', logo: '♻️' },
  ];

  return (
    <section className="partners-section">
      <div className="partners-container">
        <div className="section-header">
          <h2 className="section-title">함께하는 파트너</h2>
          <p className="section-description">
            신뢰할 수 있는 기관 및 단체와 협력합니다
          </p>
        </div>

        <div className="partners-grid">
          {partners.map((partner, index) => (
            <div key={index} className="partner-card">
              <div className="partner-logo">{partner.logo}</div>
              <div className="partner-name">{partner.name}</div>
            </div>
          ))}
        </div>

        <div className="partners-cta">
          <p>귀사도 PAM-TALK과 함께하고 싶으신가요?</p>
          <button className="btn-partner">파트너 문의하기</button>
        </div>
      </div>
    </section>
  );
}

export default PartnersSection;
