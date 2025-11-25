/**
 * Coupon System Management - Digital Coupon Bulk Issuance
 * 쿠폰 시스템 관리 - 디지털 쿠폰 대량 발행
 */

import React, { useState } from 'react';
import './CouponSystemPage.css';

function CouponSystemPage() {
  const [amount, setAmount] = useState('');
  const [unitName, setUnitName] = useState('');
  const [description, setDescription] = useState('');
  const [issuing, setIssuing] = useState(false);
  const [history, setHistory] = useState([]);

  // 빠른 선택 버튼 옵션
  const quickAmounts = [
    { label: '1천개', value: 1000 },
    { label: '1만개', value: 10000 },
    { label: '10만개', value: 100000 },
    { label: '100만개', value: 1000000 },
  ];

  // 빠른 선택
  const handleQuickSelect = (value) => {
    setAmount(value.toString());
  };

  // 쿠폰 발행
  const handleIssueCoupons = async () => {
    const parsedAmount = parseInt(amount);

    // 유효성 검사
    if (!parsedAmount || parsedAmount <= 0) {
      alert('유효한 발행 수량을 입력해주세요.');
      return;
    }

    if (!unitName || unitName.trim() === '') {
      alert('쿠폰 단위명(Unit Name)을 입력해주세요.');
      return;
    }

    if (!window.confirm(`${parsedAmount.toLocaleString()}개의 ${unitName} 쿠폰을 발행하시겠습니까?`)) {
      return;
    }

    setIssuing(true);

    try {
      // API 호출
      const response = await fetch('/api/token/mint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: parsedAmount,
          unit_name: unitName.trim().toUpperCase(),
          description: description.trim() || `${unitName} 쿠폰 발행`,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        alert(`✅ 성공!\n\n${parsedAmount.toLocaleString()}개의 ${unitName} 쿠폰이 발행되었습니다.`);

        // 히스토리에 추가
        const newRecord = {
          id: Date.now(),
          amount: parsedAmount,
          unitName: unitName.trim().toUpperCase(),
          description: description.trim() || `${unitName} 쿠폰 발행`,
          timestamp: new Date().toISOString(),
          status: 'success',
        };
        setHistory([newRecord, ...history]);

        // 폼 초기화
        setAmount('');
        setUnitName('');
        setDescription('');
      } else {
        throw new Error(data.message || '쿠폰 발행에 실패했습니다.');
      }
    } catch (error) {
      console.error('쿠폰 발행 오류:', error);
      alert(`❌ 발행 실패\n\n${error.message}`);
    } finally {
      setIssuing(false);
    }
  };

  return (
    <div className="coupon-system-page">
      <div className="coupon-header">
        <h1>🎟️ 디지털 쿠폰 대량 발행</h1>
        <p>쿠폰을 대량으로 생성하고 관리합니다</p>
      </div>

      <div className="coupon-content">
        {/* 쿠폰 발행 폼 */}
        <div className="issue-section">
          <h2>📝 쿠폰 발행</h2>

          <div className="form-group">
            <label>발행 수량</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="발행할 쿠폰 수량 입력"
              className="form-input"
              min="1"
              step="1"
            />
          </div>

          <div className="quick-select-section">
            <label>빠른 선택</label>
            <div className="quick-buttons">
              {quickAmounts.map((option) => (
                <button
                  key={option.value}
                  className={`quick-btn ${amount === option.value.toString() ? 'active' : ''}`}
                  onClick={() => handleQuickSelect(option.value)}
                >
                  {option.label}
                  <span className="quick-value">{option.value.toLocaleString()}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>쿠폰 단위명 (Unit Name)</label>
            <input
              type="text"
              value={unitName}
              onChange={(e) => setUnitName(e.target.value)}
              placeholder="예: HCF, PAM, ESGDC 등"
              className="form-input"
              maxLength="8"
            />
            <small className="form-hint">영문자 8자 이내, 자동으로 대문자로 변환됩니다</small>
          </div>

          <div className="form-group">
            <label>발행 설명 (선택사항)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="쿠폰 발행 사유나 설명을 입력하세요"
              className="form-input"
              rows="3"
            />
          </div>

          <button
            className="btn-issue"
            onClick={handleIssueCoupons}
            disabled={issuing || !amount || !unitName}
          >
            {issuing ? '발행 중...' : '🎟️ 쿠폰 발행하기'}
          </button>

          {amount && unitName && (
            <div className="preview-box">
              <h4>📋 발행 미리보기</h4>
              <div className="preview-item">
                <span className="preview-label">수량:</span>
                <span className="preview-value">{parseInt(amount || 0).toLocaleString()}개</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">단위명:</span>
                <span className="preview-value">{unitName.toUpperCase()}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">쿠폰 코드 예시:</span>
                <span className="preview-code">{unitName.toUpperCase()}-A1, {unitName.toUpperCase()}-A2, ...</span>
              </div>
            </div>
          )}
        </div>

        {/* 발행 히스토리 */}
        {history.length > 0 && (
          <div className="history-section">
            <h2>📜 발행 히스토리</h2>
            <div className="history-list">
              {history.map((record) => (
                <div key={record.id} className="history-card">
                  <div className="history-header">
                    <div className="history-badge">{record.unitName}</div>
                    <div className="history-amount">{record.amount.toLocaleString()}개</div>
                  </div>
                  <div className="history-body">
                    <div className="history-description">{record.description}</div>
                    <div className="history-time">
                      {new Date(record.timestamp).toLocaleString('ko-KR')}
                    </div>
                  </div>
                  <div className="history-status success">✅ 발행 완료</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {history.length === 0 && (
          <div className="empty-history">
            <div className="empty-icon">📭</div>
            <p>발행 히스토리가 없습니다.</p>
            <p className="empty-hint">위 양식을 통해 쿠폰을 발행하면 이곳에 기록됩니다.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default CouponSystemPage;
