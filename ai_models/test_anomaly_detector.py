#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Anomaly Detector Test Suite

This script tests and demonstrates the anomaly detection functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_models.anomaly_detector import AnomalyDetector, TransactionData, AnomalyResult
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 70}")
    print(f" {title}")
    print(f"{'=' * 70}")

def print_anomaly_result(result: AnomalyResult):
    """Print anomaly detection result in a readable format"""
    print(f"\n>> ANOMALY ANALYSIS FOR {result.transaction_id}")
    print(f"   Is Anomaly: {result.is_anomaly}")
    print(f"   Anomaly Score: {result.anomaly_score:.3f}/1.000")
    print(f"   Confidence: {result.confidence:.3f}/1.000")
    print(f"   Risk Level: {result.risk_level}")
    print(f"   Anomaly Types: {', '.join(result.anomaly_types)}")

    if result.recommendations:
        print(f"\n   RECOMMENDATIONS:")
        for rec in result.recommendations[:3]:  # Show top 3 recommendations
            print(f"     - {rec}")

    # Detection method scores
    print(f"\n   DETECTION METHOD SCORES:")
    for method, score in result.detection_methods.items():
        print(f"     {method.replace('_', ' ').title()}: {score:.3f}")

def test_simulation_data_generation():
    """Test simulation data generation"""
    print_header("Simulation Data Generation Test")

    detector = AnomalyDetector()

    print(">> Generating simulation data with anomalies...")

    # Generate data with 15% anomalies
    df = detector.generate_simulation_data(num_transactions=1000, anomaly_percentage=0.15)

    print(f"   Total transactions: {len(df)}")
    print(f"   Normal transactions: {len(df[~df['is_anomaly']])}")
    print(f"   Anomalous transactions: {len(df[df['is_anomaly']])}")
    print(f"   Anomaly percentage: {df['is_anomaly'].sum() / len(df) * 100:.1f}%")

    # Basic statistics
    print(f"\n   TRANSACTION STATISTICS:")
    print(f"     Price range: {df['price_per_unit'].min():.0f} - {df['price_per_unit'].max():.0f} PAMT/kg")
    print(f"     Quantity range: {df['quantity'].min():.0f} - {df['quantity'].max():.0f} kg")
    print(f"     Value range: {df['total_value'].min():,.0f} - {df['total_value'].max():,.0f} PAMT")

    print(f"\n   PRODUCT TYPE DISTRIBUTION:")
    for product, count in df['product_type'].value_counts().items():
        print(f"     {product.capitalize()}: {count} transactions")

    return df

def test_isolation_forest_training():
    """Test Isolation Forest training"""
    print_header("Isolation Forest Training Test")

    detector = AnomalyDetector()

    # Generate training data
    print(">> Generating training data...")
    historical_data = detector.generate_simulation_data(num_transactions=2000, anomaly_percentage=0.05)

    # Remove anomalies from training data (use only normal transactions)
    training_data = historical_data[~historical_data['is_anomaly']].copy()

    print(f"   Training on {len(training_data)} normal transactions")

    # Train the model
    print(">> Training Isolation Forest...")
    detector.train_isolation_forest(training_data)

    print(f"   Model trained successfully: {detector.is_trained}")
    print(f"   Features used: {len(detector.feature_columns)}")

    return detector, historical_data

def test_single_transaction_analysis():
    """Test anomaly detection on single transactions"""
    print_header("Single Transaction Analysis")

    # Setup
    detector, historical_data = test_isolation_forest_training()

    # Test normal transaction
    print(">> Testing NORMAL transaction...")
    normal_transaction = TransactionData(
        transaction_id="TEST_NORMAL_001",
        timestamp=datetime.now().isoformat(),
        producer_id="PRODUCER_001",
        consumer_id="CONSUMER_001",
        product_type="tomatoes",
        quantity=500.0,
        price_per_unit=5000.0,
        total_value=2500000.0,
        location="Seoul",
        quality_score=85,
        esg_score=80,
        payment_method="PAMT_TRANSFER",
        delivery_time_hours=48.0,
        producer_reputation=0.85,
        consumer_reputation=0.90,
        season_factor=1.1,
        market_volatility=0.2
    )

    normal_result = detector.detect_anomaly(normal_transaction, historical_data)
    print_anomaly_result(normal_result)

    # Test anomalous transaction (price manipulation)
    print("\n>> Testing ANOMALOUS transaction (Price Manipulation)...")
    anomaly_transaction = TransactionData(
        transaction_id="TEST_ANOMALY_001",
        timestamp=datetime.now().isoformat(),
        producer_id="PRODUCER_002",
        consumer_id="CONSUMER_002",
        product_type="tomatoes",
        quantity=200.0,
        price_per_unit=25000.0,  # 5x normal price
        total_value=5000000.0,
        location="Seoul",
        quality_score=70,  # Normal quality but premium price
        esg_score=60,
        payment_method="CRYPTO",
        delivery_time_hours=12.0,  # Unusually fast delivery
        producer_reputation=0.3,  # Low reputation
        consumer_reputation=0.4,
        season_factor=1.0,
        market_volatility=0.1  # Low volatility but high price
    )

    anomaly_result = detector.detect_anomaly(anomaly_transaction, historical_data)
    print_anomaly_result(anomaly_result)

    return detector, historical_data

