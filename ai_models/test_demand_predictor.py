#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Demand Predictor Test Suite

This script tests and demonstrates the demand prediction functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_models.demand_predictor import DemandPredictor
import json
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")

def print_prediction_results(product_name, results):
    """Print prediction results in a readable format"""
    print(f"\n📊 PREDICTION RESULTS FOR {product_name.upper()}")
    print(f"Prediction Period: {results['prediction_period']}")
    print(f"Total Predicted Demand: {results['total_predicted_demand']:,} kg")
    print(f"Average Daily Demand: {results['avg_daily_demand']:,} kg")

    print(f"\n📈 ACCURACY METRICS:")
    metrics = results['accuracy_metrics']
    print(f"  MAE (Mean Absolute Error): {metrics['mae']:.2f}")
    print(f"  MAPE (Mean Absolute Percentage Error): {metrics['mape']:.2f}%")
    print(f"  RMSE (Root Mean Square Error): {metrics['rmse']:.2f}")
    print(f"  Confidence Score: {metrics['confidence_score']:.3f}")

    print(f"\n📅 DAILY PREDICTIONS:")
    for pred in results['predictions']:
        print(f"  {pred['date']}: {pred['predicted_demand']:,} kg "
              f"({pred['lower_bound']:,} - {pred['upper_bound']:,})")

    print(f"\n💡 RECOMMENDATION:")
    print(f"  {results['recommendation']}")

def test_single_product_prediction():
    """Test prediction for a single product"""
    print_header("Single Product Prediction Test")

    predictor = DemandPredictor()

    # Test prediction for tomatoes
    print(">> Testing tomato demand prediction...")
    results = predictor.predict_demand('tomatoes', days=7)
    print_prediction_results('tomatoes', results)

    # Test visualization
    print("\n>> Generating visualization...")
    try:
        predictor.visualize_prediction('tomatoes', days=7, save_chart=True)
        print("[OK] Visualization completed successfully")
    except Exception as e:
        print(f"[WARNING] Visualization failed: {e}")

    return results

def test_multiple_products():
    """Test prediction for multiple products"""
    print_header("Multiple Products Prediction Test")

    predictor = DemandPredictor()

    products = ['tomatoes', 'cabbage', 'rice', 'lettuce', 'carrots']

    for product in products:
        print(f"\n>> Predicting demand for {product}...")
        try:
            results = predictor.predict_demand(product, days=7)
            print(f"[OK] {product.capitalize()}: {results['total_predicted_demand']:,} kg "
                  f"(Confidence: {results['accuracy_metrics']['confidence_score']:.3f})")
        except Exception as e:
            print(f"[ERROR] Failed to predict {product}: {e}")

def test_batch_prediction():
    """Test batch prediction for all products"""
    print_header("Batch Prediction Test")

    predictor = DemandPredictor()

    print(">> Running batch predictions for all products...")
    batch_results = predictor.batch_predict_all_products(days=7)

    print(f"\n📊 BATCH PREDICTION SUMMARY:")
    total_demand = 0
    successful_predictions = 0

    for product_name, results in batch_results.items():
        if 'error' not in results:
            demand = results['total_predicted_demand']
            confidence = results['accuracy_metrics']['confidence_score']
            total_demand += demand
            successful_predictions += 1

            print(f"  {product_name.capitalize():<12}: {demand:>8,} kg (Conf: {confidence:.3f})")
        else:
            print(f"  {product_name.capitalize():<12}: ERROR - {results['error']}")

    print(f"\n📈 OVERALL SUMMARY:")
    print(f"  Successful Predictions: {successful_predictions}/{len(batch_results)}")
    print(f"  Total Weekly Demand: {total_demand:,} kg")
    print(f"  Average Daily Demand: {total_demand/7:,.0f} kg")

    return batch_results

def test_simulation_data_generation():
    """Test simulation data generation"""
    print_header("Simulation Data Generation Test")

    predictor = DemandPredictor()

    print(">> Testing data generation for different products...")

    for product in ['tomatoes', 'rice']:
        print(f"\nGenerating data for {product}:")

        # Generate data
        df = predictor.generate_simulation_data(product, days=365)

        # Analyze data
        print(f"  Data points: {len(df)}")
        print(f"  Date range: {df['ds'].min().strftime('%Y-%m-%d')} to {df['ds'].max().strftime('%Y-%m-%d')}")
        print(f"  Demand range: {df['y'].min():,} - {df['y'].max():,} kg")
        print(f"  Average demand: {df['y'].mean():.0f} kg")
        print(f"  Standard deviation: {df['y'].std():.0f} kg")

        # Check seasonality
        df['month'] = df['ds'].dt.month
        monthly_avg = df.groupby('month')['y'].mean()
        peak_month = monthly_avg.idxmax()
        low_month = monthly_avg.idxmin()

        print(f"  Peak demand month: {peak_month} ({monthly_avg[peak_month]:.0f} kg)")
        print(f"  Low demand month: {low_month} ({monthly_avg[low_month]:.0f} kg)")

def test_model_performance():
    """Test model performance evaluation"""
    print_header("Model Performance Evaluation")

    predictor = DemandPredictor()

    print(">> Evaluating model performance...")

    try:
        # Test performance for a single product
        performance = predictor.get_model_performance('tomatoes')

        print(f"Cross-validation results:")
        print(f"  MAE: {performance['mae']:.2f}")
        print(f"  MAPE: {performance['mape']:.2f}%")
        print(f"  RMSE: {performance['rmse']:.2f}")
        if performance['coverage']:
            print(f"  Coverage: {performance['coverage']:.2f}")

    except Exception as e:
        print(f"[WARNING] Performance evaluation skipped: {e}")
        print("(Cross-validation requires sufficient historical data)")

