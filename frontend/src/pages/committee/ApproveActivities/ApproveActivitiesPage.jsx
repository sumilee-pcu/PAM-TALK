/**
 * ESG Activity Approval & DC Distribution Page (Committee)
 * 위원회용 ESG 활동 승인 및 DC 지급 페이지
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../hooks/useAuth';
import algosdk from 'algosdk';
import '../CouponIssuance/CouponIssuancePage.css';

function ApproveActivitiesPage() {
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [selectedApp, setSelectedApp] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showDCModal, setShowDCModal] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [dcAmount, setDcAmount] = useState('');
  const [dcRecipient, setDcRecipient] = useState('');

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = () => {
    const saved = localStorage.getItem('esg_applications');
    if (saved) {
      setApplications(JSON.parse(saved));
    }
  };

  const handleViewDetails = (app) => {
    setSelectedApp(app);
    setShowModal(true);
  };

  const handleApprove = async (appId) => {
    if (!window.confirm('✅ 이 활동을 승인하시겠습니까?')) return;

    const updated = applications.map(app =>
      app.id === appId
        ? {
            ...app,
            status: 'APPROVED',
            approvedBy: user?.name || '위원회',
            approvedAt: new Date().toISOString()
          }
        : app
    );

    setApplications(updated);
    localStorage.setItem('esg_applications', JSON.stringify(updated));

    if (selectedApp && selectedApp.id === appId) {
      setSelectedApp({ ...selectedApp, status: 'APPROVED' });
    }

    alert('✅ ESG 활동이 승인되었습니다!');
  };

  const handleReject = (appId) => {
    const reason = prompt('❌ 거절 사유를 입력하세요:');
    if (!reason) return;

    const updated = applications.map(app =>
      app.id === appId
        ? {
            ...app,
            status: 'REJECTED',
            rejectedBy: user?.name || '위원회',
            rejectedAt: new Date().toISOString(),
            rejectionReason: reason
          }
        : app
    );

    setApplications(updated);
    localStorage.setItem('esg_applications', JSON.stringify(updated));

    if (selectedApp && selectedApp.id === appId) {
      setSelectedApp({ ...selectedApp, status: 'REJECTED' });
    }

    alert('❌ ESG 활동이 거절되었습니다.');
    setShowModal(false);
  };

  const handleDistributeDC = (app) => {
    setSelectedApp(app);
    setDcAmount(app.reward.toString());
    setDcRecipient('');
    setShowDCModal(true);
  };

  const handleSendDC = async () => {
    if (!dcRecipient || dcRecipient.length !== 58) {
      alert('❌ 올바른 수신자 주소를 입력하세요 (58자).');
      return;
    }

    if (!dcAmount || parseFloat(dcAmount) <= 0) {
      alert('❌ 올바른 DC 수량을 입력하세요.');
      return;
    }

    if (!window.confirm(`💸 DC를 전송하시겠습니까?\n\n수신자: ${dcRecipient.substring(0, 10)}...${dcRecipient.substring(48)}\n수량: ${dcAmount} DC`)) {
      return;
    }

    setProcessing(true);

    try {
      // 위원회 지갑 가져오기
      const committeeWallet = localStorage.getItem('algorand_wallet');
      if (!committeeWallet) {
        alert('❌ 위원회 지갑이 필요합니다.');
        setProcessing(false);
        return;
      }

      const wallet = JSON.parse(committeeWallet);
      const algodClient = new algosdk.Algodv2('', 'https://testnet-api.algonode.cloud', '');
      const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);
      const params = await algodClient.getTransactionParams().do();

      // DC 전송 트랜잭션 (Algo 전송)
      const txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
        from: account.addr,
        to: dcRecipient,
        amount: Math.round(parseFloat(dcAmount) * 1000000), // Algo to microAlgos
        note: new Uint8Array(Buffer.from(`ESG Reward: ${selectedApp?.activityName}`, 'utf-8')),
        suggestedParams: params
      });

      const signedTxn = txn.signTxn(account.sk);
      const { txId } = await algodClient.sendRawTransaction(signedTxn).do();

      alert('⏳ DC 전송 중...\n\n트랜잭션 ID: ' + txId);

      await algosdk.waitForConfirmation(algodClient, txId, 4);

      // 활동 완료 처리
      const updated = applications.map(app =>
        app.id === selectedApp.id
          ? {
              ...app,
              status: 'COMPLETED',
              dcSent: true,
              dcTxId: txId,
              dcAmount: parseFloat(dcAmount),
              completedBy: user?.name || '위원회',
              completedAt: new Date().toISOString()
            }
          : app
      );

      setApplications(updated);
      localStorage.setItem('esg_applications', JSON.stringify(updated));

      alert(`✅ DC가 성공적으로 전송되었습니다!\n\n${dcAmount} DC가 전송되었습니다.\n\n트랜잭션 ID:\n${txId}`);
      setShowDCModal(false);
      setShowModal(false);

    } catch (error) {
      console.error('DC 전송 실패:', error);
      alert('❌ DC 전송에 실패했습니다.\n\n' + error.message);
    } finally {
      setProcessing(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      'PENDING': { class: 'coupon-badge recycling', label: '대기중' },
      'APPROVED': { class: 'coupon-badge transport', label: '승인됨' },
      'REJECTED': { class: 'coupon-badge energy', label: '거절됨' },
      'COMPLETED': { class: 'coupon-badge tree', label: '완료' }
    };
    return badges[status] || badges['PENDING'];
  };

  const stats = {
    total: applications.length,
    pending: applications.filter(a => a.status === 'PENDING').length,
    approved: applications.filter(a => a.status === 'APPROVED').length,
    completed: applications.filter(a => a.status === 'COMPLETED').length
  };

  return (
    <div className="coupon-page">
      <div className="page-header">
        <h1>✅ ESG 활동 승인 및 DC 지급</h1>
        <p>사용자의 ESG 활동 신청을 검토하고 DC를 지급하세요</p>
      </div>

      {/* 통계 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-label">전체 신청</div>
            <div className="stat-value">{stats.total}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <div className="stat-label">승인 대기</div>
            <div className="stat-value">{stats.pending}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">승인됨</div>
            <div className="stat-value">{stats.approved}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🎁</div>
          <div className="stat-content">
            <div className="stat-label">완료</div>
            <div className="stat-value">{stats.completed}</div>
          </div>
        </div>
      </div>

      {/* 신청 목록 */}
      <div className="history-section">
        <h2>ESG 활동 신청 목록</h2>
        <div className="history-table">
          <table>
            <thead>
              <tr>
                <th>신청자</th>
                <th>활동</th>
                <th>예정일</th>
                <th>장소</th>
                <th>보상</th>
                <th>상태</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {applications.map(app => {
                const badge = getStatusBadge(app.status);
                return (
                  <tr key={app.id}>
                    <td>{app.userName}</td>
                    <td>
                      <span style={{fontSize: '1.2rem', marginRight: '0.5rem'}}>
                        {app.activityIcon}
                      </span>
                      {app.activityName}
                    </td>
                    <td>{app.plannedDate}</td>
                    <td>{app.location}</td>
                    <td style={{fontWeight: 700, color: '#667eea'}}>{app.reward} P</td>
                    <td>
                      <span className={badge.class}>{badge.label}</span>
                    </td>
                    <td>
                      <button
                        className="btn-quick"
                        onClick={() => handleViewDetails(app)}
                      >
                        상세
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {applications.length === 0 && (
            <div style={{padding: '3rem', textAlign: 'center', color: '#666'}}>
              신청된 ESG 활동이 없습니다
            </div>
          )}
        </div>
      </div>

      {/* 상세 모달 */}
      {showModal && selectedApp && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{maxWidth: '600px'}}>
            <div className="modal-header">
              <h2>ESG 활동 신청 상세</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                <div>
                  <label style={{fontSize: '0.9rem', color: '#666'}}>신청자</label>
                  <div style={{fontWeight: 600, marginTop: '0.25rem'}}>{selectedApp.userName}</div>
                </div>
                <div>
                  <label style={{fontSize: '0.9rem', color: '#666'}}>신청일</label>
                  <div style={{fontWeight: 600, marginTop: '0.25rem'}}>
                    {new Date(selectedApp.appliedAt).toLocaleDateString('ko-KR')}
                  </div>
                </div>
                <div style={{gridColumn: '1 / -1'}}>
                  <label style={{fontSize: '0.9rem', color: '#666'}}>활동</label>
                  <div style={{fontSize: '1.2rem', fontWeight: 700, marginTop: '0.25rem'}}>
                    {selectedApp.activityIcon} {selectedApp.activityName}
                  </div>
                </div>
                <div>
                  <label style={{fontSize: '0.9rem', color: '#666'}}>예정일</label>
                  <div style={{fontWeight: 600, marginTop: '0.25rem'}}>{selectedApp.plannedDate}</div>
                </div>
                <div>
                  <label style={{fontSize: '0.9rem', color: '#666'}}>수량</label>
                  <div style={{fontWeight: 600, marginTop: '0.25rem'}}>{selectedApp.quantity}회</div>
                </div>
                <div style={{gridColumn: '1 / -1'}}>
                  <label style={{fontSize: '0.9rem', color: '#666'}}>활동 장소</label>
                  <div style={{fontWeight: 600, marginTop: '0.25rem'}}>{selectedApp.location}</div>
                </div>
                {selectedApp.notes && (
                  <div style={{gridColumn: '1 / -1'}}>
                    <label style={{fontSize: '0.9rem', color: '#666'}}>특이사항</label>
                    <div style={{marginTop: '0.25rem', padding: '0.75rem', background: '#f8f9fa', borderRadius: '8px'}}>
                      {selectedApp.notes}
                    </div>
                  </div>
                )}
                <div>
                  <label style={{fontSize: '0.9rem', color: '#666'}}>예상 보상</label>
                  <div style={{fontSize: '1.5rem', fontWeight: 700, color: '#667eea', marginTop: '0.25rem'}}>
                    {selectedApp.reward} P
                  </div>
                </div>
                <div>
                  <label style={{fontSize: '0.9rem', color: '#666'}}>상태</label>
                  <div style={{marginTop: '0.25rem'}}>
                    <span className={getStatusBadge(selectedApp.status).class}>
                      {getStatusBadge(selectedApp.status).label}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              {selectedApp.status === 'PENDING' && (
                <>
                  <button className="btn-issue" onClick={() => handleApprove(selectedApp.id)}>
                    ✅ 승인
                  </button>
                  <button className="btn-cancel" onClick={() => handleReject(selectedApp.id)}>
                    ❌ 거절
                  </button>
                </>
              )}
              {selectedApp.status === 'APPROVED' && (
                <button className="btn-issue" onClick={() => handleDistributeDC(selectedApp)}>
                  💸 DC 지급
                </button>
              )}
              <button className="btn-cancel" onClick={() => setShowModal(false)}>
                닫기
              </button>
            </div>
          </div>
        </div>
      )}

      {/* DC 전송 모달 */}
      {showDCModal && selectedApp && (
        <div className="modal-overlay" onClick={() => setShowDCModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{maxWidth: '500px'}}>
            <div className="modal-header">
              <h2>💸 DC 지급</h2>
              <button className="btn-close" onClick={() => setShowDCModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <div style={{marginBottom: '1rem', padding: '1rem', background: '#f8f9fa', borderRadius: '8px'}}>
                <div style={{fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem'}}>활동</div>
                <div style={{fontSize: '1.1rem', fontWeight: 700}}>
                  {selectedApp.activityIcon} {selectedApp.activityName}
                </div>
                <div style={{fontSize: '0.9rem', color: '#666', marginTop: '0.5rem'}}>
                  신청자: {selectedApp.userName}
                </div>
              </div>

              <div className="form-group">
                <label>수신자 지갑 주소 *</label>
                <input
                  type="text"
                  value={dcRecipient}
                  onChange={(e) => setDcRecipient(e.target.value)}
                  placeholder="58자 Algorand 주소 입력"
                  maxLength={58}
                />
                <small style={{color: '#666'}}>사용자의 지갑 주소를 입력하세요</small>
              </div>

              <div className="form-group">
                <label>전송 수량 (DC) *</label>
                <input
                  type="number"
                  value={dcAmount}
                  onChange={(e) => setDcAmount(e.target.value)}
                  min="0.001"
                  step="0.001"
                />
                <small style={{color: '#666'}}>권장: {selectedApp.reward} DC</small>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn-issue"
                onClick={handleSendDC}
                disabled={processing}
              >
                {processing ? '⏳ 전송 중...' : '💸 DC 전송'}
              </button>
              <button className="btn-cancel" onClick={() => setShowDCModal(false)}>
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ApproveActivitiesPage;
