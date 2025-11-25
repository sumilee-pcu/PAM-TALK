/**
 * Committee Verification Page
 * 위원회 ESG 활동 검증 페이지
 */

import React, { useState, useEffect } from 'react';
import { committeeService } from '../../../services/api';
import './VerificationPage.css';

function VerificationPage() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [reviewComment, setReviewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadPendingActivities();
  }, []);

  const loadPendingActivities = async () => {
    try {
      setLoading(true);
      const response = await committeeService.getPendingActivities();
      setActivities(response.activities || []);
    } catch (error) {
      console.error('활동 로드 실패:', error);
      alert('활동을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (activityId, status) => {
    if (!reviewComment.trim()) {
      alert('검토 의견을 입력해주세요.');
      return;
    }

    try {
      setSubmitting(true);
      await committeeService.verifyActivity(activityId, status, reviewComment);

      alert(`✅ ${status === 'APPROVED' ? '승인' : '거부'}되었습니다.`);

      // 목록 새로고침
      setSelectedActivity(null);
      setReviewComment('');
      await loadPendingActivities();
    } catch (error) {
      console.error('검증 실패:', error);
      alert('검증 처리에 실패했습니다: ' + (error.error || error.message));
    } finally {
      setSubmitting(false);
    }
  };

  const openActivityDetail = (activity) => {
    setSelectedActivity(activity);
    setReviewComment('');
  };

  const closeModal = () => {
    setSelectedActivity(null);
    setReviewComment('');
  };

  if (loading) {
    return (
      <div className="verification-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>활동을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="verification-page">
      <div className="verification-header">
        <h1>✅ ESG 활동 검증</h1>
        <p>검증 대기 중인 활동: {activities.length}건</p>
      </div>

      {activities.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h2>검증 대기 중인 활동이 없습니다</h2>
          <p>모든 활동이 검증되었습니다!</p>
        </div>
      ) : (
        <div className="activities-grid">
          {activities.map((activity) => (
            <div key={activity.id} className="activity-card">
              {activity.proof && (
                <div className="activity-image">
                  <img src={activity.proof} alt="활동 증빙" />
                </div>
              )}
              <div className="activity-content">
                <h3>{activity.title}</h3>
                <p className="activity-description">{activity.description}</p>

                <div className="activity-meta">
                  <div className="meta-item">
                    <span className="meta-label">👤 사용자:</span>
                    <span className="meta-value">{activity.user?.name || 'Unknown'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">🌱 탄소 감축:</span>
                    <span className="meta-value">{activity.carbonReduction} kg CO₂</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">🪙 예상 보상:</span>
                    <span className="meta-value">{activity.potentialReward || 'N/A'} ESG-GOLD</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">📅 제출일:</span>
                    <span className="meta-value">
                      {new Date(activity.createdAt).toLocaleDateString('ko-KR')}
                    </span>
                  </div>
                </div>

                <button
                  className="btn-review"
                  onClick={() => openActivityDetail(activity)}
                >
                  🔍 상세 검증
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 검증 모달 */}
      {selectedActivity && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>ESG 활동 검증</h2>
              <button className="btn-close" onClick={closeModal}>✕</button>
            </div>

            <div className="modal-body">
              <div className="activity-detail-section">
                <h3>활동 정보</h3>
                <table className="detail-table">
                  <tbody>
                    <tr>
                      <th>제목</th>
                      <td>{selectedActivity.title}</td>
                    </tr>
                    <tr>
                      <th>설명</th>
                      <td>{selectedActivity.description}</td>
                    </tr>
                    <tr>
                      <th>사용자</th>
                      <td>{selectedActivity.user?.name || 'Unknown'}</td>
                    </tr>
                    <tr>
                      <th>활동 유형</th>
                      <td>{selectedActivity.activityType}</td>
                    </tr>
                    <tr>
                      <th>탄소 감축량</th>
                      <td>{selectedActivity.carbonReduction} kg CO₂</td>
                    </tr>
                    <tr>
                      <th>제출일시</th>
                      <td>{new Date(selectedActivity.createdAt).toLocaleString('ko-KR')}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {selectedActivity.proof && (
                <div className="activity-detail-section">
                  <h3>증빙 자료</h3>
                  <img
                    src={selectedActivity.proof}
                    alt="활동 증빙"
                    className="proof-image-large"
                  />
                </div>
              )}

              <div className="activity-detail-section">
                <h3>검토 의견</h3>
                <textarea
                  className="review-textarea"
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  placeholder="검토 의견을 입력하세요..."
                  rows="4"
                  disabled={submitting}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn-approve"
                onClick={() => handleVerify(selectedActivity.id, 'APPROVED')}
                disabled={submitting || !reviewComment.trim()}
              >
                {submitting ? '처리 중...' : '✅ 승인'}
              </button>
              <button
                className="btn-reject"
                onClick={() => handleVerify(selectedActivity.id, 'REJECTED')}
                disabled={submitting || !reviewComment.trim()}
              >
                {submitting ? '처리 중...' : '❌ 거부'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VerificationPage;
