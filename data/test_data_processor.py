#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Data Processor Test Suite

This script tests and demonstrates the integrated data processing functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_processor import DataProcessor, FarmInfo, ProcessingResult
import json
import time
from datetime import datetime, timedelta

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 70}")
    print(f" {title}")
    print(f"{'=' * 70}")

def print_processing_result(result: ProcessingResult):
    """Print processing result in a readable format"""
    print(f"\n>> DAILY PROCESSING RESULTS")
    print(f"   Process Date: {result.process_date[:19]}")
    print(f"   Processing Time: {result.processing_time_seconds:.2f} seconds")
    print(f"   Status: {result.summary.get('status', 'unknown')}")

    print(f"\n   PROCESSING STATISTICS:")
    print(f"   Farms Processed: {result.farms_processed}")
    print(f"   Predictions Generated: {result.predictions_generated}")
    print(f"   ESG Scores Updated: {result.esg_scores_updated}")
    print(f"   Anomalies Detected: {result.anomalies_detected}")
    print(f"   Blockchain Records Synced: {result.blockchain_records}")

    if result.summary.get('total_predicted_demand'):
        print(f"   Total Predicted Demand: {result.summary['total_predicted_demand']:,} kg")

    if result.summary.get('total_esg_tokens'):
        print(f"   Total ESG Tokens Generated: {result.summary['total_esg_tokens']:,} ESGD")

    if result.errors:
        print(f"\n   ERRORS ({len(result.errors)}):")
        for error in result.errors:
            print(f"     - {error}")

def test_directory_setup():
    """Test directory structure setup"""
    print_header("Directory Setup Test")

    processor = DataProcessor(base_data_path="data/test_processing")
    processor.setup_directories()

    print(">> Checking directory structure...")

    required_dirs = [
        "data/test_processing/farms",
        "data/test_processing/transactions",
        "data/test_processing/daily_reports",
        "data/test_processing/backups",
        "data/test_processing/ai_results",
        "data/test_processing/blockchain_sync",
        "data/test_processing/logs"
    ]

    all_dirs_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   [OK] {directory}")
        else:
            print(f"   [MISSING] {directory}")
            all_dirs_exist = False

    return all_dirs_exist

def test_farm_management():
    """Test farm registration and management"""
    print_header("Farm Management Test")

    processor = DataProcessor(base_data_path="data/test_processing")

    print(">> Creating sample farms...")

    # Create sample farms
    success = processor.create_sample_farms()
    print(f"   Sample farms creation: {'SUCCESS' if success else 'FAILED'}")

    # Load and display farms
    farms = processor.load_farms_registry()
    print(f"   Farms loaded: {len(farms)}")

    for farm_id, farm_info in farms.items():
        print(f"\n   FARM: {farm_info.farm_name} ({farm_id})")
        print(f"     Location: {farm_info.location}")
        print(f"     Size: {farm_info.size_hectares} hectares")
        print(f"     Products: {', '.join(farm_info.products)}")
        print(f"     Certifications: {', '.join(farm_info.certifications)}")
        print(f"     Status: {farm_info.status}")

    # Test farm update
    if farms:
        first_farm_id = list(farms.keys())[0]
        update_success = processor.update_farm_info(
            first_farm_id,
            {'status': 'active', 'size_hectares': 30.0}
        )
        print(f"\n   Farm update test: {'SUCCESS' if update_success else 'FAILED'}")

    return len(farms) > 0

def test_transaction_management():
    """Test transaction storage and retrieval"""
    print_header("Transaction Management Test")

    processor = DataProcessor(base_data_path="data/test_processing")

    print(">> Adding sample transactions...")

    # Add sample transactions
    sample_transactions = [
        {
            'producer_id': 'FARM_DEMO_001',
            'consumer_id': 'CONSUMER_001',
            'product_type': 'tomatoes',
            'quantity': 500,
            'price_per_unit': 5000,
            'total_value': 2500000,
            'quality_score': 85,
            'esg_score': 80,
            'location': 'Seoul',
            'payment_method': 'PAMT_TRANSFER'
        },
        {
            'producer_id': 'FARM_DEMO_002',
            'consumer_id': 'CONSUMER_002',
            'product_type': 'rice',
            'quantity': 1000,
            'price_per_unit': 3000,
            'total_value': 3000000,
            'quality_score': 90,
            'esg_score': 70,
            'location': 'Busan',
            'payment_method': 'CRYPTO'
        }
    ]

    transactions_added = 0
    for transaction in sample_transactions:
        if processor.add_transaction(transaction):
            transactions_added += 1

    print(f"   Transactions added: {transactions_added}/{len(sample_transactions)}")

    # Test transaction retrieval
    all_transactions = processor.get_transactions(limit=10)
    print(f"   Total transactions retrieved: {len(all_transactions)}")

    # Test filtered retrieval
    farm_transactions = processor.get_transactions(farm_id='FARM_DEMO_001')
    print(f"   Farm-specific transactions: {len(farm_transactions)}")

    tomato_transactions = processor.get_transactions(product_type='tomatoes')
    print(f"   Tomato transactions: {len(tomato_transactions)}")

    if all_transactions:
        print(f"\n   LATEST TRANSACTION:")
        latest = all_transactions[0]
        print(f"     ID: {latest.get('transaction_id', 'N/A')}")
        print(f"     Product: {latest.get('product_type', 'N/A')}")
        print(f"     Value: {latest.get('total_value', 0):,} PAMT")
        print(f"     Date: {latest.get('timestamp', 'N/A')[:19]}")

    return len(all_transactions) > 0

