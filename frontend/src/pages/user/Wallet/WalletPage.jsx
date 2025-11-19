/**
 * Wallet Page - Algorand Wallet
 * 알고랜드 지갑 페이지
 */

import React, { useState, useEffect } from 'react';
import algosdk from 'algosdk';
import './WalletPage.css';

function WalletPage() {
  const [wallet, setWallet] = useState(null);
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showMnemonic, setShowMnemonic] = useState(false);
  const [assets, setAssets] = useState([]);
  const [creatingToken, setCreatingToken] = useState(false);

  // 컴포넌트 마운트 시 저장된 지갑 불러오기
  useEffect(() => {
    const savedWallet = localStorage.getItem('algorand_wallet');
    if (savedWallet) {
      const walletData = JSON.parse(savedWallet);
      setWallet(walletData);
      fetchBalance(walletData.address);
    }
  }, []);

  // 새 지갑 생성
  const createWallet = () => {
    try {
      // 알고랜드 계정 생성
      const account = algosdk.generateAccount();

      // 니모닉 생성 (25단어)
      const mnemonic = algosdk.secretKeyToMnemonic(account.sk);

      const walletData = {
        address: account.addr,
        mnemonic: mnemonic,
        createdAt: new Date().toISOString()
      };

      // 로컬스토리지에 저장 (실제 운영에서는 암호화 필요!)
      localStorage.setItem('algorand_wallet', JSON.stringify(walletData));

      setWallet(walletData);
      setShowMnemonic(true);

      alert('🎉 알고랜드 지갑이 생성되었습니다!\n\n⚠️ 니모닉을 안전한 곳에 보관하세요!');
    } catch (error) {
      console.error('지갑 생성 실패:', error);
      alert('지갑 생성에 실패했습니다: ' + error.message);
    }
  };

  // 니모닉으로 지갑 복구
  const recoverWallet = () => {
    const mnemonic = prompt('25단어 니모닉을 입력하세요 (공백으로 구분):');

    if (!mnemonic) return;

    try {
      const account = algosdk.mnemonicToSecretKey(mnemonic);

      const walletData = {
        address: account.addr,
        mnemonic: mnemonic,
        createdAt: new Date().toISOString()
      };

      localStorage.setItem('algorand_wallet', JSON.stringify(walletData));
      setWallet(walletData);

      alert('✅ 지갑이 복구되었습니다!');
      fetchBalance(account.addr);
    } catch (error) {
      console.error('지갑 복구 실패:', error);
      alert('❌ 올바른 니모닉이 아닙니다: ' + error.message);
    }
  };

  // 잔액 조회 (TestNet)
  const fetchBalance = async (address) => {
    setLoading(true);
    try {
      // AlgoNode TestNet API 사용
      const algodClient = new algosdk.Algodv2(
        '',
        'https://testnet-api.algonode.cloud',
        ''
      );

      const accountInfo = await algodClient.accountInformation(address).do();

      // microAlgos를 ALGO로 변환 (1 ALGO = 1,000,000 microAlgos)
      const algoBalance = accountInfo.amount / 1000000;

      setBalance(algoBalance);

      // 보유 자산(토큰) 정보 가져오기
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
                unitName: assetInfo.params['unit-name'],
                creator: assetInfo.params.creator,
                total: assetInfo.params.total
              };
            } catch (error) {
              console.error('자산 정보 조회 실패:', error);
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

  // 지갑 삭제
  const deleteWallet = () => {
    if (window.confirm('⚠️ 정말로 지갑을 삭제하시겠습니까?\n\n니모닉을 백업하지 않으면 복구할 수 없습니다!')) {
      localStorage.removeItem('algorand_wallet');
      setWallet(null);
      setBalance(null);
      setShowMnemonic(false);
      alert('지갑이 삭제되었습니다.');
    }
  };

  // 주소 복사
  const copyAddress = () => {
    navigator.clipboard.writeText(wallet.address);
    alert('✅ 주소가 복사되었습니다!');
  };

  // 니모닉 복사
  const copyMnemonic = () => {
    navigator.clipboard.writeText(wallet.mnemonic);
    alert('✅ 니모닉이 복사되었습니다!');
  };

  // 토큰 Opt-in (다른 사용자가 토큰을 받기 위해 필요)
  const optInToAsset = async () => {
    const assetId = prompt('받고 싶은 토큰의 자산 ID를 입력하세요:');

    if (!assetId || isNaN(assetId)) {
      alert('❌ 올바른 자산 ID를 입력하세요.');
      return;
    }

    setLoading(true);

    try {
      const algodClient = new algosdk.Algodv2(
        '',
        'https://testnet-api.algonode.cloud',
        ''
      );

      const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);
      const params = await algodClient.getTransactionParams().do();

      // Opt-in 트랜잭션 (자신에게 0개 전송)
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

      alert('✅ 토큰 수령 설정이 완료되었습니다!\n\n이제 이 토큰을 받을 수 있습니다.');
      fetchBalance(wallet.address);
    } catch (error) {
      console.error('Opt-in 실패:', error);
      alert('❌ Opt-in에 실패했습니다.\n\n' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // 토큰 전송
  const sendToken = async () => {
    if (assets.length === 0) {
      alert('❌ 전송할 토큰이 없습니다.');
      return;
    }

    const assetId = prompt('전송할 토큰의 자산 ID를 입력하세요:\n\n' +
      assets.map(a => `${a.name} (ID: ${a.id})`).join('\n'));

    if (!assetId || isNaN(assetId)) return;

    const selectedAsset = assets.find(a => a.id === parseInt(assetId));
    if (!selectedAsset) {
      alert('❌ 해당 토큰을 보유하고 있지 않습니다.');
      return;
    }

    const recipient = prompt('받는 사람의 알고랜드 주소를 입력하세요:');
    if (!recipient || recipient.length !== 58) {
      alert('❌ 올바른 알고랜드 주소를 입력하세요 (58자).');
      return;
    }

    const amount = prompt(`전송할 ${selectedAsset.unitName} 수량을 입력하세요:\n\n보유량: ${selectedAsset.amount.toLocaleString()}`);
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
      alert('❌ 올바른 수량을 입력하세요.');
      return;
    }

    if (parseFloat(amount) > selectedAsset.amount) {
      alert('❌ 보유량보다 많은 수량을 전송할 수 없습니다.');
      return;
    }

    if (!window.confirm(`💸 토큰을 전송하시겠습니까?\n\n토큰: ${selectedAsset.name}\n수량: ${amount} ${selectedAsset.unitName}\n받는 사람: ${recipient.substring(0, 10)}...${recipient.substring(48)}`)) {
      return;
    }

    setLoading(true);

    try {
      const algodClient = new algosdk.Algodv2(
        '',
        'https://testnet-api.algonode.cloud',
        ''
      );

      const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);
      const params = await algodClient.getTransactionParams().do();

      // 토큰 전송 트랜잭션
      const txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
        from: account.addr,
        to: recipient,
        amount: Math.round(parseFloat(amount) * Math.pow(10, selectedAsset.decimals)),
        assetIndex: parseInt(assetId),
        suggestedParams: params
      });

      const signedTxn = txn.signTxn(account.sk);
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();

      alert('⏳ 토큰 전송 중...\n\n트랜잭션 ID: ' + txId);

      await algosdk.waitForConfirmation(algodClient, txId, 4);

      alert(`✅ 토큰이 전송되었습니다!\n\n${amount} ${selectedAsset.unitName}가 성공적으로 전송되었습니다.`);
      fetchBalance(wallet.address);
    } catch (error) {
      console.error('토큰 전송 실패:', error);
      alert('❌ 토큰 전송에 실패했습니다.\n\n' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // ESG-GOLD 토큰 생성
  const createToken = async () => {
    if (!wallet) return;

    // 잔액 확인
    if (balance < 0.2) {
      alert('❌ 토큰 생성을 위해 최소 0.2 ALGO가 필요합니다.\n\n현재 잔액: ' + balance.toFixed(6) + ' ALGO\n\nTestNet Dispenser에서 ALGO를 받아주세요.');
      return;
    }

    if (!window.confirm('🪙 ESG-GOLD 토큰을 생성하시겠습니까?\n\n토큰명: ESG-GOLD\n총 발행량: 1,000,000 ESGOLD\n\n약 0.1 ALGO의 수수료가 발생합니다.')) {
      return;
    }

    setCreatingToken(true);

    try {
      // 알고랜드 클라이언트 설정
      const algodClient = new algosdk.Algodv2(
        '',
        'https://testnet-api.algonode.cloud',
        ''
      );

      // 계정 복구 (서명을 위해 필요)
      const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);

      // 네트워크 파라미터 가져오기
      const params = await algodClient.getTransactionParams().do();

      // ASA 생성 트랜잭션 구성
      const txn = algosdk.makeAssetCreateTxnWithSuggestedParamsFromObject({
        from: account.addr,
        total: 1000000 * 100, // 1,000,000 토큰 (소수점 2자리)
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

      // 트랜잭션 서명
      const signedTxn = txn.signTxn(account.sk);

      // 트랜잭션 전송
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();

      // 트랜잭션 확정 대기
      alert('⏳ 토큰 생성 중입니다...\n\n트랜잭션 ID: ' + txId + '\n\n약 4-5초 후 확정됩니다.');

      const confirmedTxn = await algosdk.waitForConfirmation(algodClient, txId, 4);

      // 생성된 자산 ID
      const assetId = confirmedTxn['asset-index'];

      alert('🎉 ESG-GOLD 토큰이 생성되었습니다!\n\n자산 ID: ' + assetId + '\n총 발행량: 1,000,000 ESGOLD\n\n지갑 정보에 자산 ID를 저장합니다.');

      // 지갑에 토큰 정보 저장
      const updatedWallet = {
        ...wallet,
        esgGoldAssetId: assetId
      };
      localStorage.setItem('algorand_wallet', JSON.stringify(updatedWallet));
      setWallet(updatedWallet);

      // 잔액 새로고침
      fetchBalance(wallet.address);
    } catch (error) {
      console.error('토큰 생성 실패:', error);
      alert('❌ 토큰 생성에 실패했습니다.\n\n' + error.message);
    } finally {
      setCreatingToken(false);
    }
  };

  return (
    <div className="wallet-page">
      <div className="wallet-container">
        <div className="wallet-header">
          <h1>🔐 알고랜드 지갑</h1>
          <p>블록체인 기반 디지털 쿠폰 지갑</p>
        </div>

        {!wallet ? (
          // 지갑이 없는 경우
          <div className="wallet-empty">
            <div className="empty-icon">💳</div>
            <h2>지갑이 없습니다</h2>
            <p>새로운 지갑을 생성하거나 기존 지갑을 복구하세요</p>

            <div className="wallet-actions">
              <button className="btn-create" onClick={createWallet}>
                🆕 새 지갑 생성
              </button>
              <button className="btn-recover" onClick={recoverWallet}>
                🔄 지갑 복구
              </button>
            </div>

            <div className="wallet-info">
              <h3>📘 알고랜드 지갑이란?</h3>
              <ul>
                <li>블록체인 기반 디지털 지갑</li>
                <li>ESG-GOLD 토큰(디지털 쿠폰) 보관</li>
                <li>25단어 니모닉으로 안전하게 복구 가능</li>
                <li>즉시 완결성 (4.5초 이내 거래 확정)</li>
              </ul>
            </div>
          </div>
        ) : (
          // 지갑이 있는 경우
          <div className="wallet-content">
            {/* 잔액 카드 */}
            <div className="balance-card">
              <div className="balance-label">총 잔액</div>
              <div className="balance-amount">
                {loading ? (
                  <div className="loading-spinner">조회 중...</div>
                ) : (
                  <>
                    <span className="amount">{balance !== null ? balance.toFixed(6) : '---'}</span>
                    <span className="currency">ALGO</span>
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
                        <div className="token-amount">
                          {asset.amount.toLocaleString()}
                        </div>
                        <div className="token-unit">{asset.unitName}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {wallet.esgGoldAssetId && (
                <div className="token-info-box">
                  <small>
                    💡 ESG-GOLD 자산 ID: {wallet.esgGoldAssetId}<br/>
                    다른 사용자에게 이 ID를 공유하면 토큰을 받을 수 있습니다
                  </small>
                </div>
              )}

              <div className="token-actions">
                <button
                  className="btn-token-action"
                  onClick={sendToken}
                  disabled={loading || assets.length === 0}
                >
                  💸 토큰 전송
                </button>
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
                {wallet.address}
              </div>
              <div className="address-qr">
                <p>💡 이 주소로 ALGO를 받을 수 있습니다</p>
              </div>
            </div>

            {/* 테스트 ALGO 받기 */}
            <div className="faucet-card">
              <h3>🚰 테스트 ALGO 받기</h3>
              <p>테스트넷에서 무료로 ALGO를 받아보세요</p>
              <a
                href="https://bank.testnet.algorand.network/"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-faucet"
              >
                TestNet Dispenser 열기 →
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

            {/* 니모닉 카드 */}
            <div className="mnemonic-card">
              <div className="card-header">
                <h3>🔑 복구 니모닉</h3>
                <button
                  className="btn-toggle"
                  onClick={() => setShowMnemonic(!showMnemonic)}
                >
                  {showMnemonic ? '👁️ 숨기기' : '👁️‍🗨️ 보기'}
                </button>
              </div>

              {showMnemonic && (
                <>
                  <div className="warning-box">
                    ⚠️ 절대 다른 사람과 공유하지 마세요!
                  </div>
                  <div className="mnemonic-box">
                    {wallet.mnemonic}
                  </div>
                  <button className="btn-copy-mnemonic" onClick={copyMnemonic}>
                    📋 니모닉 복사
                  </button>
                </>
              )}
            </div>

            {/* 지갑 정보 */}
            <div className="wallet-meta">
              <p>생성일: {new Date(wallet.createdAt).toLocaleString('ko-KR')}</p>
              <p>네트워크: Algorand TestNet</p>
              <p>상태: 🟢 활성</p>
            </div>

            {/* 위험 구역 */}
            <div className="danger-zone">
              <h3>⚠️ 위험 구역</h3>
              <button className="btn-delete" onClick={deleteWallet}>
                🗑️ 지갑 삭제
              </button>
              <p className="danger-warning">
                지갑을 삭제하면 니모닉 없이는 복구할 수 없습니다!
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default WalletPage;
