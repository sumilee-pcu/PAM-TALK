import React, { useState, useEffect } from 'react';
import './PWAInstallPrompt.css';

function PWAInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [showIOSPrompt, setShowIOSPrompt] = useState(false);

  useEffect(() => {
    // iOS 체크
    const isIOSDevice = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    setIsIOS(isIOSDevice);

    // iOS에서 이미 설치되었는지 확인
    const isInStandaloneMode = window.matchMedia('(display-mode: standalone)').matches;

    if (isIOSDevice && !isInStandaloneMode) {
      // localStorage로 iOS 프롬프트를 이전에 닫았는지 확인
      const iosPromptClosed = localStorage.getItem('ios-install-prompt-closed');
      if (!iosPromptClosed) {
        setTimeout(() => setShowIOSPrompt(true), 3000);
      }
    }

    // Android/Desktop PWA 설치 이벤트
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);

      // localStorage로 프롬프트를 이전에 닫았는지 확인
      const promptClosed = localStorage.getItem('pwa-install-prompt-closed');
      if (!promptClosed) {
        setTimeout(() => setShowPrompt(true), 3000);
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // 앱이 설치되었을 때
    window.addEventListener('appinstalled', () => {
      console.log('✅ PWA가 설치되었습니다!');
      setShowPrompt(false);
      setDeferredPrompt(null);
    });

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      console.log('사용자가 PWA 설치를 수락했습니다');
    } else {
      console.log('사용자가 PWA 설치를 거부했습니다');
    }

    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleClose = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-install-prompt-closed', 'true');
  };

  const handleIOSClose = () => {
    setShowIOSPrompt(false);
    localStorage.setItem('ios-install-prompt-closed', 'true');
  };

  // iOS 설치 안내
  if (isIOS && showIOSPrompt) {
    return (
      <div className="pwa-install-prompt ios">
        <div className="prompt-content">
          <button className="close-btn" onClick={handleIOSClose}>✕</button>
          <div className="prompt-icon">📱</div>
          <h3>홈 화면에 추가</h3>
          <p>PAM-TALK을 앱처럼 사용하세요!</p>

          <div className="ios-steps">
            <div className="step">
              <span className="step-icon">1️⃣</span>
              <span>하단의 공유 버튼(<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M16 5l-1.42 1.42-1.59-1.59V16h-1.98V4.83L9.42 6.42 8 5l4-4 4 4zm4 5v11c0 1.1-.9 2-2 2H6c-1.11 0-2-.9-2-2V10c0-1.11.89-2 2-2h3v2H6v11h12V10h-3V8h3c1.1 0 2 .89 2 2z"/></svg>) 탭</span>
            </div>
            <div className="step">
              <span className="step-icon">2️⃣</span>
              <span>"홈 화면에 추가" 선택</span>
            </div>
            <div className="step">
              <span className="step-icon">3️⃣</span>
              <span>추가 버튼 탭</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Android/Desktop 설치 프롬프트
  if (!isIOS && showPrompt && deferredPrompt) {
    return (
      <div className="pwa-install-prompt">
        <div className="prompt-content">
          <button className="close-btn" onClick={handleClose}>✕</button>
          <div className="prompt-icon">🚀</div>
          <h3>앱으로 설치하기</h3>
          <p>PAM-TALK을 홈 화면에 추가하고<br/>앱처럼 빠르게 사용하세요!</p>

          <div className="prompt-benefits">
            <div className="benefit">✅ 빠른 실행</div>
            <div className="benefit">✅ 오프라인 사용</div>
            <div className="benefit">✅ 푸시 알림</div>
          </div>

          <button className="install-btn" onClick={handleInstallClick}>
            📲 설치하기
          </button>
          <button className="later-btn" onClick={handleClose}>
            나중에
          </button>
        </div>
      </div>
    );
  }

  return null;
}

export default PWAInstallPrompt;
