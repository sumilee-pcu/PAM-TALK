/**
 * ESG Activities Management Page (Admin)
 * 관리자용 ESG 활동 등록 및 관리 페이지
 */

import React, { useState, useEffect } from 'react';
import '../Users/UsersPage.css';

function ESGActivitiesPage() {
  const [activities, setActivities] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingActivity, setEditingActivity] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    category: 'recycling',
    icon: '♻️',
    reward: 50,
    description: '',
    status: 'ACTIVE'
  });

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = () => {
    const saved = localStorage.getItem('admin_esg_activities');
    if (saved) {
      setActivities(JSON.parse(saved));
    } else {
      // 기본 활동 목록
      const defaultActivities = [
        { id: 1, name: '플라스틱 재활용', category: 'recycling', icon: '♻️', reward: 30, description: '플라스틱 분리수거', status: 'ACTIVE', created: '2024-11-20' },
        { id: 2, name: '종이 재활용', category: 'recycling', icon: '📄', reward: 40, description: '종이류 분리수거', status: 'ACTIVE', created: '2024-11-20' },
        { id: 3, name: '대중교통 이용', category: 'green_transport', icon: '🚌', reward: 50, description: '버스/지하철 이용', status: 'ACTIVE', created: '2024-11-20' },
        { id: 4, name: '자전거 출퇴근', category: 'green_transport', icon: '🚲', reward: 80, description: '자전거로 출퇴근', status: 'ACTIVE', created: '2024-11-20' },
        { id: 5, name: '나무 심기', category: 'tree_planting', icon: '🌳', reward: 200, description: '나무 심기 활동', status: 'ACTIVE', created: '2024-11-20' },
        { id: 6, name: 'LED 전구 사용', category: 'clean_energy', icon: '💡', reward: 100, description: 'LED 전구로 교체', status: 'ACTIVE', created: '2024-11-21' }
      ];
      setActivities(defaultActivities);
      localStorage.setItem('admin_esg_activities', JSON.stringify(defaultActivities));
    }
  };

  const categories = {
    recycling: { label: '재활용', color: '#3498db' },
    green_transport: { label: '친환경 교통', color: '#2ecc71' },
    tree_planting: { label: '나무 심기', color: '#27ae60' },
    clean_energy: { label: '청정 에너지', color: '#f39c12' },
    water_saving: { label: '물 절약', color: '#1abc9c' },
    waste_reduction: { label: '폐기물 감축', color: '#e74c3c' }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCreateNew = () => {
    setEditingActivity(null);
    setFormData({
      name: '',
      category: 'recycling',
      icon: '♻️',
      reward: 50,
      description: '',
      status: 'ACTIVE'
    });
    setShowModal(true);
  };

  const handleEdit = (activity) => {
    setEditingActivity(activity);
    setFormData({
      name: activity.name,
      category: activity.category,
      icon: activity.icon,
      reward: activity.reward,
      description: activity.description,
      status: activity.status
    });
    setShowModal(true);
  };

  const handleSave = () => {
    if (!formData.name || !formData.description) {
      alert('❌ 활동명과 설명을 입력하세요.');
      return;
    }

    if (formData.reward <= 0) {
      alert('❌ 보상 포인트는 0보다 커야 합니다.');
      return;
    }

    let updated;
    if (editingActivity) {
      // 수정
      updated = activities.map(a =>
        a.id === editingActivity.id
          ? { ...editingActivity, ...formData }
          : a
      );
      alert('✅ ESG 활동이 수정되었습니다.');
    } else {
      // 신규 생성
      const newActivity = {
        id: Math.max(...activities.map(a => a.id), 0) + 1,
        ...formData,
        created: new Date().toISOString().split('T')[0]
      };
      updated = [...activities, newActivity];
      alert('✅ 새로운 ESG 활동이 등록되었습니다.');
    }

    setActivities(updated);
    localStorage.setItem('admin_esg_activities', JSON.stringify(updated));
    setShowModal(false);
  };

  const handleDelete = (id) => {
    if (!window.confirm('⚠️ 정말 이 활동을 삭제하시겠습니까?')) return;

    const updated = activities.filter(a => a.id !== id);
    setActivities(updated);
    localStorage.setItem('admin_esg_activities', JSON.stringify(updated));
    alert('✅ ESG 활동이 삭제되었습니다.');
  };

  const handleStatusToggle = (id) => {
    const updated = activities.map(a =>
      a.id === id
        ? { ...a, status: a.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE' }
        : a
    );
    setActivities(updated);
    localStorage.setItem('admin_esg_activities', JSON.stringify(updated));
  };

  const stats = {
    total: activities.length,
    active: activities.filter(a => a.status === 'ACTIVE').length,
    inactive: activities.filter(a => a.status === 'INACTIVE').length,
    avgReward: Math.round(activities.reduce((sum, a) => sum + a.reward, 0) / activities.length) || 0
  };

  return (
    <div className="users-page">
      <div className="page-header">
        <h1>🌱 ESG 활동 관리</h1>
        <p>ESG 활동 종류 등록 및 관리</p>
        <button className="btn-create" onClick={handleCreateNew}>
          ➕ 새 활동 등록
        </button>
      </div>

      {/* 통계 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-label">전체 활동</div>
            <div className="stat-value">{stats.total}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">활성 활동</div>
            <div className="stat-value">{stats.active}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏸️</div>
          <div className="stat-content">
            <div className="stat-label">비활성 활동</div>
            <div className="stat-value">{stats.inactive}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🎁</div>
          <div className="stat-content">
            <div className="stat-label">평균 보상</div>
            <div className="stat-value">{stats.avgReward} P</div>
          </div>
        </div>
      </div>

      {/* 활동 테이블 */}
      <div className="users-table-container">
        <h2 style={{marginBottom: '1rem'}}>등록된 ESG 활동</h2>
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>아이콘</th>
              <th>활동명</th>
              <th>카테고리</th>
              <th>보상</th>
              <th>상태</th>
              <th>등록일</th>
              <th>작업</th>
            </tr>
          </thead>
          <tbody>
            {activities.map(activity => (
              <tr key={activity.id}>
                <td>{activity.id}</td>
                <td style={{fontSize: '1.5rem'}}>{activity.icon}</td>
                <td className="user-name">{activity.name}</td>
                <td>
                  <span
                    className="role-badge"
                    style={{
                      background: categories[activity.category]?.color || '#999',
                      color: 'white'
                    }}
                  >
                    {categories[activity.category]?.label || activity.category}
                  </span>
                </td>
                <td className="points">{activity.reward} P</td>
                <td>
                  <span className={`status-badge ${activity.status === 'ACTIVE' ? 'active' : 'suspended'}`}>
                    {activity.status === 'ACTIVE' ? '활성' : '비활성'}
                  </span>
                </td>
                <td style={{fontSize: '0.9rem'}}>{activity.created}</td>
                <td>
                  <button className="btn-view" onClick={() => handleEdit(activity)}>
                    수정
                  </button>
                  <button
                    className={activity.status === 'ACTIVE' ? 'btn-suspend' : 'btn-activate'}
                    onClick={() => handleStatusToggle(activity.id)}
                    style={{marginLeft: '0.5rem'}}
                  >
                    {activity.status === 'ACTIVE' ? '비활성화' : '활성화'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 활동 등록/수정 모달 */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingActivity ? 'ESG 활동 수정' : '새 ESG 활동 등록'}</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>활동명 *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="예: 플라스틱 재활용"
                />
              </div>

              <div className="form-group">
                <label>카테고리 *</label>
                <select name="category" value={formData.category} onChange={handleInputChange}>
                  {Object.entries(categories).map(([key, cat]) => (
                    <option key={key} value={key}>{cat.label}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>아이콘 (이모지) *</label>
                <input
                  type="text"
                  name="icon"
                  value={formData.icon}
                  onChange={handleInputChange}
                  placeholder="♻️"
                  maxLength={2}
                />
              </div>

              <div className="form-group">
                <label>보상 포인트 *</label>
                <input
                  type="number"
                  name="reward"
                  value={formData.reward}
                  onChange={handleInputChange}
                  min="1"
                  placeholder="50"
                />
              </div>

              <div className="form-group">
                <label>설명 *</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="활동에 대한 자세한 설명을 입력하세요"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>상태</label>
                <select name="status" value={formData.status} onChange={handleInputChange}>
                  <option value="ACTIVE">활성</option>
                  <option value="INACTIVE">비활성</option>
                </select>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-activate" onClick={handleSave}>
                💾 저장
              </button>
              {editingActivity && (
                <button
                  className="btn-suspend"
                  onClick={() => {
                    handleDelete(editingActivity.id);
                    setShowModal(false);
                  }}
                >
                  🗑️ 삭제
                </button>
              )}
              <button className="btn-cancel" onClick={() => setShowModal(false)}>
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ESGActivitiesPage;
