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
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState('');
  const [showChatModal, setShowChatModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [newChatMessage, setNewChatMessage] = useState('');
  const [currentRoomId, setCurrentRoomId] = useState(null);
  const socketRef = useRef(null);
  const API_BASE_URL = 'https://web-production-1b6c.up.railway.app';

  // 댓글 관련 state
  const [postComments, setPostComments] = useState({}); // { postId: [comments] }
  const [newComment, setNewComment] = useState({}); // { postId: 'comment text' }
  const [showComments, setShowComments] = useState({}); // { postId: true/false }

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

  // 게시물 목록 불러오기
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/community/posts`);
        const result = await response.json();

        if (result.success && result.data) {
          // 백엔드 데이터를 프론트엔드 형식으로 변환
          const formattedPosts = result.data.map(post => ({
            id: post.post_id,
            user: {
              name: post.username,
              avatar: getRoleAvatar('farmer'),
              location: '지역'
            },
            time: new Date(post.created_at).toLocaleString('ko-KR'),
            content: post.content,
            hashtags: post.tags || [],
            image: post.images?.[0] || null,
            eco: { carbon: 0, distance: 0 },
            likes: post.likes_count || 0,
            comments: post.comments_count || 0,
            shares: 0,
            liked: false
          }));
          setPosts(formattedPosts);
        }
      } catch (error) {
        console.error('게시물 로딩 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  const handleLike = async (postId) => {
    if (!user) {
      alert('로그인이 필요합니다.');
      return;
    }

    try {
      const post = posts.find(p => p.id === postId);
      const isLiked = post.liked;

      if (isLiked) {
        // 좋아요 취소
        await fetch(`${API_BASE_URL}/api/community/likes`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: user.email,
            target_type: 'post',
            target_id: postId
          })
        });
      } else {
        // 좋아요 추가
        await fetch(`${API_BASE_URL}/api/community/likes`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: user.email,
            target_type: 'post',
            target_id: postId
          })
        });
      }

      // UI 업데이트
      setPosts(posts.map(p =>
        p.id === postId
          ? { ...p, liked: !p.liked, likes: p.liked ? p.likes - 1 : p.likes + 1 }
          : p
      ));
    } catch (error) {
      console.error('좋아요 처리 실패:', error);
      alert('좋아요 처리 중 오류가 발생했습니다.');
    }
  };

  const handleCreatePost = async () => {
    if (!newPost.trim()) return;
    if (!user) {
      alert('로그인이 필요합니다.');
      return;
    }

    try {
      // 해시태그 추출
      const hashtags = newPost.match(/#[^\s#]+/g) || [];

      const response = await fetch(`${API_BASE_URL}/api/community/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.email,
          username: user.name || '익명',
          content: newPost,
          tags: hashtags,
          category: 'general'
        })
      });

      const result = await response.json();

      if (result.success && result.data) {
        // 새 게시물을 목록 맨 위에 추가
        const newPostData = {
          id: result.data.post_id,
          user: {
            name: result.data.username,
            avatar: getRoleAvatar(user.role),
            location: '지역'
          },
          time: '방금 전',
          content: result.data.content,
          hashtags: result.data.tags || [],
          image: null,
          eco: { carbon: 0, distance: 0 },
          likes: 0,
          comments: 0,
          shares: 0,
          liked: false
        };

        setPosts([newPostData, ...posts]);
        setNewPost('');
        alert('게시글이 작성되었습니다! 📝');
      } else {
        alert('게시글 작성 실패');
      }
    } catch (error) {
      console.error('게시글 작성 실패:', error);
      alert('게시글 작성 중 오류가 발생했습니다.');
    }
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

  // 댓글 토글 및 불러오기
  const handleToggleComments = async (postId) => {
    // 댓글 섹션 토글
    setShowComments(prev => ({
      ...prev,
      [postId]: !prev[postId]
    }));

    // 이미 불러온 댓글이 있으면 API 호출 생략
    if (postComments[postId]) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/community/posts/${postId}/comments`);
      const result = await response.json();

      if (result.success && result.data) {
        setPostComments(prev => ({
          ...prev,
          [postId]: result.data
        }));
      }
    } catch (error) {
      console.error('댓글 로딩 실패:', error);
    }
  };

  // 댓글 작성
  const handleAddComment = async (postId) => {
    if (!user) {
      alert('로그인이 필요합니다.');
      return;
    }

    const commentText = newComment[postId];
    if (!commentText || !commentText.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/community/posts/${postId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.email,
          username: user.name || '익명',
          content: commentText
        })
      });

      const result = await response.json();

      if (result.success && result.data) {
        // 새 댓글을 목록에 추가
        setPostComments(prev => ({
          ...prev,
          [postId]: [...(prev[postId] || []), result.data]
        }));

        // 입력창 초기화
        setNewComment(prev => ({
          ...prev,
          [postId]: ''
        }));

        // 게시물의 댓글 카운트 업데이트
        setPosts(posts.map(p =>
          p.id === postId ? { ...p, comments: p.comments + 1 } : p
        ));
      }
    } catch (error) {
      console.error('댓글 작성 실패:', error);
      alert('댓글 작성 중 오류가 발생했습니다.');
    }
  };

  // 댓글 삭제
  const handleDeleteComment = async (postId, commentId) => {
    if (!user) return;

    if (!window.confirm('댓글을 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/community/comments/${commentId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.email
        })
      });

      const result = await response.json();

      if (result.success) {
        // 댓글 목록에서 제거
        setPostComments(prev => ({
          ...prev,
          [postId]: (prev[postId] || []).filter(c => c.comment_id !== commentId)
        }));

        // 게시물의 댓글 카운트 업데이트
        setPosts(posts.map(p =>
          p.id === postId ? { ...p, comments: Math.max(0, p.comments - 1) } : p
        ));
      }
    } catch (error) {
      console.error('댓글 삭제 실패:', error);
      alert('댓글 삭제 중 오류가 발생했습니다.');
    }
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
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem' }}>
              <p>게시물을 불러오는 중...</p>
            </div>
          ) : posts.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', background: 'white', borderRadius: '15px' }}>
              <p style={{ color: '#666' }}>아직 게시물이 없습니다.</p>
              <p style={{ color: '#666' }}>첫 게시물을 작성해보세요! ✍️</p>
            </div>
          ) : null}

          {!loading && posts.map(post => (
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
                <button
                  className="interaction-btn"
                  onClick={() => handleToggleComments(post.id)}
                >
                  <i className="far fa-comment"></i>
                  댓글 {post.comments > 0 && `(${post.comments})`}
                </button>
                <button className="interaction-btn">
                  <i className="fas fa-share"></i>
                  공유
                </button>
              </div>

              {/* 댓글 섹션 */}
              {showComments[post.id] && (
                <div style={{
                  marginTop: '1rem',
                  paddingTop: '1rem',
                  borderTop: '1px solid #eee'
                }}>
                  {/* 댓글 목록 */}
                  <div style={{ marginBottom: '1rem' }}>
                    {(!postComments[post.id] || postComments[post.id].length === 0) ? (
                      <p style={{
                        textAlign: 'center',
                        color: '#999',
                        fontSize: '0.9rem',
                        padding: '1rem 0'
                      }}>
                        첫 댓글을 작성해보세요!
                      </p>
                    ) : (
                      postComments[post.id].map(comment => (
                        <div
                          key={comment.comment_id}
                          style={{
                            display: 'flex',
                            gap: '0.75rem',
                            marginBottom: '1rem',
                            padding: '0.75rem',
                            background: '#f8f9fa',
                            borderRadius: '10px'
                          }}
                        >
                          <div className="user-avatar-small" style={{
                            width: '35px',
                            height: '35px',
                            fontSize: '1rem',
                            flexShrink: 0
                          }}>
                            👤
                          </div>
                          <div style={{ flex: 1 }}>
                            <div style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'flex-start',
                              marginBottom: '0.25rem'
                            }}>
                              <div>
                                <strong style={{ fontSize: '0.9rem' }}>
                                  {comment.username}
                                </strong>
                                <span style={{
                                  marginLeft: '0.5rem',
                                  color: '#888',
                                  fontSize: '0.75rem'
                                }}>
                                  {new Date(comment.created_at).toLocaleString('ko-KR')}
                                </span>
                              </div>
                              {user && comment.user_id === user.email && (
                                <button
                                  onClick={() => handleDeleteComment(post.id, comment.comment_id)}
                                  style={{
                                    background: 'none',
                                    border: 'none',
                                    color: '#999',
                                    cursor: 'pointer',
                                    fontSize: '0.8rem',
                                    padding: '0.25rem 0.5rem'
                                  }}
                                >
                                  삭제
                                </button>
                              )}
                            </div>
                            <p style={{
                              margin: 0,
                              fontSize: '0.9rem',
                              lineHeight: '1.5'
                            }}>
                              {comment.content}
                            </p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>

                  {/* 댓글 작성 폼 */}
                  <div style={{
                    display: 'flex',
                    gap: '0.75rem',
                    alignItems: 'flex-start'
                  }}>
                    <div className="user-avatar-small" style={{
                      width: '35px',
                      height: '35px',
                      fontSize: '1rem',
                      flexShrink: 0
                    }}>
                      {user ? getRoleAvatar(user.role) : '👤'}
                    </div>
                    <div style={{ flex: 1 }}>
                      <textarea
                        style={{
                          width: '100%',
                          padding: '0.75rem',
                          border: '2px solid #eee',
                          borderRadius: '10px',
                          resize: 'none',
                          fontSize: '0.9rem',
                          fontFamily: 'inherit',
                          minHeight: '60px'
                        }}
                        placeholder="댓글을 입력하세요..."
                        value={newComment[post.id] || ''}
                        onChange={(e) => setNewComment(prev => ({
                          ...prev,
                          [post.id]: e.target.value
                        }))}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleAddComment(post.id);
                          }
                        }}
                      />
                      <button
                        onClick={() => handleAddComment(post.id)}
                        style={{
                          marginTop: '0.5rem',
                          padding: '0.5rem 1.5rem',
                          background: '#27ae60',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '0.9rem',
                          fontWeight: '600'
                        }}
                      >
                        댓글 작성
                      </button>
                    </div>
                  </div>
                </div>
              )}
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