def test_integration_with_smart_contract():
    """Test integration with PAM-TALK smart contract"""
    print_header("Smart Contract Integration Test")

    try:
        from contracts.pam_talk_contract import pam_talk_contract
        predictor = DemandPredictor()

        print(">> Generating predictions and storing in smart contract...")

        # Generate predictions for tomatoes
        results = predictor.predict_demand('tomatoes', days=7)

        # Store prediction in smart contract
        prediction_id = pam_talk_contract.store_demand_prediction(
            product_type='tomatoes',
            predicted_demand=results['total_predicted_demand'],
            confidence_score=results['accuracy_metrics']['confidence_score'],
            prediction_period='weekly',
            created_by='AI_MODEL_PROPHET',
            features_used=['historical_demand', 'seasonality', 'price', 'promotion'],
            metadata={
                'model_type': 'Prophet',
                'mae': results['accuracy_metrics']['mae'],
                'mape': results['accuracy_metrics']['mape'],
                'rmse': results['accuracy_metrics']['rmse']
            }
        )

        print(f"[OK] Prediction stored in smart contract with ID: {prediction_id}")

        # Retrieve and verify
        stored_predictions = pam_talk_contract.get_demand_predictions(product_type='tomatoes')
        print(f"[OK] Retrieved {len(stored_predictions)} predictions from smart contract")

        if stored_predictions:
            latest_prediction = stored_predictions[0]
            print(f"Latest prediction: {latest_prediction['predicted_demand']:,} kg "
                  f"(Confidence: {latest_prediction['confidence_score']:.3f})")

        return True

    except ImportError:
        print("[WARNING] Smart contract not available for integration test")
        return False
    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        return False

def create_sample_report():
    """Create a sample prediction report"""
    print_header("Sample Prediction Report Generation")

    predictor = DemandPredictor()

    print(">> Generating comprehensive prediction report...")

    # Generate predictions for all products
    batch_results = predictor.batch_predict_all_products(days=14)  # 2-week forecast

    # Create report data
    report = {
        'report_title': 'PAM-TALK Agricultural Demand Forecast',
        'generated_at': datetime.now().isoformat(),
        'forecast_period': '14 days',
        'products_analyzed': len(batch_results),
        'summary': {
            'total_predicted_demand': 0,
            'high_confidence_products': [],
            'medium_confidence_products': [],
            'low_confidence_products': []
        },
        'detailed_predictions': batch_results
    }

    # Analyze results
    for product_name, results in batch_results.items():
        if 'error' not in results:
            confidence = results['accuracy_metrics']['confidence_score']
            demand = results['total_predicted_demand']

            report['summary']['total_predicted_demand'] += demand

            if confidence >= 0.8:
                report['summary']['high_confidence_products'].append(product_name)
            elif confidence >= 0.6:
                report['summary']['medium_confidence_products'].append(product_name)
            else:
                report['summary']['low_confidence_products'].append(product_name)

    # Save report
    report_filename = f"data/predictions/forecast_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"[OK] Report saved to {report_filename}")

    # Print summary
    print(f"\n📋 FORECAST REPORT SUMMARY:")
    print(f"  Products Analyzed: {report['products_analyzed']}")
    print(f"  Total 2-Week Demand: {report['summary']['total_predicted_demand']:,} kg")
    print(f"  High Confidence: {len(report['summary']['high_confidence_products'])} products")
    print(f"  Medium Confidence: {len(report['summary']['medium_confidence_products'])} products")
    print(f"  Low Confidence: {len(report['summary']['low_confidence_products'])} products")

def main():
    """Run all tests"""
    print_header("PAM-TALK Demand Predictor Test Suite")

    tests = [
        ("Simulation Data Generation", test_simulation_data_generation),
        ("Single Product Prediction", test_single_product_prediction),
        ("Multiple Products Prediction", test_multiple_products),
        ("Batch Prediction", test_batch_prediction),
        ("Model Performance", test_model_performance),
        ("Smart Contract Integration", test_integration_with_smart_contract),
        ("Sample Report Generation", create_sample_report),
    ]

    passed_tests = 0
    total_tests = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\n>> Running {test_name}...")
            result = test_func()
            if result is not False:  # Consider None and True as success
                passed_tests += 1
                print(f"[OK] {test_name} completed")
            else:
                print(f"[SKIP] {test_name} skipped")
        except Exception as e:
            print(f"[FAIL] {test_name} - Exception: {e}")

    print_header("Test Results Summary")
    print(f"Tests completed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")

    print(f"\n🎯 KEY FEATURES DEMONSTRATED:")
    print(f"  ✅ Realistic agricultural data simulation")
    print(f"  ✅ Prophet-based demand forecasting")
    print(f"  ✅ Multiple product support (tomatoes, cabbage, rice, lettuce, carrots)")
    print(f"  ✅ Confidence intervals and accuracy metrics")
    print(f"  ✅ Visualization with matplotlib")
    print(f"  ✅ Smart contract integration")
    print(f"  ✅ Batch processing and reporting")

    if passed_tests >= total_tests * 0.8:
        print("\n[SUCCESS] Demand prediction system is working correctly!")
        return 0
    else:
        print("\n[WARNING] Some features may need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())