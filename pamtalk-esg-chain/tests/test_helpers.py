"""
Test Helper Functions and Utilities
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Any


class MockTransactionBuilder:
    """Helper to build mock Algorand transactions"""

    @staticmethod
    def application_call(sender: str, app_id: int, args: List[bytes]) -> Dict:
        """Create mock application call transaction"""
        return {
            'type': 'appl',
            'sender': sender,
            'app_id': app_id,
            'app_args': args,
            'timestamp': datetime.now().isoformat(),
            'tx_id': f"TX-{hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:16]}"
        }

    @staticmethod
    def payment(sender: str, receiver: str, amount: int) -> Dict:
        """Create mock payment transaction"""
        return {
            'type': 'pay',
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'tx_id': f"TX-{hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:16]}"
        }

    @staticmethod
    def group_transaction(txns: List[Dict]) -> List[Dict]:
        """Create mock grouped transaction"""
        group_id = f"GRP-{hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:16]}"
        for txn in txns:
            txn['group_id'] = group_id
        return txns


class ContractSimulator:
    """Simulates smart contract execution for testing"""

    def __init__(self):
        self.global_state = {}
        self.local_state = {}
        self.logs = []

    def put_global(self, key: str, value: Any):
        """Simulate global state write"""
        self.global_state[key] = value
        self.logs.append(f"GlobalPut: {key} = {value}")

    def get_global(self, key: str, default=None) -> Any:
        """Simulate global state read"""
        value = self.global_state.get(key, default)
        self.logs.append(f"GlobalGet: {key} -> {value}")
        return value

    def put_local(self, address: str, key: str, value: Any):
        """Simulate local state write"""
        if address not in self.local_state:
            self.local_state[address] = {}
        self.local_state[address][key] = value
        self.logs.append(f"LocalPut({address}): {key} = {value}")

    def get_local(self, address: str, key: str, default=None) -> Any:
        """Simulate local state read"""
        value = self.local_state.get(address, {}).get(key, default)
        self.logs.append(f"LocalGet({address}): {key} -> {value}")
        return value

    def clear_logs(self):
        """Clear execution logs"""
        self.logs = []

    def get_logs(self) -> List[str]:
        """Get execution logs"""
        return self.logs.copy()


class ESGTokenSimulator(ContractSimulator):
    """Simulates ESG-Gold Token contract"""

    def __init__(self, admin_address: str):
        super().__init__()
        self.put_global('total_supply', 0)
        self.put_global('admin_address', admin_address)
        self.put_global('is_paused', 0)

    def opt_in(self, address: str):
        """Simulate opt-in"""
        self.put_local(address, 'balance', 0)
        self.put_local(address, 'frozen', 0)
        return True

    def mint(self, recipient: str, amount: int, sender: str) -> bool:
        """Simulate minting"""
        if self.get_global('is_paused') == 1:
            return False

        # Update balance
        current_balance = self.get_local(recipient, 'balance', 0)
        self.put_local(recipient, 'balance', current_balance + amount)

        # Update total supply
        total_supply = self.get_global('total_supply', 0)
        self.put_global('total_supply', total_supply + amount)

        return True

    def burn(self, sender: str, amount: int) -> bool:
        """Simulate burning"""
        if self.get_global('is_paused') == 1:
            return False

        balance = self.get_local(sender, 'balance', 0)
        if balance < amount:
            return False

        self.put_local(sender, 'balance', balance - amount)

        total_supply = self.get_global('total_supply', 0)
        self.put_global('total_supply', total_supply - amount)

        return True

    def transfer(self, sender: str, recipient: str, amount: int) -> bool:
        """Simulate transfer"""
        if self.get_global('is_paused') == 1:
            return False

        if self.get_local(sender, 'frozen', 0) == 1:
            return False

        sender_balance = self.get_local(sender, 'balance', 0)
        if sender_balance < amount:
            return False

        # Deduct from sender
        self.put_local(sender, 'balance', sender_balance - amount)

        # Add to recipient
        recipient_balance = self.get_local(recipient, 'balance', 0)
        self.put_local(recipient, 'balance', recipient_balance + amount)

        return True


class RewardSimulator(ContractSimulator):
    """Simulates Auto Reward contract"""

    def __init__(self, admin_address: str, token_app_id: int):
        super().__init__()
        self.put_global('admin_address', admin_address)
        self.put_global('token_app_id', token_app_id)
        self.put_global('reward_rate', 1000)
        self.put_global('total_distributed', 0)

    def opt_in(self, address: str):
        """Simulate opt-in"""
        self.put_local(address, 'pending_rewards', 0)
        self.put_local(address, 'claimed_rewards', 0)
        self.put_local(address, 'total_carbon_reduction', 0)
        return True

    def register_activity(self, sender: str, carbon_kg: int) -> int:
        """Simulate registering carbon reduction activity"""
        reward_rate = self.get_global('reward_rate', 1000)
        reward = carbon_kg * reward_rate

        # Update user stats
        pending = self.get_local(sender, 'pending_rewards', 0)
        self.put_local(sender, 'pending_rewards', pending + reward)

        carbon = self.get_local(sender, 'total_carbon_reduction', 0)
        self.put_local(sender, 'total_carbon_reduction', carbon + carbon_kg)

        return reward

    def claim_reward(self, sender: str, token_simulator: ESGTokenSimulator) -> int:
        """Simulate claiming rewards"""
        reward = self.get_local(sender, 'pending_rewards', 0)
        if reward == 0:
            return 0

        # Mint tokens (simulated inner transaction)
        token_simulator.mint(sender, reward, self.get_global('admin_address'))

        # Update balances
        self.put_local(sender, 'pending_rewards', 0)

        claimed = self.get_local(sender, 'claimed_rewards', 0)
        self.put_local(sender, 'claimed_rewards', claimed + reward)

        total_dist = self.get_global('total_distributed', 0)
        self.put_global('total_distributed', total_dist + reward)

        return reward


class SettlementSimulator(ContractSimulator):
    """Simulates Charging Settlement contract"""

    def __init__(self, admin_address: str, token_app_id: int):
        super().__init__()
        self.put_global('admin_address', admin_address)
        self.put_global('token_app_id', token_app_id)
        self.put_global('platform_fee_rate', 500)  # 5%
        self.put_global('total_volume', 0)
        self.stations = {}
        self.settlements = {}

    def register_station(self, station_id: str, operator: str, admin: str) -> bool:
        """Simulate registering station"""
        if admin != self.get_global('admin_address'):
            return False

        self.stations[station_id] = {
            'operator': operator,
            'status': 1,
            'volume': 0,
            'fees_paid': 0,
            'pending': 0,
            'settled': 0
        }
        return True

    def record_transaction(self, station_id: str, amount: int) -> Dict:
        """Simulate recording charging transaction"""
        if station_id not in self.stations or self.stations[station_id]['status'] != 1:
            return {'success': False}

        fee_rate = self.get_global('platform_fee_rate', 500)
        fee = (amount * fee_rate) // 10000
        net = amount - fee

        station = self.stations[station_id]
        station['volume'] += amount
        station['fees_paid'] += fee
        station['pending'] += net

        total_vol = self.get_global('total_volume', 0)
        self.put_global('total_volume', total_vol + amount)

        return {
            'success': True,
            'amount': amount,
            'fee': fee,
            'net': net
        }

    def request_settlement(self, station_id: str, settlement_id: str, operator: str) -> bool:
        """Simulate settlement request"""
        if station_id not in self.stations:
            return False

        station = self.stations[station_id]
        if station['operator'] != operator:
            return False

        if station['pending'] == 0:
            return False

        self.settlements[settlement_id] = {
            'station_id': station_id,
            'amount': station['pending'],
            'status': 0  # Pending
        }
        return True

    def approve_settlement(self, settlement_id: str, admin: str) -> bool:
        """Simulate settlement approval"""
        if admin != self.get_global('admin_address'):
            return False

        if settlement_id not in self.settlements:
            return False

        self.settlements[settlement_id]['status'] = 1  # Approved
        return True


class EscrowSimulator(ContractSimulator):
    """Simulates Enterprise Escrow contract"""

    def __init__(self, admin_address: str, token_app_id: int):
        super().__init__()
        self.put_global('admin_address', admin_address)
        self.put_global('token_app_id', token_app_id)
        self.put_global('total_escrowed', 0)
        self.escrows = {}

    def create_escrow(self, escrow_id: str, buyer: str, seller: str, amount: int) -> bool:
        """Simulate creating escrow"""
        self.escrows[escrow_id] = {
            'buyer': buyer,
            'seller': seller,
            'amount': amount,
            'deposit_amount': 0,
            'status': 0,  # Created
            'buyer_confirmed': False,
            'seller_confirmed': False
        }
        return True

    def deposit_funds(self, escrow_id: str, buyer: str, token_simulator: ESGTokenSimulator) -> bool:
        """Simulate depositing funds"""
        if escrow_id not in self.escrows:
            return False

        escrow = self.escrows[escrow_id]
        if escrow['buyer'] != buyer or escrow['status'] != 0:
            return False

        # Transfer tokens from buyer to escrow (simulated)
        amount = escrow['amount']
        if not token_simulator.transfer(buyer, 'ESCROW_CONTRACT', amount):
            return False

        escrow['deposit_amount'] = amount
        escrow['status'] = 1  # Funded

        total_esc = self.get_global('total_escrowed', 0)
        self.put_global('total_escrowed', total_esc + amount)

        return True

    def confirm_shipment(self, escrow_id: str, seller: str) -> bool:
        """Simulate confirming shipment"""
        if escrow_id not in self.escrows:
            return False

        escrow = self.escrows[escrow_id]
        if escrow['seller'] != seller or escrow['status'] != 1:
            return False

        escrow['seller_confirmed'] = True
        escrow['status'] = 2  # Shipped
        return True

    def confirm_receipt(self, escrow_id: str, buyer: str) -> bool:
        """Simulate confirming receipt"""
        if escrow_id not in self.escrows:
            return False

        escrow = self.escrows[escrow_id]
        if escrow['buyer'] != buyer or escrow['status'] != 2:
            return False

        escrow['buyer_confirmed'] = True
        return True

    def release_funds(self, escrow_id: str, token_simulator: ESGTokenSimulator) -> bool:
        """Simulate releasing funds"""
        if escrow_id not in self.escrows:
            return False

        escrow = self.escrows[escrow_id]
        if not (escrow['buyer_confirmed'] and escrow['seller_confirmed']):
            return False

        # Transfer from escrow to seller (simulated)
        amount = escrow['amount']
        token_simulator.transfer('ESCROW_CONTRACT', escrow['seller'], amount)

        escrow['status'] = 3  # Completed

        total_esc = self.get_global('total_escrowed', 0)
        self.put_global('total_escrowed', total_esc - amount)

        return True


def generate_test_data():
    """Generate test data for integration tests"""
    return {
        'users': [
            {'id': 'USER001', 'name': 'Test User 1', 'address': 'ADDR1'},
            {'id': 'USER002', 'name': 'Test User 2', 'address': 'ADDR2'},
            {'id': 'USER003', 'name': 'Test User 3', 'address': 'ADDR3'},
        ],
        'stations': [
            {'id': 'STATION001', 'name': 'Seoul Station', 'operator': 'ADDR4'},
            {'id': 'STATION002', 'name': 'Busan Station', 'operator': 'ADDR5'},
        ],
        'enterprises': [
            {'id': 'ENT001', 'name': 'Samsung', 'address': 'ADDR6'},
            {'id': 'ENT002', 'name': 'LG', 'address': 'ADDR7'},
        ],
        'activities': [
            {'user': 'USER001', 'carbon_kg': 100, 'type': 'public_transport'},
            {'user': 'USER002', 'carbon_kg': 50, 'type': 'bicycle'},
            {'user': 'USER003', 'carbon_kg': 75, 'type': 'ev_charging'},
        ]
    }
