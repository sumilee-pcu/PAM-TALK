import json
import time
from typing import Dict, List, Optional, Tuple
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn, wait_for_confirmation
from algosdk.error import AlgodHTTPError
from config import Config

class AlgorandSimulator:
    def __init__(self):
        self.config = Config()
        self.simulation_mode = self.config.SIMULATION_MODE
        self.accounts_data = {}
        self.balance_data = {}

        # Initialize test accounts
        self.test_accounts = {
            'producer': None,
            'consumer': None,
            'government': None
        }

        # Try to connect to real algod, fall back to simulation
        self.algod_client = None
        self.is_connected = False
        self._try_connect()

    def _try_connect(self):
        """Try to connect to Algorand node, fall back to simulation mode"""
        try:
            self.algod_client = algod.AlgodClient(
                self.config.ALGORAND_ALGOD_TOKEN,
                self.config.ALGORAND_ALGOD_ADDRESS
            )
            # Test connection
            status = self.algod_client.status()
            self.is_connected = True
            self.simulation_mode = False
            print(f"✅ Connected to Algorand node: {self.config.ALGORAND_ALGOD_ADDRESS}")
            print(f"Network: {status.get('genesis-id', 'Unknown')}")
        except Exception as e:
            print(f"⚠️  Cannot connect to Algorand node: {e}")
            print("🔄 Falling back to simulation mode")
            self.simulation_mode = True
            self.is_connected = False

    def create_account(self, role: str = None) -> Dict:
        """Create a new account with optional role"""
        private_key, address = account.generate_account()
        account_mnemonic = mnemonic.from_private_key(private_key)

        account_info = {
            'address': address,
            'private_key': private_key,
            'mnemonic': account_mnemonic,
            'role': role or 'user',
            'balance': 0
        }

        # Store account data
        self.accounts_data[address] = account_info

        # Initialize balance in simulation mode
        if self.simulation_mode:
            self.balance_data[address] = self.config.INITIAL_BALANCE
            account_info['balance'] = self.config.INITIAL_BALANCE

        return account_info

    def get_balance(self, address: str) -> int:
        """Get account balance (simulation or real)"""
        if self.simulation_mode:
            return self.balance_data.get(address, 0)
        else:
            try:
                account_info = self.algod_client.account_info(address)
                return account_info.get('amount', 0)
            except Exception as e:
                print(f"Error getting balance for {address}: {e}")
                return 0

    def transfer_algo(self, sender_address: str, sender_private_key: str,
                     receiver_address: str, amount: int, note: str = "") -> Dict:
        """Transfer ALGO between accounts"""
        if self.simulation_mode:
            return self._simulate_transfer(sender_address, receiver_address, amount, note)
        else:
            return self._real_transfer(sender_address, sender_private_key, receiver_address, amount, note)

    def _simulate_transfer(self, sender: str, receiver: str, amount: int, note: str) -> Dict:
        """Simulate ALGO transfer"""
        sender_balance = self.balance_data.get(sender, 0)

        if sender_balance < amount:
            return {
                'success': False,
                'error': f'Insufficient balance: {sender_balance} < {amount}',
                'txid': None
            }

        # Update balances
        self.balance_data[sender] = sender_balance - amount
        self.balance_data[receiver] = self.balance_data.get(receiver, 0) + amount

        # Generate fake transaction ID
        fake_txid = f"SIM{int(time.time())}{hash(f'{sender}{receiver}{amount}') % 1000000}"

        return {
            'success': True,
            'txid': fake_txid,
            'amount': amount,
            'sender': sender,
            'receiver': receiver,
            'note': note,
            'simulation': True
        }

    def _real_transfer(self, sender: str, sender_private_key: str,
                      receiver: str, amount: int, note: str) -> Dict:
        """Execute real ALGO transfer"""
        try:
            params = self.algod_client.suggested_params()

            txn = PaymentTxn(
                sender=sender,
                sp=params,
                receiver=receiver,
                amt=amount,
                note=note.encode()
            )

            signed_txn = txn.sign(sender_private_key)
            txid = self.algod_client.send_transaction(signed_txn)

            # Wait for confirmation
            wait_for_confirmation(self.algod_client, txid, 4)

            return {
                'success': True,
                'txid': txid,
                'amount': amount,
                'sender': sender,
                'receiver': receiver,
                'note': note,
                'simulation': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'txid': None
            }

    def create_test_accounts(self) -> Dict:
        """Create test accounts for producer, consumer, and government"""
        roles = ['producer', 'consumer', 'government']

        for role in roles:
            account_info = self.create_account(role)
            self.test_accounts[role] = account_info
            print(f"✅ Created {role} account: {account_info['address'][:8]}...")

        return self.test_accounts

    def get_network_status(self) -> Dict:
        """Get network status information"""
        if self.simulation_mode:
            return {
                'mode': 'simulation',
                'connected': False,
                'network': 'local_simulation',
                'accounts': len(self.accounts_data),
                'total_balance': sum(self.balance_data.values())
            }
        else:
            try:
                status = self.algod_client.status()
                return {
                    'mode': 'real',
                    'connected': True,
                    'network': status.get('genesis-id', 'Unknown'),
                    'last_round': status.get('last-round', 0),
                    'node_address': self.config.ALGORAND_ALGOD_ADDRESS
                }
            except Exception as e:
                return {
                    'mode': 'error',
                    'connected': False,
                    'error': str(e)
                }

    def get_account_info(self, address: str) -> Dict:
        """Get detailed account information"""
        base_info = self.accounts_data.get(address, {})
        balance = self.get_balance(address)

        return {
            'address': address,
            'balance': balance,
            'balance_algo': balance / 1000000,  # Convert microalgos to ALGO
            'role': base_info.get('role', 'unknown'),
            'simulation': self.simulation_mode
        }

    def save_accounts_to_file(self, filename: str = 'test_accounts.json'):
        """Save account information to JSON file"""
        accounts_export = {}

        for role, account in self.test_accounts.items():
            if account:
                accounts_export[role] = {
                    'address': account['address'],
                    'mnemonic': account['mnemonic'],
                    'role': account['role'],
                    'balance': self.get_balance(account['address'])
                }

        with open(filename, 'w') as f:
            json.dump(accounts_export, f, indent=2)

        print(f"💾 Accounts saved to {filename}")

    def load_accounts_from_file(self, filename: str = 'test_accounts.json'):
        """Load account information from JSON file"""
        try:
            with open(filename, 'r') as f:
                accounts_data = json.load(f)

            for role, account_data in accounts_data.items():
                if role in self.test_accounts:
                    # Reconstruct account info
                    private_key = mnemonic.to_private_key(account_data['mnemonic'])
                    self.test_accounts[role] = {
                        'address': account_data['address'],
                        'private_key': private_key,
                        'mnemonic': account_data['mnemonic'],
                        'role': account_data['role'],
                        'balance': account_data.get('balance', 0)
                    }

                    self.accounts_data[account_data['address']] = self.test_accounts[role]

                    if self.simulation_mode:
                        self.balance_data[account_data['address']] = account_data.get('balance', self.config.INITIAL_BALANCE)

            print(f"📁 Accounts loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"⚠️  File {filename} not found")
            return False
        except Exception as e:
            print(f"❌ Error loading accounts: {e}")
            return False