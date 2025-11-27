/**
 * Activities Page (Feed)
 * 실시간 활동 피드 페이지
 */

import React, { useState } from 'react';
import './ActivitiesPage.css';

function ActivitiesPage() {
  const [activities, setActivities] = useState([
    {
      id: 1,
      user: {
        name: '김농부',
        icon: '🌾',
        role: '농부',
        location: '경기도 용인시',
        time: '방금 전'
      },
      content: '오늘 아침 수확한 토마토들! 🍅 30년간 키워온 노하우로 당도 최고예요',
      image: 'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=600&h=400&fit=crop&q=80',
      hashtags: ['토마토', '수확', '유기농'],
      eco: {
        carbon: 2.1,
        distance: 0
      },
      interactions: {
        likes: 45,
        comments: 12,
        shares: 8,
        liked: false
      }
    },
    {
      id: 2,
      user: {
        name: '박도시',
        icon: '🏠',
        role: '소비자',
        location: '서울시 강남구',
        time: '1시간 전'
      },
      content: '김농부님 토마토로 만든 파스타 🍝 정말 맛있어요!',
      image: 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&h=400&fit=crop&q=80',
      hashtags: ['리뷰', '로컬푸드', '파스타'],
      eco: {
        carbon: 1.5,
        distance: 35.2
      },
      interactions: {
        likes: 28,
        comments: 5,
        shares: 3,
        liked: false
      }
    },
    {
      id: 3,
      user: {
        name: '맛집사장',
        icon: '🍽️',
        role: '레스토랑',
        location: '서울시 홍대',
        time: '3시간 전'
      },
      content: '오늘 메뉴는 로컬 채소로 만든 비건 샐러드! 🥗 신선함이 달라요',
      image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&h=400&fit=crop&q=80',
      hashtags: ['로컬식재료', '비건', '레스토랑'],
      eco: {
        carbon: 3.2,
        distance: 18.5
      },
      interactions: {
        likes: 67,
        comments: 23,
        shares: 15,
        liked: false
      }
    }
  ]);

  const [newPost, setNewPost] = useState('');

  const handleLike = (activityId) => {
    setActivities(activities.map(activity =>
      activity.id === activityId
        ? {
            ...activity,
            interactions: {
              ...activity.interactions,
              liked: !activity.interactions.liked,
              likes: activity.interactions.liked
                ? activity.interactions.likes - 1
                : activity.interactions.likes + 1
            }
          }
        : activity
    ));
  };

  const handlePost = () => {
    if (!newPost.trim()) return;

    const newActivity = {
      id: activities.length + 1,
      user: {
        name: '나',
        icon: '👤',
        role: '소비자',
        location: '서울시',
        time: '방금 전'
      },
      content: newPost,
      hashtags: [],
      eco: {
        carbon: 0,
        distance: 0
      },
      interactions: {
        likes: 0,
        comments: 0,
        shares: 0,
        liked: false
      }
    };

    setActivities([newActivity, ...activities]);
    setNewPost('');
    alert('게시글이 등록되었습니다! 🎉');
  };

  return (
    <div className="activities-page">
      <div className="activities-container">
        {/* Main Feed Section */}
        <div className="feed-section">
          {/* Create Post */}
          <div className="create-activity">
            <div className="create-activity-header">
              <div className="user-avatar-small">👤</div>
              <div className="post-input">
                <textarea
                  className="post-textarea"
                  placeholder="오늘의 활동을 공유해보세요..."
                  rows="3"
                  value={newPost}
                  onChange={(e) => setNewPost(e.target.value)}
                />
              </div>
            </div>
            <div className="post-actions">
              <div className="post-options">
                <button className="post-option-btn">
                  <span>📷</span> 사진
                </button>
                <button className="post-option-btn">
                  <span>📍</span> 위치
                </button>
                <button className="post-option-btn">
                  <span>🏷️</span> 태그
                </button>
              </div>
              <button className="btn-post" onClick={handlePost}>
                공유하기
              </button>
            </div>
          </div>

          {/* Activity Feed */}
          {activities.map(activity => (
            <div key={activity.id} className="activity-card">
              <div className="activity-header">
                <div className="activity-user-info">
                  <div className="user-avatar">{activity.user.icon}</div>
                  <div className="user-details">
                    <h4>{activity.user.name}</h4>
                    <div className="activity-meta">
                      <span>{activity.user.role}</span>
                      <span>•</span>
                      <span>{activity.user.location}</span>
                      <span>•</span>
                      <span>{activity.user.time}</span>
                    </div>
                  </div>
                </div>
                <button className="activity-menu-btn">⋯</button>
              </div>

              <div className="activity-content">
                <p>{activity.content}</p>
                {activity.hashtags.length > 0 && (
                  <div className="activity-hashtags">
                    {activity.hashtags.map((tag, index) => (
                      <span key={index} className="hashtag">#{tag}</span>
                    ))}
                  </div>
                )}
              </div>

              {activity.image && (
                <img src={activity.image} alt="Activity" className="activity-image" />
              )}

              <div className="activity-eco-stats">
                <div className="eco-stat-item">
                  <span>🌱</span>
                  <span className="eco-stat-value">-{activity.eco.carbon}kg CO₂</span>
                  <span className="eco-stat-label">절약</span>
                </div>
                <div className="eco-stat-item">
                  <span>📍</span>
                  <span className="eco-stat-value">{activity.eco.distance}km</span>
                  <span className="eco-stat-label">로컬 거리</span>
                </div>
              </div>

              <div className="activity-interactions">
                <div className="interaction-stats">
                  <span>좋아요 {activity.interactions.likes}</span>
                  <span>댓글 {activity.interactions.comments}</span>
                  <span>공유 {activity.interactions.shares}</span>
                </div>
                <div className="interaction-buttons">
                  <button
                    className={`interaction-btn ${activity.interactions.liked ? 'liked' : ''}`}
                    onClick={() => handleLike(activity.id)}
                  >
                    ❤️ 좋아요
                  </button>
                  <button className="interaction-btn">
                    💬 댓글
                  </button>
                  <button className="interaction-btn">
                    🔗 공유
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Sidebar */}
        <div className="sidebar">
          {/* Challenge Widget */}
          <div className="sidebar-widget challenge-widget">
            <h3 className="widget-title">🎯 탄소 챌린지</h3>
            <div className="challenge-info">
              <h4>로컬푸드 한 달 챌린지</h4>
              <div className="challenge-progress">
                <div className="progress-label">
                  <span>진행률</span>
                  <span>75%</span>
                </div>
                <div className="progress-bar-small">
                  <div className="progress-fill" style={{ width: '75%' }}></div>
                </div>
              </div>
              <div className="challenge-participants">
                <span>👥 156명 참여 중</span>
              </div>
              <button className="btn-join-challenge">챌린지 참여하기</button>
            </div>
          </div>

          {/* Popular Topics Widget */}
          <div className="sidebar-widget topics-widget">
            <h3 className="widget-title">🔥 인기 토픽</h3>
            <ul className="topics-list">
              <li className="topic-item">
                <span className="topic-name">#유기농토마토</span>
                <span className="topic-count">234</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">#로컬푸드</span>
                <span className="topic-count">189</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">#제로웨이스트</span>
                <span className="topic-count">156</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">#농부이야기</span>
                <span className="topic-count">142</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">#친환경요리</span>
                <span className="topic-count">128</span>
              </li>
            </ul>
          </div>

          {/* Eco Stats Widget */}
          <div className="sidebar-widget eco-stats-widget">
            <h3 className="widget-title">🌍 나의 에코 스탯</h3>
            <div className="eco-stats-grid">
              <div className="eco-stat-box">
                <div className="eco-stat-box-value">-12.5kg</div>
                <div className="eco-stat-box-label">탄소 절약</div>
              </div>
              <div className="eco-stat-box">
                <div className="eco-stat-box-value">890pt</div>
                <div className="eco-stat-box-label">에코 포인트</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ActivitiesPage;
