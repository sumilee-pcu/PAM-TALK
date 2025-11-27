import React, { useState, useEffect } from 'react';
import './MatchingPage.css';

const MatchingPage = () => {
  const [userType, setUserType] = useState('consumer'); // 'consumer' or 'farmer'
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState([]);
  const [formData, setFormData] = useState({
    // Consumer fields
    product_types: [],
    farming_method: 'organic',
    max_distance_km: 50,
    max_price_per_kg: 6000,
    min_esg_score: 70,
    certifications_required: [],

    // Farmer fields (if needed)
    crop_types: [],
    available_quantity: 0,
    price_min: 0,
    price_max: 10000
  });

  const productOptions = [
    { value: 'tomato', label: '토마토' },
    { value: 'lettuce', label: '상추' },
    { value: 'cucumber', label: '오이' },
    { value: 'apple', label: '사과' },
    { value: 'pear', label: '배' },
    { value: 'rice', label: '쌀' },
    { value: 'corn', label: '옥수수' }
  ];

  const certificationOptions = [
    { value: 'organic', label: '유기농 인증' },
    { value: 'gmo_free', label: 'Non-GMO' },
    { value: 'sustainable', label: '지속가능농업' },
    { value: 'carbon_neutral', label: '탄소중립' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const toggleArrayItem = (field, value) => {
    setFormData(prev => {
      const array = prev[field] || [];
      const newArray = array.includes(value)
        ? array.filter(item => item !== value)
        : [...array, value];
      return { ...prev, [field]: newArray };
    });
  };

  const findMatches = async () => {
    setLoading(true);

    try {
      const token = localStorage.getItem('pam_token');
      const userInfo = JSON.parse(localStorage.getItem('user') || '{}');

      // Get user's location (would normally come from profile)
      const latitude = 37.4979; // Seoul Gangnam (example)
      const longitude = 127.0276;

      const requestBody = {
        consumer_id: userInfo.id || 'C001',
        consumer_name: userInfo.name || '사용자',
        region: '서울',
        latitude,
        longitude,
        preferences: {
          product_types: formData.product_types,
          farming_method: formData.farming_method,
          max_distance_km: formData.max_distance_km,
          max_price_per_kg: formData.max_price_per_kg,
          min_esg_score: formData.min_esg_score,
          certifications_required: formData.certifications_required
        },
        top_n: 10
      };

      const response = await fetch('http://localhost:5002/api/matching/find-farmers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (data.success) {
        setMatches(data.data.matches || []);
      } else {
        alert('매칭 실패: ' + (data.error?.message || '알 수 없는 오류'));
      }
    } catch (error) {
      console.error('Matching error:', error);
      alert('매칭 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#27ae60';
    if (score >= 60) return '#f39c12';
    return '#e74c3c';
  };

  const getMethodBadge = (method) => {
    const badges = {
      'organic': { text: '유기농', color: '#27ae60' },
      'sustainable': { text: '지속가능', color: '#3498db' },
      'conventional': { text: '일반', color: '#95a5a6' }
    };
    return badges[method] || badges.conventional;
  };

  return (
    <div className="matching-page">
      <div className="matching-container">
        {/* Header */}
        <div className="matching-header">
          <h1>🔍 스마트 매칭</h1>
          <p>AI 기반 농부-소비자 최적 매칭 시스템</p>
        </div>

        {/* Preferences Form */}
        <div className="matching-form-card">
          <h2>매칭 조건 설정</h2>

          {/* Product Types */}
          <div className="form-group">
            <label>원하는 농산물</label>
            <div className="checkbox-grid">
              {productOptions.map(option => (
                <div
                  key={option.value}
                  className={`checkbox-item ${formData.product_types.includes(option.value) ? 'checked' : ''}`}
                  onClick={() => toggleArrayItem('product_types', option.value)}
                >
                  <span className="checkbox-icon">
                    {formData.product_types.includes(option.value) ? '✓' : ''}
                  </span>
                  <span>{option.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Farming Method */}
          <div className="form-group">
            <label>선호 재배 방식</label>
            <select
              value={formData.farming_method}
              onChange={(e) => handleInputChange('farming_method', e.target.value)}
            >
              <option value="organic">유기농</option>
              <option value="sustainable">지속가능농업</option>
              <option value="conventional">일반농법</option>
            </select>
          </div>

          {/* Distance Range */}
          <div className="form-group">
            <label>최대 거리: {formData.max_distance_km}km</label>
            <input
              type="range"
              min="10"
              max="200"
              value={formData.max_distance_km}
              onChange={(e) => handleInputChange('max_distance_km', parseInt(e.target.value))}
            />
            <div className="range-labels">
              <span>10km</span>
              <span>200km</span>
            </div>
          </div>

          {/* Price Range */}
          <div className="form-group">
            <label>최대 가격: {formData.max_price_per_kg.toLocaleString()}원/kg</label>
            <input
              type="range"
              min="1000"
              max="20000"
              step="500"
              value={formData.max_price_per_kg}
              onChange={(e) => handleInputChange('max_price_per_kg', parseInt(e.target.value))}
            />
            <div className="range-labels">
              <span>1,000원</span>
              <span>20,000원</span>
            </div>
          </div>

          {/* ESG Score */}
          <div className="form-group">
            <label>최소 ESG 점수: {formData.min_esg_score}점</label>
            <input
              type="range"
              min="0"
              max="100"
              value={formData.min_esg_score}
              onChange={(e) => handleInputChange('min_esg_score', parseInt(e.target.value))}
            />
            <div className="range-labels">
              <span>0점</span>
              <span>100점</span>
            </div>
          </div>

          {/* Certifications */}
          <div className="form-group">
            <label>필수 인증서</label>
            <div className="checkbox-grid">
              {certificationOptions.map(option => (
                <div
                  key={option.value}
                  className={`checkbox-item ${formData.certifications_required.includes(option.value) ? 'checked' : ''}`}
                  onClick={() => toggleArrayItem('certifications_required', option.value)}
                >
                  <span className="checkbox-icon">
                    {formData.certifications_required.includes(option.value) ? '✓' : ''}
                  </span>
                  <span>{option.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            className="find-matches-btn"
            onClick={findMatches}
            disabled={loading}
          >
            {loading ? '매칭 중...' : '🔍 농부 찾기'}
          </button>
        </div>

        {/* Results */}
        {matches.length > 0 && (
          <div className="matching-results">
            <h2>매칭 결과 ({matches.length}명)</h2>

            <div className="matches-grid">
              {matches.map((match, index) => (
                <div key={index} className="match-card">
                  {/* Match Score Badge */}
                  <div className="match-score-badge" style={{ backgroundColor: getScoreColor(match.match_score) }}>
                    {match.match_score}점
                  </div>

                  {/* Farmer Info */}
                  <div className="match-header">
                    <div className="farmer-avatar">
                      {match.farmer_name.charAt(0)}
                    </div>
                    <div className="farmer-info">
                      <h3>{match.farmer_name}</h3>
                      <p className="farmer-id">ID: {match.farmer_id}</p>
                    </div>
                  </div>

                  {/* Match Details */}
                  <div className="match-details">
                    <div className="detail-row">
                      <span className="detail-icon">📍</span>
                      <span>거리: {match.distance_km}km</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-icon">💡</span>
                      <span>{match.reason}</span>
                    </div>
                  </div>

                  {/* Score Breakdown */}
                  <div className="score-breakdown">
                    <h4>상세 점수</h4>
                    <div className="score-bars">
                      {Object.entries(match.breakdown).map(([key, value]) => (
                        <div key={key} className="score-bar-item">
                          <div className="score-label">
                            <span>{getScoreLabelKorean(key)}</span>
                            <span>{value.toFixed(0)}점</span>
                          </div>
                          <div className="score-bar">
                            <div
                              className="score-bar-fill"
                              style={{
                                width: `${value}%`,
                                backgroundColor: getScoreColor(value)
                              }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="match-actions">
                    <button className="btn-view-profile">프로필 보기</button>
                    <button className="btn-contact">연락하기</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Results */}
        {!loading && matches.length === 0 && (
          <div className="no-results">
            <p>🔍 조건에 맞는 농부를 찾아보세요!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function
function getScoreLabelKorean(key) {
  const labels = {
    'distance': '거리',
    'price': '가격',
    'esg_score': 'ESG 점수',
    'farming_method': '재배 방식',
    'product_match': '제품 일치도',
    'certification': '인증서'
  };
  return labels[key] || key;
}

export default MatchingPage;
