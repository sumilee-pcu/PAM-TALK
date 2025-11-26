/**
 * LSTM Demand Prediction Demo Page
 * LSTM 수요 예측 시연 페이지
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LSTMDemoPage.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5002/api';

function LSTMDemoPage() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('tomatoes');
  const [daysAhead, setDaysAhead] = useState(7);
  const [predictions, setPredictions] = useState([]);
  const [trainingResults, setTrainingResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState(null);

  // 제품 목록 로드
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_URL}/lstm/products`);
      const data = await response.json();
      if (data.success) {
        setProducts(data.data.products);
      }
    } catch (err) {
      console.error('제품 목록 로드 실패:', err);
    }
  };

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/lstm/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product: selectedProduct,
          days_ahead: daysAhead
        })
      });

      const data = await response.json();
      if (data.success) {
        setPredictions(data.data.predictions);
      } else {
        setError(data.error?.message || '예측 실패');
      }
    } catch (err) {
      setError('예측 중 오류가 발생했습니다.');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/lstm/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product: selectedProduct,
          epochs: 20,
          training_days: 90
        })
      });

      const data = await response.json();
      if (data.success) {
        setTrainingResults(data.data.training_results);
        alert('모델 학습이 완료되었습니다!');
      } else {
        setError(data.error?.message || '학습 실패');
      }
    } catch (err) {
      setError('학습 중 오류가 발생했습니다.');
      console.error('Training error:', err);
    } finally {
      setTraining(false);
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('ko-KR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(num);
  };

  const getProductInfo = () => {
    return products.find(p => p.name === selectedProduct);
  };

  return (
    <div className="lstm-demo-page">
      {/* Header */}
      <header className="demo-header">
        <div className="header-content">
          <button className="btn-back" onClick={() => navigate('/')}>
            ← 홈으로
          </button>
          <div className="header-title">
            <h1>LSTM 수요 예측 시스템</h1>
            <p>딥러닝 기반 농산물 수요 예측 데모</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="demo-container">
        {/* Control Panel */}
        <div className="control-panel">
          <h2>예측 설정</h2>

          <div className="control-group">
            <label>제품 선택</label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              disabled={loading || training}
            >
              {products.map(product => (
                <option key={product.name} value={product.name}>
                  {product.description || product.name}
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label>예측 기간 (일)</label>
            <select
              value={daysAhead}
              onChange={(e) => setDaysAhead(parseInt(e.target.value))}
              disabled={loading || training}
            >
              <option value={7}>7일</option>
              <option value={14}>14일</option>
              <option value={30}>30일</option>
            </select>
          </div>

          {getProductInfo() && (
            <div className="product-info">
              <h3>제품 정보</h3>
              <p><strong>설명:</strong> {getProductInfo().description}</p>
              <p><strong>기본 수요:</strong> {formatNumber(getProductInfo().base_demand)} kg</p>
            </div>
          )}

          <div className="control-actions">
            <button
              className="btn-predict"
              onClick={handlePredict}
              disabled={loading || training}
            >
              {loading ? '예측 중...' : '수요 예측 실행'}
            </button>
            <button
              className="btn-train"
              onClick={handleTrain}
              disabled={loading || training}
            >
              {training ? '학습 중...' : '모델 재학습'}
            </button>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="results-panel">
          {/* Predictions */}
          {predictions.length > 0 && (
            <div className="predictions-section">
              <h2>예측 결과</h2>
              <div className="predictions-chart">
                {predictions.map((pred, idx) => (
                  <div key={idx} className="prediction-bar">
                    <div className="prediction-date">
                      {new Date(pred.date).toLocaleDateString('ko-KR', {
                        month: 'short',
                        day: 'numeric'
                      })}
                    </div>
                    <div className="bar-container">
                      <div
                        className="bar-fill"
                        style={{
                          width: `${(pred.predicted_demand / Math.max(...predictions.map(p => p.predicted_demand))) * 100}%`
                        }}
                      >
                        <span className="bar-value">
                          {formatNumber(pred.predicted_demand)} kg
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="predictions-table">
                <table>
                  <thead>
                    <tr>
                      <th>날짜</th>
                      <th>예측 수요 (kg)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {predictions.map((pred, idx) => (
                      <tr key={idx}>
                        <td>{new Date(pred.date).toLocaleDateString('ko-KR')}</td>
                        <td>{formatNumber(pred.predicted_demand)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Training Results */}
          {trainingResults && (
            <div className="training-section">
              <h2>학습 결과</h2>
              <div className="training-metrics">
                <div className="metric-card">
                  <div className="metric-label">Test Loss (MSE)</div>
                  <div className="metric-value">{trainingResults.test_loss.toFixed(4)}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Test MAE</div>
                  <div className="metric-value">{trainingResults.test_mae.toFixed(4)}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Test MAPE</div>
                  <div className="metric-value">{trainingResults.test_mape.toFixed(2)}%</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Epochs</div>
                  <div className="metric-value">{trainingResults.epochs_trained}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Training Time</div>
                  <div className="metric-value">{trainingResults.training_time.toFixed(1)}s</div>
                </div>
              </div>
            </div>
          )}

          {/* Info Section */}
          {predictions.length === 0 && !trainingResults && (
            <div className="info-section">
              <h2>LSTM 수요 예측이란?</h2>
              <p>
                LSTM(Long Short-Term Memory)은 시계열 데이터 예측에 특화된
                딥러닝 신경망입니다. 과거 수요 패턴을 학습하여 미래 수요를
                예측합니다.
              </p>
              <h3>주요 특징</h3>
              <ul>
                <li>계절성 및 추세 패턴 자동 학습</li>
                <li>여러 특성을 동시에 고려 (가격, 요일, 공휴일 등)</li>
                <li>장기 의존성 포착 가능</li>
                <li>실시간 예측 및 모델 업데이트</li>
              </ul>
              <h3>사용 방법</h3>
              <ol>
                <li>왼쪽에서 제품과 예측 기간을 선택하세요</li>
                <li>"수요 예측 실행" 버튼을 클릭하세요</li>
                <li>예측 결과가 차트와 표로 표시됩니다</li>
                <li>"모델 재학습" 버튼으로 모델을 재학습할 수 있습니다</li>
              </ol>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default LSTMDemoPage;
