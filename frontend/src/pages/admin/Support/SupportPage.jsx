/**
 * Support Page
 * 고객 지원 페이지
 */

import React, { useState } from 'react';
import '../Users/UsersPage.css';

function SupportPage() {
  const [tickets, setTickets] = useState([
    {
      id: 1,
      user: '김소비',
      email: 'consumer@pamtalk.com',
      subject: '쿠폰 사용 관련 문의',
      category: '쿠폰',
      status: 'OPEN',
      priority: 'HIGH',
      created: '2024-11-22 09:30:00',
      updated: '2024-11-22 10:15:00'
    },
    {
      id: 2,
      user: '이농부',
      email: 'farmer@pamtalk.com',
      subject: 'ESG 포인트가 적립되지 않습니다',
      category: 'ESG',
      status: 'IN_PROGRESS',
      priority: 'HIGH',
      created: '2024-11-22 08:15:00',
      updated: '2024-11-22 09:45:00'
    },
    {
      id: 3,
      user: '정소비자',
      email: 'user1@example.com',
      subject: '비밀번호 재설정 요청',
      category: '계정',
      status: 'RESOLVED',
      priority: 'NORMAL',
      created: '2024-11-21 15:20:00',
      updated: '2024-11-21 16:30:00'
    },
    {
      id: 4,
      user: '강농부',
      email: 'farmer2@example.com',
      subject: '활동 인증 사진이 업로드되지 않습니다',
      category: '기술',
      status: 'OPEN',
      priority: 'NORMAL',
      created: '2024-11-21 14:10:00',
      updated: '2024-11-21 14:10:00'
    }
  ]);

  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const stats = {
    total: tickets.length,
    open: tickets.filter(t => t.status === 'OPEN').length,
    inProgress: tickets.filter(t => t.status === 'IN_PROGRESS').length,
    resolved: tickets.filter(t => t.status === 'RESOLVED').length
  };

  const getStatusBadge = (status) => {
    const classes = {
      'OPEN': 'role-badge admin',
      'IN_PROGRESS': 'role-badge committee',
      'RESOLVED': 'role-badge farmer'
    };
    return classes[status] || 'role-badge';
  };

  const getStatusLabel = (status) => {
    const labels = {
      'OPEN': '대기',
      'IN_PROGRESS': '처리중',
      'RESOLVED': '완료'
    };
    return labels[status] || status;
  };

  const getPriorityBadge = (priority) => {
    return priority === 'HIGH' ? 'status-badge suspended' : 'status-badge active';
  };

  const getPriorityLabel = (priority) => {
    return priority === 'HIGH' ? '높음' : '보통';
  };

  const handleViewTicket = (ticket) => {
    setSelectedTicket(ticket);
    setShowModal(true);
  };

  const handleUpdateStatus = (ticketId, newStatus) => {
    const updated = tickets.map(t =>
      t.id === ticketId ? { ...t, status: newStatus, updated: new Date().toISOString().replace('T', ' ').substring(0, 19) } : t
    );
    setTickets(updated);

    if (selectedTicket && selectedTicket.id === ticketId) {
      setSelectedTicket({ ...selectedTicket, status: newStatus });
    }

    alert(`✅ 티켓 상태가 "${getStatusLabel(newStatus)}"(으)로 변경되었습니다.`);
  };

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>💬 고객 지원</h1>
        <p>사용자 문의 및 지원 티켓 관리</p>
      </div>

      {/* 통계 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-label">전체 티켓</div>
            <div className="stat-value">{stats.total}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🆕</div>
          <div className="stat-content">
            <div className="stat-label">대기중</div>
            <div className="stat-value">{stats.open}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <div className="stat-label">처리중</div>
            <div className="stat-value">{stats.inProgress}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">완료</div>
            <div className="stat-value">{stats.resolved}</div>
          </div>
        </div>
      </div>

      {/* 티켓 테이블 */}
      <div className="users-table-container">
        <h2 style={{marginBottom: '1rem'}}>지원 티켓</h2>
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>사용자</th>
              <th>제목</th>
              <th>카테고리</th>
              <th>우선순위</th>
              <th>상태</th>
              <th>생성일</th>
              <th>작업</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map(ticket => (
              <tr key={ticket.id}>
                <td>{ticket.id}</td>
                <td className="user-name">{ticket.user}</td>
                <td>{ticket.subject}</td>
                <td>{ticket.category}</td>
                <td>
                  <span className={getPriorityBadge(ticket.priority)}>
                    {getPriorityLabel(ticket.priority)}
                  </span>
                </td>
                <td>
                  <span className={getStatusBadge(ticket.status)}>
                    {getStatusLabel(ticket.status)}
                  </span>
                </td>
                <td style={{fontSize: '0.9rem'}}>{ticket.created}</td>
                <td>
                  <button className="btn-view" onClick={() => handleViewTicket(ticket)}>
                    상세
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 티켓 상세 모달 */}
      {showModal && selectedTicket && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>티켓 상세 정보</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <div className="user-detail-grid">
                <div className="detail-item">
                  <label>티켓 ID</label>
                  <div>#{selectedTicket.id}</div>
                </div>
                <div className="detail-item">
                  <label>사용자</label>
                  <div>{selectedTicket.user}</div>
                </div>
                <div className="detail-item">
                  <label>이메일</label>
                  <div>{selectedTicket.email}</div>
                </div>
                <div className="detail-item">
                  <label>카테고리</label>
                  <div>{selectedTicket.category}</div>
                </div>
                <div className="detail-item">
                  <label>우선순위</label>
                  <div>
                    <span className={getPriorityBadge(selectedTicket.priority)}>
                      {getPriorityLabel(selectedTicket.priority)}
                    </span>
                  </div>
                </div>
                <div className="detail-item">
                  <label>상태</label>
                  <div>
                    <span className={getStatusBadge(selectedTicket.status)}>
                      {getStatusLabel(selectedTicket.status)}
                    </span>
                  </div>
                </div>
                <div className="detail-item" style={{gridColumn: '1 / -1'}}>
                  <label>제목</label>
                  <div style={{fontSize: '1.1rem', fontWeight: 600}}>{selectedTicket.subject}</div>
                </div>
                <div className="detail-item">
                  <label>생성일</label>
                  <div>{selectedTicket.created}</div>
                </div>
                <div className="detail-item">
                  <label>최종 수정</label>
                  <div>{selectedTicket.updated}</div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              {selectedTicket.status === 'OPEN' && (
                <button
                  className="btn-activate"
                  onClick={() => handleUpdateStatus(selectedTicket.id, 'IN_PROGRESS')}
                >
                  ⏳ 처리 시작
                </button>
              )}
              {selectedTicket.status === 'IN_PROGRESS' && (
                <button
                  className="btn-activate"
                  onClick={() => handleUpdateStatus(selectedTicket.id, 'RESOLVED')}
                >
                  ✅ 완료 처리
                </button>
              )}
              {selectedTicket.status === 'RESOLVED' && (
                <button
                  className="btn-suspend"
                  onClick={() => handleUpdateStatus(selectedTicket.id, 'OPEN')}
                >
                  🔄 재오픈
                </button>
              )}
              <button className="btn-cancel" onClick={() => setShowModal(false)}>
                닫기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SupportPage;