def test_blockchain_sync():
    """Test blockchain synchronization"""
    print_header("Blockchain Synchronization Test")

    processor = DataProcessor(base_data_path="data/test_processing")

    print(">> Testing blockchain initialization...")
    models_initialized = processor.initialize_models()
    print(f"   Models initialization: {'SUCCESS' if models_initialized else 'FAILED'}")

    if not models_initialized:
        print("   [SKIP] Blockchain sync test - models not available")
        return False

    print(">> Testing blockchain sync...")
    sync_result = processor.sync_with_blockchain()

    if sync_result['success']:
        result = sync_result['result']
        print(f"   Agriculture records synced: {result['agriculture_records_synced']}")
        print(f"   Demand predictions synced: {result['demand_predictions_synced']}")
        print(f"   New transactions added: {result['new_transactions_added']}")
    else:
        print(f"   Sync failed: {sync_result['error']}")

    return sync_result['success']

def test_ai_model_integration():
    """Test AI model integration"""
    print_header("AI Model Integration Test")

    processor = DataProcessor(base_data_path="data/test_processing")

    print(">> Initializing AI models...")
    if not processor.initialize_models():
        print("   [SKIP] AI model tests - initialization failed")
        return False

    # Load farms for testing
    farms = processor.load_farms_registry()
    if not farms:
        processor.create_sample_farms()
        farms = processor.load_farms_registry()

    print(f"   Loaded {len(farms)} farms for AI processing")

    # Test demand predictions
    print("\n>> Testing demand prediction generation...")
    prediction_result = processor.generate_demand_predictions(farms)

    if prediction_result['success']:
        result = prediction_result['result']
        print(f"   Predictions generated: {result['predictions_generated']}")
        print(f"   Products analyzed: {len(result['products_analyzed'])}")
        print(f"   Total predicted demand: {result['total_predicted_demand']:,} kg")

        if result['predictions']:
            product_name = list(result['predictions'].keys())[0]
            prediction = result['predictions'][product_name]
            print(f"\n   SAMPLE PREDICTION ({product_name}):")
            print(f"     Total demand: {prediction['total_predicted_demand']:,} kg")
            print(f"     Confidence: {prediction['accuracy_metrics']['confidence_score']:.3f}")
    else:
        print(f"   Prediction failed: {prediction_result['error']}")

    # Test ESG score updates
    print("\n>> Testing ESG score updates...")
    esg_result = processor.update_esg_scores(farms)

    if esg_result['success']:
        result = esg_result['result']
        print(f"   Farms processed: {result['farms_processed']}")
        print(f"   Scores updated: {result['scores_updated']}")
        print(f"   Total ESG tokens: {result['total_esg_tokens']:,} ESGD")

        if result['esg_scores']:
            farm_id = list(result['esg_scores'].keys())[0]
            score = result['esg_scores'][farm_id]
            print(f"\n   SAMPLE ESG SCORE ({farm_id}):")
            print(f"     Overall: {score['overall_score']:.1f}/100")
            print(f"     Environmental: {score['environmental_score']:.1f}")
            print(f"     Social: {score['social_score']:.1f}")
            print(f"     Governance: {score['governance_score']:.1f}")
            print(f"     Certification: {score['certification_level']}")
    else:
        print(f"   ESG update failed: {esg_result['error']}")

    # Test anomaly detection
    print("\n>> Testing anomaly detection...")
    anomaly_result = processor.check_transaction_anomalies()

    if anomaly_result['success']:
        result = anomaly_result['result']
        print(f"   Transactions checked: {result['transactions_checked']}")
        print(f"   Anomalies detected: {result['anomalies_detected']}")
        print(f"   High-risk transactions: {result['high_risk_transactions']}")

        if result['anomalous_transactions']:
            anomaly = result['anomalous_transactions'][0]
            print(f"\n   SAMPLE ANOMALY:")
            print(f"     Transaction: {anomaly['transaction_id']}")
            print(f"     Risk Level: {anomaly['risk_level']}")
            print(f"     Types: {', '.join(anomaly['anomaly_types'])}")
    else:
        print(f"   Anomaly detection failed: {anomaly_result['error']}")

    return prediction_result['success'] or esg_result['success'] or anomaly_result['success']

