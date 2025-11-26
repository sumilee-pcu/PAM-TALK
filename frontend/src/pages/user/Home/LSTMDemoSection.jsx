/**
 * LSTM Demo Section
 * LSTM 수요 예측 데모 섹션
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

function LSTMDemoSection() {
  const navigate = useNavigate();

  return (
    <section className="lstm-demo-section">
      <div className="lstm-demo-container">
        <div className="demo-visual">
          <div className="demo-graphic">
            <div className="neural-network">
              <div className="network-layer input-layer">
                <div className="neuron"></div>
                <div className="neuron"></div>
                <div className="neuron"></div>
                <div className="neuron"></div>
              </div>
              <div className="network-layer hidden-layer">
                <div className="neuron"></div>
                <div className="neuron"></div>
                <div className="neuron"></div>
              </div>
              <div className="network-layer output-layer">
                <div className="neuron"></div>
              </div>
            </div>
            <div className="demo-badge">
              <span className="badge-icon">🤖</span>
              <span className="badge-text">AI 기반</span>
            </div>
          </div>
        </div>

        <div className="demo-content">
          <div className="demo-header">
            <span className="demo-tag">AI Technology</span>
            <h2 className="demo-title">
              <span className="gradient-text">LSTM 딥러닝</span>으로<br />
              수요를 예측합니다
            </h2>
          </div>

          <p className="demo-description">
            PAM-TALK은 최첨단 LSTM(Long Short-Term Memory) 신경망을 활용하여
            농산물 수요를 정확하게 예측합니다. 과거 데이터의 패턴을 학습하고
            미래 수요를 예측하여 재고 관리와 가격 최적화에 활용됩니다.
          </p>

          <div className="demo-features">
            <div className="demo-feature-item">
              <div className="feature-icon">📊</div>
              <div className="feature-text">
                <h4>실시간 예측</h4>
                <p>7일~30일 앞선 수요 예측</p>
              </div>
            </div>
            <div className="demo-feature-item">
              <div className="feature-icon">🎯</div>
              <div className="feature-text">
                <h4>높은 정확도</h4>
                <p>평균 22% MAPE 달성</p>
              </div>
            </div>
            <div className="demo-feature-item">
              <div className="feature-icon">⚡</div>
              <div className="feature-text">
                <h4>빠른 학습</h4>
                <p>90일 데이터로 15초 학습</p>
              </div>
            </div>
          </div>

          <button
            className="btn-demo"
            onClick={() => navigate('/demo/lstm')}
          >
            <span>실시간 데모 체험하기</span>
            <span className="btn-icon">→</span>
          </button>

          <div className="demo-tech-stack">
            <span className="tech-badge">TensorFlow</span>
            <span className="tech-badge">Keras</span>
            <span className="tech-badge">Python</span>
            <span className="tech-badge">LSTM</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default LSTMDemoSection;
