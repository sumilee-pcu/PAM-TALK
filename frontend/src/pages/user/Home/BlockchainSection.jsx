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
            <img src="https://algorand.foundation/static/algorand-logo.svg" alt="Algorand" />
          </div>
          <h2 className="blockchain-title">
            <span className="gradient-text">Algorand</span> 블록체인<br />
            기반의 투명한 시스템
          </h2>
          <p className="blockchain-description">
            PAM-TALK은 탄소 중립 블록체인인 Algorand를 사용하여 모든 탄소 감축 활동과 검증 결과를
            투명하고 안전하게 기록합니다.
          </p>

          <div className="blockchain-features">
            <div className="blockchain-feature">
              <div className="feature-icon-wrapper">
                <span className="feature-icon">🌱</span>
              </div>
              <h4>탄소 중립</h4>
              <p>에너지 효율적인 Pure Proof-of-Stake로 환경을 보호합니다</p>
            </div>
            <div className="blockchain-feature">
              <div className="feature-icon-wrapper">
                <span className="feature-icon">⚡</span>
              </div>
              <h4>초고속 처리</h4>
              <p>4.5초 이내 거래 완결로 즉시 리워드를 받을 수 있습니다</p>
            </div>
            <div className="blockchain-feature">
              <div className="feature-icon-wrapper">
                <span className="feature-icon">🔒</span>
              </div>
              <h4>완벽한 보안</h4>
              <p>블록체인 기술로 데이터 위변조가 불가능합니다</p>
            </div>
            <div className="blockchain-feature">
              <div className="feature-icon-wrapper">
                <span className="feature-icon">💰</span>
              </div>
              <h4>저렴한 수수료</h4>
              <p>0.001 ALGO의 최소 수수료로 경제적입니다</p>
            </div>
          </div>

          <div className="blockchain-stats">
            <div className="stat">
              <div className="stat-value">3,330,375,002</div>
              <div className="stat-label">PAM Token Asset ID</div>
            </div>
            <div className="stat">
              <div className="stat-value">100%</div>
              <div className="stat-label">투명성 보장</div>
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
