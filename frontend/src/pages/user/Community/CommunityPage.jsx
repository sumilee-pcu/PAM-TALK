/**
 * Community Page
 * 커뮤니티 소셜 피드
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../../hooks/useAuth';
import { io } from 'socket.io-client';
import './CommunityPage.css';

function CommunityPage() {
  const { user } = useAuth();
  const [posts, setPosts] = useState([
    {
      id: 1,
      user: { name: '김농부', avatar: '👨‍🌾', location: '경기 용인' },
      time: '2시간 전',
      content: '오늘 첫 토마토 수확! 햇볕 가득 받아 정말 맛있게 자랐어요. 로컬푸드로 탄소발자국도 줄이고 신선한 농산물도 맛보세요 🍅',
      hashtags: ['#로컬푸드', '#토마토', '#신선함'],
      image: null,
      eco: { carbon: 2.1, distance: 15 },
      likes: 24,
      comments: 5,
      shares: 3,
      liked: false
    },
    {
      id: 2,
      user: { name: '이소비자', avatar: '👩', location: '서울 강남' },
      time: '4시간 전',
      content: '오늘 30일 로컬푸드 챌린지 완료! 한 달 동안 지역 농산물만 구매하니 정말 뿌듯하네요. 농부님들 덕분에 신선한 채소 매일 먹었어요 💚',
      hashtags: ['#챌린지완료', '#로컬푸드', '#환경보호'],
      image: null,
      eco: { carbon: 12.5, distance: 8 },
      likes: 42,
      comments: 12,
      shares: 8,
      liked: true
    },
    {
      id: 3,
      user: { name: '박농부', avatar: '👨‍🌾', location: '강원 춘천' },
      time: '6시간 전',
      content: '제철 채소가 정말 최고예요! 노지에서 자란 상추는 맛이 다릅니다. 농약 없이 건강하게 키웠습니다 🥬',
      hashtags: ['#유기농', '#제철채소', '#건강식품'],
      image: null,
      eco: { carbon: 1.8, distance: 45 },
      likes: 18,
      comments: 3,
      shares: 2,
      liked: false
    }
  ]);

  const [newPost, setNewPost] = useState('');
  const [showChatModal, setShowChatModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [newChatMessage, setNewChatMessage] = useState('');
  const [currentRoomId, setCurrentRoomId] = useState(null);
  const socketRef = useRef(null);
  const API_BASE_URL = 'https://web-production-1b6c.up.railway.app';

  // 사용자 역할에 따른 아바타 매핑
  const getRoleAvatar = (role) => {
    const avatars = {
      'CONSUMER': '👤',
      'SUPPLIER': '🏭',
      'COMPANY': '🏢',
      'COMMITTEE': '🎯',
      'ADMIN': '⚙️',
      'FARMER': '👨‍🌾'
    };
    return avatars[role] || '👤';
  };

  // 전체 사용자 목록 (실제로는 API에서 가져와야 함)
  const allUsers = [
    { id: 'consumer', email: 'consumer@pamtalk.com', name: '소비자', role: 'CONSUMER', avatar: '👤' },
    { id: 'supplier', email: 'supplier@pamtalk.com', name: '공급자', role: 'SUPPLIER', avatar: '🏭' },
    { id: 'company', email: 'company@pamtalk.com', name: '기업담당자', role: 'COMPANY', avatar: '🏢' },
    { id: 'committee', email: 'committee@pamtalk.com', name: '위원회', role: 'COMMITTEE', avatar: '🎯' },
    { id: 'farmer1', email: 'farmer@pamtalk.com', name: '농부', role: 'FARMER', avatar: '👨‍🌾' }
  ];

  // 현재 로그인한 사용자를 제외한 활성 사용자 목록
  const getActiveUsers = () => {
    if (!user) return allUsers;

    // 현재 사용자 제외
    const otherUsers = allUsers.filter(u => u.email !== user.email);

    // 역할에 따라 상대방을 맨 위로
    if (user.role === 'CONSUMER') {
      // 소비자가 로그인했으면 공급자를 맨 위로
      return otherUsers.sort((a, b) => {
        if (a.role === 'SUPPLIER') return -1;
        if (b.role === 'SUPPLIER') return 1;
        return 0;
      });
    } else if (user.role === 'SUPPLIER') {
      // 공급자가 로그인했으면 소비자를 맨 위로
      return otherUsers.sort((a, b) => {
        if (a.role === 'CONSUMER') return -1;
        if (b.role === 'CONSUMER') return 1;
        return 0;
      });
    }

    return otherUsers;
  };

  const [activeUsers, setActiveUsers] = useState(getActiveUsers());

  // 사용자 변경 시 활성 사용자 목록 업데이트
  useEffect(() => {
    setActiveUsers(getActiveUsers());
  }, [user]);

  // Socket.IO 연결 초기화
  useEffect(() => {
    if (!socketRef.current) {
      socketRef.current = io(API_BASE_URL, {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
      });

      // 연결 성공
      socketRef.current.on('connect', () => {
        console.log('✅ Socket.IO 연결됨');
      });

      // 연결 실패
      socketRef.current.on('connect_error', (error) => {
        console.error('❌ Socket.IO 연결 실패:', error);
      });

      // 새 메시지 수신
      socketRef.current.on('new_message', (message) => {
        console.log('📨 새 메시지 수신:', message);
        setChatMessages(prev => {
          const messagesWithIsMe = [...prev, {
            ...message,
            isMe: message.user_id === user?.email || message.username === user?.name
          }];
          return messagesWithIsMe;
        });
      });

      // 사용자 입장
      socketRef.current.on('user_joined', (data) => {
        console.log('👋 사용자 입장:', data);
      });

      // 사용자 퇴장
      socketRef.current.on('user_left', (data) => {
        console.log('👋 사용자 퇴장:', data);
      });
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, [user]);

  // 채팅방 나가기 (모달 닫을 때)
  useEffect(() => {
    if (!showChatModal && currentRoomId && socketRef.current) {
      socketRef.current.emit('leave', {
        room_id: currentRoomId,
        username: user?.name || '익명'
      });
      setCurrentRoomId(null);
    }
  }, [showChatModal, currentRoomId, user]);

  const handleLike = (postId) => {
    setPosts(posts.map(post =>
      post.id === postId
        ? { ...post, liked: !post.liked, likes: post.liked ? post.likes - 1 : post.likes + 1 }
        : post
    ));
  };

  const handleCreatePost = () => {
    if (!newPost.trim()) return;

    const post = {
      id: Date.now(),
      user: { name: '나', avatar: '👤', location: '서울' },
      time: '방금 전',
      content: newPost,
      hashtags: [],
      image: null,
      eco: { carbon: 0, distance: 0 },
      likes: 0,
      comments: 0,
      shares: 0,
      liked: false
    };

    setPosts([post, ...posts]);
    setNewPost('');
    alert('게시글이 작성되었습니다! 📝');
  };

  const handleStartChat = async (chatUser) => {
    if (!user) {
      alert('로그인이 필요합니다.');
      return;
    }

    setSelectedUser(chatUser);
    setShowChatModal(true);

    try {
      // 1:1 채팅방 가져오기 또는 생성
      const response = await fetch(`${API_BASE_URL}/api/community/chat/private`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user1_email: user.email,
          user2_email: chatUser.email,
          user1_name: user.name || '나',
          user2_name: chatUser.name
        })
      });

      if (!response.ok) {
        throw new Error('채팅방 생성 실패');
      }

      const result = await response.json();
      if (result.success) {
        const roomId = result.data.room.room_id;
        const messages = result.data.messages || [];

        setCurrentRoomId(roomId);

        // 기존 메시지를 현재 사용자 관점으로 변환
        const messagesWithIsMe = messages.map(msg => ({
          ...msg,
          isMe: msg.user_id === user.email || msg.username === (user.name || '나')
        }));

        setChatMessages(messagesWithIsMe);

        // 소켓으로 채팅방 입장
        if (socketRef.current) {
          socketRef.current.emit('join', {
            room_id: roomId,
            username: user.name || '나'
          });
        }
      }
    } catch (error) {
      console.error('채팅방 로드 실패:', error);
      alert('채팅을 시작할 수 없습니다. 다시 시도해주세요.');
    }
  };

  const handleSendMessage = () => {
    if (!newChatMessage.trim() || !user || !selectedUser || !currentRoomId) return;

    if (!socketRef.current || !socketRef.current.connected) {
      alert('채팅 서버에 연결되지 않았습니다. 잠시 후 다시 시도해주세요.');
      return;
    }

    // SocketIO로 메시지 전송
    socketRef.current.emit('send_message', {
      room_id: currentRoomId,
      user_id: user.email,
      username: user.name || '나',
      content: newChatMessage,
      message_type: 'text'
    });

    setNewChatMessage('');
  };

  return (
    <div className="community-page">
      <div className="community-container">
        {/* Feed Section */}
        <div className="feed-section">
          {/* Create Post */}
          <div className="create-post">
            <div className="create-post-header">
              <div className="user-avatar-small">👤</div>
              <div className="post-input">
                <textarea
                  className="post-textarea"
                  placeholder="농산물 이야기를 공유해보세요..."
                  rows="3"
                  value={newPost}
                  onChange={(e) => setNewPost(e.target.value)}
                />
              </div>
            </div>
            <div className="post-actions">
              <div className="post-options">
                <button className="post-option-btn">
                  <i className="fas fa-image"></i>
                  사진
                </button>
                <button className="post-option-btn">
                  <i className="fas fa-map-marker-alt"></i>
                  위치
                </button>
                <button className="post-option-btn">
                  <i className="fas fa-tag"></i>
                  태그
                </button>
              </div>
              <button className="btn-post" onClick={handleCreatePost}>
                게시
              </button>
            </div>
          </div>

          {/* Feed Posts */}
          {posts.map(post => (
            <div key={post.id} className="feed-post">
              <div className="post-header">
                <div className="post-user-info">
                  <div className="user-avatar-small">{post.user.avatar}</div>
                  <div className="post-user-details">
                    <h4>{post.user.name}</h4>
                    <div className="post-meta">
                      <i className="fas fa-map-marker-alt"></i> {post.user.location} · {post.time}
                    </div>
                  </div>
                </div>
              </div>

              <div className="post-content">
                {post.content}
                {post.hashtags.length > 0 && (
                  <div className="post-hashtags">
                    {post.hashtags.map((tag, idx) => (
                      <span key={idx} className="hashtag">{tag}</span>
                    ))}
                  </div>
                )}
              </div>

              {post.image && (
                <img src={post.image} alt="Post" className="post-image" />
              )}

              <div className="post-eco-stats">
                <div className="eco-stat-item">
                  <i className="fas fa-leaf"></i>
                  <span className="eco-stat-value">-{post.eco.carbon}kg CO₂</span>
                  <span>절약</span>
                </div>
                <div className="eco-stat-item">
                  <i className="fas fa-map-marked-alt"></i>
                  <span className="eco-stat-value">{post.eco.distance}km</span>
                  <span>로컬 거리</span>
                </div>
              </div>

              <div className="post-interactions">
                <div className="interaction-stats">
                  <span>좋아요 {post.likes}</span>
                  <span>댓글 {post.comments}</span>
                  <span>공유 {post.shares}</span>
                </div>
              </div>

              <div className="interaction-buttons">
                <button
                  className={`interaction-btn ${post.liked ? 'liked' : ''}`}
                  onClick={() => handleLike(post.id)}
                >
                  <i className={`${post.liked ? 'fas' : 'far'} fa-heart`}></i>
                  좋아요
                </button>
                <button className="interaction-btn">
                  <i className="far fa-comment"></i>
                  댓글
                </button>
                <button className="interaction-btn">
                  <i className="fas fa-share"></i>
                  공유
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Sidebar */}
        <aside className="sidebar">
          {/* Eco Stats Widget */}
          <div className="sidebar-widget eco-stats-widget">
            <h3 className="widget-title">🌱 나의 에코 통계</h3>
            <div className="eco-stats-grid">
              <div className="eco-stat-box">
                <div className="eco-stat-box-value">-42.5kg</div>
                <div className="eco-stat-box-label">탄소 절약</div>
              </div>
              <div className="eco-stat-box">
                <div className="eco-stat-box-value">1,850</div>
                <div className="eco-stat-box-label">에코 포인트</div>
              </div>
              <div className="eco-stat-box">
                <div className="eco-stat-box-value">12</div>
                <div className="eco-stat-box-label">참여 활동</div>
              </div>
            </div>
          </div>

          {/* Challenge Widget */}
          <div className="sidebar-widget">
            <h3 className="widget-title">🎯 진행 중인 챌린지</h3>
            <div className="challenge-widget-progress">
              <div className="progress-label">
                <span>로컬푸드 30일</span>
                <span>75%</span>
              </div>
              <div className="progress-bar-small">
                <div className="progress-fill" style={{ width: '75%' }}></div>
              </div>
            </div>
            <button className="btn-post" style={{ width: '100%' }}>
              챌린지 보기
            </button>
          </div>

          {/* Popular Topics */}
          <div className="sidebar-widget">
            <h3 className="widget-title">🔥 인기 토픽</h3>
            <ul className="topics-list">
              <li className="topic-item">
                <span className="topic-name">#로컬푸드</span>
                <span className="topic-count">1,234</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">#유기농</span>
                <span className="topic-count">987</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">#제철음식</span>
                <span className="topic-count">756</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">#환경보호</span>
                <span className="topic-count">654</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">#농부직거래</span>
                <span className="topic-count">542</span>
              </li>
            </ul>
          </div>

          {/* Active Users */}
          <div className="sidebar-widget">
            <h3 className="widget-title">💬 활성 사용자</h3>
            <ul className="topics-list">
              {activeUsers.map(user => (
                <li key={user.id} className="topic-item" style={{ cursor: 'pointer' }} onClick={() => handleStartChat(user)}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '20px' }}>{user.avatar}</span>
                    <span className="topic-name">{user.name}</span>
                    <span style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: '#27ae60',
                      marginLeft: 'auto'
                    }}></span>
                  </div>
                </li>
              ))}
            </ul>
            <p style={{
              fontSize: '0.85rem',
              color: '#666',
              marginTop: '10px',
              textAlign: 'center'
            }}>
              클릭하여 채팅 시작
            </p>
          </div>

          {/* Platform Stats */}
          <div className="sidebar-widget">
            <h3 className="widget-title">📊 플랫폼 통계</h3>
            <ul className="topics-list">
              <li className="topic-item">
                <span className="topic-name">총 사용자</span>
                <span className="topic-count">3,247명</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">CO₂ 절약</span>
                <span className="topic-count">125.7톤</span>
              </li>
              <li className="topic-item">
                <span className="topic-name">직거래액</span>
                <span className="topic-count">₩25.8M</span>
              </li>
            </ul>
          </div>
        </aside>
      </div>

      {/* Chat Modal */}
      {showChatModal && selectedUser && (
        <div className="chat-modal-overlay" onClick={() => setShowChatModal(false)}>
          <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
            {/* Chat Header */}
            <div className="chat-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px' }}>{selectedUser.avatar}</span>
                <div>
                  <h3>{selectedUser.name}</h3>
                  <p style={{ fontSize: '0.85rem', color: '#27ae60', margin: 0 }}>● 온라인</p>
                </div>
              </div>
              <button className="chat-close-btn" onClick={() => setShowChatModal(false)}>
                ✕
              </button>
            </div>

            {/* Chat Messages */}
            <div className="chat-messages">
              {chatMessages.length === 0 && (
                <div style={{ textAlign: 'center', color: '#999', padding: '2rem' }}>
                  <p>채팅을 시작해보세요! 💬</p>
                  <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
                    {selectedUser.name}님과 대화를 나눠보세요
                  </p>
                </div>
              )}
              {chatMessages.map((message, index) => (
                <div key={message.message_id || message.id || index} className={`chat-message ${message.isMe ? 'chat-message-me' : 'chat-message-other'}`}>
                  {!message.isMe && (
                    <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.25rem', marginLeft: '0.5rem' }}>
                      {message.username || message.fromName || '익명'}
                    </div>
                  )}
                  <div className="chat-message-bubble">
                    <p>{message.content}</p>
                    <span className="chat-message-time">
                      {message.created_at
                        ? new Date(message.created_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
                        : message.time || ''}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Chat Input */}
            <div className="chat-input-container">
              <input
                type="text"
                className="chat-input"
                placeholder="메시지를 입력하세요..."
                value={newChatMessage}
                onChange={(e) => setNewChatMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              />
              <button className="chat-send-btn" onClick={handleSendMessage}>
                <i className="fas fa-paper-plane"></i>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CommunityPage;
