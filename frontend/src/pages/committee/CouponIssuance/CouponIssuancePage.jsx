/**
 * Committee Coupon Issuance Page
 * 위원회 디지털 쿠폰 발행 페이지
 * - ESG 활동 인증 쿠폰 발행
 * - 프로젝트별 쿠폰 관리
 */

import React, { useState, useEffect } from 'react';
import './CouponIssuancePage.css';

function CouponIssuancePage() {
  const [couponType, setCouponType] = useState('');
  const [amount, setAmount] = useState('');
  const [projectName, setProjectName] = useState('');
  const [targetGroup, setTargetGroup] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [description, setDescription] = useState('');
  const [issuing, setIssuing] = useState(false);
  const [history, setHistory] = useState([]);

  // 쿠폰 타입 옵션
  const couponTypes = [
    { id: 'recycling', name: '재활용 인증 쿠폰', icon: '♻️', unitName: 'RCYC' },
    { id: 'transport', name: '친환경 교통 쿠폰', icon: '🚲', unitName: 'TRNC' },
    { id: 'tree', name: '나무심기 쿠폰', icon: '🌳', unitName: 'TREE' },
    { id: 'energy', name: '에너지 절약 쿠폰', icon: '💡', unitName: 'ENGY' },
    { id: 'water', name: '물 절약 쿠폰', icon: '💧', unitName: 'WATR' },
    { id: 'general', name: 'ESG 범용 쿠폰', icon: '🎟️', unitName: 'ESGC' },
  ];

  // 빠른 수량 선택
  const quickAmounts = [
    { label: '100개', value: 100 },
    { label: '500개', value: 500 },
    { label: '1,000개', value: 1000 },
    { label: '5,000개', value: 5000 },
  ];

  // localStorage에서 히스토리 로드
  useEffect(() => {
    const savedHistory = localStorage.getItem('committee_coupon_history');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  // 쿠폰 타입 선택
  const handleCouponTypeSelect = (type) => {
    setCouponType(type.id);
  };

  // 빠른 수량 선택
  const handleQuickAmount = (value) => {
    setAmount(value.toString());
  };

  // 쿠폰 발행
  const handleIssueCoupons = async () => {
    // 유효성 검사
    if (!couponType) {
      alert('쿠폰 타입을 선택해주세요.');
      return;
    }

    const parsedAmount = parseInt(amount);
    if (!parsedAmount || parsedAmount <= 0) {
      alert('유효한 발행 수량을 입력해주세요.');
      return;
    }

    if (!projectName || projectName.trim() === '') {
      alert('프로젝트명을 입력해주세요.');
      return;
    }

    if (!targetGroup || targetGroup.trim() === '') {
      alert('대상 그룹을 입력해주세요.');
      return;
    }

    const selectedType = couponTypes.find(t => t.id === couponType);

    if (!window.confirm(
      `${selectedType.name} ${parsedAmount.toLocaleString()}개를 발행하시겠습니까?\n\n` +
      `프로젝트: ${projectName}\n` +
      `대상: ${targetGroup}`
    )) {
      return;
    }

    setIssuing(true);

    try {
      // API 호출 (실제로는 백엔드 API를 호출해야 함)
      const response = await fetch('/api/committee/coupon/issue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('pam_token')}`,
        },
        body: JSON.stringify({
          coupon_type: couponType,
          unit_name: selectedType.unitName,
          amount: parsedAmount,
          project_name: projectName.trim(),
          target_group: targetGroup.trim(),
          expiry_date: expiryDate || null,
          description: description.trim() || `${selectedType.name} 발행`,
          issued_by: 'committee',
        }),
      });

      let data;
      try {
        data = await response.json();
      } catch (e) {
        // JSON 파싱 실패 시 (개발 환경에서 API가 없을 수 있음)
        data = { success: false, message: 'API 연결 실패 (개발 모드)' };
      }

      if (response.ok && data.success) {
        // 성공
        const newRecord = {
          id: Date.now(),
          couponType: selectedType.name,
          icon: selectedType.icon,
          unitName: selectedType.unitName,
          amount: parsedAmount,
          projectName: projectName.trim(),
          targetGroup: targetGroup.trim(),
          expiryDate: expiryDate || '무기한',
          description: description.trim() || `${selectedType.name} 발행`,
          timestamp: new Date().toISOString(),
          status: 'issued',
          txId: data.txId || null,
        };

        const updatedHistory = [newRecord, ...history];
        setHistory(updatedHistory);
        localStorage.setItem('committee_coupon_history', JSON.stringify(updatedHistory));

        alert(
          `✅ 쿠폰 발행 완료!\n\n` +
          `종류: ${selectedType.name}\n` +
          `수량: ${parsedAmount.toLocaleString()}개\n` +
          `프로젝트: ${projectName}\n` +
          `대상: ${targetGroup}`
        );

        // 폼 초기화
        setCouponType('');
        setAmount('');
        setProjectName('');
        setTargetGroup('');
        setExpiryDate('');
        setDescription('');

      } else {
        // 개발 모드: API가 없어도 임시로 발행 기록 저장
        if (!response.ok) {
          console.warn('API 미구현 - 개발 모드에서 임시 발행');

          const newRecord = {
            id: Date.now(),
            couponType: selectedType.name,
            icon: selectedType.icon,
            unitName: selectedType.unitName,
            amount: parsedAmount,
            projectName: projectName.trim(),
            targetGroup: targetGroup.trim(),
            expiryDate: expiryDate || '무기한',
            description: description.trim() || `${selectedType.name} 발행`,
            timestamp: new Date().toISOString(),
            status: 'pending',
            txId: null,
          };

          const updatedHistory = [newRecord, ...history];
          setHistory(updatedHistory);
          localStorage.setItem('committee_coupon_history', JSON.stringify(updatedHistory));

          alert(
            `⚠️ 개발 모드 - 임시 발행\n\n` +
            `종류: ${selectedType.name}\n` +
            `수량: ${parsedAmount.toLocaleString()}개\n` +
            `프로젝트: ${projectName}\n\n` +
            `실제 배포 시 블록체인에 기록됩니다.`
          );

          // 폼 초기화
          setCouponType('');
          setAmount('');
          setProjectName('');
          setTargetGroup('');
          setExpiryDate('');
          setDescription('');
        } else {
          throw new Error(data.message || '쿠폰 발행에 실패했습니다.');
        }
      }
    } catch (error) {
      console.error('쿠폰 발행 오류:', error);
      alert(`❌ 발행 실패\n\n${error.message}`);
    } finally {
      setIssuing(false);
    }
  };

  const selectedCouponType = couponTypes.find(t => t.id === couponType);

  return (
    <div className="coupon-issuance-page">
      <div className="page-header">
        <h1>🎟️ 위원회 디지털 쿠폰 발행</h1>
        <p>ESG 활동 인증 및 프로젝트별 쿠폰을 발행합니다</p>
      </div>

      <div className="page-content">
        {/* 쿠폰 타입 선택 */}
        <section className="section">
          <h2>1️⃣ 쿠폰 종류 선택</h2>
          <div className="coupon-type-grid">
            {couponTypes.map((type) => (
              <button
                key={type.id}
                className={`type-card ${couponType === type.id ? 'selected' : ''}`}
                onClick={() => handleCouponTypeSelect(type)}
              >
                <div className="type-icon">{type.icon}</div>
                <div className="type-name">{type.name}</div>
                <div className="type-unit">{type.unitName}</div>
              </button>
            ))}
          </div>
        </section>

        {/* 발행 정보 입력 */}
        {couponType && (
          <section className="section">
            <h2>2️⃣ 발행 정보 입력</h2>

            <div className="form-grid">
              <div className="form-group">
                <label>발행 수량 *</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="발행할 쿠폰 수량"
                  className="form-input"
                  min="1"
                  step="1"
                />
                <div className="quick-select">
                  {quickAmounts.map((option) => (
                    <button
                      key={option.value}
                      className={`quick-btn ${amount === option.value.toString() ? 'active' : ''}`}
                      onClick={() => handleQuickAmount(option.value)}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>프로젝트명 *</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="예: 2025 봄 재활용 캠페인"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>대상 그룹 *</label>
                <input
                  type="text"
                  value={targetGroup}
                  onChange={(e) => setTargetGroup(e.target.value)}
                  placeholder="예: 서울시 거주 시민, 전국 대학생 등"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>유효기간 (선택)</label>
                <input
                  type="date"
                  value={expiryDate}
                  onChange={(e) => setExpiryDate(e.target.value)}
                  className="form-input"
                  min={new Date().toISOString().split('T')[0]}
                />
                <small className="form-hint">미입력 시 무기한</small>
              </div>

              <div className="form-group full-width">
                <label>발행 목적 및 설명 (선택)</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="쿠폰 발행 목적이나 사용 방법을 입력하세요"
                  className="form-textarea"
                  rows="3"
                />
              </div>
            </div>
          </section>
        )}

        {/* 발행 미리보기 */}
        {couponType && amount && projectName && targetGroup && selectedCouponType && (
          <section className="section preview-section">
            <h2>3️⃣ 발행 미리보기</h2>
            <div className="preview-card">
              <div className="preview-header">
                <span className="preview-icon">{selectedCouponType.icon}</span>
                <span className="preview-title">{selectedCouponType.name}</span>
              </div>
              <div className="preview-body">
                <div className="preview-row">
                  <span className="preview-label">발행 수량:</span>
                  <span className="preview-value">{parseInt(amount).toLocaleString()}개</span>
                </div>
                <div className="preview-row">
                  <span className="preview-label">쿠폰 코드:</span>
                  <span className="preview-value">{selectedCouponType.unitName}-001, {selectedCouponType.unitName}-002, ...</span>
                </div>
                <div className="preview-row">
                  <span className="preview-label">프로젝트:</span>
                  <span className="preview-value">{projectName}</span>
                </div>
                <div className="preview-row">
                  <span className="preview-label">대상 그룹:</span>
                  <span className="preview-value">{targetGroup}</span>
                </div>
                <div className="preview-row">
                  <span className="preview-label">유효기간:</span>
                  <span className="preview-value">{expiryDate || '무기한'}</span>
                </div>
              </div>
            </div>

            <button
              className="btn-issue-primary"
              onClick={handleIssueCoupons}
              disabled={issuing}
            >
              {issuing ? '🔄 발행 처리 중...' : '✅ 쿠폰 발행하기'}
            </button>
          </section>
        )}

        {/* 발행 히스토리 */}
        <section className="section history-section">
          <h2>📜 발행 히스토리</h2>
          {history.length > 0 ? (
            <div className="history-list">
              {history.map((record) => (
                <div key={record.id} className="history-item">
                  <div className="history-icon">{record.icon}</div>
                  <div className="history-content">
                    <div className="history-title">
                      {record.couponType} ({record.unitName})
                    </div>
                    <div className="history-details">
                      <span>수량: {record.amount.toLocaleString()}개</span>
                      <span>프로젝트: {record.projectName}</span>
                      <span>대상: {record.targetGroup}</span>
                    </div>
                    <div className="history-meta">
                      <span>{new Date(record.timestamp).toLocaleString('ko-KR')}</span>
                      {record.status === 'issued' && <span className="status-badge success">✅ 발행완료</span>}
                      {record.status === 'pending' && <span className="status-badge pending">⏳ 대기중</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📭</div>
              <p>발행 히스토리가 없습니다.</p>
              <p className="empty-hint">쿠폰을 발행하면 이곳에 기록됩니다.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default CouponIssuancePage;