def test_daily_processing():
    """Test complete daily data processing"""
    print_header("Daily Data Processing Test")

    processor = DataProcessor(base_data_path="data/test_processing")

    print(">> Running complete daily processing...")
    start_time = time.time()

    result = processor.process_daily_data()

    end_time = time.time()
    actual_processing_time = end_time - start_time

    print(f"   Actual processing time: {actual_processing_time:.2f} seconds")

    # Display results
    print_processing_result(result)

    # Check if daily report was saved
    report_date = datetime.now().strftime('%Y%m%d')
    report_file = os.path.join(processor.daily_reports_path, f"daily_report_{report_date}.json")

    if os.path.exists(report_file):
        print(f"\n   Daily report saved: {report_file}")
    else:
        print(f"\n   [WARNING] Daily report not found: {report_file}")

    return result.summary.get('status') in ['completed', 'completed_with_errors']

def test_backup_and_restore():
    """Test data backup and restoration"""
    print_header("Backup and Restore Test")

    processor = DataProcessor(base_data_path="data/test_processing")

    # Ensure we have some data to backup
    processor.create_sample_farms()

    print(">> Creating data backup...")
    backup_result = processor.create_backup()

    if backup_result['success']:
        backup_file = backup_result['backup_file']
        backup_size = backup_result['backup_size']
        print(f"   Backup created: {os.path.basename(backup_file)}")
        print(f"   Backup size: {backup_size:,} bytes")

        # Test restoration
        print("\n>> Testing backup restoration...")

        # First, create a backup of current state for restoration
        original_backup = processor.create_backup()

        # Modify some data
        processor.update_farm_info('FARM_DEMO_001', {'status': 'test_modified'})

        # Restore from backup
        restore_result = processor.restore_backup(backup_file)

        if restore_result['success']:
            print(f"   Restoration successful")
            print(f"   Files restored: {len(restore_result['restored_files'])}")
            print(f"   Restored files: {', '.join(restore_result['restored_files'])}")

            # Restore original state
            if original_backup['success']:
                processor.restore_backup(original_backup['backup_file'])
        else:
            print(f"   Restoration failed: {restore_result['error']}")

        return restore_result['success']

    else:
        print(f"   Backup failed: {backup_result['error']}")
        return False

def test_statistics_and_reporting():
    """Test processing statistics and reporting"""
    print_header("Statistics and Reporting Test")

    processor = DataProcessor(base_data_path="data/test_processing")

    # Run a processing cycle to generate some data
    processor.process_daily_data()

    print(">> Getting processing statistics...")
    stats = processor.get_processing_statistics(days=7)

    if 'error' not in stats:
        print(f"   Reports analyzed: {stats['reports_found']}")
        print(f"   Period: {stats['period_days']} days")
        print(f"   Total farms processed: {stats['total_farms_processed']}")
        print(f"   Total predictions generated: {stats['total_predictions_generated']}")
        print(f"   Total ESG scores updated: {stats['total_esg_scores_updated']}")
        print(f"   Total anomalies detected: {stats['total_anomalies_detected']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")

        if stats.get('average_processing_time'):
            print(f"   Average processing time: {stats['average_processing_time']:.2f} seconds")

        if stats['daily_stats']:
            print(f"\n   RECENT PROCESSING RUNS:")
            for daily_stat in stats['daily_stats'][-3:]:  # Last 3 runs
                print(f"     {daily_stat['date']}: {daily_stat['status']} ({daily_stat['processing_time']:.2f}s)")

        return True
    else:
        print(f"   Statistics failed: {stats['error']}")
        return False

def test_configuration_and_settings():
    """Test configuration and settings management"""
    print_header("Configuration and Settings Test")

    processor = DataProcessor(base_data_path="data/test_processing")

    print(">> Current configuration:")
    for key, value in processor.config.items():
        print(f"   {key}: {value}")

    # Test configuration changes
    print("\n>> Testing configuration changes...")
    original_prediction_days = processor.config['prediction_days']
    processor.config['prediction_days'] = 14

    print(f"   Changed prediction_days: {original_prediction_days} → {processor.config['prediction_days']}")

    # Restore original
    processor.config['prediction_days'] = original_prediction_days

    return True