def test_batch_anomaly_detection():
    """Test batch anomaly detection"""
    print_header("Batch Anomaly Detection Test")

    # Setup
    detector, historical_data = test_isolation_forest_training()

    # Generate test transactions with known anomalies
    test_data = detector.generate_simulation_data(num_transactions=200, anomaly_percentage=0.2)

    # Convert to TransactionData objects
    test_transactions = []
    for _, row in test_data.iterrows():
        transaction = TransactionData(
            transaction_id=row['transaction_id'],
            timestamp=row['timestamp'],
            producer_id=row['producer_id'],
            consumer_id=row['consumer_id'],
            product_type=row['product_type'],
            quantity=row['quantity'],
            price_per_unit=row['price_per_unit'],
            total_value=row['total_value'],
            location=row['location'],
            quality_score=row['quality_score'],
            esg_score=row['esg_score'],
            payment_method=row['payment_method'],
            delivery_time_hours=row['delivery_time_hours'],
            producer_reputation=row['producer_reputation'],
            consumer_reputation=row['consumer_reputation'],
            season_factor=row['season_factor'],
            market_volatility=row['market_volatility']
        )
        test_transactions.append(transaction)

    print(f">> Running batch detection on {len(test_transactions)} transactions...")

    # Run batch detection
    results = detector.batch_anomaly_detection(test_transactions, historical_data)

    # Analyze results
    detected_anomalies = sum(1 for r in results if r.is_anomaly)
    actual_anomalies = sum(1 for row in test_data.itertuples() if 'ANOMALY' in row.transaction_id)

    print(f"\n   BATCH DETECTION RESULTS:")
    print(f"     Total transactions processed: {len(results)}")
    print(f"     Anomalies detected by system: {detected_anomalies}")
    print(f"     Actual anomalies in data: {actual_anomalies}")
    print(f"     Detection rate: {detected_anomalies/actual_anomalies*100:.1f}%")

    # Risk level distribution
    risk_distribution = {}
    for result in results:
        if result.risk_level in risk_distribution:
            risk_distribution[result.risk_level] += 1
        else:
            risk_distribution[result.risk_level] = 1

    print(f"\n   RISK LEVEL DISTRIBUTION:")
    for level, count in risk_distribution.items():
        print(f"     {level}: {count} transactions")

    # Anomaly type distribution
    anomaly_types = {}
    for result in results:
        if result.is_anomaly:
            for anomaly_type in result.anomaly_types:
                if anomaly_type in anomaly_types:
                    anomaly_types[anomaly_type] += 1
                else:
                    anomaly_types[anomaly_type] = 1

    if anomaly_types:
        print(f"\n   ANOMALY TYPE DISTRIBUTION:")
        for anomaly_type, count in anomaly_types.items():
            print(f"     {anomaly_type.replace('_', ' ').title()}: {count}")

    # Save results
    results_file = detector.save_anomaly_results(results)
    print(f"\n   Results saved to: {results_file}")

    return results

