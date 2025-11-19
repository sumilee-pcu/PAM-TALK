/**
 * CTA Section
 * Call-to-Action 섹션
 */

import React from 'react';
import { Link } from 'react-router-dom';

function CTASection() {
  return (
    <section className="cta-section">
      <div className="cta-container">
        <div className="cta-content">
          <h2 className="cta-title">
            오늘부터 시작하는<br />
            <span className="gradient-text">지속 가능한 미래</span>
          </h2>
          <p className="cta-description">
            PAM-TALK과 함께 작은 실천으로 큰 변화를 만들어보세요.<br />
            지금 가입하고 웰컴 쿠폰 100 포인트를 받으세요!
          </p>
          <div className="cta-actions">
            <Link to="/signup" className="btn-cta-primary">
              무료로 시작하기
              <span className="btn-icon">🚀</span>
            </Link>
            <Link to="/learn-more" className="btn-cta-secondary">
              더 알아보기
            </Link>
          </div>
          <div className="cta-features">
            <div className="cta-feature">
              <span className="check-icon">✓</span>
              <span>신용카드 불필요</span>
            </div>
            <div className="cta-feature">
              <span className="check-icon">✓</span>
              <span>언제든 무료</span>
            </div>
            <div className="cta-feature">
              <span className="check-icon">✓</span>
              <span>즉시 시작 가능</span>
            </div>
          </div>
        </div>
        <div className="cta-visual">
          <div className="cta-image-wrapper">
            <img
              src="https://images.unsplash.com/photo-1569163139394-de4798aa62b6?w=600&h=600&fit=crop"
              alt="Join PAM-TALK"
              className="cta-image"
            />
            <div className="cta-badge">
              <div className="badge-icon">🎁</div>
              <div className="badge-content">
                <div className="badge-title">웰컴 보너스</div>
                <div className="badge-value">100 포인트</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default CTASection;
