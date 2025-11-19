import React from 'react';
import './OptInGuide.css';

/**
 * Asset Opt-in 안내 컴포넌트
 *
 * Props:
 *   - assetId: Asset ID (기본값: 3330375002)
 *   - onClose: 닫기 버튼 콜백
 */
const OptInGuide = ({ assetId = 3330375002, onClose }) => {
  return (
    <div className="optin-guide-overlay">
      <div className="optin-guide-modal">
        <div className="optin-guide-header">
          <h2>🎁 디지털 쿠폰 받기 준비</h2>
          {onClose && (
            <button className="close-button" onClick={onClose}>
              ✕
            </button>
          )}
        </div>

        <div className="optin-guide-content">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>페라 월렛 설치</h3>
              <p>iOS 또는 Android에서 Pera Wallet 앱 다운로드</p>
              <div className="app-links">
                <a href="https://apps.apple.com/app/pera-wallet/id1459898525" target="_blank" rel="noopener noreferrer">
                  App Store
                </a>
                <a href="https://play.google.com/store/apps/details?id=com.algorand.android" target="_blank" rel="noopener noreferrer">
                  Google Play
                </a>
              </div>
            </div>
          </div>

          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>지갑 생성</h3>
              <p>페라 월렛에서 새 계정 생성 또는 기존 계정 가져오기</p>
            </div>
          </div>

          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Asset Opt-in</h3>
              <p>PAM-POINT 토큰을 받기 위해 Asset 추가</p>
              <div className="optin-instructions">
                <ol>
                  <li>페라 월렛 열기</li>
                  <li>"Add Asset" 또는 "+" 버튼 탭</li>
                  <li>Asset ID 입력: <code className="asset-id">{assetId}</code></li>
                  <li>"Add" 버튼 탭 (수수료: 0.001 ALGO)</li>
                </ol>
              </div>
            </div>
          </div>

          <div className="step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h3>주소 복사</h3>
              <p>페라 월렛에서 내 알고랜드 주소 복사하여 입력</p>
            </div>
          </div>
        </div>

        <div className="optin-guide-footer">
          <div className="info-box">
            <strong>💡 참고:</strong> Opt-in은 최초 1회만 필요하며, 이후에는 자동으로 쿠폰을 받을 수 있습니다.
          </div>
        </div>
      </div>
    </div>
  );
};

export default OptInGuide;