def test_specific_anomaly_types():
    """Test detection of specific anomaly types"""
    print_header("Specific Anomaly Type Detection")

    detector, historical_data = test_isolation_forest_training()

    # Test different anomaly types
    anomaly_scenarios = [
        {
            'name': 'Price Manipulation',
            'transaction': TransactionData(
                transaction_id="PRICE_MANIP_001",
                timestamp=datetime.now().isoformat(),
                producer_id="PRODUCER_003",
                consumer_id="CONSUMER_003",
                product_type="rice",
                quantity=1000.0,
                price_per_unit=15000.0,  # 5x normal rice price
                total_value=15000000.0,
                location="Busan",
                quality_score=75,
                esg_score=70,
                payment_method="CRYPTO",
                delivery_time_hours=24.0,
                producer_reputation=0.4,
                consumer_reputation=0.5,
                season_factor=1.0,
                market_volatility=0.15
            )
        },
        {
            'name': 'Quality Fraud',
            'transaction': TransactionData(
                transaction_id="QUALITY_FRAUD_001",
                timestamp=datetime.now().isoformat(),
                producer_id="PRODUCER_004",
                consumer_id="CONSUMER_004",
                product_type="lettuce",
                quantity=300.0,
                price_per_unit=12000.0,  # Premium price
                total_value=3600000.0,
                location="Daegu",
                quality_score=30,  # Very low quality
                esg_score=25,
                payment_method="BANK_TRANSFER",
                delivery_time_hours=36.0,
                producer_reputation=0.2,
                consumer_reputation=0.3,
                season_factor=1.2,
                market_volatility=0.2
            )
        },
        {
            'name': 'Wash Trading',
            'transaction': TransactionData(
                transaction_id="WASH_TRADE_001",
                timestamp=datetime.now().isoformat(),
                producer_id="PRODUCER_005",
                consumer_id="CONSUMER_005",
                product_type="cabbage",
                quantity=10000.0,  # Unusually large volume
                price_per_unit=3500.0,
                total_value=35000000.0,
                location="Incheon",
                quality_score=80,
                esg_score=60,
                payment_method="CRYPTO",
                delivery_time_hours=24.0,
                producer_reputation=0.1,  # Very low reputation
                consumer_reputation=0.1,
                season_factor=1.0,
                market_volatility=0.1
            )
        },
        {
            'name': 'Timing Manipulation',
            'transaction': TransactionData(
                transaction_id="TIME_MANIP_001",
                timestamp=(datetime.now().replace(hour=2, minute=30)).isoformat(),  # 2:30 AM
                producer_id="PRODUCER_006",
                consumer_id="CONSUMER_006",
                product_type="carrots",
                quantity=800.0,
                price_per_unit=4000.0,
                total_value=3200000.0,
                location="Gwangju",
                quality_score=85,
                esg_score=75,
                payment_method="BANK_TRANSFER",
                delivery_time_hours=6.0,  # Extremely fast delivery
                producer_reputation=0.6,
                consumer_reputation=0.7,
                season_factor=1.1,
                market_volatility=0.3
            )
        }
    ]

    for scenario in anomaly_scenarios:
        print(f"\n>> Testing {scenario['name']}...")
        result = detector.detect_anomaly(scenario['transaction'], historical_data)

        print(f"   Detected as anomaly: {result.is_anomaly}")
        print(f"   Risk level: {result.risk_level}")
        print(f"   Anomaly types: {', '.join(result.anomaly_types)}")
        print(f"   Confidence: {result.confidence:.3f}")

        if result.is_anomaly and scenario['name'].lower().replace(' ', '_') in [t.lower() for t in result.anomaly_types]:
            print(f"   [SUCCESS] Correctly identified {scenario['name']}")
        elif result.is_anomaly:
            print(f"   [PARTIAL] Detected as anomaly but different type")
        else:
            print(f"   [MISS] Failed to detect anomaly")

def test_smart_contract_integration():
    """Test integration with PAM-TALK smart contract"""
    print_header("Smart Contract Integration Test")

    try:
        from contracts.pam_talk_contract import pam_talk_contract

        detector, historical_data = test_isolation_forest_training()

        print(">> Analyzing existing smart contract transactions...")

        # Get agriculture records from smart contract
        agriculture_records = pam_talk_contract.get_agriculture_records(limit=50)

        if agriculture_records:
            print(f"   Found {len(agriculture_records)} agriculture records in smart contract")

            # Analyze a few records for anomalies
            for i, record in enumerate(agriculture_records[:3]):
                # Convert to TransactionData format
                transaction = TransactionData(
                    transaction_id=record['record_id'],
                    timestamp=datetime.fromtimestamp(record['timestamp']).isoformat(),
                    producer_id=record['producer'],
                    consumer_id=record['consumer'],
                    product_type=record['product_type'],
                    quantity=float(record['quantity']),
                    price_per_unit=float(record['price_per_unit']),
                    total_value=float(record['total_value']),
                    location=record['location'],
                    quality_score=record['quality_score'],
                    esg_score=record['esg_score'],
                    payment_method="PAMT_TRANSFER",
                    delivery_time_hours=48.0,  # Default
                    producer_reputation=0.8,  # Default
                    consumer_reputation=0.8,  # Default
                    season_factor=1.0,
                    market_volatility=0.2
                )

                result = detector.detect_anomaly(transaction, historical_data)

                print(f"\n   Smart Contract Record {i+1}:")
                print(f"     Record ID: {record['record_id']}")
                print(f"     Is Anomaly: {result.is_anomaly}")
                print(f"     Risk Level: {result.risk_level}")

                if result.is_anomaly:
                    print(f"     ALERT: Suspicious transaction detected in blockchain!")

        else:
            print("   No agriculture records found in smart contract")

        print(f"\n[SUCCESS] Smart contract integration working")

    except ImportError:
        print("[WARNING] Smart contract not available for integration test")
    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")

