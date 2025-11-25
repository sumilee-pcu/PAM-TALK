/**
 * ESG Activity Application Page (User)
 * 사용자 ESG 활동 신청 페이지
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import './ESGPage.css';

function ESGApplicationPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activities, setActivities] = useState([]);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [myApplications, setMyApplications] = useState([]);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [applicationForm, setApplicationForm] = useState({
    plannedDate: '',
    location: '',
    notes: '',
    quantity: 1
  });

  useEffect(() => {
    loadActivities();
    loadMyApplications();
  }, []);

  const loadActivities = () => {
    const saved = localStorage.getItem('admin_esg_activities');
    if (saved) {
      const all = JSON.parse(saved);
      setActivities(all.filter(a => a.status === 'ACTIVE'));
    }
  };

  const loadMyApplications = () => {
    const saved = localStorage.getItem('esg_applications');
    if (saved) {
      const all = JSON.parse(saved);
      setMyApplications(all.filter(app => app.userId === user?.id));
    }
  };

  const handleApply = (activity) => {
    setSelectedActivity(activity);
    setApplicationForm({
      plannedDate: new Date().toISOString().split('T')[0],
      location: '',
      notes: '',
      quantity: 1
    });
    setShowApplicationModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setApplicationForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmitApplication = () => {
    if (!applicationForm.plannedDate || !applicationForm.location) {
      alert('❌ 예정일과 활동 장소를 입력하세요.');
      return;
    }

    const newApplication = {
      id: Date.now(),
      userId: user?.id || 1,
      userName: user?.name || '사용자',
      activityId: selectedActivity.id,
      activityName: selectedActivity.name,
      activityIcon: selectedActivity.icon,
      category: selectedActivity.category,
      reward: selectedActivity.reward,
      plannedDate: applicationForm.plannedDate,
      location: applicationForm.location,
      notes: applicationForm.notes,
      quantity: parseInt(applicationForm.quantity) || 1,
      status: 'PENDING',
      appliedAt: new Date().toISOString(),
      approvedBy: null,
      approvedAt: null
    };

    const allApplications = JSON.parse(localStorage.getItem('esg_applications') || '[]');
    allApplications.push(newApplication);
    localStorage.setItem('esg_applications', JSON.stringify(allApplications));

    setMyApplications([...myApplications, newApplication]);
    setShowApplicationModal(false);
    alert('✅ ESG 활동 신청이 완료되었습니다!\n\n위원회 승인 후 활동을 진행해주세요.');
  };

  const handleCancelApplication = (appId) => {
    if (!window.confirm('⚠️ 신청을 취소하시겠습니까?')) return;

    const allApplications = JSON.parse(localStorage.getItem('esg_applications') || '[]');
    const updated = allApplications.filter(app => app.id !== appId);
    localStorage.setItem('esg_applications', JSON.stringify(updated));

    setMyApplications(myApplications.filter(app => app.id !== appId));
    alert('✅ 신청이 취소되었습니다.');
  };

  const getStatusBadge = (status) => {
    const badges = {
      'PENDING': { class: 'role-badge committee', label: '대기중' },
      'APPROVED': { class: 'role-badge farmer', label: '승인됨' },
      'REJECTED': { class: 'role-badge admin', label: '거절됨' },
      'COMPLETED': { class: 'status-badge active', label: '완료' }
    };
    return badges[status] || badges['PENDING'];
  };

  const categories = {
    recycling: { label: '재활용', color: '#3498db' },
    green_transport: { label: '친환경 교통', color: '#2ecc71' },
    tree_planting: { label: '나무 심기', color: '#27ae60' },
    clean_energy: { label: '청정 에너지', color: '#f39c12' },
    water_saving: { label: '물 절약', color: '#1abc9c' },
    waste_reduction: { label: '폐기물 감축', color: '#e74c3c' }
  };

  return (
    <div className="esg-page">
      <div className="esg-container">
        <div className="esg-header">
          <h1>📝 ESG 활동 신청</h1>
          <p>참여하고 싶은 ESG 활동을 신청하세요</p>
        </div>

        {/* 내 신청 현황 */}
        {myApplications.length > 0 && (
          <div className="users-table-container" style={{marginBottom: '2rem'}}>
            <h2 style={{marginBottom: '1rem'}}>내 신청 현황</h2>
            <table className="users-table">
              <thead>
                <tr>
                  <th>활동</th>
                  <th>예정일</th>
                  <th>장소</th>
                  <th>보상</th>
                  <th>상태</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {myApplications.map(app => {
                  const badge = getStatusBadge(app.status);
                  return (
                    <tr key={app.id}>
                      <td>
                        <span style={{fontSize: '1.2rem', marginRight: '0.5rem'}}>
                          {app.activityIcon}
                        </span>
                        {app.activityName}
                      </td>
                      <td>{app.plannedDate}</td>
                      <td>{app.location}</td>
                      <td className="points">{app.reward} P</td>
                      <td>
                        <span className={badge.class}>{badge.label}</span>
                      </td>
                      <td>
                        {app.status === 'PENDING' && (
                          <button
                            className="btn-suspend"
                            onClick={() => handleCancelApplication(app.id)}
                          >
                            취소
                          </button>
                        )}
                        {app.status === 'APPROVED' && (
                          <button
                            className="btn-activate"
                            onClick={() => navigate('/esg')}
                          >
                            인증하기
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* 신청 가능한 활동 */}
        <div className="esg-content">
          <h2 className="section-title">신청 가능한 ESG 활동</h2>
          <div className="category-grid">
            {activities.map(activity => (
              <div
                key={activity.id}
                className="category-card"
                style={{ borderColor: categories[activity.category]?.color || '#999' }}
              >
                <div
                  className="category-icon"
                  style={{ background: categories[activity.category]?.color || '#999' }}
                >
                  {activity.icon}
                </div>
                <h3 className="category-name">{activity.name}</h3>
                <p className="category-description">{activity.description}</p>
                <div className="category-reward-range">{activity.reward} 포인트</div>
                <button
                  className="btn-start-certification"
                  style={{marginTop: '1rem', width: '100%'}}
                  onClick={() => handleApply(activity)}
                >
                  📝 신청하기
                </button>
              </div>
            ))}
          </div>

          {activities.length === 0 && (
            <div className="empty-state" style={{padding: '3rem', textAlign: 'center'}}>
              <p>현재 신청 가능한 ESG 활동이 없습니다.</p>
            </div>
          )}
        </div>

        {/* 신청 모달 */}
        {showApplicationModal && selectedActivity && (
          <div className="modal-overlay" onClick={() => setShowApplicationModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>ESG 활동 신청</h2>
                <button className="btn-close" onClick={() => setShowApplicationModal(false)}>✕</button>
              </div>

              <div className="modal-body">
                <div className="user-detail-grid">
                  <div className="detail-item" style={{gridColumn: '1 / -1'}}>
                    <label>선택한 활동</label>
                    <div style={{fontSize: '1.2rem', fontWeight: 600}}>
                      {selectedActivity.icon} {selectedActivity.name}
                    </div>
                  </div>

                  <div className="detail-item">
                    <label>카테고리</label>
                    <div>{categories[selectedActivity.category]?.label}</div>
                  </div>

                  <div className="detail-item">
                    <label>예상 보상</label>
                    <div className="points-large">{selectedActivity.reward} P</div>
                  </div>

                  <div className="detail-item" style={{gridColumn: '1 / -1'}}>
                    <label>활동 예정일 *</label>
                    <input
                      type="date"
                      name="plannedDate"
                      value={applicationForm.plannedDate}
                      onChange={handleInputChange}
                      min={new Date().toISOString().split('T')[0]}
                      style={{width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd'}}
                    />
                  </div>

                  <div className="detail-item" style={{gridColumn: '1 / -1'}}>
                    <label>활동 장소 *</label>
                    <input
                      type="text"
                      name="location"
                      value={applicationForm.location}
                      onChange={handleInputChange}
                      placeholder="예: 서울시 강남구 역삼동"
                      style={{width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd'}}
                    />
                  </div>

                  <div className="detail-item" style={{gridColumn: '1 / -1'}}>
                    <label>수량 (횟수)</label>
                    <input
                      type="number"
                      name="quantity"
                      value={applicationForm.quantity}
                      onChange={handleInputChange}
                      min="1"
                      style={{width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd'}}
                    />
                  </div>

                  <div className="detail-item" style={{gridColumn: '1 / -1'}}>
                    <label>특이사항</label>
                    <textarea
                      name="notes"
                      value={applicationForm.notes}
                      onChange={handleInputChange}
                      placeholder="활동에 대한 추가 정보를 입력하세요 (선택사항)"
                      rows="3"
                      style={{width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd'}}
                    />
                  </div>
                </div>
              </div>

              <div className="modal-footer">
                <button className="btn-activate" onClick={handleSubmitApplication}>
                  ✅ 신청하기
                </button>
                <button className="btn-cancel" onClick={() => setShowApplicationModal(false)}>
                  취소
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ESGApplicationPage;
