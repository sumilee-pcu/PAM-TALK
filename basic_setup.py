#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Algorand LocalNet Setup Script

This script demonstrates the Algorand LocalNet simulation environment setup.
It creates test accounts, assigns balances, and tests basic operations.
"""

import os
import sys
from algorand_utils import AlgorandSimulator

# Set console encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 50}")
    print(f" {title}")
    print(f"{'=' * 50}")

def print_account_info(simulator, role, account):
    """Print detailed account information"""
    if not account:
        print(f"❌ {role.capitalize()} account not found")
        return

    account_info = simulator.get_account_info(account['address'])
    print(f"\n📋 {role.upper()} ACCOUNT:")
    print(f"   Address: {account['address']}")
    print(f"   Balance: {account_info['balance']:,} microALGO ({account_info['balance_algo']:.2f} ALGO)")
    print(f"   Role: {account_info['role']}")
    print(f"   Mnemonic: {account['mnemonic'][:50]}...")

def test_transfers(simulator):
    """Test ALGO transfers between accounts"""
    print_header("Testing ALGO Transfers")

    producer = simulator.test_accounts['producer']
    consumer = simulator.test_accounts['consumer']
    government = simulator.test_accounts['government']

    if not all([producer, consumer, government]):
        print("❌ Missing test accounts for transfer test")
        return

    # Test 1: Producer to Consumer
    print("\n🔄 Test 1: Producer sends 100 ALGO to Consumer")
    result = simulator.transfer_algo(
        sender_address=producer['address'],
        sender_private_key=producer['private_key'],
        receiver_address=consumer['address'],
        amount=100_000_000,  # 100 ALGO in microalgos
        note="Energy payment"
    )

    if result['success']:
        print(f"✅ Transfer successful: {result['txid']}")
        print(f"   Amount: {result['amount']:,} microALGO")
        print(f"   Note: {result['note']}")
    else:
        print(f"❌ Transfer failed: {result['error']}")

    # Test 2: Government tax collection
    print("\n🔄 Test 2: Government collects 10 ALGO tax from Producer")
    result = simulator.transfer_algo(
        sender_address=producer['address'],
        sender_private_key=producer['private_key'],
        receiver_address=government['address'],
        amount=10_000_000,  # 10 ALGO
        note="Energy tax"
    )

    if result['success']:
        print(f"✅ Tax collection successful: {result['txid']}")
    else:
        print(f"❌ Tax collection failed: {result['error']}")

def display_final_balances(simulator):
    """Display final account balances"""
    print_header("Final Account Balances")

    for role, account in simulator.test_accounts.items():
        if account:
            account_info = simulator.get_account_info(account['address'])
            print(f"{role.capitalize():>10}: {account_info['balance_algo']:>10.2f} ALGO")

def save_and_load_test(simulator):
    """Test saving and loading account data"""
    print_header("Testing Account Persistence")

    # Save accounts
    filename = "test_accounts_demo.json"
    simulator.save_accounts_to_file(filename)

    # Create new simulator and load accounts
    print("🔄 Testing account loading...")
    new_simulator = AlgorandSimulator()
    if new_simulator.load_accounts_from_file(filename):
        print("✅ Account loading successful")

        # Verify loaded accounts
        for role in ['producer', 'consumer', 'government']:
            if new_simulator.test_accounts[role]:
                original_addr = simulator.test_accounts[role]['address']
                loaded_addr = new_simulator.test_accounts[role]['address']
                if original_addr == loaded_addr:
                    print(f"✅ {role.capitalize()} account verified")
                else:
                    print(f"❌ {role.capitalize()} account mismatch")
    else:
        print("❌ Account loading failed")

    # Cleanup
    try:
        os.remove(filename)
        print(f"🧹 Cleaned up {filename}")
    except:
        pass

def main():
    """Main setup and demonstration function"""
    print_header("PAM-TALK Algorand LocalNet Setup")

    # Initialize simulator
    print(">> Initializing Algorand Simulator...")
    simulator = AlgorandSimulator()

    # Display network status
    print_header("Network Status")
    status = simulator.get_network_status()
    print(f"Mode: {status['mode']}")
    print(f"Connected: {status['connected']}")

    if status['mode'] == 'simulation':
        print(f"Network: {status['network']}")
        print(f"Accounts: {status.get('accounts', 0)}")
        print(f"Total Balance: {status.get('total_balance', 0):,} microALGO")
    elif status['mode'] == 'real':
        print(f"Network: {status['network']}")
        print(f"Last Round: {status.get('last_round', 0)}")
        print(f"Node Address: {status.get('node_address', 'N/A')}")
    else:
        print(f"Error: {status.get('error', 'Unknown error')}")

    # Create test accounts
    print_header("Creating Test Accounts")
    try:
        # Try to load existing accounts first
        if simulator.load_accounts_from_file():
            print("📁 Loaded existing test accounts")
        else:
            print("🔨 Creating new test accounts...")
            simulator.create_test_accounts()
            print("✅ Test accounts created successfully")
    except Exception as e:
        print(f"❌ Failed to create test accounts: {e}")
        return 1

    # Display account information
    print_header("Account Information")
    for role, account in simulator.test_accounts.items():
        print_account_info(simulator, role, account)

    # Test transfers if in simulation mode
    if simulator.simulation_mode:
        test_transfers(simulator)
        display_final_balances(simulator)

    # Test account persistence
    save_and_load_test(simulator)

    # Connection test
    print_header("Connection Test Results")
    if simulator.is_connected:
        print("✅ Successfully connected to Algorand node")
        print(f"   Network: {simulator.config.ALGORAND_NETWORK}")
        print(f"   Address: {simulator.config.ALGORAND_ALGOD_ADDRESS}")
    else:
        print("⚠️  Running in simulation mode")
        print("   To connect to a real network:")
        print("   1. Start Algorand sandbox or local node")
        print("   2. Update .env with correct ALGORAND_ALGOD_ADDRESS and TOKEN")
        print("   3. Set SIMULATION_MODE=False")

    print_header("Setup Complete")
    print("🎉 PAM-TALK Algorand environment is ready!")
    print("\nNext steps:")
    print("1. Update .env with your Algorand node credentials (if using real network)")
    print("2. Run smart contract deployment scripts")
    print("3. Start the Flask API server with: python app.py")

    return 0

if __name__ == "__main__":
    sys.exit(main())