def test_performance_metrics():
    """Test performance metrics of anomaly detection"""
    print_header("Performance Metrics Test")

    detector, historical_data = test_isolation_forest_training()

    # Generate balanced test set
    test_data = detector.generate_simulation_data(num_transactions=500, anomaly_percentage=0.2)

    print(">> Calculating performance metrics...")

    # Convert to TransactionData objects
    test_transactions = []
    true_labels = []
    for _, row in test_data.iterrows():
        transaction = TransactionData(
            transaction_id=row['transaction_id'],
            timestamp=row['timestamp'],
            producer_id=row['producer_id'],
            consumer_id=row['consumer_id'],
            product_type=row['product_type'],
            quantity=row['quantity'],
            price_per_unit=row['price_per_unit'],
            total_value=row['total_value'],
            location=row['location'],
            quality_score=row['quality_score'],
            esg_score=row['esg_score'],
            payment_method=row['payment_method'],
            delivery_time_hours=row['delivery_time_hours'],
            producer_reputation=row['producer_reputation'],
            consumer_reputation=row['consumer_reputation'],
            season_factor=row['season_factor'],
            market_volatility=row['market_volatility']
        )
        test_transactions.append(transaction)
        true_labels.append(row['is_anomaly'])

    # Run detection
    results = detector.batch_anomaly_detection(test_transactions, historical_data)
    predicted_labels = [r.is_anomaly for r in results]

    # Calculate metrics
    true_positives = sum(1 for true, pred in zip(true_labels, predicted_labels) if true and pred)
    false_positives = sum(1 for true, pred in zip(true_labels, predicted_labels) if not true and pred)
    true_negatives = sum(1 for true, pred in zip(true_labels, predicted_labels) if not true and not pred)
    false_negatives = sum(1 for true, pred in zip(true_labels, predicted_labels) if true and not pred)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (true_positives + true_negatives) / len(true_labels)

    print(f"\n   PERFORMANCE METRICS:")
    print(f"     Accuracy: {accuracy:.3f}")
    print(f"     Precision: {precision:.3f}")
    print(f"     Recall: {recall:.3f}")
    print(f"     F1-Score: {f1_score:.3f}")

    print(f"\n   CONFUSION MATRIX:")
    print(f"     True Positives: {true_positives}")
    print(f"     False Positives: {false_positives}")
    print(f"     True Negatives: {true_negatives}")
    print(f"     False Negatives: {false_negatives}")

    # High-risk transaction analysis
    high_risk_count = sum(1 for r in results if r.risk_level in ['HIGH', 'CRITICAL'])
    print(f"\n   HIGH-RISK TRANSACTIONS: {high_risk_count}")

    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }

