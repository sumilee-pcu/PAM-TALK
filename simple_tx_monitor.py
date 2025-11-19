#!/usr/bin/env python3
"""
Simple Transaction Monitor for PAM-TALK
ASCII-only output for Windows compatibility
"""

import requests
import time
from datetime import datetime

def check_status():
    """Check PAM-TALK transaction and account status"""

    print("PAM-TALK Transaction & Account Monitor")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Configuration
    tx_id = "IGZONMA3F64TZHDY3IP2DBV3VMEQRO4GQZVTRXXRNDXNKQ5N7MXQ"
    admin_addr = "MM7ZDYCD4RD5CVUO5RO6NAA7K7S7T7REFYEVQJ5AGQWVB63G7JD66SDKBM"

    # Check account balance
    print("1. ACCOUNT STATUS")
    print("-" * 20)
    try:
        url = f"https://testnet-api.algonode.cloud/v2/accounts/{admin_addr}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            balance = data.get('account', {}).get('amount', 0) / 1000000
            status = data.get('account', {}).get('status', 'Unknown')

            print(f"Address: {admin_addr[:25]}...")
            print(f"Balance: {balance:.6f} ALGO")
            print(f"Status: {status}")

            if balance > 0:
                print("SUCCESS: Account has ALGO!")
                funding_status = "COMPLETED"
            else:
                print("WAITING: Account needs ALGO")
                funding_status = "PENDING"
        else:
            print(f"ERROR: Account API returned {response.status_code}")
            funding_status = "ERROR"
            balance = 0
    except Exception as e:
        print(f"ERROR: Account check failed - {e}")
        funding_status = "ERROR"
        balance = 0

    print()

    # Check transaction status
    print("2. TRANSACTION STATUS")
    print("-" * 25)
    try:
        url = f"https://testnet-api.algonode.cloud/v2/transactions/{tx_id}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            tx_data = data.get('transaction', {})
            round_num = tx_data.get('confirmed-round')

            print(f"TX ID: {tx_id[:30]}...")
            print(f"Status: CONFIRMED")
            print(f"Round: {round_num}")

            # Payment details
            if 'payment-transaction' in tx_data:
                payment = tx_data['payment-transaction']
                amount = payment.get('amount', 0) / 1000000
                print(f"Amount: {amount:.6f} ALGO")

            tx_status = "CONFIRMED"

        elif response.status_code == 404:
            print(f"TX ID: {tx_id[:30]}...")
            print("Status: PENDING (not on blockchain yet)")
            print("Note: May take several minutes to confirm")
            tx_status = "PENDING"
        else:
            print(f"ERROR: Transaction API returned {response.status_code}")
            tx_status = "ERROR"
    except Exception as e:
        print(f"ERROR: Transaction check failed - {e}")
        tx_status = "ERROR"

    print()

    # Summary and recommendations
    print("3. SUMMARY & NEXT STEPS")
    print("-" * 30)

    if funding_status == "COMPLETED":
        print("FUNDING: COMPLETE")
        print("NEXT: Ready to create PAM token")
        print("COMMAND: cd pamtalk-esg-chain && python step2_create_token.py")
    elif tx_status == "CONFIRMED" and funding_status == "PENDING":
        print("FUNDING: Transaction confirmed but balance not updated")
        print("WAIT: API may be delayed, check again in 5 minutes")
    elif tx_status == "PENDING":
        print("FUNDING: Transaction still processing")
        print("WAIT: Check again in 10-30 minutes")
    else:
        print("FUNDING: May need to retry")
        print("ACTION: Try alternative faucet or create new account")

    print()

    # Status summary
    print("4. STATUS SUMMARY")
    print("-" * 20)
    print(f"Account Balance: {balance:.6f} ALGO")
    print(f"Transaction: {tx_status}")
    print(f"Overall Status: {funding_status}")

    return {
        'balance': balance,
        'tx_status': tx_status,
        'funding_status': funding_status,
        'timestamp': datetime.now().isoformat()
    }

def continuous_monitor(duration_minutes=30):
    """Monitor continuously for specified duration"""
    print(f"Starting continuous monitoring for {duration_minutes} minutes...")
    print("Press Ctrl+C to stop early")
    print()

    start_time = datetime.now()
    check_interval = 60  # seconds

    try:
        while True:
            result = check_status()

            # Stop if funding is complete
            if result['funding_status'] == 'COMPLETED':
                print("MONITOR: Funding completed! Stopping monitor.")
                break

            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds() / 60
            if elapsed >= duration_minutes:
                print(f"MONITOR: Timeout reached ({duration_minutes} minutes)")
                break

            print(f"MONITOR: Waiting {check_interval} seconds for next check...")
            print("=" * 50)
            time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\\nMONITOR: Stopped by user")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        continuous_monitor(30)
    else:
        check_status()