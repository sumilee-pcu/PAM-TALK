#!/usr/bin/env python3
"""
Monitor the new PAM-TALK account funding
"""

import requests
import time
from datetime import datetime

def monitor_new_account():
    """Monitor the new account until funding is confirmed"""

    new_addr = "HFRJPS4VWQEQMWVPKKDYDTVAJQH2MHNIR37HRNQIPXFMI4BCEKK4OX4ZFI"
    tx_id = "AHMIHQW44N5BFYR6CQJO63GBHUJRE7X3H5ORVHPZ3WWLBYYUTBHQ"

    print("PAM-TALK New Account Monitor")
    print("=" * 40)
    print(f"Account: {new_addr[:25]}...")
    print(f"TX ID: {tx_id[:25]}...")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print()

    max_checks = 20  # 10 minutes maximum
    check_interval = 30  # 30 seconds

    for i in range(max_checks):
        try:
            # Check account balance
            api_url = f"https://testnet-api.algonode.cloud/v2/accounts/{new_addr}"
            response = requests.get(api_url, timeout=10)

            timestamp = datetime.now().strftime("%H:%M:%S")

            if response.status_code == 200:
                data = response.json()
                balance = data.get('account', {}).get('amount', 0) / 1000000
                status = data.get('account', {}).get('status', 'Unknown')

                print(f"[{timestamp}] Balance: {balance:.6f} ALGO, Status: {status}")

                if balance >= 1.0:
                    print()
                    print("SUCCESS: Account funded!")
                    print(f"Final balance: {balance:.6f} ALGO")
                    print()
                    print("NEXT STEPS:")
                    print("1. Update PAM-TALK config with new account")
                    print("2. Create PAM token using new account")
                    print("3. Test ESG chain integration")

                    # Save new account info for PAM-TALK
                    save_config(new_addr, tx_id, balance)
                    return True

            else:
                print(f"[{timestamp}] API Error: {response.status_code}")

        except Exception as e:
            print(f"[{timestamp}] Error: {e}")

        if i < max_checks - 1:  # Don't sleep on last iteration
            print(f"Waiting {check_interval} seconds for next check...")
            time.sleep(check_interval)

    print()
    print("TIMEOUT: Account not funded within 10 minutes")
    print("Possible issues:")
    print("- Algorand testnet congestion")
    print("- API synchronization delay")
    print("- Faucet processing delay")
    print()
    print("Recommendation: Check again in 30 minutes")
    return False

def save_config(address, tx_id, balance):
    """Save new account configuration for PAM-TALK"""

    config_data = f"""# PAM-TALK New Account Configuration
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

NEW_ADMIN_ADDRESS = "{address}"
FUNDING_TX_ID = "{tx_id}"
CONFIRMED_BALANCE = {balance:.6f}

# Usage:
# 1. Update pamtalk-esg-chain config to use NEW_ADMIN_ADDRESS
# 2. Use this account for PAM token creation
# 3. This account has sufficient ALGO for transactions

# Mnemonic (from new_account_info.txt):
# fantasy prize inherit wealth mansion also guide drastic hip cart shoot together design between life have love any stairs enrich ritual rural blame absorb follow
"""

    with open("pam_new_account_config.py", "w") as f:
        f.write(config_data)

    print(f"Configuration saved to: pam_new_account_config.py")

if __name__ == "__main__":
    success = monitor_new_account()

    if success:
        print("Account ready for PAM token creation!")
    else:
        print("Continue monitoring manually or try alternative approaches")