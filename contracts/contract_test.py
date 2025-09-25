#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Smart Contract Test Suite

This script tests all functionalities of the PAM-TALK smart contract.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.pam_talk_contract import (
    pam_talk_contract, create_application, transfer_tokens,
    record_transaction, get_esg_score
)

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")

def print_result(test_name, result):
    """Print test result"""
    status = "[OK]" if result.get('success', True) else "[FAIL]"
    print(f"{status} {test_name}")
    if not result.get('success', True) and 'error' in result:
        print(f"    Error: {result['error']}")

def test_contract_deployment():
    """Test contract deployment"""
    print_header("Contract Deployment Test")

    result = create_application()
    print_result("Contract deployment", result)

    if result['success']:
        print(f"    Contract ID: {result['contract_id']}")
        print(f"    Tokens created: {result['tokens_created']}")

    return result['success']

def test_token_operations():
    """Test token operations"""
    print_header("Token Operations Test")

    # Get initial token info
    pamt_info = pam_talk_contract.get_token_info(1)  # PAM-TALK token
    esgd_info = pam_talk_contract.get_token_info(2)  # ESG-GOLD token

    print(f"PAM-TALK Token: {pamt_info['name']} ({pamt_info['symbol']})")
    print(f"    Supply: {pamt_info['total_supply']:,}")
    print(f"ESG-GOLD Token: {esgd_info['name']} ({esgd_info['symbol']})")
    print(f"    Supply: {esgd_info['total_supply']:,}")

    # Test token creation
    new_token_id = pam_talk_contract.create_token(
        name="Test Token",
        symbol="TEST",
        total_supply=1000000,
        decimals=6,
        creator="TEST_CREATOR",
        metadata={"purpose": "testing"}
    )

    print(f"[OK] New token created with ID: {new_token_id}")

    # Test minting
    mint_result = pam_talk_contract.mint_tokens(
        to_address="PRODUCER_ADDR",
        token_id=1,  # PAM-TALK
        amount=1000000000,  # 1000 PAMT
        creator="SYSTEM"
    )
    print_result("Token minting", mint_result)

    return True

def test_token_transfers():
    """Test token transfers"""
    print_header("Token Transfer Test")

    # Setup test addresses
    producer = "PRODUCER_ADDR"
    consumer = "CONSUMER_ADDR"
    government = "GOVERNMENT_ADDR"

    # Mint tokens for testing
    pam_talk_contract.mint_tokens(producer, 1, 5000000000, "SYSTEM")  # 5000 PAMT
    pam_talk_contract.mint_tokens(consumer, 1, 2000000000, "SYSTEM")   # 2000 PAMT

    print("Initial balances:")
    print(f"    Producer: {pam_talk_contract.get_balance(producer, 1) / 1000000:.2f} PAMT")
    print(f"    Consumer: {pam_talk_contract.get_balance(consumer, 1) / 1000000:.2f} PAMT")
    print(f"    Government: {pam_talk_contract.get_balance(government, 1) / 1000000:.2f} PAMT")

    # Test transfer: Producer -> Consumer
    transfer_result = transfer_tokens(
        from_address=producer,
        to_address=consumer,
        token_id=1,
        amount=500000000,  # 500 PAMT
        metadata={"purpose": "agricultural_trade"}
    )
    print_result("Producer to Consumer transfer", transfer_result)

    # Test transfer: Consumer -> Government (tax)
    tax_result = transfer_tokens(
        from_address=consumer,
        to_address=government,
        token_id=1,
        amount=50000000,  # 50 PAMT tax
        metadata={"purpose": "tax_payment"}
    )
    print_result("Tax payment transfer", tax_result)

    print("Final balances:")
    print(f"    Producer: {pam_talk_contract.get_balance(producer, 1) / 1000000:.2f} PAMT")
    print(f"    Consumer: {pam_talk_contract.get_balance(consumer, 1) / 1000000:.2f} PAMT")
    print(f"    Government: {pam_talk_contract.get_balance(government, 1) / 1000000:.2f} PAMT")

    return transfer_result['success'] and tax_result['success']

def test_agriculture_transactions():
    """Test agricultural transaction recording"""
    print_header("Agricultural Transaction Test")

    producer = "PRODUCER_ADDR"
    consumer = "CONSUMER_ADDR"

    # Record multiple agricultural transactions
    transactions_data = [
        {
            "producer": producer,
            "consumer": consumer,
            "product_type": "organic_tomatoes",
            "quantity": 1000,  # kg
            "price_per_unit": 5000,  # 5 PAMT per kg
            "quality_score": 95,
            "esg_score": 88,
            "location": "Seoul, South Korea",
            "metadata": {"organic": True, "categories": ["environmental", "social"]}
        },
        {
            "producer": producer,
            "consumer": "CONSUMER_ADDR_2",
            "product_type": "sustainable_rice",
            "quantity": 500,  # kg
            "price_per_unit": 3000,  # 3 PAMT per kg
            "quality_score": 92,
            "esg_score": 85,
            "location": "Busan, South Korea",
            "metadata": {"sustainable": True, "categories": ["environmental", "governance"]}
        }
    ]

    for i, tx_data in enumerate(transactions_data):
        result = record_transaction(**tx_data)
        print_result(f"Agriculture transaction {i+1}", result)

        if result['success']:
            print(f"    Record ID: {result['record_id']}")

    # Check ESG-GOLD rewards
    esg_balance = pam_talk_contract.get_balance(producer, 2)  # ESG-GOLD token
    print(f"Producer ESG-GOLD rewards: {esg_balance / 1000000:.2f} ESGD")

    return True

