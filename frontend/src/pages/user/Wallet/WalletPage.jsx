/**
 * Wallet Page - Simplified Digital Coupon Box
 * 디지털 쿠폰함 (간소화된 UI)
 */

import React, { useState, useEffect } from 'react';
import algosdk from 'algosdk';
import './WalletPage.css';

function WalletPage() {
  const [wallet, setWallet] = useState(null);
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [assets, setAssets] = useState([]);
  const [advancedMode, setAdvancedMode] = useState(false);
  const [showMnemonic, setShowMnemonic] = useState(false);
  const [esgPoints, setEsgPoints] = useState(0);
  const [coupons, setCoupons] = useState(0);
  const [activities, setActivities] = useState([]);
  const [creatingToken, setCreatingToken] = useState(false);

  // 컴포넌트 마운트 시 데이터 로드
  useEffect(() => {
    autoCreateWallet();
    loadUserData();
  }, []);

  // 사용자 데이터 로드 (localStorage)
  const loadUserData = () => {
    const activityHistory = JSON.parse(localStorage.getItem('esg_activity_history') || '[]');
    const totalPoints = activityHistory.reduce((sum, activity) => sum + (activity.reward || 0), 0);
    const totalCoupons = Math.floor(totalPoints / 100);

    setEsgPoints(totalPoints);
    setCoupons(totalCoupons);
    setActivities(activityHistory.slice(0, 5)); // 최근 5개
  };

  // 자동 지갑 생성 (사용자 모르게)
  const autoCreateWallet = () => {
    const savedWallet = localStorage.getItem('algorand_wallet');

    if (savedWallet) {
      try {
        const walletData = JSON.parse(savedWallet);

        // 주소가 객체인 경우 문자열로 변환
        if (typeof walletData.address === 'object' && walletData.address.addr) {
          walletData.address = walletData.address.addr;
          localStorage.setItem('algorand_wallet', JSON.stringify(walletData));
        }

        // 주소가 유효한 문자열인지 확인
        if (typeof walletData.address === 'string' && walletData.address.length === 58) {
          setWallet(walletData);
          if (advancedMode) {
            fetchBalance(walletData.address);
          }
        } else {
          createWalletSilently();
        }
      } catch (error) {
        console.error('지갑 로드 실패:', error);
        createWalletSilently();
      }
    } else {
      // 지갑이 없으면 자동으로 생성
      createWalletSilently();
    }
  };

  // 조용히 지갑 생성 (알림 없이)
  const createWalletSilently = () => {
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
    } catch (error) {
      console.error('자동 지갑 생성 실패:', error);
    }
  };

  // 잔액 조회 (고급 모드에서만)
  const fetchBalance = async (address) => {
    setLoading(true);
    try {
      const algodClient = new algosdk.Algodv2(
        '',
        'https://testnet-api.algonode.cloud',
        ''
      );

      const accountInfo = await algodClient.accountInformation(address).do();
      const algoBalance = accountInfo.amount / 1000000;
      setBalance(algoBalance);

      // 보유 자산 정보
      if (accountInfo.assets && accountInfo.assets.length > 0) {
        const assetList = await Promise.all(
          accountInfo.assets.map(async (asset) => {
            try {
              const assetInfo = await algodClient.getAssetByID(asset['asset-id']).do();
              return {
                id: asset['asset-id'],
                amount: asset.amount / Math.pow(10, assetInfo.params.decimals),
                decimals: assetInfo.params.decimals,
                name: assetInfo.params.name,
                unitName: assetInfo.params['unit-name']
              };
            } catch (error) {
              return null;
            }
          })
        );
        setAssets(assetList.filter(asset => asset !== null));
      } else {
        setAssets([]);
      }
    } catch (error) {
      console.error('잔액 조회 실패:', error);
      setBalance(0);
      setAssets([]);
    } finally {
      setLoading(false);
    }
  };

  // 고급 모드 토글
  const toggleAdvancedMode = () => {
    const newMode = !advancedMode;
    setAdvancedMode(newMode);

    if (newMode && wallet) {
      fetchBalance(wallet.address);
    }
  };

  // 주소 복사
  const copyAddress = () => {
    navigator.clipboard.writeText(wallet.address);
    alert('✅ 주소가 복사되었습니다!');
  };

  // 복구 문구 복사
  const copyMnemonic = () => {
    navigator.clipboard.writeText(wallet.mnemonic);
    alert('✅ 복구 문구가 복사되었습니다!');
  };

  // 지갑 삭제
  const deleteWallet = () => {
    if (window.confirm('⚠️ 정말로 지갑을 삭제하시겠습니까?\n\n복구 문구를 백업하지 않으면 복구할 수 없습니다!')) {
      localStorage.removeItem('algorand_wallet');
      setWallet(null);
      setBalance(null);
      createWalletSilently();
    }
  };

  // ESG-GOLD 토큰 생성
  const createToken = async () => {
    if (!wallet) return;

    if (balance < 0.2) {
      alert('❌ 토큰 생성을 위해 최소 0.2 DC가 필요합니다.\n\n테스트 DC 받기에서 DC를 받아주세요.');
      return;
    }

    if (!window.confirm('🪙 ESG-GOLD 토큰을 생성하시겠습니까?\n\n총 발행량: 1,000,000 ESG-GOLD\n수수료: 약 0.1 DC')) {
      return;
    }

    setCreatingToken(true);

    try {
      const algodClient = new algosdk.Algodv2('', 'https://testnet-api.algonode.cloud', '');
      const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);
      const params = await algodClient.getTransactionParams().do();

      const txn = algosdk.makeAssetCreateTxnWithSuggestedParamsFromObject({
        from: account.addr,
        total: 1000000 * 100,
        decimals: 2,
        assetName: 'ESG-GOLD',
        unitName: 'ESGOLD',
        assetURL: 'https://pam-talk.com',
        manager: account.addr,
        reserve: account.addr,
        freeze: account.addr,
        clawback: account.addr,
        defaultFrozen: false,
        suggestedParams: params
      });

      const signedTxn = txn.signTxn(account.sk);
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();

      alert('⏳ 토큰 생성 중...\n\n약 4-5초 후 확정됩니다.');

      const confirmedTxn = await algosdk.waitForConfirmation(algodClient, txId, 4);
      const assetId = confirmedTxn['asset-index'];

      alert('🎉 ESG-GOLD 토큰이 생성되었습니다!\n\n자산 ID: ' + assetId);

      const updatedWallet = { ...wallet, esgGoldAssetId: assetId };
      localStorage.setItem('algorand_wallet', JSON.stringify(updatedWallet));
      setWallet(updatedWallet);

      setTimeout(() => fetchBalance(wallet.address), 1500);
    } catch (error) {
      console.error('토큰 생성 실패:', error);
      alert('❌ 토큰 생성에 실패했습니다.\n\n' + error.message);
    } finally {
      setCreatingToken(false);
    }
  };

  // 토큰 Opt-in
  const optInToAsset = async () => {
    const assetId = prompt('받고 싶은 토큰의 자산 ID를 입력하세요:');
    if (!assetId || isNaN(assetId)) return;

    setLoading(true);
    try {
      const algodClient = new algosdk.Algodv2('', 'https://testnet-api.algonode.cloud', '');
      const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);
      const params = await algodClient.getTransactionParams().do();

      const txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
        from: account.addr,
        to: account.addr,
        amount: 0,
        assetIndex: parseInt(assetId),
        suggestedParams: params
      });

      const signedTxn = txn.signTxn(account.sk);
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();
      await algosdk.waitForConfirmation(algodClient, txId, 4);

      alert('✅ 토큰 수령 설정이 완료되었습니다!');
      fetchBalance(wallet.address);
    } catch (error) {
      alert('❌ Opt-in에 실패했습니다.\n\n' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="wallet-page">
      <div className="wallet-container">
        {/* 헤더 */}
        <div className="wallet-header">
          <h1>💳 디지털 쿠폰함</h1>
          <p>ESG 활동으로 받은 보상을 확인하세요</p>
          <button
            className="btn-advanced-toggle"
            onClick={toggleAdvancedMode}
          >
            {advancedMode ? '🔧 간편 모드' : '⚙️ 고급 모드'}
          </button>
        </div>

        {!advancedMode ? (
          /* ========== 간편 모드 (일반 사용자용) ========== */
          <div className="simple-mode">
            {/* 포인트 요약 */}
            <div className="summary-cards">
              <div className="summary-card primary">
                <div className="card-icon">🌟</div>
                <div className="card-content">
                  <div className="card-label">보유 포인트</div>
                  <div className="card-value">{esgPoints.toLocaleString()} P</div>
                  <div className="card-desc">ESG 활동으로 적립</div>
                </div>
              </div>

              <div className="summary-card success">
                <div className="card-icon">🎟️</div>
                <div className="card-content">
                  <div className="card-label">사용 가능 쿠폰</div>
                  <div className="card-value">{coupons}개</div>
                  <div className="card-desc">100P당 1개 쿠폰</div>
                </div>
              </div>

              <div className="summary-card info">
                <div className="card-icon">📊</div>
                <div className="card-content">
                  <div className="card-label">총 활동</div>
                  <div className="card-value">{activities.length}회</div>
                  <div className="card-desc">친환경 실천</div>
                </div>
              </div>
            </div>

            {/* 최근 활동 내역 */}
            <div className="activity-section">
              <h3>💰 최근 포인트 적립 내역</h3>
              {activities.length > 0 ? (
                <div className="activity-list">
                  {activities.map((activity, index) => (
                    <div key={index} className="activity-item">
                      <div className="activity-icon">✅</div>
                      <div className="activity-info">
                        <div className="activity-name">{activity.activityName}</div>
                        <div className="activity-date">
                          {new Date(activity.timestamp).toLocaleDateString('ko-KR')}
                        </div>
                      </div>
                      <div className="activity-reward">+{activity.reward} P</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-activity">
                  <p>📭 아직 활동 내역이 없습니다</p>
                  <small>ESG 활동을 시작하고 포인트를 받아보세요!</small>
                </div>
              )}
            </div>

            {/* 안내 정보 */}
            <div className="info-box">
              <h4>💡 포인트 사용 방법</h4>
              <ul>
                <li>🎟️ 포인트 100P마다 디지털 쿠폰 1개 발급</li>
                <li>🏪 마켓플레이스에서 친환경 제품 구매</li>
                <li>🎁 특별 이벤트 및 혜택 참여</li>
                <li>🌱 환경 보호 프로젝트 후원</li>
              </ul>
            </div>
          </div>
        ) : (
          /* ========== 고급 모드 (블록체인 전문 사용자용) ========== */
          <div className="advanced-mode">
            {/* 잔액 카드 */}
            <div className="balance-card">
              <div className="balance-label">블록체인 잔액 (DC)</div>
              <div className="balance-amount">
                {loading ? (
                  <div className="loading-spinner">조회 중...</div>
                ) : (
                  <>
                    <span className="amount">{balance !== null ? balance.toFixed(6) : '---'}</span>
                    <span className="currency">DC</span>
                  </>
                )}
              </div>
              <button
                className="btn-refresh"
                onClick={() => fetchBalance(wallet.address)}
                disabled={loading}
              >
                🔄 {loading ? '조회 중...' : '잔액 새로고침'}
              </button>
            </div>

            {/* 토큰 카드 */}
            <div className="token-card">
              <div className="card-header">
                <h3>🪙 보유 토큰</h3>
                <button
                  className="btn-create-token"
                  onClick={createToken}
                  disabled={creatingToken || balance < 0.2}
                >
                  {creatingToken ? '⏳ 생성 중...' : '✨ ESG-GOLD 생성'}
                </button>
              </div>

              {assets.length === 0 ? (
                <div className="token-empty">
                  <p>🔍 보유한 토큰이 없습니다</p>
                  <small>ESG-GOLD 토큰을 생성하거나 다른 사용자로부터 토큰을 받아보세요</small>
                </div>
              ) : (
                <div className="token-list">
                  {assets.map((asset) => (
                    <div key={asset.id} className="token-item">
                      <div className="token-icon">
                        {asset.name === 'ESG-GOLD' ? '🌿' : '🪙'}
                      </div>
                      <div className="token-info">
                        <div className="token-name">{asset.name}</div>
                        <div className="token-id">ID: {asset.id}</div>
                      </div>
                      <div className="token-balance">
                        <div className="token-amount">{asset.amount.toLocaleString()}</div>
                        <div className="token-unit">{asset.unitName}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="token-actions">
                <button
                  className="btn-token-action"
                  onClick={optInToAsset}
                  disabled={loading}
                >
                  📥 토큰 받기 설정
                </button>
              </div>
            </div>

            {/* 주소 카드 */}
            <div className="address-card">
              <div className="card-header">
                <h3>📍 지갑 주소</h3>
                <button className="btn-copy" onClick={copyAddress}>
                  📋 복사
                </button>
              </div>
              <div className="address-box">
                {wallet && (typeof wallet.address === 'string' ? wallet.address : String(wallet.address))}
              </div>
              <div className="address-qr">
                <p>💡 이 주소로 DC를 받을 수 있습니다</p>
              </div>
            </div>

            {/* 테스트 DC 받기 */}
            <div className="faucet-card">
              <h3>🚰 테스트 DC 받기</h3>
              <p>테스트 환경에서 무료로 DC를 받아보세요</p>
              <a
                href="https://bank.testnet.algorand.network/"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-faucet"
              >
                DC 받기 →
              </a>
              <div className="faucet-info">
                <small>
                  1. 위 링크를 클릭<br/>
                  2. 지갑 주소 입력<br/>
                  3. "Dispense" 버튼 클릭<br/>
                  4. 5-10초 후 잔액 새로고침
                </small>
              </div>
            </div>

            {/* 복구 문구 카드 */}
            <div className="mnemonic-card">
              <div className="card-header">
                <h3>🔑 복구 문구</h3>
                <button
                  className="btn-toggle"
                  onClick={() => setShowMnemonic(!showMnemonic)}
                >
                  {showMnemonic ? '👁️ 숨기기' : '👁️‍🗨️ 보기'}
                </button>
              </div>

              {showMnemonic && wallet && (
                <>
                  <div className="warning-box">
                    ⚠️ 절대 다른 사람과 공유하지 마세요!
                  </div>
                  <div className="mnemonic-box">
                    {wallet.mnemonic}
                  </div>
                  <button className="btn-copy-mnemonic" onClick={copyMnemonic}>
                    📋 복구 문구 복사
                  </button>
                </>
              )}
            </div>

            {/* 위험 구역 */}
            <div className="danger-zone">
              <h3>⚠️ 위험 구역</h3>
              <button className="btn-delete" onClick={deleteWallet}>
                🔄 지갑 재생성
              </button>
              <p className="danger-warning">
                지갑을 재생성하면 새로운 주소가 발급됩니다
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default WalletPage;
