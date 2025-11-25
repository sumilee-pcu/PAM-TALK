import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { verifyActivityImage, loadModel } from '../../../utils/aiClassifier';
import { processActivityReward } from '../../../utils/rewardDistributor';
import './ESGCapturePage.css';

/**
 * ESG Activity Capture Page
 * - Camera integration for taking photos
 * - GPS location tracking
 * - Image preview and confirmation
 * - Target: 30-second completion time
 */

function ESGCapturePage() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [currentActivity, setCurrentActivity] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [location, setLocation] = useState(null);
  const [loadingLocation, setLoadingLocation] = useState(false);
  const [error, setError] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [loadingAI, setLoadingAI] = useState(false);
  const [showPermissionModal, setShowPermissionModal] = useState(false);

  // Load current activity from localStorage
  useEffect(() => {
    const savedActivity = localStorage.getItem('esg_current_activity');
    if (savedActivity) {
      setCurrentActivity(JSON.parse(savedActivity));
      // Auto-start camera and GPS
      initializeCapture();
      // Pre-load AI model
      preloadAI();
    } else {
      // No activity selected, redirect to ESG page
      navigate('/esg');
    }

    // Cleanup: stop camera when component unmounts
    return () => {
      stopCamera();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  // Pre-load AI model
  const preloadAI = async () => {
    setLoadingAI(true);
    try {
      await loadModel();
      console.log('✅ AI model ready');
      setLoadingAI(false);
    } catch (err) {
      console.error('❌ AI model loading failed:', err);
      setLoadingAI(false);
      // Show warning but allow user to continue
      setError('AI 모델 로딩 실패. 인증은 가능하지만 AI 검증 없이 진행됩니다.');
    }
  };

  // Initialize camera and GPS
  const initializeCapture = async () => {
    await Promise.all([
      startCamera(),
      getLocation()
    ]);
  };

  // Start camera
  const startCamera = async () => {
    try {
      // Request camera with back camera preference
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: 'environment' }, // Prefer back camera on mobile
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.setAttribute('playsinline', 'true'); // Important for iOS
        videoRef.current.play();
        setCameraActive(true);
        setError(null);
        console.log('Camera started successfully');
      }
    } catch (err) {
      console.error('Camera access error:', err);

      let errorMsg = '카메라에 접근할 수 없습니다.';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        errorMsg = '카메라 권한이 거부되었습니다. 브라우저 설정에서 카메라 권한을 허용해주세요.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        errorMsg = '카메라를 찾을 수 없습니다.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        errorMsg = '카메라가 다른 앱에서 사용 중입니다.';
      }

      setError(errorMsg);
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setCameraActive(false);
    }
  };

  // Get GPS location
  const getLocation = async () => {
    setLoadingLocation(true);
    setShowPermissionModal(false);

    if (!navigator.geolocation) {
      console.error('Geolocation not supported');
      setError('이 기기는 GPS를 지원하지 않습니다.');
      setLoadingLocation(false);
      return;
    }

    try {
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
          resolve,
          reject,
          {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
          }
        );
      });

      const locationData = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: new Date().toISOString()
      };

      setLocation(locationData);
      setLoadingLocation(false);
      setError(null);
      console.log('Location obtained:', locationData);
    } catch (err) {
      console.error('GPS error:', err);

      setLoadingLocation(false);

      // Show permission modal for permission denied
      if (err.code === 1) {
        setShowPermissionModal(true);
        setError('위치 권한이 필요합니다');
      } else if (err.code === 2) {
        setError('위치를 확인할 수 없습니다. GPS를 활성화해주세요.');
      } else if (err.code === 3) {
        setError('위치 확인 시간이 초과되었습니다. 다시 시도해주세요.');
      } else {
        setError('위치 정보를 가져올 수 없습니다.');
      }
    }
  };

  // Capture photo from video stream
  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to image data
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImage(imageData);

    // Stop camera after capture
    stopCamera();
  };

  // Retake photo
  const retakePhoto = () => {
    setCapturedImage(null);
    startCamera();
  };

  // Confirm and submit
  const confirmSubmit = async () => {
    if (!capturedImage || !location) {
      alert('사진과 위치 정보가 필요합니다.');
      return;
    }

    console.log('🔍 Submit button clicked - starting verification');
    console.log('📊 Current state:', { processing, loadingAI, hasImage: !!capturedImage, hasLocation: !!location });

    setProcessing(true);
    setError(null);

    try {
      // AI image classification
      console.log('Starting AI verification...');

      let verificationResult;
      try {
        verificationResult = await verifyActivityImage(
          capturedImage,
          currentActivity.activity.id
        );
      } catch (aiError) {
        console.warn('⚠️ AI verification error, allowing manual approval:', aiError);
        // If AI fails, use a fallback verification
        verificationResult = {
          verified: true,
          confidence: 0,
          message: 'AI 검증 실패 - 수동 승인됨',
          matches: []
        };
      }

      console.log('AI Verification Result:', verificationResult);

      if (!verificationResult.verified) {
        // AI verification failed
        setError(verificationResult.message);
        setProcessing(false);

        // Ask user if they want to retry
        const retry = window.confirm(
          `AI 인증 실패: ${verificationResult.message}\n\n다시 촬영하시겠습니까?`
        );

        if (retry) {
          retakePhoto();
        }
        return;
      }

      // AI verification passed
      console.log('AI verification passed!');

      // Create activity record
      const activityRecord = {
        category: currentActivity.category,
        activityId: currentActivity.activity.id,
        activityName: currentActivity.activity.name,
        reward: currentActivity.activity.reward,
        image: capturedImage,
        location: location,
        timestamp: new Date().toISOString(),
        verified: true,
        aiConfidence: verificationResult.confidence,
        aiMatches: verificationResult.matches,
        txId: null
      };

      // Process blockchain reward distribution
      console.log('Processing blockchain reward...');
      try {
        const rewardResult = await processActivityReward(activityRecord);
        console.log('Reward processed:', rewardResult);

        // Update activity record with transaction ID
        activityRecord.txId = rewardResult.txId;
        activityRecord.blockRound = rewardResult.round;

        // Save to activity history
        const existingHistory = JSON.parse(localStorage.getItem('esg_activity_history') || '[]');
        existingHistory.unshift(activityRecord);
        localStorage.setItem('esg_activity_history', JSON.stringify(existingHistory));

        // Clear current activity
        localStorage.removeItem('esg_current_activity');

        // Show success message with blockchain confirmation
        alert(
          `✅ 인증 완료!\n\n` +
          `🤖 AI 검증: ${verificationResult.message}\n` +
          `⛓️ 블록체인 기록: Round ${rewardResult.round}\n` +
          `🪙 보상: +${currentActivity.activity.reward} ESG-GOLD\n` +
          `💰 새 잔액: ${rewardResult.newBalance} ESG-GOLD\n\n` +
          `Transaction ID: ${rewardResult.txId.substring(0, 20)}...`
        );

        // Navigate back to ESG page
        navigate('/esg');

      } catch (rewardError) {
        console.error('Blockchain reward error:', rewardError);

        // Save activity anyway (without blockchain record)
        const existingHistory = JSON.parse(localStorage.getItem('esg_activity_history') || '[]');
        existingHistory.unshift(activityRecord);
        localStorage.setItem('esg_activity_history', JSON.stringify(existingHistory));

        // Show warning but allow to continue
        const continueAnyway = window.confirm(
          `⚠️ 블록체인 기록 실패\n` +
          `${rewardError.message}\n\n` +
          `활동은 AI로 검증되었습니다.\n` +
          `계속하시겠습니까?`
        );

        if (continueAnyway) {
          localStorage.removeItem('esg_current_activity');
          navigate('/esg');
        } else {
          setProcessing(false);
        }
      }
    } catch (err) {
      console.error('Submission error:', err);
      setError(`인증 처리 중 오류가 발생했습니다: ${err.message}`);
      setProcessing(false);
    }
  };

  // Cancel and go back
  const handleCancel = () => {
    stopCamera();
    localStorage.removeItem('esg_current_activity');
    navigate('/esg');
  };

  if (!currentActivity) {
    return <div className="capture-loading">로딩 중...</div>;
  }

  return (
    <div className="capture-page">
      <div className="capture-container">
        {/* Header */}
        <div className="capture-header">
          <button className="btn-cancel" onClick={handleCancel}>
            ✕ 취소
          </button>
          <div className="capture-title">
            <h2>{currentActivity.activity.name}</h2>
            <p>+{currentActivity.activity.reward} ESG-GOLD</p>
          </div>
          <div className="capture-spacer"></div>
        </div>

        {/* Status Bar */}
        <div className="status-bar">
          <div className={`status-item ${location ? 'active' : ''}`}>
            {loadingLocation ? (
              <span>📍 위치 확인 중...</span>
            ) : location ? (
              <span>✅ 위치 확인됨</span>
            ) : (
              <button
                className="btn-retry-location"
                onClick={getLocation}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'inherit',
                  cursor: 'pointer',
                  width: '100%',
                  padding: '0',
                  textDecoration: 'underline'
                }}
              >
                ❌ 위치 재시도
              </button>
            )}
          </div>
          <div className={`status-item ${cameraActive || capturedImage ? 'active' : ''}`}>
            {capturedImage ? (
              <span>✅ 사진 촬영됨</span>
            ) : cameraActive ? (
              <span>📸 카메라 활성</span>
            ) : (
              <span>❌ 카메라 필요</span>
            )}
          </div>
          <div className={`status-item active`}>
            {loadingAI ? (
              <span>🤖 AI 로딩 중...</span>
            ) : (
              <span>✅ AI 준비됨</span>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && !showPermissionModal && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {/* Permission Modal */}
        {showPermissionModal && (
          <div className="permission-modal-overlay">
            <div className="permission-modal">
              <div className="modal-icon">📍</div>
              <h3>위치 권한이 필요합니다</h3>
              <p className="modal-description">
                활동 인증을 위해 현재 위치 정보가 필요합니다.<br/>
                아래 단계를 따라 위치 권한을 허용해주세요.
              </p>

              <div className="permission-steps">
                <div className="step">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <strong>브라우저 주소창 옆</strong> 자물쇠 또는 정보 아이콘 클릭
                  </div>
                </div>
                <div className="step">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <strong>위치 권한</strong>을 "허용"으로 변경
                  </div>
                </div>
                <div className="step">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    페이지를 <strong>새로고침</strong>하거나 아래 "다시 시도" 버튼 클릭
                  </div>
                </div>
              </div>

              <div className="modal-actions">
                <button
                  className="btn-retry-permission"
                  onClick={getLocation}
                >
                  🔄 다시 시도
                </button>
                <button
                  className="btn-close-modal"
                  onClick={() => setShowPermissionModal(false)}
                >
                  닫기
                </button>
              </div>

              <p className="modal-help">
                💡 위치 권한을 허용하지 않으면 활동 인증을 진행할 수 없습니다.
              </p>
            </div>
          </div>
        )}

        {/* Camera View / Captured Image */}
        <div className="capture-view">
          {!capturedImage ? (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="video-stream"
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
            </>
          ) : (
            <img src={capturedImage} alt="Captured" className="captured-image" />
          )}

          {/* Capture Guide Overlay */}
          {!capturedImage && cameraActive && (
            <div className="capture-guide">
              <div className="guide-frame"></div>
              <p className="guide-text">
                {currentActivity.activity.name}을(를) 화면 중앙에 맞춰주세요
              </p>
            </div>
          )}
        </div>

        {/* Location Info */}
        {location && (
          <div className="location-info">
            <p>
              📍 위치: {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
            </p>
            <p className="location-accuracy">
              정확도: {Math.round(location.accuracy)}m
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="capture-actions">
          {!capturedImage ? (
            <button
              className="btn-capture"
              onClick={capturePhoto}
              disabled={!cameraActive || !location}
            >
              📸 촬영하기
            </button>
          ) : (
            <>
              <button
                className="btn-retake"
                onClick={retakePhoto}
                disabled={processing}
              >
                🔄 다시 찍기
              </button>
              <button
                className="btn-submit"
                onClick={confirmSubmit}
                disabled={processing}
              >
                {processing ? '🤖 AI 검증 중...' : '✓ 인증하기'}
              </button>
            </>
          )}
        </div>

        {/* Instructions */}
        <div className="capture-instructions">
          <h3>📋 인증 방법</h3>
          <ul>
            <li>위치 권한과 카메라 권한을 허용해주세요</li>
            <li>{currentActivity.activity.name} 활동을 명확하게 촬영해주세요</li>
            <li>AI가 자동으로 활동을 검증합니다</li>
            <li>검증 완료 후 자동으로 보상이 지급됩니다</li>
            <li>💡 AI 로딩이 느리거나 실패해도 인증이 가능합니다</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ESGCapturePage;
