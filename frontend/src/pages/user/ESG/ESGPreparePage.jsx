/**
 * ESG Activity Preparation Page
 * ESG 활동 준비 페이지 - 디지털 쿠폰함 확인 및 포인트 조회
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import algosdk from 'algosdk';
import './ESGPage.css';

function ESGPreparePage() {
  const navigate = useNavigate();
  const [currentActivity, setCurrentActivity] = useState(null);
  const [wallet, setWallet] = useState(null);
  const [balance, setBalance] = useState(null);
  const [esgPoints, setEsgPoints] = useState(0);
  const [loading, setLoading] = useState(true);
  const [checkingBalance, setCheckingBalance] = useState(false);
  const [activityHistory, setActivityHistory] = useState([]);

  useEffect(() => {
    loadActivity();
    checkWallet();
    loadPoints();
  }, []);

  const loadActivity = () => {
    const savedActivity = localStorage.getItem('esg_current_activity');
    if (savedActivity) {
      setCurrentActivity(JSON.parse(savedActivity));
    } else {
      navigate('/esg');
    }
  };

  const checkWallet = async () => {
    setLoading(true);
    const savedWallet = localStorage.getItem('algorand_wallet');

    if (savedWallet) {
      try {
        const walletData = JSON.parse(savedWallet);

        // 주소가 객체인 경우 문자열로 변환
        if (typeof walletData.address === 'object' && walletData.address.addr) {
          walletData.address = walletData.address.addr;
          localStorage.setItem('algorand_wallet', JSON.stringify(walletData));
        }

        setWallet(walletData);
        await fetchBalance(walletData.address);
      } catch (error) {
        console.error('지갑 로드 실패:', error);
        setWallet(null);
      }
    } else {
      setWallet(null);
    }

    setLoading(false);
  };

  const loadPoints = () => {
    const history = JSON.parse(localStorage.getItem('esg_activity_history') || '[]');
    const totalPoints = history.reduce((sum, act) => sum + (act.reward || 0), 0);
    setEsgPoints(totalPoints);
    setActivityHistory(history);
  };

  const fetchBalance = async (address) => {
    setCheckingBalance(true);
    try {
      const algodClient = new algosdk.Algodv2('', 'https://testnet-api.algonode.cloud', '');
      const accountInfo = await algodClient.accountInformation(address).do();
      const algoBalance = accountInfo.amount / 1000000;
      setBalance(algoBalance);
    } catch (error) {
      console.error('잔액 조회 실패:', error);
      setBalance(0);
    } finally {
      setCheckingBalance(false);
    }
  };

  const createWallet = () => {
    try {
      const account = algosdk.generateAccount();
      const address = account.addr;
      const secretKey = account.sk;
      const mnemonic = algosdk.secretKeyToMnemonic(secretKey);

      const walletData = {
        address: address,
        mnemonic: mnemonic,
        createdAt: new Date().toISOString()
      };

      localStorage.setItem('algorand_wallet', JSON.stringify(walletData));
      setWallet(walletData);

      alert('🎉 디지털 쿠폰함이 준비되었습니다!\n\nESG 활동을 인증하고 보상을 받으실 수 있습니다.');
      fetchBalance(address);
    } catch (error) {
      console.error('지갑 생성 실패:', error);
      alert('❌ 디지털 쿠폰함 준비에 실패했습니다.');
    }
  };

  const startCapture = () => {
    if (!wallet) {
      alert('❌ 먼저 쿠폰함을 준비해주세요!');
      return;
    }

    navigate('/esg/capture');
  };

  const goBack = () => {
    localStorage.removeItem('esg_current_activity');
    navigate('/esg');
  };

  if (loading) {
    return (
      <div className="esg-page">
        <div className="esg-container">
          <div className="esg-header">
            <h1>🔄 준비 중...</h1>
            <p>잠시만 기다려주세요</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="esg-page">
      <div className="esg-container">
        {/* 헤더 */}
        <div className="esg-header">
          <h1>📸 활동 인증 준비</h1>
          <p>활동을 시작하기 전에 준비사항을 확인하세요</p>
        </div>

        {/* 선택한 활동 정보 */}
        {currentActivity && (
          <div className="users-table-container" style={{marginBottom: '2rem'}}>
            <h2 style={{marginBottom: '1rem'}}>선택한 활동</h2>
            <div style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '2rem',
              borderRadius: '16px',
              textAlign: 'center'
            }}>
              <div style={{fontSize: '4rem', marginBottom: '1rem'}}>
                {currentActivity.activity?.icon || '🌱'}
              </div>
              <h2 style={{fontSize: '2rem', marginBottom: '0.5rem'}}>
                {currentActivity.activity?.name}
              </h2>
              <div style={{fontSize: '1.5rem', opacity: 0.9}}>
                예상 보상: <span style={{fontWeight: 700}}>{currentActivity.activity?.reward} 포인트</span>
              </div>
            </div>
          </div>
        )}

        {/* 쿠폰 잔액 */}
        <div className="users-table-container" style={{marginBottom: '2rem'}}>
          <h2 style={{marginBottom: '1rem'}}>💳 쿠폰 잔액</h2>

          {!wallet ? (
            <div style={{textAlign: 'center', padding: '3rem', background: '#fff3cd', borderRadius: '12px', border: '2px solid #ffc107'}}>
              <div style={{fontSize: '4rem', marginBottom: '1rem'}}>⚠️</div>
              <h3 style={{fontSize: '1.5rem', marginBottom: '1rem', color: '#856404'}}>
                쿠폰함 준비 중
              </h3>
              <p style={{color: '#856404', marginBottom: '2rem'}}>
                ESG 활동 보상을 받으려면 먼저 디지털 쿠폰함을 준비해야 합니다.
              </p>
              <button
                onClick={createWallet}
                style={{
                  padding: '1rem 3rem',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                🆕 쿠폰함 준비하기
              </button>
              <div style={{marginTop: '1.5rem', fontSize: '0.9rem', color: '#666'}}>
                <p>✅ 무료로 생성</p>
                <p>✅ 즉시 사용 가능</p>
                <p>✅ 안전하게 보관</p>
              </div>
            </div>
          ) : (
            <div style={{background: '#d4edda', padding: '2rem', borderRadius: '12px', border: '2px solid #28a745'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem'}}>
                <div style={{fontSize: '3rem'}}>✅</div>
                <div>
                  <h3 style={{fontSize: '1.3rem', color: '#155724', marginBottom: '0.25rem'}}>
                    쿠폰함 준비 완료
                  </h3>
                  <p style={{fontSize: '0.9rem', color: '#155724', opacity: 0.8}}>
                    활동 인증 후 보상을 받을 수 있습니다
                  </p>
                </div>
              </div>

              {checkingBalance ? (
                <div style={{textAlign: 'center', color: '#155724'}}>
                  🔄 잔액 조회 중...
                </div>
              ) : (
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: '0.9rem', color: '#155724', marginBottom: '0.25rem'}}>
                    ESG-GOLD 디지털쿠폰 잔액
                  </div>
                  <div style={{fontSize: '1.5rem', fontWeight: 700, color: '#155724'}}>
                    {balance !== null ? balance.toFixed(6) : '---'} DC
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* 현재 포인트 */}
        <div className="users-table-container" style={{marginBottom: '2rem'}}>
          <h2 style={{marginBottom: '1rem'}}>🌟 현재 보유 포인트</h2>

          <div style={{
            background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
            padding: '2rem',
            borderRadius: '16px',
            textAlign: 'center'
          }}>
            <div style={{fontSize: '3rem', fontWeight: 700, color: '#667eea', marginBottom: '0.5rem'}}>
              {esgPoints.toLocaleString()} P
            </div>
            <div style={{fontSize: '1rem', color: '#666'}}>
              총 {activityHistory.length}회 활동 완료
            </div>

            {activityHistory.length > 0 && (
              <div style={{marginTop: '1.5rem', textAlign: 'left'}}>
                <div style={{fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.5rem', color: '#333'}}>
                  최근 활동:
                </div>
                {activityHistory.slice(0, 3).map((act, idx) => (
                  <div key={idx} style={{
                    padding: '0.75rem',
                    background: 'rgba(255,255,255,0.7)',
                    borderRadius: '8px',
                    marginBottom: '0.5rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <span style={{fontSize: '0.9rem'}}>{act.activityName}</span>
                    <span style={{fontWeight: 700, color: '#51cf66'}}>+{act.reward} P</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 안내사항 */}
        <div className="users-table-container" style={{marginBottom: '2rem'}}>
          <h2 style={{marginBottom: '1rem'}}>📋 인증 안내</h2>

          <div style={{background: '#f8f9fa', padding: '1.5rem', borderRadius: '12px'}}>
            <div style={{marginBottom: '1rem'}}>
              <strong style={{color: '#667eea'}}>✓ 준비물:</strong>
              <ul style={{marginTop: '0.5rem', paddingLeft: '1.5rem', color: '#666'}}>
                <li>스마트폰 카메라 (활동 사진 촬영)</li>
                <li>GPS 위치 정보 (활동 위치 확인)</li>
                <li>디지털 쿠폰함 (보상 수령)</li>
              </ul>
            </div>

            <div style={{marginBottom: '1rem'}}>
              <strong style={{color: '#667eea'}}>✓ 인증 방법:</strong>
              <ul style={{marginTop: '0.5rem', paddingLeft: '1.5rem', color: '#666'}}>
                <li>활동 사진을 명확하게 촬영하세요</li>
                <li>AI가 자동으로 활동을 검증합니다</li>
                <li>GPS로 위치가 기록됩니다</li>
                <li>검증 완료 시 즉시 포인트가 지급됩니다</li>
              </ul>
            </div>

            <div>
              <strong style={{color: '#667eea'}}>✓ 예상 소요 시간:</strong>
              <p style={{marginTop: '0.5rem', color: '#666'}}>약 30초 (사진 촬영 → AI 검증 → 보상 지급)</p>
            </div>
          </div>
        </div>

        {/* 액션 버튼 */}
        <div style={{display: 'flex', gap: '1rem', justifyContent: 'center'}}>
          <button
            onClick={goBack}
            style={{
              padding: '1rem 2rem',
              background: 'white',
              color: '#666',
              border: '2px solid #ddd',
              borderRadius: '12px',
              fontSize: '1.1rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            ← 뒤로 가기
          </button>

          <button
            onClick={startCapture}
            disabled={!wallet}
            style={{
              padding: '1rem 3rem',
              background: wallet ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#ccc',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '1.1rem',
              fontWeight: 600,
              cursor: wallet ? 'pointer' : 'not-allowed',
              boxShadow: wallet ? '0 4px 12px rgba(102, 126, 234, 0.3)' : 'none'
            }}
          >
            📸 인증 시작하기
          </button>
        </div>
      </div>
    </div>
  );
}

export default ESGPreparePage;
