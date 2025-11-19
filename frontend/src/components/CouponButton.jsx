import React, { useState } from 'react';
import './CouponButton.css';

/**
 * PAM 디지털 쿠폰 받기 버튼 컴포넌트
 *
 * Props:
 *   - userAddress: 사용자 알고랜드 주소
 *   - amount: 지급할 포인트 (100 = 1.00 포인트, decimals=2)
 *   - apiUrl: API 서버 URL (기본값: http://localhost:5000)
 *   - onSuccess: 성공 시 콜백
 *   - onError: 실패 시 콜백
 */
const CouponButton = ({
  userAddress,
  amount = 10000,
  apiUrl = 'http://localhost:5000',
  onSuccess,
  onError
}) => {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [txId, setTxId] = useState('');

  const checkOptIn = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/check-opt-in`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_address: userAddress })
      });

      const data = await response.json();
      return data.opted_in;
    } catch (error) {
      console.error('Opt-in check failed:', error);
      return false;
    }
  };

  const receiveCoupon = async () => {
    if (!userAddress) {
      setStatus('❌ 알고랜드 주소를 입력해주세요');
      return;
    }

    setLoading(true);
    setStatus('확인 중...');
    setTxId('');

    try {
      // 1. Opt-in 확인
      const optedIn = await checkOptIn();

      if (!optedIn) {
        setStatus('❌ Asset Opt-in이 필요합니다');
        setLoading(false);

        if (onError) {
          onError({
            type: 'NOT_OPTED_IN',
            message: 'Asset Opt-in이 필요합니다',
            assetId: 3330375002
          });
        }
        return;
      }

      // 2. 쿠폰 지급 요청
      setStatus('쿠폰 발송 중...');

      const response = await fetch(`${apiUrl}/api/give-coupon`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_address: userAddress,
          amount: amount
        })
      });

      const data = await response.json();

      if (data.success) {
        setStatus(`✅ 쿠폰 ${data.amount_display} PAMP 받기 완료!`);
        setTxId(data.txid);

        if (onSuccess) {
          onSuccess(data);
        }
      } else {
        setStatus(`❌ 실패: ${data.error}`);

        if (onError) {
          onError(data);
        }
      }
    } catch (error) {
      setStatus(`❌ 오류: ${error.message}`);

      if (onError) {
        onError({ type: 'NETWORK_ERROR', message: error.message });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="coupon-button-container">
      <button
        onClick={receiveCoupon}
        disabled={loading || !userAddress}
        className="coupon-button"
      >
        {loading ? '처리 중...' : `🎁 쿠폰 ${amount / 100} 포인트 받기`}
      </button>

      {status && (
        <div className={`status-message ${status.startsWith('✅') ? 'success' : 'error'}`}>
          {status}
        </div>
      )}

      {txId && (
        <div className="tx-link">
          <a
            href={`https://algoexplorer.io/tx/${txId}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            거래 확인하기 →
          </a>
        </div>
      )}
    </div>
  );
};

export default CouponButton;
