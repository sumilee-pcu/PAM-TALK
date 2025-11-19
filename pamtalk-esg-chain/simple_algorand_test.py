"""
Simple Algorand Test Script
Real blockchain integration test without database dependencies
"""
import os
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, AssetTransferTxn
import time

class AlgorandTester:
    def __init__(self):
        # Algorand testnet client
        self.algod_address = "https://testnet-api.algonode.cloud"
        self.algod_token = ""
        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address)
        print("Connected to Algorand Testnet!")

    def create_account(self):
        """Create new account"""
        private_key, address = account.generate_account()
        account_mnemonic = mnemonic.from_private_key(private_key)
        return {
            'address': address,
            'private_key': private_key,
            'mnemonic': account_mnemonic
        }

    def check_balance(self, address):
        """Check account balance"""
        try:
            account_info = self.algod_client.account_info(address)
            balance = account_info['amount'] / 1000000  # microAlgos to Algos
            return balance
        except Exception as e:
            print(f"Balance check error: {e}")
            return 0

    def create_pam_token(self, creator_private_key):
        """Create PAM-TALK ESG Token (ASA)"""
        try:
            creator_address = account.address_from_private_key(creator_private_key)

            # Check balance
            balance = self.check_balance(creator_address)
            if balance < 0.1:
                print(f"Insufficient balance: {balance} ALGO")
                print(f"Get test ALGO: https://testnet.algoexplorer.io/dispenser")
                print(f"Address: {creator_address}")
                return None, None

            print(f"Balance: {balance} ALGO - Creating token...")

            # Network parameters
            params = self.algod_client.suggested_params()

            # ASA creation transaction
            txn = AssetConfigTxn(
                sender=creator_address,
                sp=params,
                total=1000000000,  # 1 billion tokens
                default_frozen=False,
                unit_name="PAM",
                asset_name="PAM-TALK ESG Token",
                manager=creator_address,
                reserve=creator_address,
                freeze=creator_address,
                clawback=creator_address,
                url="https://pam-talk.io/esg-token",
                decimals=3,
                note="Agricultural ESG Activity Reward Token".encode()
            )

            # Sign transaction
            stxn = txn.sign(creator_private_key)

            # Send to blockchain
            tx_id = self.algod_client.send_transaction(stxn)
            print(f"Transaction sent: {tx_id}")
            print(f"Explorer: https://testnet.algoexplorer.io/tx/{tx_id}")

            # Wait for confirmation
            print("Waiting for confirmation...")
            confirmed_txn = self.wait_for_confirmation(tx_id)

            # Get ASA ID
            asset_id = confirmed_txn["asset-index"]

            print(f"SUCCESS! PAM-TALK ESG Token Created!")
            print(f"ASA ID: {asset_id}")
            print(f"Token Info: https://testnet.algoexplorer.io/asset/{asset_id}")

            return tx_id, asset_id

        except Exception as e:
            print(f"Token creation error: {e}")
            return None, None

    def opt_in_asset(self, user_private_key, asset_id):
        """Asset opt-in (prepare to receive tokens)"""
        try:
            user_address = account.address_from_private_key(user_private_key)
            params = self.algod_client.suggested_params()

            # opt-in transaction (send 0 tokens to self)
            txn = AssetTransferTxn(
                sender=user_address,
                sp=params,
                receiver=user_address,
                amt=0,
                index=asset_id
            )

            stxn = txn.sign(user_private_key)
            tx_id = self.algod_client.send_transaction(stxn)

            self.wait_for_confirmation(tx_id)

            print(f"SUCCESS! {user_address} ASA opt-in completed")
            print(f"Explorer: https://testnet.algoexplorer.io/tx/{tx_id}")

            return tx_id

        except Exception as e:
            print(f"Opt-in error: {e}")
            return None

    def transfer_tokens(self, sender_private_key, recipient_address, asset_id, amount):
        """Transfer tokens"""
        try:
            sender_address = account.address_from_private_key(sender_private_key)
            params = self.algod_client.suggested_params()

            # Token transfer transaction
            txn = AssetTransferTxn(
                sender=sender_address,
                sp=params,
                receiver=recipient_address,
                amt=amount,
                index=asset_id,
                note=f"PAM-TALK ESG Reward: {amount/1000} PAM".encode()
            )

            stxn = txn.sign(sender_private_key)
            tx_id = self.algod_client.send_transaction(stxn)

            self.wait_for_confirmation(tx_id)

            print(f"SUCCESS! {amount/1000} PAM tokens transferred!")
            print(f"From: {sender_address}")
            print(f"To: {recipient_address}")
            print(f"Explorer: https://testnet.algoexplorer.io/tx/{tx_id}")

            return tx_id

        except Exception as e:
            print(f"Token transfer error: {e}")
            return None

    def wait_for_confirmation(self, tx_id):
        """Wait for transaction confirmation"""
        try:
            confirmed_txn = self.algod_client.pending_transaction_info(tx_id)
            while confirmed_txn.get("confirmed-round", 0) == 0:
                print("Waiting for confirmation...")
                time.sleep(2)
                confirmed_txn = self.algod_client.pending_transaction_info(tx_id)

            print(f"Confirmed! Block: {confirmed_txn['confirmed-round']}")
            return confirmed_txn

        except Exception as e:
            print(f"Confirmation error: {e}")
            raise

