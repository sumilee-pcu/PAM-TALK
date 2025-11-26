# LSTM 수요 예측 모델 사용 가이드

## 개요

LSTM(Long Short-Term Memory) 신경망을 사용한 농산물 수요 예측 시스템입니다.

## 주요 기능

### 1. 학습 데이터 설정
- **학습 기간**: 30일 ~ 365일 자유 설정
- **데이터 특성**: 수요, 가격, 요일, 월, 주말 여부, 공휴일 등
- **제품별 설정**: 각 농산물별 독립적인 파라미터 설정

### 2. 모델 구성
- **LSTM 레이어**: 다층 구조 지원 (기본: [64, 32] 유닛)
- **Dropout**: 과적합 방지 (기본: 0.2)
- **Dense 레이어**: 완전연결층 (기본: 16 유닛)

### 3. 학습 파라미터
- **Batch Size**: 기본 32
- **Epochs**: 최대 100 (Early Stopping 적용)
- **Learning Rate**: 기본 0.001
- **Validation Split**: 20%

## 설정 파일 (`lstm_config.json`)

```json
{
  "model_parameters": {
    "lookback_period": 30,        // 과거 몇 일을 참조할지
    "lstm_units": [64, 32],        // LSTM 레이어 구성
    "dropout_rate": 0.2,           // Dropout 비율
    "dense_units": 16,             // Dense 레이어 유닛 수
    "activation": "relu",          // 활성화 함수
    "output_activation": "linear"  // 출력 활성화 함수
  },

  "training_parameters": {
    "batch_size": 32,              // 배치 크기
    "epochs": 100,                 // 최대 에포크 수
    "validation_split": 0.2,       // 검증 데이터 비율
    "learning_rate": 0.001,        // 학습률
    "early_stopping_patience": 10, // Early Stopping 인내심
    "reduce_lr_patience": 5        // Learning Rate 감소 인내심
  },

  "data_parameters": {
    "training_days": 365,          // 학습 데이터 일수
    "test_split": 0.2,             // 테스트 데이터 비율
    "features": [                  // 사용할 특성들
      "demand",
      "price",
      "day_of_week",
      "month",
      "is_weekend",
      "is_holiday"
    ],
    "target": "demand"             // 예측 대상
  },

  "products": {
    "tomatoes": {
      "base_demand": 1000,         // 기본 수요량
      "seasonal_amplitude": 300,   // 계절성 진폭
      "growth_rate": 0.0005,       // 성장률
      "noise_level": 0.15          // 노이즈 수준
    }
  }
}
```

## 사용 방법

### 1. 기본 사용

```python
from lstm_demand_predictor import LSTMDemandPredictor

# 모델 초기화
predictor = LSTMDemandPredictor()

# 모델 학습
results = predictor.train('tomatoes', save_model=True)

# 예측
predictions = predictor.predict('tomatoes', days_ahead=7)
print(predictions)
```

### 2. 설정 변경

```python
# 학습 데이터 기간 변경
new_config = {
    "data_parameters": {
        "training_days": 180  # 6개월 데이터로 변경
    }
}
predictor.update_config(new_config)

# 모델 파라미터 변경
new_config = {
    "model_parameters": {
        "lstm_units": [128, 64, 32],  # 3층 LSTM으로 변경
        "dropout_rate": 0.3
    }
}
predictor.update_config(new_config)

# 학습 파라미터 변경
new_config = {
    "training_parameters": {
        "batch_size": 64,
        "epochs": 150,
        "learning_rate": 0.0005
    }
}
predictor.update_config(new_config)
```

### 3. 새로운 제품 추가

`lstm_config.json` 파일의 `products` 섹션에 추가:

```json
{
  "products": {
    "새제품명": {
      "base_demand": 500,
      "seasonal_amplitude": 150,
      "growth_rate": 0.0004,
      "noise_level": 0.15,
      "description": "제품 설명"
    }
  }
}
```

### 4. 실제 데이터 사용

현재는 시뮬레이션 데이터를 사용하지만, 실제 데이터로 변경 가능:

