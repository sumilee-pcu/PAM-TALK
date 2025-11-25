/**
 * Committee Management Page
 * 위원회 관리 페이지
 */

import React, { useState, useEffect } from 'react';
import '../Users/UsersPage.css'; // 공통 스타일 재사용

function CommitteeManagement() {
  const [committees, setCommittees] = useState([]);
  const [selectedCommittee, setSelectedCommittee] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadCommittees();
  }, []);

  const loadCommittees = () => {
    const savedCommittees = localStorage.getItem('admin_committees_list');

    if (savedCommittees) {
      setCommittees(JSON.parse(savedCommittees));
    } else {
      const demoData = [
        {
          id: 1,
          name: '박위원',
          email: 'committee@pamtalk.com',
          role: '검증 위원',
          status: 'ACTIVE',
          verifications: 120,
          approvalRate: 95.5,
          joinDate: '2024-01-10'
        },
        {
          id: 2,
          name: '김검증',
          email: 'committee2@example.com',
          role: '검증 위원',
          status: 'ACTIVE',
          verifications: 85,
          approvalRate: 92.3,
          joinDate: '2024-02-15'
        },
        {
          id: 3,
          name: '이심사',
          email: 'committee3@example.com',
          role: '심사 위원',
          status: 'ACTIVE',
          verifications: 150,
          approvalRate: 97.1,
          joinDate: '2023-12-01'
        }
      ];

      setCommittees(demoData);
      localStorage.setItem('admin_committees_list', JSON.stringify(demoData));
    }
  };

  const handleViewDetails = (committee) => {
    setSelectedCommittee(committee);
    setShowModal(true);
  };

  const handleToggleStatus = (id) => {
    const updated = committees.map(c =>
      c.id === id ? { ...c, status: c.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE' } : c
    );
    setCommittees(updated);
    localStorage.setItem('admin_committees_list', JSON.stringify(updated));

    if (selectedCommittee && selectedCommittee.id === id) {
      setSelectedCommittee({
        ...selectedCommittee,
        status: selectedCommittee.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE'
      });
    }
  };

  const stats = {
    total: committees.length,
    active: committees.filter(c => c.status === 'ACTIVE').length,
    totalVerifications: committees.reduce((sum, c) => sum + c.verifications, 0),
    avgApprovalRate: (committees.reduce((sum, c) => sum + c.approvalRate, 0) / committees.length).toFixed(1)
  };

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>🏛️ 위원회 관리</h1>
        <p>검증 위원 관리 및 활동 현황</p>
      </div>

      {/* 통계 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-label">전체 위원</div>
            <div className="stat-value">{stats.total}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">활성 위원</div>
            <div className="stat-value">{stats.active}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <div className="stat-label">총 검증 건수</div>
            <div className="stat-value">{stats.totalVerifications}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">평균 승인율</div>
            <div className="stat-value">{stats.avgApprovalRate}%</div>
          </div>
        </div>
      </div>

      {/* 위원 테이블 */}
      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>이름</th>
              <th>이메일</th>
              <th>역할</th>
              <th>상태</th>
              <th>검증 건수</th>
              <th>승인율</th>
              <th>가입일</th>
              <th>작업</th>
            </tr>
          </thead>
          <tbody>
            {committees.map(committee => (
              <tr key={committee.id}>
                <td>{committee.id}</td>
                <td className="user-name">{committee.name}</td>
                <td>{committee.email}</td>
                <td>{committee.role}</td>
                <td>
                  <span className={`status-badge ${committee.status === 'ACTIVE' ? 'active' : 'suspended'}`}>
                    {committee.status === 'ACTIVE' ? '활성' : '정지'}
                  </span>
                </td>
                <td>{committee.verifications}</td>
                <td className="points">{committee.approvalRate}%</td>
                <td>{committee.joinDate}</td>
                <td>
                  <button className="btn-view" onClick={() => handleViewDetails(committee)}>
                    상세
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 상세 모달 */}
      {showModal && selectedCommittee && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>위원 상세 정보</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <div className="user-detail-grid">
                <div className="detail-item">
                  <label>이름</label>
                  <div>{selectedCommittee.name}</div>
                </div>
                <div className="detail-item">
                  <label>이메일</label>
                  <div>{selectedCommittee.email}</div>
                </div>
                <div className="detail-item">
                  <label>역할</label>
                  <div>{selectedCommittee.role}</div>
                </div>
                <div className="detail-item">
                  <label>검증 건수</label>
                  <div className="points-large">{selectedCommittee.verifications}</div>
                </div>
                <div className="detail-item">
                  <label>승인율</label>
                  <div className="points-large">{selectedCommittee.approvalRate}%</div>
                </div>
                <div className="detail-item">
                  <label>가입일</label>
                  <div>{selectedCommittee.joinDate}</div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className={selectedCommittee.status === 'ACTIVE' ? 'btn-suspend' : 'btn-activate'}
                onClick={() => handleToggleStatus(selectedCommittee.id)}
              >
                {selectedCommittee.status === 'ACTIVE' ? '🚫 활동 정지' : '✅ 활동 재개'}
              </button>
              <button className="btn-cancel" onClick={() => setShowModal(false)}>닫기</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CommitteeManagement;