def main():
    """Main test execution"""
    print("PAM-TALK ESG Chain Blockchain Test Start!")
    print("=" * 50)

    tester = AlgorandTester()

    # 1. Create admin account
    print("\n1. Creating Admin Account")
    admin_account = tester.create_account()
    print(f"Admin Address: {admin_account['address']}")
    print(f"Mnemonic: {admin_account['mnemonic']}")
    print(f"Get Test ALGO: https://testnet.algoexplorer.io/dispenser")
    print(f"Check Wallet: https://testnet.algoexplorer.io/address/{admin_account['address']}")

    # Wait for user to get ALGO
    input("\nPlease get ALGO from the dispenser above, then press Enter...")

    # 2. Create PAM Token
    print("\n2. Creating PAM-TALK ESG Token")
    tx_hash, asset_id = tester.create_pam_token(admin_account['private_key'])

    if not asset_id:
        print("Token creation failed. Please restart the script.")
        return

    # 3. Create user account
    print("\n3. Creating User Account")
    user_account = tester.create_account()
    print(f"User Address: {user_account['address']}")
    print(f"Check Wallet: https://testnet.algoexplorer.io/address/{user_account['address']}")

    # 4. User opt-in
    print("\n4. User PAM Token Opt-in")
    print(f"User also needs ALGO: https://testnet.algoexplorer.io/dispenser")
    print(f"User Address: {user_account['address']}")
    input("Please get ALGO for user address, then press Enter...")

    opt_in_tx = tester.opt_in_asset(user_account['private_key'], asset_id)

    if opt_in_tx:
        # 5. Transfer tokens (reward payment)
        print("\n5. PAM Token Transfer (Reward Payment)")
        transfer_tx = tester.transfer_tokens(
            admin_account['private_key'],
            user_account['address'],
            asset_id,
            50000  # 50.000 PAM
        )

        if transfer_tx:
            print("\nTEST COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print("FINAL RESULTS:")
            print(f"PAM Token ASA ID: {asset_id}")
            print(f"Token Info: https://testnet.algoexplorer.io/asset/{asset_id}")
            print(f"Admin Wallet: https://testnet.algoexplorer.io/address/{admin_account['address']}")
            print(f"User Wallet: https://testnet.algoexplorer.io/address/{user_account['address']}")
            print(f"Transfer TX: https://testnet.algoexplorer.io/tx/{transfer_tx}")
            print("\nALL LINKS NOW WORK IN REAL BLOCKCHAIN EXPLORER!")

            # Save results to file
            results = {
                'asset_id': asset_id,
                'admin_address': admin_account['address'],
                'admin_mnemonic': admin_account['mnemonic'],
                'user_address': user_account['address'],
                'user_mnemonic': user_account['mnemonic'],
                'creation_tx': tx_hash,
                'transfer_tx': transfer_tx
            }

            with open('blockchain_test_results.txt', 'w') as f:
                f.write("PAM-TALK ESG Chain Blockchain Test Results\n")
                f.write("=" * 50 + "\n")
                f.write(f"ASA ID: {asset_id}\n")
                f.write(f"Token URL: https://testnet.algoexplorer.io/asset/{asset_id}\n")
                f.write(f"Admin Address: {admin_account['address']}\n")
                f.write(f"User Address: {user_account['address']}\n")
                f.write(f"Transfer TX: https://testnet.algoexplorer.io/tx/{transfer_tx}\n")

            print(f"\nResults saved to: blockchain_test_results.txt")

if __name__ == "__main__":
    main()