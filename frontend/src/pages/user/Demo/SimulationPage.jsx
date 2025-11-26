/**
 * Simulation Dashboard Page
 * PAM-TALK 플랫폼 효과 시뮬레이션 대시보드
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SimulationPage.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5002/api';

function SimulationPage() {
  const navigate = useNavigate();
  const [population, setPopulation] = useState(100000);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/simulation/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ population })
      });

      const data = await response.json();
      if (data.success) {
        setResults(data.data.simulation_results);
      } else {
        setError(data.error?.message || '시뮬레이션 실패');
      }
    } catch (err) {
      setError('시뮬레이션 중 오류가 발생했습니다.');
      console.error('Simulation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('ko-KR').format(Math.round(num));
  };

  const renderSummary = () => {
    if (!results) return null;
    const summary = results.summary;

    return (
      <div className="summary-section">
        <h2>시뮬레이션 결과 요약</h2>

        <div className="kpi-grid">
          <div className="kpi-card distribution">
            <div className="kpi-icon">📊</div>
            <div className="kpi-content">
              <h3>유통 효율화</h3>
              <div className="kpi-value">
                {summary.key_metrics.distribution.stage_reduction}
              </div>
              <div className="kpi-label">유통 단계 감축</div>
              <ul className="kpi-details">
                <li>유통 마진: {summary.key_metrics.distribution.margin_reduction} 절감</li>
                <li>생산자 수익: {summary.key_metrics.distribution.producer_price_increase} 증가</li>
                <li>소비자 가격: {summary.key_metrics.distribution.consumer_price_decrease} 하락</li>
              </ul>
            </div>
          </div>

          <div className="kpi-card carbon">
            <div className="kpi-icon">🌱</div>
            <div className="kpi-content">
              <h3>탄소 절감</h3>
              <div className="kpi-value">
                {summary.key_metrics.carbon.total_reduction_ton}톤
              </div>
              <div className="kpi-label">연간 CO₂e 절감</div>
              <ul className="kpi-details">
                <li>절감률: {summary.key_metrics.carbon.reduction_pct}</li>
                <li>환산: 승용차 {summary.key_metrics.carbon.car_equivalent}대 배출량</li>
              </ul>
            </div>
          </div>

          <div className="kpi-card economic">
            <div className="kpi-icon">💰</div>
            <div className="kpi-content">
              <h3>경제 활성화</h3>
              <div className="kpi-value">
                {summary.key_metrics.economic.total_impact_billion}억원
              </div>
              <div className="kpi-label">연간 경제 효과</div>
              <ul className="kpi-details">
                <li>1인당: {formatNumber(summary.key_metrics.economic.per_capita_benefit_krw)}원/년</li>
                <li>고용창출: 약 {summary.key_metrics.economic.jobs_created}명</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="achievements-section">
          <h3>주요 성과</h3>
          <div className="achievements-grid">
            {summary.achievements.map((achievement, index) => (
              <div key={index} className="achievement-card">
                <h4>{achievement.category}</h4>
                <p className="achievement-text">{achievement.achievement}</p>
                <p className="benefit-text">{achievement.benefit}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderDistribution = () => {
    if (!results) return null;
    const dist = results.distribution;

    return (
      <div className="distribution-section">
        <h2>유통 구조 분석</h2>

        <div className="comparison-grid">
          <div className="comparison-card baseline">
            <h3>기준선 (Baseline)</h3>
            <ul>
              <li>유통 단계: {dist.overall.baseline.stages}단계</li>
              <li>평균 마진: {dist.overall.baseline.avg_margin}%</li>
              <li>로컬푸드: {dist.overall.baseline.local_food_ratio}%</li>
              <li>푸드마일리지: {dist.overall.baseline.food_mileage}km</li>
              <li>포장재 사용: {dist.overall.baseline.packaging_rate}%</li>
            </ul>
          </div>

          <div className="comparison-card improved">
            <h3>개선안 (PAM-TALK)</h3>
            <ul>
              <li>유통 단계: {dist.overall.improved.stages}단계</li>
              <li>평균 마진: {dist.overall.improved.avg_margin}%</li>
              <li>로컬푸드: {dist.overall.improved.local_food_ratio}%</li>
              <li>푸드마일리지: {dist.overall.improved.food_mileage}km</li>
              <li>포장재 사용: {dist.overall.improved.packaging_rate}%</li>
            </ul>
          </div>
        </div>

        <div className="product-types-section">
          <h3>농산물 유형별 분석</h3>
          <div className="product-grid">
            {dist.product_types.map((product, index) => (
              <div key={index} className="product-card">
                <h4>{product.name}</h4>
                <div className="product-stats">
                  <div className="stat">
                    <label>유통 마진</label>
                    <div className="stat-change">
                      <span className="old">{product.baseline_margin}%</span>
                      <span className="arrow">→</span>
                      <span className="new">{product.improved_margin}%</span>
                    </div>
                  </div>
                  <div className="stat">
                    <label>생산자 수익</label>
                    <span className="increase">+{product.producer_price_increase}%</span>
                  </div>
                  <div className="stat">
                    <label>소비자 가격</label>
                    <span className="decrease">-{product.consumer_price_decrease}%</span>
                  </div>
                  <div className="stat">
                    <label>거래량</label>
                    <span className="increase">+{product.volume_increase}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderCarbon = () => {
    if (!results) return null;
    const carbon = results.carbon;

    return (
      <div className="carbon-section">
        <h2>탄소 절감 효과</h2>
        <p className="standard-badge">ISO 14067:2018 표준 적용</p>

        <div className="carbon-total">
          <div className="total-box">
            <div className="total-value">{carbon.total.total_reduction_ton}톤 CO₂e</div>
            <div className="total-label">연간 총 탄소 절감</div>
            <div className="total-pct">{carbon.total.reduction_pct}% 감축</div>
          </div>
          <div className="equivalent-box">
            <p>{carbon.total.equivalent.description}</p>
          </div>
        </div>

        <div className="carbon-details">
          {Object.entries(carbon.details).map(([key, detail], index) => (
            <div key={index} className="carbon-item">
              <h4>{detail.category}</h4>
              {key === 'food_mileage' && (
                <div className="carbon-metrics">
                  <div className="metric">
                    <label>운송 거리</label>
                    <span>{detail.baseline.distance_km}km → {detail.improved.distance_km}km</span>
                  </div>
                  <div className="metric highlight">
                    <label>연간 절감</label>
                    <span>{detail.reduction.annual_reduction_ton}톤 CO₂e</span>
                  </div>
                </div>
              )}
              {key === 'packaging' && (
                <div className="carbon-metrics">
                  <div className="metric">
                    <label>사용률</label>
                    <span>{detail.baseline.usage_rate_pct}% → {detail.improved.usage_rate_pct}%</span>
                  </div>
                  <div className="metric highlight">
                    <label>연간 절감</label>
                    <span>{detail.reduction.annual_reduction_ton}톤 CO₂e</span>
                  </div>
                </div>
              )}
              {key === 'esg_activity' && (
                <div className="carbon-metrics">
                  <div className="metric">
                    <label>참여자 증가</label>
                    <span>{detail.reduction.participant_increase}명</span>
                  </div>
                  <div className="metric highlight">
                    <label>연간 절감</label>
                    <span>{detail.reduction.annual_reduction_ton}톤 CO₂e</span>
                  </div>
                </div>
              )}
              {key === 'infrastructure' && (
                <div className="carbon-metrics">
                  <div className="metric">
                    <label>전기차 충전</label>
                    <span>월 {detail.ev_charging.monthly_count}건</span>
                  </div>
                  <div className="metric highlight">
                    <label>연간 절감</label>
                    <span>{detail.total.annual_reduction_ton}톤 CO₂e</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderEconomic = () => {
    if (!results) return null;
    const econ = results.economic;

    return (
      <div className="economic-section">
        <h2>경제적 효과 분석</h2>
        <p className="methodology-badge">{econ.methodology}</p>

        <div className="economic-total">
          <div className="effect-box direct">
            <h3>직접 효과</h3>
            <div className="amount">{econ.total_impact.direct_total_billion}억원</div>
          </div>
          <div className="effect-box indirect">
            <h3>간접 효과</h3>
            <div className="amount">{econ.total_impact.indirect_total_billion}억원</div>
          </div>
          <div className="effect-box total">
            <h3>총 효과</h3>
            <div className="amount">{econ.total_impact.total_impact_billion}억원</div>
          </div>
        </div>

        <div className="direct-effects">
          <h3>직접 효과 상세</h3>
          <div className="effects-grid">
            <div className="effect-card">
              <h4>{econ.direct_effects.local_consumption.description}</h4>
              <p>로컬푸드 비중: {econ.direct_effects.local_consumption.baseline_ratio}% →
                {econ.direct_effects.local_consumption.improved_ratio}%</p>
              <div className="amount-highlight">
                {econ.direct_effects.local_consumption.annual_increase_billion}억원
              </div>
            </div>
            <div className="effect-card">
              <h4>{econ.direct_effects.producer_income.description}</h4>
              <p>수취가격 증가: {econ.direct_effects.producer_income.price_increase_rate}%</p>
              <div className="amount-highlight">
                {econ.direct_effects.producer_income.annual_increase_billion}억원
              </div>
            </div>
            <div className="effect-card">
              <h4>{econ.direct_effects.store_revenue.description}</h4>
              <p>매출 증가율: {econ.direct_effects.store_revenue.revenue_increase_rate}%</p>
              <div className="amount-highlight">
                {econ.direct_effects.store_revenue.annual_increase_billion}억원
              </div>
            </div>
          </div>
        </div>

        <div className="indirect-effects">
          <h3>간접 효과 상세</h3>
          <div className="multipliers">
            <div className="multiplier-item">
              <label>생산 유발 계수</label>
              <span>{econ.multipliers.production}</span>
            </div>
            <div className="multiplier-item">
              <label>부가가치 유발 계수</label>
              <span>{econ.multipliers.value_added}</span>
            </div>
            <div className="multiplier-item">
              <label>고용 유발</label>
              <span>약 {Math.round(econ.total_impact.employment_created)}명</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="simulation-page">
      {/* Header */}
      <header className="sim-header">
        <div className="header-content">
          <button className="btn-back" onClick={() => navigate('/')}>
            ← 홈으로
          </button>
          <div className="header-title">
            <h1>PAM-TALK 플랫폼 효과 시뮬레이션</h1>
            <p>유통/탄소/경제 효과 종합 분석</p>
          </div>
        </div>
      </header>

      {/* Control Panel */}
      <div className="sim-container">
        <div className="control-panel">
          <h2>시뮬레이션 설정</h2>
          <div className="control-group">
            <label>대상 지역 인구</label>
            <input
              type="number"
              value={population}
              onChange={(e) => setPopulation(parseInt(e.target.value))}
              min="10000"
              max="1000000"
              step="10000"
              disabled={loading}
            />
            <span className="unit">명</span>
          </div>

          <button
            className="btn-run"
            onClick={runSimulation}
            disabled={loading}
          >
            {loading ? '시뮬레이션 실행 중...' : '시뮬레이션 실행'}
          </button>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="info-box">
            <h4>시뮬레이션 가정</h4>
            <ul>
              <li>생산자: 100명</li>
              <li>소비자: 2,000명</li>
              <li>가맹점: 30개</li>
              <li>참여 기업: 5개</li>
            </ul>
          </div>
        </div>

        {/* Results Panel */}
        {results && (
          <div className="results-panel">
            <div className="tabs">
              <button
                className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
                onClick={() => setActiveTab('summary')}
              >
                종합 요약
              </button>
              <button
                className={`tab ${activeTab === 'distribution' ? 'active' : ''}`}
                onClick={() => setActiveTab('distribution')}
              >
                유통 구조
              </button>
              <button
                className={`tab ${activeTab === 'carbon' ? 'active' : ''}`}
                onClick={() => setActiveTab('carbon')}
              >
                탄소 절감
              </button>
              <button
                className={`tab ${activeTab === 'economic' ? 'active' : ''}`}
                onClick={() => setActiveTab('economic')}
              >
                경제 효과
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'summary' && renderSummary()}
              {activeTab === 'distribution' && renderDistribution()}
              {activeTab === 'carbon' && renderCarbon()}
              {activeTab === 'economic' && renderEconomic()}
            </div>
          </div>
        )}

        {!results && !loading && (
          <div className="intro-panel">
            <h2>시뮬레이션 소개</h2>
            <p>
              PAM-TALK 플랫폼 도입 효과를 정량적으로 분석하는 시뮬레이션입니다.
              실제 지역 농산물 유통 데이터, 선행 연구, 환경부 배출 계수를 기반으로
              1년 단위 효과를 산정합니다.
            </p>
            <div className="intro-features">
              <div className="feature">
                <h3>📊 유통 구조 분석</h3>
                <p>5단계 유통을 2단계로 단축, 유통 마진 30%p 절감</p>
              </div>
              <div className="feature">
                <h3>🌱 탄소 절감 효과</h3>
                <p>ISO 14067:2018 표준 적용, 연간 166톤 CO₂e 절감</p>
              </div>
              <div className="feature">
                <h3>💰 경제 활성화</h3>
                <p>산업연관분석, 연간 71.2억원 경제적 효과</p>
              </div>
              <div className="feature">
                <h3>🤖 LSTM 수요 예측</h3>
                <p>85% 정확도, 재고 비용 18% 절감, 폐기율 27% 감소</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SimulationPage;
