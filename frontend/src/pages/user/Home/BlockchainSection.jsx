/**
 * Blockchain Section
 * 블록체인 기술 섹션
 */

import React from 'react';

function BlockchainSection() {
  return (
    <section className="blockchain-section">
      <div className="blockchain-container">
        <div className="blockchain-content">
          <div className="blockchain-badge">
            <span style={{ fontSize: '3rem' }}>🪙</span>
          </div>
          <h2 className="blockchain-title">
            <span className="gradient-text">ESG-GOLD</span> 디지털 쿠폰<br />
            블록체인 기반 보상 시스템
          </h2>
          <p className="blockchain-description">
            PAM-TALK은 블록체인 기술을 활용하여 ESG-GOLD 디지털 쿠폰을 발행하고,
            모든 탄소 감축 활동과 거래 내역을 투명하고 안전하게 기록합니다.
          </p>

          <div className="blockchain-features">
            <div className="blockchain-feature">
              <div className="feature-icon-wrapper">
                <span className="feature-icon">🌱</span>
              </div>
              <h4>친환경 기술</h4>
              <p>탄소 중립 블록체인으로 환경을 보호합니다</p>
            </div>
            <div className="blockchain-feature">
              <div className="feature-icon-wrapper">
                <span className="feature-icon">⚡</span>
              </div>
              <h4>즉시 보상</h4>
              <p>활동 인증 즉시 ESG-GOLD 쿠폰을 받을 수 있습니다</p>
            </div>
            <div className="blockchain-feature">
              <div className="feature-icon-wrapper">
                <span className="feature-icon">🔒</span>
              </div>
              <h4>완벽한 보안</h4>
              <p>블록체인 기술로 쿠폰 위변조가 불가능합니다</p>
            </div>
            <div className="blockchain-feature">
              <div className="feature-icon-wrapper">
                <span className="feature-icon">💰</span>
              </div>
              <h4>자유로운 거래</h4>
              <p>ESG-GOLD로 농산물 구매 및 다양한 거래가 가능합니다</p>
            </div>
          </div>

          <div className="blockchain-stats">
            <div className="stat">
              <div className="stat-value">ESG-GOLD</div>
              <div className="stat-label">디지털 쿠폰 발행</div>
            </div>
            <div className="stat">
              <div className="stat-value">100%</div>
              <div className="stat-label">블록체인 투명성</div>
            </div>
          </div>
        </div>

        <div className="blockchain-visual">
          <div className="blockchain-animation">
            <div className="blockchain-network">
              <div className="network-node node-1">
                <div className="node-pulse"></div>
              </div>
              <div className="network-node node-2">
                <div className="node-pulse"></div>
              </div>
              <div className="network-node node-3">
                <div className="node-pulse"></div>
              </div>
              <div className="network-node node-4">
                <div className="node-pulse"></div>
              </div>
              <div className="network-node node-5">
                <div className="node-pulse"></div>
              </div>
              <svg className="network-connections" viewBox="0 0 500 500">
                <line x1="250" y1="100" x2="400" y2="200" className="connection" />
                <line x1="250" y1="100" x2="100" y2="200" className="connection" />
                <line x1="400" y1="200" x2="400" y2="350" className="connection" />
                <line x1="100" y1="200" x2="100" y2="350" className="connection" />
                <line x1="100" y1="350" x2="400" y2="350" className="connection" />
                <line x1="250" y1="400" x2="100" y2="350" className="connection" />
                <line x1="250" y1="400" x2="400" y2="350" className="connection" />
              </svg>
            </div>
            <div className="tx-badge badge-1">
              <span>TX: Carbon Record</span>
            </div>
            <div className="tx-badge badge-2">
              <span>Verified ✓</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default BlockchainSection;
