/**
 * User Profile Page
 * 사용자 프로필 관리 페이지
 */

import React, { useState, useEffect } from 'react';
import './ProfilePage.css';

function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    name: '',
    nickname: '',
    email: '',
    phone: '',
    bio: '',
    location: '',
    profileImage: null
  });
  const [tempData, setTempData] = useState({...profileData});
  const [imagePreview, setImagePreview] = useState(null);

  // 컴포넌트 마운트 시 저장된 프로필 로드
  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = () => {
    const savedProfile = localStorage.getItem('user_profile');
    if (savedProfile) {
      const profile = JSON.parse(savedProfile);
      setProfileData(profile);
      setTempData(profile);
      if (profile.profileImage) {
        setImagePreview(profile.profileImage);
      }
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    setTempData({...profileData});
  };

  const handleCancel = () => {
    setIsEditing(false);
    setTempData({...profileData});
    setImagePreview(profileData.profileImage);
  };

  const handleSave = () => {
    setProfileData(tempData);
    localStorage.setItem('user_profile', JSON.stringify(tempData));
    setIsEditing(false);
    alert('✅ 프로필이 저장되었습니다!');
  };

  const handleInputChange = (field, value) => {
    setTempData({
      ...tempData,
      [field]: value
    });
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // 파일 크기 체크 (5MB 제한)
      if (file.size > 5 * 1024 * 1024) {
        alert('❌ 이미지 크기는 5MB 이하여야 합니다.');
        return;
      }

      // 이미지 파일 타입 체크
      if (!file.type.startsWith('image/')) {
        alert('❌ 이미지 파일만 업로드 가능합니다.');
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
        setTempData({
          ...tempData,
          profileImage: reader.result
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setImagePreview(null);
    setTempData({
      ...tempData,
      profileImage: null
    });
  };

  const getInitials = () => {
    if (profileData.name) {
      return profileData.name.charAt(0).toUpperCase();
    }
    if (profileData.nickname) {
      return profileData.nickname.charAt(0).toUpperCase();
    }
    return '👤';
  };

  return (
    <div className="profile-page">
      <div className="profile-container">
        {/* 헤더 */}
        <div className="profile-header">
          <h1>프로필</h1>
          <p>개인 정보를 관리하고 수정하세요</p>
        </div>

        {/* 프로필 카드 */}
        <div className="profile-card">
          {/* 프로필 이미지 섹션 */}
          <div className="profile-image-section">
            <div className="profile-image-container">
              {imagePreview ? (
                <img src={imagePreview} alt="프로필" className="profile-image" />
              ) : (
                <div className="profile-image-placeholder">
                  <div className="placeholder-icon">
                    <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="12" cy="8" r="4" fill="currentColor" opacity="0.3"/>
                      <path d="M4 20C4 16.6863 6.68629 14 10 14H14C17.3137 14 20 16.6863 20 20V21H4V20Z" fill="currentColor" opacity="0.3"/>
                    </svg>
                  </div>
                  {!isEditing && (
                    <div className="placeholder-hint">사진 없음</div>
                  )}
                </div>
              )}

              {isEditing && (
                <div className="image-actions">
                  <label htmlFor="image-upload" className="btn-image-upload">
                    📷 {imagePreview ? '사진 변경' : '사진 추가'}
                    <input
                      id="image-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      style={{ display: 'none' }}
                    />
                  </label>
                  {imagePreview && (
                    <button onClick={removeImage} className="btn-image-remove">
                      🗑️ 삭제
                    </button>
                  )}
                </div>
              )}
            </div>

            <div className="profile-image-info">
              <h3>{profileData.name || profileData.nickname || '사용자'}</h3>
              <p>{profileData.email || '이메일을 추가하세요'}</p>
            </div>
          </div>

          {/* 프로필 정보 섹션 */}
          <div className="profile-info-section">
            <div className="section-header">
              <h2>기본 정보</h2>
              {!isEditing ? (
                <button onClick={handleEdit} className="btn-edit">
                  ✏️ 수정
                </button>
              ) : (
                <div className="edit-actions">
                  <button onClick={handleCancel} className="btn-cancel">
                    취소
                  </button>
                  <button onClick={handleSave} className="btn-save">
                    💾 저장
                  </button>
                </div>
              )}
            </div>

            <div className="profile-fields">
              {/* 이름 */}
              <div className="field-group">
                <label>이름</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={tempData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="이름을 입력하세요"
                    className="field-input"
                  />
                ) : (
                  <div className="field-value">
                    {profileData.name || <span className="placeholder">이름을 추가하세요</span>}
                  </div>
                )}
              </div>

              {/* 닉네임 */}
              <div className="field-group">
                <label>닉네임</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={tempData.nickname}
                    onChange={(e) => handleInputChange('nickname', e.target.value)}
                    placeholder="닉네임을 입력하세요"
                    className="field-input"
                  />
                ) : (
                  <div className="field-value">
                    {profileData.nickname || <span className="placeholder">닉네임을 추가하세요</span>}
                  </div>
                )}
              </div>

              {/* 이메일 */}
              <div className="field-group">
                <label>이메일</label>
                {isEditing ? (
                  <input
                    type="email"
                    value={tempData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    placeholder="example@email.com"
                    className="field-input"
                  />
                ) : (
                  <div className="field-value">
                    {profileData.email || <span className="placeholder">이메일을 추가하세요</span>}
                  </div>
                )}
              </div>

              {/* 전화번호 */}
              <div className="field-group">
                <label>전화번호 <span className="optional">(선택)</span></label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={tempData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    placeholder="010-1234-5678"
                    className="field-input"
                  />
                ) : (
                  <div className="field-value">
                    {profileData.phone || <span className="placeholder">전화번호를 추가하세요</span>}
                  </div>
                )}
              </div>

              {/* 위치 */}
              <div className="field-group">
                <label>위치 <span className="optional">(선택)</span></label>
                {isEditing ? (
                  <input
                    type="text"
                    value={tempData.location}
                    onChange={(e) => handleInputChange('location', e.target.value)}
                    placeholder="서울특별시 강남구"
                    className="field-input"
                  />
                ) : (
                  <div className="field-value">
                    {profileData.location || <span className="placeholder">위치를 추가하세요</span>}
                  </div>
                )}
              </div>

              {/* 자기소개 */}
              <div className="field-group">
                <label>자기소개 <span className="optional">(선택)</span></label>
                {isEditing ? (
                  <textarea
                    value={tempData.bio}
                    onChange={(e) => handleInputChange('bio', e.target.value)}
                    placeholder="자기소개를 입력하세요..."
                    className="field-textarea"
                    rows="4"
                  />
                ) : (
                  <div className="field-value bio">
                    {profileData.bio || <span className="placeholder">자기소개를 추가하세요</span>}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 안내 정보 */}
          <div className="profile-info-box">
            <div className="info-icon">💡</div>
            <div className="info-content">
              <h4>프로필 정보 안내</h4>
              <ul>
                <li>프로필 사진은 5MB 이하의 이미지 파일만 업로드 가능합니다</li>
                <li>모든 정보는 안전하게 저장되며, 언제든지 수정할 수 있습니다</li>
                <li>필수 항목: 이름, 닉네임, 이메일</li>
                <li>선택 항목: 전화번호, 위치, 자기소개</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