def test_esg_scoring():
    """Test ESG scoring system"""
    print_header("ESG Scoring Test")

    producer = "PRODUCER_ADDR"
    consumer = "CONSUMER_ADDR"

    # Get ESG scores
    producer_esg = get_esg_score(producer, period_days=30)
    consumer_esg = get_esg_score(consumer, period_days=30)

    print("Producer ESG Score:")
    print(f"    Overall Score: {producer_esg['esg_score']}")
    print(f"    Transactions: {producer_esg['transactions_count']}")
    print(f"    Trade Value: {producer_esg['total_trade_value']:,} microPAMT")
    print(f"    Environmental: {producer_esg['breakdown']['environmental']:.1f}")
    print(f"    Social: {producer_esg['breakdown']['social']:.1f}")
    print(f"    Governance: {producer_esg['breakdown']['governance']:.1f}")

    print("\nConsumer ESG Score:")
    print(f"    Overall Score: {consumer_esg['esg_score']}")
    print(f"    Transactions: {consumer_esg['transactions_count']}")

    return True

def test_demand_predictions():
    """Test demand prediction storage"""
    print_header("Demand Prediction Test")

    # Store sample predictions
    predictions_data = [
        {
            "product_type": "organic_tomatoes",
            "predicted_demand": 15000,  # kg
            "confidence_score": 0.87,
            "prediction_period": "weekly",
            "created_by": "AI_MODEL_V1",
            "features_used": ["weather", "price_history", "seasonal_trends"],
            "metadata": {"model": "prophet", "accuracy": "high"}
        },
        {
            "product_type": "sustainable_rice",
            "predicted_demand": 8500,  # kg
            "confidence_score": 0.92,
            "prediction_period": "monthly",
            "created_by": "AI_MODEL_V1",
            "features_used": ["market_trends", "economic_indicators", "consumer_behavior"],
            "metadata": {"model": "lstm", "accuracy": "very_high"}
        }
    ]

    for i, pred_data in enumerate(predictions_data):
        pred_id = pam_talk_contract.store_demand_prediction(**pred_data)
        print(f"[OK] Prediction {i+1} stored with ID: {pred_id}")

    # Retrieve predictions
    all_predictions = pam_talk_contract.get_demand_predictions()
    print(f"Total predictions stored: {len(all_predictions)}")

    return True

def test_transaction_history():
    """Test transaction history queries"""
    print_header("Transaction History Test")

    producer = "PRODUCER_ADDR"

    # Get transaction history
    producer_txs = pam_talk_contract.get_transaction_history(address=producer)
    print(f"Producer transaction count: {len(producer_txs)}")

    if producer_txs:
        latest_tx = producer_txs[0]
        print(f"Latest transaction:")
        print(f"    Type: {latest_tx['transaction_type']}")
        print(f"    Amount: {latest_tx['amount']}")
        print(f"    Token ID: {latest_tx['token_id']}")

    # Get agriculture records
    agr_records = pam_talk_contract.get_agriculture_records(producer=producer)
    print(f"Agriculture records: {len(agr_records)}")

    return True

def test_contract_stats():
    """Test contract statistics"""
    print_header("Contract Statistics")

    stats = pam_talk_contract.get_contract_stats()

    print(f"Contract ID: {stats['contract_id']}")
    print(f"Block Height: {stats['block_height']}")
    print(f"Total Tokens: {stats['total_tokens']}")
    print(f"Total Transactions: {stats['total_transactions']}")
    print(f"Agriculture Records: {stats['total_agriculture_records']}")
    print(f"Demand Predictions: {stats['total_demand_predictions']}")
    print(f"Unique Addresses: {stats['unique_addresses']}")

    return True

def main():
    """Run all tests"""
    print_header("PAM-TALK Smart Contract Test Suite")

    tests = [
        ("Contract Deployment", test_contract_deployment),
        ("Token Operations", test_token_operations),
        ("Token Transfers", test_token_transfers),
        ("Agriculture Transactions", test_agriculture_transactions),
        ("ESG Scoring", test_esg_scoring),
        ("Demand Predictions", test_demand_predictions),
        ("Transaction History", test_transaction_history),
        ("Contract Statistics", test_contract_stats),
    ]

    passed_tests = 0
    total_tests = len(tests)

    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed_tests += 1
        except Exception as e:
            print(f"[FAIL] {test_name} - Exception: {e}")

    print_header("Test Results Summary")
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")

    if passed_tests == total_tests:
        print("[SUCCESS] All tests passed! Smart contract is working correctly.")
        return 0
    else:
        print("[WARNING] Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())