```python
# CSV 파일에서 데이터 로드
import pandas as pd

real_data = pd.read_csv('real_demand_data.csv')
# real_data는 다음 컬럼을 포함해야 합니다:
# ['date', 'demand', 'price', 'day_of_week', 'month', 'is_weekend', 'is_holiday']

# 시퀀스 준비 및 학습
X, y = predictor.prepare_sequences(real_data)
# ... 학습 코드
```

## 출력 파일

### 1. 학습된 모델
- 위치: `data/models/lstm_{제품명}.h5`
- 형식: Keras HDF5 모델 파일

### 2. 학습 기록
- 위치: `data/models/lstm_{제품명}_history.json`
- 내용: Loss, MAE, MAPE 등 학습 메트릭

### 3. 학습 차트
- 위치: `data/charts/lstm_training_{제품명}.png`
- 내용: Loss, MAE, MAPE, Learning Rate 그래프

### 4. 예측 결과
- 위치: `data/predictions/lstm_{제품명}_forecast.csv`
- 내용: 날짜별 예측 수요량

## 성능 지표

- **MSE (Mean Squared Error)**: 평균 제곱 오차
- **MAE (Mean Absolute Error)**: 평균 절대 오차
- **MAPE (Mean Absolute Percentage Error)**: 평균 절대 백분율 오차

## 모범 사례

### 1. 학습 데이터 양
- 최소 90일 이상 권장
- 계절성을 고려하려면 365일(1년) 권장
- 더 많은 데이터 = 더 나은 예측 (일반적으로)

### 2. Lookback Period
- 단기 예측(1-7일): 7-14일
- 중기 예측(1-4주): 30-60일
- 장기 예측(1-3개월): 60-90일

### 3. LSTM Units
- 작은 데이터셋: [32, 16]
- 중간 데이터셋: [64, 32]
- 큰 데이터셋: [128, 64, 32]

### 4. Epochs
- Early Stopping을 사용하므로 큰 값 설정 가능
- 일반적으로 50-150 범위
- Validation Loss가 수렴하면 자동 중단

### 5. Learning Rate
- 기본값: 0.001
- 학습이 불안정하면: 0.0005 또는 0.0001
- 학습이 느리면: 0.005 또는 0.01

## 문제 해결

### 1. 과적합 (Overfitting)
**증상**: Training Loss는 낮지만 Validation Loss가 높음

**해결책**:
- Dropout Rate 증가 (0.2 → 0.3 또는 0.4)
- LSTM Units 감소
- Early Stopping Patience 감소
- 더 많은 학습 데이터

### 2. 과소적합 (Underfitting)
**증상**: Training Loss와 Validation Loss 모두 높음

**해결책**:
- LSTM Units 증가
- Lookback Period 증가
- 더 많은 Epochs
- Learning Rate 조정

### 3. 학습이 느림
**해결책**:
- Batch Size 증가
- Learning Rate 증가 (주의: 안정성 감소)
- LSTM Units 감소

### 4. 예측이 부정확함
**해결책**:
- 더 많은 학습 데이터
- Feature 추가 (날씨, 이벤트 등)
- Lookback Period 조정
- 모델 구조 변경 (레이어 추가)

## 고급 사용

### 1. 앙상블 예측
여러 모델의 예측을 결합:

```python
models = []
for i in range(5):
    predictor = LSTMDemandPredictor()
    predictor.train('tomatoes')
    models.append(predictor)

# 각 모델로 예측
predictions = [model.predict('tomatoes', 7) for model in models]

# 평균 예측
ensemble_pred = pd.concat(predictions).groupby('date').mean()
```

### 2. 교차 검증
시계열 데이터에 적합한 교차 검증:

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
# 각 fold에서 학습 및 평가
```

### 3. 하이퍼파라미터 튜닝
최적의 파라미터 찾기:

```python
param_grid = {
    'lstm_units': [[32, 16], [64, 32], [128, 64]],
    'dropout_rate': [0.1, 0.2, 0.3],
    'learning_rate': [0.0001, 0.001, 0.01]
}

# Grid search 또는 Random search
```

## 참고 자료

- TensorFlow/Keras 문서: https://keras.io/
- LSTM 논문: https://www.bioinf.jku.at/publications/older/2604.pdf
- Time Series Forecasting: https://www.tensorflow.org/tutorials/structured_data/time_series

## 라이선스

PAM-TALK 프로젝트의 일부로 제공됩니다.
