"""
Simple Balance Checker
"""
import requests

def check_balance():
    address = "HXEHBWEDLO272XOIFFME26D5EAWULT4PGE75V3NKGGBIMQL2JM7S4ZU5PM"

    try:
        api_url = f"https://testnet-api.algonode.cloud/v2/accounts/{address}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            balance = data.get("amount", 0) / 1000000
            print(f"Admin Balance: {balance} ALGO")

            if balance > 0:
                print("Ready to create PAM token!")
                print("Run: python step2_create_token.py")
                return True
            else:
                print("Still need ALGO from faucet")
                return False
        else:
            print(f"API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_balance()