/**
 * Hero Section
 * 메인 히어로 섹션
 */

import React from 'react';
import { Link } from 'react-router-dom';

function HeroSection() {
  return (
    <section className="hero-section">
      <div className="hero-container">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-icon">🌍</span>
            <span className="badge-text">지속 가능한 라이프스타일 플랫폼</span>
          </div>

          <h1 className="hero-title">
            작은 실천으로<br />
            <span className="gradient-text">지구를 지키고</span><br />
            리워드를 받으세요
          </h1>

          <p className="hero-description">
            친환경 활동에 참여하고 포인트를 모아보세요.<br />
            PAM-TALK과 함께 즐겁게 지구를 지켜요.
          </p>

          <div className="hero-actions">
            <Link to="/signup" className="btn-hero-primary">
              무료로 시작하기
              <span className="btn-arrow">→</span>
            </Link>
            <Link to="/about" className="btn-hero-secondary">
              더 알아보기
            </Link>
          </div>

          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-number">12,500+</div>
              <div className="stat-label">활동 참여자</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">285톤</div>
              <div className="stat-label">탄소 감축량</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">₩8.5M</div>
              <div className="stat-label">리워드 지급</div>
            </div>
          </div>
        </div>

        <div className="hero-image">
          <div className="hero-image-wrapper">
            <img
              src="https://images.unsplash.com/photo-1497436072909-60f360e1d4b1?w=800&h=1000&fit=crop"
              alt="Green Earth"
              className="hero-main-image"
            />
            <div className="hero-floating-card card-1">
              <div className="card-icon">🌱</div>
              <div className="card-content">
                <div className="card-title">로컬푸드 구매</div>
                <div className="card-value">+50 포인트</div>
              </div>
            </div>
            <div className="hero-floating-card card-2">
              <div className="card-icon">♻️</div>
              <div className="card-content">
                <div className="card-title">재활용 활동</div>
                <div className="card-value">+30 포인트</div>
              </div>
            </div>
            <div className="hero-floating-card card-3">
              <div className="card-icon">🚌</div>
              <div className="card-content">
                <div className="card-title">대중교통 이용</div>
                <div className="card-value">+20 포인트</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="scroll-indicator">
        <div className="scroll-mouse">
          <div className="scroll-wheel"></div>
        </div>
        <span>스크롤하여 더 알아보기</span>
      </div>
    </section>
  );
}

export default HeroSection;