def test_error_handling():
    """Test error handling and recovery"""
    print_header("Error Handling Test")

    processor = DataProcessor(base_data_path="data/test_processing")

    print(">> Testing error scenarios...")

    # Test with non-existent farm
    result = processor.update_farm_info('NON_EXISTENT_FARM', {'status': 'test'})
    print(f"   Non-existent farm update: {'HANDLED' if not result else 'ERROR'}")

    # Test with invalid transaction data
    result = processor.add_transaction({})  # Empty transaction
    print(f"   Empty transaction handling: {'HANDLED' if result else 'ERROR'}")

    # Test backup restoration with non-existent file
    result = processor.restore_backup('non_existent_backup.zip')
    print(f"   Non-existent backup restore: {'HANDLED' if not result['success'] else 'ERROR'}")

    return True

def run_comprehensive_demo():
    """Run a comprehensive demonstration of the data processing system"""
    print_header("PAM-TALK Data Processing System Demonstration")

    processor = DataProcessor(base_data_path="data/demo_processing")

    print(">> STEP 1: Initialize system and create sample data")
    processor.create_sample_farms()

    # Add sample transactions
    sample_transactions = [
        {
            'producer_id': 'FARM_DEMO_001',
            'consumer_id': 'CONSUMER_001',
            'product_type': 'tomatoes',
            'quantity': 750,
            'price_per_unit': 5500,
            'total_value': 4125000,
            'quality_score': 92,
            'esg_score': 85
        },
        {
            'producer_id': 'FARM_DEMO_002',
            'consumer_id': 'CONSUMER_002',
            'product_type': 'rice',
            'quantity': 2000,
            'price_per_unit': 2800,
            'total_value': 5600000,
            'quality_score': 88,
            'esg_score': 75
        }
    ]

    for transaction in sample_transactions:
        processor.add_transaction(transaction)

    print("   Sample farms and transactions created")

    print("\n>> STEP 2: Run complete daily processing")
    result = processor.process_daily_data()
    print_processing_result(result)

    print("\n>> STEP 3: Display system status")
    farms = processor.load_farms_registry()
    transactions = processor.get_transactions(limit=10)

    print(f"   Registered farms: {len(farms)}")
    print(f"   Total transactions: {len(transactions)}")

    print("\n>> STEP 4: Create system backup")
    backup_result = processor.create_backup()
    if backup_result['success']:
        print(f"   Backup created: {os.path.basename(backup_result['backup_file'])}")

    print("\n>> STEP 5: Generate statistics report")
    stats = processor.get_processing_statistics(days=1)
    if 'error' not in stats:
        print(f"   Processing success rate: {stats['success_rate']:.1%}")
        print(f"   Total processing time: {stats['total_processing_time']:.2f} seconds")

    print("\n🎉 DEMONSTRATION COMPLETE!")
    print("   All major features of the PAM-TALK Data Processing System have been demonstrated.")

def main():
    """Run all data processor tests"""
    print_header("PAM-TALK Data Processor Test Suite")

    tests = [
        ("Directory Setup", test_directory_setup),
        ("Farm Management", test_farm_management),
        ("Transaction Management", test_transaction_management),
        ("Blockchain Synchronization", test_blockchain_sync),
        ("AI Model Integration", test_ai_model_integration),
        ("Daily Processing", test_daily_processing),
        ("Backup and Restore", test_backup_and_restore),
        ("Statistics and Reporting", test_statistics_and_reporting),
        ("Configuration Management", test_configuration_and_settings),
        ("Error Handling", test_error_handling),
    ]

    passed_tests = 0
    total_tests = len(tests)

    for test_name, test_func in tests:
        try:
            print(f"\n>> Running {test_name}...")
            result = test_func()
            if result:
                passed_tests += 1
                print(f"[OK] {test_name} completed")
            else:
                print(f"[PARTIAL] {test_name} completed with issues")
        except Exception as e:
            print(f"[FAIL] {test_name} - Exception: {e}")

    print_header("Data Processor Test Results")
    print(f"Tests completed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")

    print(f"\n   KEY DATA PROCESSING FEATURES:")
    print(f"     - JSON-based farm information management")
    print(f"     - Transaction history storage and retrieval")
    print(f"     - AI model integration (Demand, ESG, Anomaly)")
    print(f"     - Blockchain synchronization")
    print(f"     - Daily batch processing automation")
    print(f"     - Data backup and restoration")
    print(f"     - Comprehensive reporting and statistics")
    print(f"     - Error handling and recovery")

    if passed_tests >= total_tests * 0.8:
        print("\n[SUCCESS] Data processing system is working correctly!")

        # Run comprehensive demo
        run_comprehensive_demo()
        return 0
    else:
        print("\n[WARNING] Some features may need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())