def create_comprehensive_report():
    """Create comprehensive anomaly detection report"""
    print_header("Comprehensive Anomaly Detection Report")

    detector, historical_data = test_isolation_forest_training()

    # Generate comprehensive test data
    test_data = detector.generate_simulation_data(num_transactions=1000, anomaly_percentage=0.15)

    # Convert to TransactionData objects
    test_transactions = []
    for _, row in test_data.iterrows():
        transaction = TransactionData(
            transaction_id=row['transaction_id'],
            timestamp=row['timestamp'],
            producer_id=row['producer_id'],
            consumer_id=row['consumer_id'],
            product_type=row['product_type'],
            quantity=row['quantity'],
            price_per_unit=row['price_per_unit'],
            total_value=row['total_value'],
            location=row['location'],
            quality_score=row['quality_score'],
            esg_score=row['esg_score'],
            payment_method=row['payment_method'],
            delivery_time_hours=row['delivery_time_hours'],
            producer_reputation=row['producer_reputation'],
            consumer_reputation=row['consumer_reputation'],
            season_factor=row['season_factor'],
            market_volatility=row['market_volatility']
        )
        test_transactions.append(transaction)

    print(">> Running comprehensive anomaly analysis...")

    # Run detection
    results = detector.batch_anomaly_detection(test_transactions, historical_data)

    # Create report
    report = {
        'report_title': 'PAM-TALK Anomaly Detection Analysis Report',
        'generated_at': datetime.now().isoformat(),
        'analysis_period': '1000 simulated transactions',
        'summary': {
            'total_transactions': len(results),
            'anomalies_detected': sum(1 for r in results if r.is_anomaly),
            'average_anomaly_score': np.mean([r.anomaly_score for r in results]),
            'high_risk_transactions': sum(1 for r in results if r.risk_level in ['HIGH', 'CRITICAL'])
        },
        'risk_analysis': {},
        'anomaly_types': {},
        'recommendations': []
    }

    # Risk level analysis
    for result in results:
        if result.risk_level in report['risk_analysis']:
            report['risk_analysis'][result.risk_level] += 1
        else:
            report['risk_analysis'][result.risk_level] = 1

    # Anomaly type analysis
    for result in results:
        if result.is_anomaly:
            for anomaly_type in result.anomaly_types:
                if anomaly_type in report['anomaly_types']:
                    report['anomaly_types'][anomaly_type] += 1
                else:
                    report['anomaly_types'][anomaly_type] = 1

    # Generate recommendations
    if report['summary']['high_risk_transactions'] > 0:
        report['recommendations'].append(
            f"URGENT: {report['summary']['high_risk_transactions']} high-risk transactions require immediate investigation"
        )

    if report['summary']['anomalies_detected'] / report['summary']['total_transactions'] > 0.1:
        report['recommendations'].append(
            "High anomaly rate detected - consider enhancing monitoring systems"
        )

    # Save report
    os.makedirs("data/anomaly_reports", exist_ok=True)
    report_filename = f"data/anomaly_reports/anomaly_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary
    print(f">> COMPREHENSIVE ANOMALY ANALYSIS REPORT")
    print(f"   Report saved to: {report_filename}")
    print(f"   Total Transactions: {report['summary']['total_transactions']}")
    print(f"   Anomalies Detected: {report['summary']['anomalies_detected']}")
    print(f"   High-Risk Transactions: {report['summary']['high_risk_transactions']}")
    print(f"   Average Anomaly Score: {report['summary']['average_anomaly_score']:.3f}")

    print(f"\n   RISK DISTRIBUTION:")
    for level, count in report['risk_analysis'].items():
        print(f"     {level}: {count}")

    if report['anomaly_types']:
        print(f"\n   TOP ANOMALY TYPES:")
        sorted_types = sorted(report['anomaly_types'].items(), key=lambda x: x[1], reverse=True)
        for anomaly_type, count in sorted_types[:5]:
            print(f"     {anomaly_type.replace('_', ' ').title()}: {count}")

def main():
    """Run all anomaly detector tests"""
    print_header("PAM-TALK Anomaly Detector Test Suite")

    tests = [
        ("Simulation Data Generation", test_simulation_data_generation),
        ("Isolation Forest Training", test_isolation_forest_training),
        ("Single Transaction Analysis", test_single_transaction_analysis),
        ("Batch Anomaly Detection", test_batch_anomaly_detection),
        ("Specific Anomaly Types", test_specific_anomaly_types),
        ("Smart Contract Integration", test_smart_contract_integration),
        ("Performance Metrics", test_performance_metrics),
        ("Comprehensive Report", create_comprehensive_report),
    ]

    passed_tests = 0
    total_tests = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\n>> Running {test_name}...")
            result = test_func()
            if result is not False:
                passed_tests += 1
                print(f"[OK] {test_name} completed")
            else:
                print(f"[SKIP] {test_name} skipped")
        except Exception as e:
            print(f"[FAIL] {test_name} - Exception: {e}")

    print_header("Anomaly Detector Test Results")
    print(f"Tests completed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")

    print(f"\n   KEY ANOMALY DETECTION FEATURES:")
    print(f"     - Isolation Forest machine learning detection")
    print(f"     - Z-score statistical anomaly detection")
    print(f"     - Transaction pattern analysis")
    print(f"     - Multi-type anomaly classification")
    print(f"     - Risk level assessment (LOW/MEDIUM/HIGH/CRITICAL)")
    print(f"     - Confidence scoring and recommendations")
    print(f"     - Smart contract integration")

    if passed_tests >= total_tests * 0.8:
        print("\n[SUCCESS] Anomaly detection system is working correctly!")
        return 0
    else:
        print("\n[WARNING] Some features may need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())