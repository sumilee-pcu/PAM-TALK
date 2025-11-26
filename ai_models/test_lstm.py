#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LSTM Demand Predictor Test Script

Quick test script to verify LSTM model functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_models.lstm_demand_predictor import LSTMDemandPredictor
import pandas as pd
import matplotlib.pyplot as plt

def test_basic_training():
    """Test basic LSTM training"""
    print("\n" + "="*70)
    print("TEST 1: 기본 LSTM 학습 테스트")
    print("="*70)

    predictor = LSTMDemandPredictor()

    # Train with minimal epochs for quick testing
    predictor.config['training_parameters']['epochs'] = 10
    predictor.config['data_parameters']['training_days'] = 90

    results = predictor.train('tomatoes', save_model=True)

    print(f"\n✅ 테스트 완료!")
    print(f"   - Test Loss: {results['test_loss']:.2f}")
    print(f"   - Test MAE: {results['test_mae']:.2f}")
    print(f"   - Test MAPE: {results['test_mape']:.2f}%")

    return results


def test_prediction():
    """Test prediction functionality"""
    print("\n" + "="*70)
    print("TEST 2: 예측 기능 테스트")
    print("="*70)

    predictor = LSTMDemandPredictor()

    # Make predictions
    predictions = predictor.predict('tomatoes', days_ahead=14)

    print("\n📊 향후 14일 수요 예측:")
    print(predictions.to_string(index=False))

    # Plot predictions
    plt.figure(figsize=(12, 6))
    plt.plot(predictions['date'], predictions['predicted_demand'], marker='o')
    plt.title('LSTM Demand Forecast - Tomatoes (14 days)')
    plt.xlabel('Date')
    plt.ylabel('Predicted Demand (kg)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    chart_file = 'data/charts/lstm_test_forecast.png'
    plt.savefig(chart_file, dpi=150, bbox_inches='tight')
    print(f"\n💾 예측 차트 저장: {chart_file}")
    plt.close()

    return predictions


def test_config_update():
    """Test configuration update"""
    print("\n" + "="*70)
    print("TEST 3: 설정 변경 테스트")
    print("="*70)

    predictor = LSTMDemandPredictor()

    print("\n📋 기본 설정:")
    print(f"   - Lookback Period: {predictor.config['model_parameters']['lookback_period']}")
    print(f"   - LSTM Units: {predictor.config['model_parameters']['lstm_units']}")
    print(f"   - Batch Size: {predictor.config['training_parameters']['batch_size']}")

    # Update configuration
    new_config = {
        "model_parameters": {
            "lookback_period": 14,
            "lstm_units": [32, 16]
        },
        "training_parameters": {
            "batch_size": 16,
            "epochs": 5
        }
    }

    predictor.update_config(new_config)

    print("\n📋 변경된 설정:")
    print(f"   - Lookback Period: {predictor.config['model_parameters']['lookback_period']}")
    print(f"   - LSTM Units: {predictor.config['model_parameters']['lstm_units']}")
    print(f"   - Batch Size: {predictor.config['training_parameters']['batch_size']}")

    print("\n✅ 설정 변경 성공!")


def test_multiple_products():
    """Test training for multiple products"""
    print("\n" + "="*70)
    print("TEST 4: 다중 제품 학습 테스트")
    print("="*70)

    predictor = LSTMDemandPredictor()

    # Quick training for multiple products
    predictor.config['training_parameters']['epochs'] = 5
    predictor.config['data_parameters']['training_days'] = 60

    products = ['tomatoes', 'cabbage', 'rice']
    results = {}

    for product in products:
        print(f"\n{'='*60}")
        print(f"학습 중: {product}")
        print('='*60)

        result = predictor.train(product, save_model=True)
        results[product] = result

    print("\n" + "="*70)
    print("📊 다중 제품 학습 결과 요약")
    print("="*70)

    summary_df = pd.DataFrame([
        {
            'Product': product,
            'Test Loss': result['test_loss'],
            'Test MAE': result['test_mae'],
            'Test MAPE': result['test_mape'],
            'Epochs': result['epochs_trained']
        }
        for product, result in results.items()
    ])

    print("\n" + summary_df.to_string(index=False))

    # Save summary
    summary_file = 'data/predictions/lstm_multi_product_summary.csv'
    summary_df.to_csv(summary_file, index=False)
    print(f"\n💾 요약 저장: {summary_file}")


def test_data_generation():
    """Test data generation"""
    print("\n" + "="*70)
    print("TEST 5: 학습 데이터 생성 테스트")
    print("="*70)

    predictor = LSTMDemandPredictor()

    # Generate data
    data = predictor.generate_training_data('tomatoes')

    print(f"\n✅ 데이터 생성 완료:")
    print(f"   - 총 일수: {len(data)}")
    print(f"   - 컬럼: {list(data.columns)}")
    print(f"\n📊 통계:")
    print(data[['demand', 'price']].describe())

    # Plot data
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))

    # Demand
    axes[0].plot(data['date'], data['demand'])
    axes[0].set_title('Synthetic Demand Data - Tomatoes')
    axes[0].set_xlabel('Date')
    axes[0].set_ylabel('Demand (kg)')
    axes[0].grid(True, alpha=0.3)

    # Price
    axes[1].plot(data['date'], data['price'])
    axes[1].set_title('Synthetic Price Data - Tomatoes')
    axes[1].set_xlabel('Date')
    axes[1].set_ylabel('Price (PAMT/kg)')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()

    chart_file = 'data/charts/lstm_test_data.png'
    plt.savefig(chart_file, dpi=150, bbox_inches='tight')
    print(f"\n💾 데이터 차트 저장: {chart_file}")
    plt.close()


def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀"*35)
    print("LSTM Demand Predictor - 전체 테스트 실행")
    print("🚀"*35)

    try:
        # Test 1: Basic training
        test_basic_training()

        # Test 2: Prediction
        test_prediction()

        # Test 3: Config update
        test_config_update()

        # Test 4: Data generation
        test_data_generation()

        # Test 5: Multiple products (optional, takes longer)
        # test_multiple_products()

        print("\n" + "="*70)
        print("✅ 모든 테스트 완료!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("data/models", exist_ok=True)
    os.makedirs("data/predictions", exist_ok=True)
    os.makedirs("data/charts", exist_ok=True)

    # Run tests
    run_all_tests()
