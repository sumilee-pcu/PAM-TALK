/**
 * Bulk DC Distribution Page (Admin)
 * 관리자용 대량 DC 전송 페이지
 */

import React, { useState, useEffect } from 'react';
import algosdk from 'algosdk';
import '../Users/UsersPage.css';

function BulkDCPage() {
  const [users, setUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [dcAmount, setDcAmount] = useState('');
  const [memo, setMemo] = useState('');
  const [processing, setProcessing] = useState(false);
  const [sendHistory, setSendHistory] = useState([]);
  const [mode, setMode] = useState('select'); // 'select' or 'manual'
  const [manualAddresses, setManualAddresses] = useState('');

  useEffect(() => {
    loadUsers();
    loadHistory();
  }, []);

  const loadUsers = () => {
    // 실제로는 백엔드에서 가져와야 하지만, 데모용으로 localStorage 사용
    const demoUsers = [
      { id: 1, name: '김소비', email: 'consumer@pamtalk.com', wallet: '' },
      { id: 2, name: '이농부', email: 'farmer@pamtalk.com', wallet: '' },
      { id: 3, name: '박위원', email: 'committee@pamtalk.com', wallet: '' },
      { id: 4, name: '최관리', email: 'admin@pamtalk.com', wallet: '' },
      { id: 5, name: '정사용자', email: 'user1@example.com', wallet: '' },
      { id: 6, name: '강테스트', email: 'user2@example.com', wallet: '' }
    ];
    setUsers(demoUsers);
  };

  const loadHistory = () => {
    const saved = localStorage.getItem('bulk_dc_history');
    if (saved) {
      setSendHistory(JSON.parse(saved));
    }
  };

  const handleUserToggle = (userId) => {
    if (selectedUsers.includes(userId)) {
      setSelectedUsers(selectedUsers.filter(id => id !== userId));
    } else {
      setSelectedUsers([...selectedUsers, userId]);
    }
  };

  const handleSelectAll = () => {
    if (selectedUsers.length === users.length) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(users.map(u => u.id));
    }
  };

  const handleBulkSend = async () => {
    let recipients = [];

    if (mode === 'select') {
      if (selectedUsers.length === 0) {
        alert('❌ 수신자를 선택하세요.');
        return;
      }
      // 선택된 사용자의 지갑 주소 (실제로는 DB에서 가져와야 함)
      recipients = selectedUsers.map(id => {
        const user = users.find(u => u.id === id);
        return {
          name: user.name,
          address: user.wallet || prompt(`${user.name}님의 지갑 주소를 입력하세요 (58자):`)
        };
      }).filter(r => r.address && r.address.length === 58);

      if (recipients.length === 0) {
        alert('❌ 유효한 지갑 주소가 없습니다.');
        return;
      }
    } else {
      // 수동 입력 모드
      const addresses = manualAddresses.split('\n').filter(a => a.trim().length === 58);
      if (addresses.length === 0) {
        alert('❌ 유효한 지갑 주소를 입력하세요 (한 줄에 하나씩).');
        return;
      }
      recipients = addresses.map((addr, idx) => ({
        name: `수신자 ${idx + 1}`,
        address: addr.trim()
      }));
    }

    if (!dcAmount || parseFloat(dcAmount) <= 0) {
      alert('❌ 전송할 DC 수량을 입력하세요.');
      return;
    }

    const totalAmount = parseFloat(dcAmount) * recipients.length;
    if (!window.confirm(`💸 총 ${recipients.length}명에게 각 ${dcAmount} DC를 전송하시겠습니까?\n\n총 전송량: ${totalAmount} DC`)) {
      return;
    }

    setProcessing(true);

    try {
      // 관리자 지갑 가져오기
      const adminWallet = localStorage.getItem('algorand_wallet');
      if (!adminWallet) {
        alert('❌ 관리자 지갑이 필요합니다.');
        setProcessing(false);
        return;
      }

      const wallet = JSON.parse(adminWallet);
      const algodClient = new algosdk.Algodv2('', 'https://testnet-api.algonode.cloud', '');
      const account = algosdk.mnemonicToSecretKey(wallet.mnemonic);

      // 잔액 확인
      const accountInfo = await algodClient.accountInformation(account.addr).do();
      const balance = accountInfo.amount / 1000000;

      if (balance < totalAmount) {
        alert(`❌ 잔액이 부족합니다.\n\n필요: ${totalAmount} DC\n보유: ${balance.toFixed(6)} DC`);
        setProcessing(false);
        return;
      }

      const results = [];
      const params = await algodClient.getTransactionParams().do();

      // 각 수신자에게 전송
      for (let i = 0; i < recipients.length; i++) {
        const recipient = recipients[i];

        try {
          const noteText = memo || 'Bulk DC Distribution';
          const note = new Uint8Array(Buffer.from(noteText, 'utf-8'));

          const txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
            from: account.addr,
            to: recipient.address,
            amount: Math.round(parseFloat(dcAmount) * 1000000),
            note: note,
            suggestedParams: params
          });

          const signedTxn = txn.signTxn(account.sk);
          const { txId } = await algodClient.sendRawTransaction(signedTxn).do();

          await algosdk.waitForConfirmation(algodClient, txId, 4);

          results.push({
            name: recipient.name,
            address: recipient.address,
            amount: parseFloat(dcAmount),
            status: 'SUCCESS',
            txId: txId
          });

          console.log(`✅ ${recipient.name}: ${txId}`);

        } catch (error) {
          console.error(`❌ ${recipient.name} 전송 실패:`, error);
          results.push({
            name: recipient.name,
            address: recipient.address,
            amount: parseFloat(dcAmount),
            status: 'FAILED',
            error: error.message
          });
        }

        // 진행률 표시 (선택사항)
        if (i < recipients.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 500)); // 0.5초 대기
        }
      }

      // 전송 내역 저장
      const newRecord = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        recipientCount: recipients.length,
        amountPerRecipient: parseFloat(dcAmount),
        totalAmount: totalAmount,
        memo: memo,
        results: results,
        successCount: results.filter(r => r.status === 'SUCCESS').length,
        failCount: results.filter(r => r.status === 'FAILED').length
      };

      const updatedHistory = [newRecord, ...sendHistory];
      setSendHistory(updatedHistory);
      localStorage.setItem('bulk_dc_history', JSON.stringify(updatedHistory));

      // 결과 표시
      const successCount = results.filter(r => r.status === 'SUCCESS').length;
      const failCount = results.filter(r => r.status === 'FAILED').length;

      alert(`✅ DC 전송이 완료되었습니다!\n\n성공: ${successCount}명\n실패: ${failCount}명\n\n상세 내역은 전송 내역에서 확인하세요.`);

      // 폼 초기화
      setSelectedUsers([]);
      setDcAmount('');
      setMemo('');
      setManualAddresses('');

    } catch (error) {
      console.error('대량 전송 실패:', error);
      alert('❌ DC 전송에 실패했습니다.\n\n' + error.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>💸 대량 DC 전송</h1>
        <p>여러 사용자에게 한번에 DC를 전송하세요</p>
      </div>

      {/* 모드 선택 */}
      <div className="controls-section" style={{marginBottom: '2rem'}}>
        <div className="filters">
          <button
            className={mode === 'select' ? 'btn-activate' : 'btn-cancel'}
            onClick={() => setMode('select')}
          >
            👥 사용자 선택
          </button>
          <button
            className={mode === 'manual' ? 'btn-activate' : 'btn-cancel'}
            onClick={() => setMode('manual')}
            style={{marginLeft: '1rem'}}
          >
            ✍️ 주소 직접 입력
          </button>
        </div>
      </div>

      {/* 사용자 선택 모드 */}
      {mode === 'select' && (
        <div className="users-table-container" style={{marginBottom: '2rem'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
            <h2>수신자 선택</h2>
            <button className="btn-view" onClick={handleSelectAll}>
              {selectedUsers.length === users.length ? '전체 해제' : '전체 선택'}
            </button>
          </div>
          <table className="users-table">
            <thead>
              <tr>
                <th style={{width: '50px'}}>
                  <input
                    type="checkbox"
                    checked={selectedUsers.length === users.length}
                    onChange={handleSelectAll}
                  />
                </th>
                <th>ID</th>
                <th>이름</th>
                <th>이메일</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(user.id)}
                      onChange={() => handleUserToggle(user.id)}
                    />
                  </td>
                  <td>{user.id}</td>
                  <td className="user-name">{user.name}</td>
                  <td>{user.email}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{marginTop: '1rem', color: '#667eea', fontWeight: 600}}>
            선택된 사용자: {selectedUsers.length}명
          </div>
        </div>
      )}

      {/* 수동 입력 모드 */}
      {mode === 'manual' && (
        <div className="users-table-container" style={{marginBottom: '2rem'}}>
          <h2 style={{marginBottom: '1rem'}}>수신자 주소 입력</h2>
          <textarea
            value={manualAddresses}
            onChange={(e) => setManualAddresses(e.target.value)}
            placeholder="지갑 주소를 한 줄에 하나씩 입력하세요&#10;예:&#10;ADDR1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890ABCDEF&#10;ADDR2234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890ABCDEF"
            rows="10"
            style={{
              width: '100%',
              padding: '1rem',
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              border: '1px solid #ddd',
              borderRadius: '8px'
            }}
          />
          <div style={{marginTop: '1rem', color: '#667eea', fontWeight: 600}}>
            입력된 주소: {manualAddresses.split('\n').filter(a => a.trim().length === 58).length}개
          </div>
        </div>
      )}

      {/* 전송 설정 */}
      <div className="users-table-container" style={{marginBottom: '2rem'}}>
        <h2 style={{marginBottom: '1rem'}}>전송 설정</h2>
        <div className="user-detail-grid">
          <div className="detail-item">
            <label>1인당 전송 수량 (DC) *</label>
            <input
              type="number"
              value={dcAmount}
              onChange={(e) => setDcAmount(e.target.value)}
              min="0.001"
              step="0.001"
              placeholder="예: 10"
              style={{width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd'}}
            />
          </div>
          <div className="detail-item">
            <label>총 전송량 (DC)</label>
            <div className="points-large">
              {(parseFloat(dcAmount) || 0) * (mode === 'select' ? selectedUsers.length : manualAddresses.split('\n').filter(a => a.trim().length === 58).length)} DC
            </div>
          </div>
          <div className="detail-item" style={{gridColumn: '1 / -1'}}>
            <label>메모 (선택사항)</label>
            <input
              type="text"
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              placeholder="예: ESG 활동 보상"
              maxLength={100}
              style={{width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd'}}
            />
          </div>
        </div>
        <button
          className="btn-activate"
          onClick={handleBulkSend}
          disabled={processing}
          style={{marginTop: '1.5rem', width: '100%', fontSize: '1.1rem', padding: '1rem'}}
        >
          {processing ? '⏳ 전송 중...' : '💸 DC 전송 시작'}
        </button>
      </div>

      {/* 전송 내역 */}
      {sendHistory.length > 0 && (
        <div className="users-table-container">
          <h2 style={{marginBottom: '1rem'}}>전송 내역</h2>
          {sendHistory.map((record, index) => (
            <div key={record.id} style={{marginBottom: '1.5rem', padding: '1.5rem', background: '#f8f9fa', borderRadius: '12px'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '1rem'}}>
                <div>
                  <div style={{fontWeight: 700, fontSize: '1.1rem'}}>
                    {new Date(record.timestamp).toLocaleString('ko-KR')}
                  </div>
                  <div style={{fontSize: '0.9rem', color: '#666', marginTop: '0.25rem'}}>
                    {record.memo || '메모 없음'}
                  </div>
                </div>
                <div style={{textAlign: 'right'}}>
                  <div style={{fontSize: '1.2rem', fontWeight: 700, color: '#667eea'}}>
                    {record.totalAmount.toLocaleString()} DC
                  </div>
                  <div style={{fontSize: '0.9rem', color: '#666'}}>
                    {record.recipientCount}명 × {record.amountPerRecipient} DC
                  </div>
                </div>
              </div>
              <div style={{display: 'flex', gap: '1rem'}}>
                <span className="status-badge active">
                  ✅ 성공: {record.successCount}명
                </span>
                {record.failCount > 0 && (
                  <span className="status-badge suspended">
                    ❌ 실패: {record.failCount}명
                  </span>
                )}
              </div>
              {record.results && (
                <details style={{marginTop: '1rem'}}>
                  <summary style={{cursor: 'pointer', fontWeight: 600}}>상세 내역 보기</summary>
                  <div style={{marginTop: '1rem', maxHeight: '200px', overflowY: 'auto'}}>
                    {record.results.map((result, idx) => (
                      <div key={idx} style={{padding: '0.5rem', borderBottom: '1px solid #ddd'}}>
                        <div style={{display: 'flex', justifyContent: 'space-between'}}>
                          <span>{result.name}</span>
                          <span style={{fontFamily: 'monospace', fontSize: '0.85rem'}}>
                            {result.address.substring(0, 10)}...{result.address.substring(48)}
                          </span>
                          <span className={result.status === 'SUCCESS' ? 'points' : 'user-email'}>
                            {result.status === 'SUCCESS' ? `✅ ${result.amount} DC` : '❌ 실패'}
                          </span>
                        </div>
                        {result.txId && (
                          <div style={{fontSize: '0.8rem', color: '#666', marginTop: '0.25rem'}}>
                            TX: {result.txId.substring(0, 20)}...
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default BulkDCPage;
