/**
 * Users Management Page
 * 사용자 관리 페이지
 */

import React, { useState, useEffect } from 'react';
import './UsersPage.css';

function UsersPage() {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // 초기 데모 데이터 로드
  useEffect(() => {
    loadUsers();
  }, []);

  // 검색 및 필터링
  useEffect(() => {
    let result = users;

    // 검색어 필터링
    if (searchTerm) {
      result = result.filter(user =>
        user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // 역할 필터링
    if (roleFilter !== 'ALL') {
      result = result.filter(user => user.role === roleFilter);
    }

    // 상태 필터링
    if (statusFilter !== 'ALL') {
      result = result.filter(user => user.status === statusFilter);
    }

    setFilteredUsers(result);
  }, [searchTerm, roleFilter, statusFilter, users]);

  const loadUsers = () => {
    // 개발 모드: localStorage에서 사용자 로드
    const savedUsers = localStorage.getItem('admin_users_list');

    if (savedUsers) {
      setUsers(JSON.parse(savedUsers));
    } else {
      // 초기 데모 데이터
      const demoUsers = [
        {
          id: 1,
          name: '김소비',
          email: 'consumer@pamtalk.com',
          role: 'CONSUMER',
          status: 'ACTIVE',
          joinDate: '2024-01-15',
          lastLogin: '2024-11-22',
          esgPoints: 1250,
          activities: 45
        },
        {
          id: 2,
          name: '이농부',
          email: 'farmer@pamtalk.com',
          role: 'FARMER',
          status: 'ACTIVE',
          joinDate: '2024-02-01',
          lastLogin: '2024-11-21',
          esgPoints: 3400,
          activities: 78
        },
        {
          id: 3,
          name: '박위원',
          email: 'committee@pamtalk.com',
          role: 'COMMITTEE',
          status: 'ACTIVE',
          joinDate: '2024-01-10',
          lastLogin: '2024-11-22',
          esgPoints: 0,
          activities: 0
        },
        {
          id: 4,
          name: '최관리',
          email: 'admin@pamtalk.com',
          role: 'ADMIN',
          status: 'ACTIVE',
          joinDate: '2024-01-01',
          lastLogin: '2024-11-22',
          esgPoints: 0,
          activities: 0
        },
        {
          id: 5,
          name: '정소비자',
          email: 'user1@example.com',
          role: 'CONSUMER',
          status: 'ACTIVE',
          joinDate: '2024-03-15',
          lastLogin: '2024-11-20',
          esgPoints: 890,
          activities: 32
        },
        {
          id: 6,
          name: '강농부',
          email: 'farmer2@example.com',
          role: 'FARMER',
          status: 'SUSPENDED',
          joinDate: '2024-02-20',
          lastLogin: '2024-11-10',
          esgPoints: 2100,
          activities: 56
        }
      ];

      setUsers(demoUsers);
      localStorage.setItem('admin_users_list', JSON.stringify(demoUsers));
    }
  };

  const getRoleBadgeClass = (role) => {
    const classes = {
      'ADMIN': 'role-badge admin',
      'COMMITTEE': 'role-badge committee',
      'FARMER': 'role-badge farmer',
      'CONSUMER': 'role-badge consumer'
    };
    return classes[role] || 'role-badge';
  };

  const getRoleLabel = (role) => {
    const labels = {
      'ADMIN': '관리자',
      'COMMITTEE': '위원회',
      'FARMER': '농부',
      'CONSUMER': '소비자'
    };
    return labels[role] || role;
  };

  const getStatusBadgeClass = (status) => {
    return status === 'ACTIVE' ? 'status-badge active' : 'status-badge suspended';
  };

  const getStatusLabel = (status) => {
    return status === 'ACTIVE' ? '활성' : '정지';
  };

  const handleViewUser = (user) => {
    setSelectedUser(user);
    setShowModal(true);
  };

  const handleToggleStatus = (userId) => {
    const updatedUsers = users.map(user => {
      if (user.id === userId) {
        return {
          ...user,
          status: user.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE'
        };
      }
      return user;
    });

    setUsers(updatedUsers);
    localStorage.setItem('admin_users_list', JSON.stringify(updatedUsers));

    if (selectedUser && selectedUser.id === userId) {
      setSelectedUser({
        ...selectedUser,
        status: selectedUser.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE'
      });
    }
  };

  const handleDeleteUser = (userId) => {
    if (!window.confirm('정말 이 사용자를 삭제하시겠습니까?')) {
      return;
    }

    const updatedUsers = users.filter(user => user.id !== userId);
    setUsers(updatedUsers);
    localStorage.setItem('admin_users_list', JSON.stringify(updatedUsers));
    setShowModal(false);
  };

  const stats = {
    total: users.length,
    active: users.filter(u => u.status === 'ACTIVE').length,
    suspended: users.filter(u => u.status === 'SUSPENDED').length,
    admins: users.filter(u => u.role === 'ADMIN').length,
    committee: users.filter(u => u.role === 'COMMITTEE').length,
    farmers: users.filter(u => u.role === 'FARMER').length,
    consumers: users.filter(u => u.role === 'CONSUMER').length
  };

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>👥 사용자 관리</h1>
        <p>전체 사용자 조회 및 관리</p>
      </div>

      {/* 통계 카드 */}
      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-icon">👤</div>
          <div className="stat-content">
            <div className="stat-label">전체 사용자</div>
            <div className="stat-value">{stats.total}</div>
          </div>
        </div>
        <div className="stat-card active">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">활성 사용자</div>
            <div className="stat-value">{stats.active}</div>
          </div>
        </div>
        <div className="stat-card suspended">
          <div className="stat-icon">🚫</div>
          <div className="stat-content">
            <div className="stat-label">정지 사용자</div>
            <div className="stat-value">{stats.suspended}</div>
          </div>
        </div>
        <div className="stat-card roles">
          <div className="stat-icon">🎭</div>
          <div className="stat-content">
            <div className="stat-label">역할별</div>
            <div className="stat-breakdown">
              관리자: {stats.admins} | 위원회: {stats.committee}<br/>
              농부: {stats.farmers} | 소비자: {stats.consumers}
            </div>
          </div>
        </div>
      </div>

      {/* 검색 및 필터 */}
      <div className="controls-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="이름 또는 이메일 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filters">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="filter-select"
          >
            <option value="ALL">모든 역할</option>
            <option value="ADMIN">관리자</option>
            <option value="COMMITTEE">위원회</option>
            <option value="FARMER">농부</option>
            <option value="CONSUMER">소비자</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="ALL">모든 상태</option>
            <option value="ACTIVE">활성</option>
            <option value="SUSPENDED">정지</option>
          </select>
        </div>
      </div>

      {/* 사용자 테이블 */}
      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>이름</th>
              <th>이메일</th>
              <th>역할</th>
              <th>상태</th>
              <th>가입일</th>
              <th>마지막 로그인</th>
              <th>ESG 포인트</th>
              <th>활동수</th>
              <th>작업</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.length > 0 ? (
              filteredUsers.map(user => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td className="user-name">{user.name}</td>
                  <td>{user.email}</td>
                  <td>
                    <span className={getRoleBadgeClass(user.role)}>
                      {getRoleLabel(user.role)}
                    </span>
                  </td>
                  <td>
                    <span className={getStatusBadgeClass(user.status)}>
                      {getStatusLabel(user.status)}
                    </span>
                  </td>
                  <td>{user.joinDate}</td>
                  <td>{user.lastLogin}</td>
                  <td className="points">{user.esgPoints.toLocaleString()}</td>
                  <td>{user.activities}</td>
                  <td>
                    <button
                      className="btn-view"
                      onClick={() => handleViewUser(user)}
                    >
                      상세
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="10" className="no-data">
                  검색 결과가 없습니다.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* 사용자 상세 모달 */}
      {showModal && selectedUser && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>사용자 상세 정보</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <div className="user-detail-grid">
                <div className="detail-item">
                  <label>ID</label>
                  <div>{selectedUser.id}</div>
                </div>
                <div className="detail-item">
                  <label>이름</label>
                  <div>{selectedUser.name}</div>
                </div>
                <div className="detail-item">
                  <label>이메일</label>
                  <div>{selectedUser.email}</div>
                </div>
                <div className="detail-item">
                  <label>역할</label>
                  <div>
                    <span className={getRoleBadgeClass(selectedUser.role)}>
                      {getRoleLabel(selectedUser.role)}
                    </span>
                  </div>
                </div>
                <div className="detail-item">
                  <label>상태</label>
                  <div>
                    <span className={getStatusBadgeClass(selectedUser.status)}>
                      {getStatusLabel(selectedUser.status)}
                    </span>
                  </div>
                </div>
                <div className="detail-item">
                  <label>가입일</label>
                  <div>{selectedUser.joinDate}</div>
                </div>
                <div className="detail-item">
                  <label>마지막 로그인</label>
                  <div>{selectedUser.lastLogin}</div>
                </div>
                <div className="detail-item">
                  <label>ESG 포인트</label>
                  <div className="points-large">{selectedUser.esgPoints.toLocaleString()}</div>
                </div>
                <div className="detail-item">
                  <label>활동 수</label>
                  <div>{selectedUser.activities}건</div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className={selectedUser.status === 'ACTIVE' ? 'btn-suspend' : 'btn-activate'}
                onClick={() => handleToggleStatus(selectedUser.id)}
              >
                {selectedUser.status === 'ACTIVE' ? '🚫 계정 정지' : '✅ 계정 활성화'}
              </button>
              <button
                className="btn-delete"
                onClick={() => handleDeleteUser(selectedUser.id)}
              >
                🗑️ 삭제
              </button>
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

export default UsersPage;
