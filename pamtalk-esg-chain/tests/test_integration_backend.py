"""
Integration Tests for Backend-Contract Integration
Tests the integration between backend services and smart contracts
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_helpers import ESGTokenSimulator, RewardSimulator, SettlementSimulator, EscrowSimulator


class MockBackendService:
    """Mock backend service for testing integration"""

    def __init__(self, contract_simulator):
        self.contract = contract_simulator
        self.database = {}

    def save_to_db(self, key, value):
        """Save data to mock database"""
        self.database[key] = value

    def get_from_db(self, key):
        """Retrieve data from mock database"""
        return self.database.get(key)


class TestRewardServiceIntegration:
    """Test integration between reward service and contract"""

    def test_activity_registration_flow(self):
        """
        Test complete flow from API to contract
        1. User submits activity via API
        2. Backend validates and stores in DB
        3. Backend calls contract to record activity
        4. Rewards calculated and stored
        """
        admin = "ADMIN"
        user = "USER001"

        # Initialize
        token = ESGTokenSimulator(admin)
        reward_contract = RewardSimulator(admin, 1001)
        backend_service = MockBackendService(reward_contract)

        # Setup
        token.opt_in(user)
        reward_contract.opt_in(user)

        # Simulate API request
        activity_data = {
            'user_id': user,
            'carbon_kg': 75,
            'activity_type': 'public_transport',
            'evidence_hash': 'ABC123',
            'timestamp': '2025-01-15T10:30:00'
        }

        # Backend processing
        # 1. Validate data
        assert activity_data['carbon_kg'] > 0
        assert activity_data['user_id'] == user

        # 2. Save to database
        activity_id = f"ACT_{activity_data['timestamp']}_{user}"
        backend_service.save_to_db(activity_id, activity_data)

        # 3. Call contract
        reward_amount = reward_contract.register_activity(
            user,
            activity_data['carbon_kg']
        )

        # 4. Update database with reward info
        activity_data['reward_amount'] = reward_amount
        backend_service.save_to_db(activity_id, activity_data)

        # Verify
        stored_activity = backend_service.get_from_db(activity_id)
        assert stored_activity['reward_amount'] == 75000  # 75 kg * 1000

        # Verify contract state
        assert reward_contract.get_local(user, 'pending_rewards') == 75000
        assert reward_contract.get_local(user, 'total_carbon_reduction') == 75

    def test_claim_reward_integration(self):
        """
        Test reward claim process
        1. User requests to claim via API
        2. Backend checks pending rewards
        3. Backend calls contract to mint tokens
        4. Backend updates transaction history
        """
        admin = "ADMIN"
        user = "USER001"

        # Initialize
        token = ESGTokenSimulator(admin)
        reward_contract = RewardSimulator(admin, 1001)
        backend_service = MockBackendService(reward_contract)

        # Setup
        token.opt_in(user)
        reward_contract.opt_in(user)

        # Register some activities first
        reward_contract.register_activity(user, 100)

        # User requests claim
        claim_request = {
            'user_id': user,
            'timestamp': '2025-01-15T11:00:00'
        }

        # Backend processing
        # 1. Check pending rewards
        pending = reward_contract.get_local(user, 'pending_rewards')
        assert pending > 0

        # 2. Call contract to claim
        claimed_amount = reward_contract.claim_reward(user, token)

        # 3. Save transaction to DB
        claim_id = f"CLAIM_{claim_request['timestamp']}_{user}"
        claim_record = {
            **claim_request,
            'amount': claimed_amount,
            'status': 'completed'
        }
        backend_service.save_to_db(claim_id, claim_record)

        # Verify
        stored_claim = backend_service.get_from_db(claim_id)
        assert stored_claim['amount'] == 100000
        assert stored_claim['status'] == 'completed'

        # Verify contract state
        assert reward_contract.get_local(user, 'pending_rewards') == 0
        assert reward_contract.get_local(user, 'claimed_rewards') == 100000
        assert token.get_local(user, 'balance') == 100000


class TestChargingServiceIntegration:
    """Test integration between charging service and settlement contract"""

    def test_charging_transaction_flow(self):
        """
        Test charging flow from QR scan to settlement
        1. User scans QR code at station
        2. Backend generates transaction
        3. Payment processed
        4. Contract records transaction
        5. Receipt generated
        """
        admin = "ADMIN"
        user = "USER001"
        operator = "OPERATOR001"
        station_id = "STATION001"

        # Initialize
        token = ESGTokenSimulator(admin)
        settlement_contract = SettlementSimulator(admin, 1001)
        backend_service = MockBackendService(settlement_contract)

        # Setup
        token.opt_in(user)
        token.opt_in(operator)
        token.mint(user, 100000, admin)
        settlement_contract.register_station(station_id, operator, admin)

        # User initiates charging
        charging_request = {
            'user_id': user,
            'station_id': station_id,
            'amount': 50000,
            'qr_code': 'QR123456',
            'timestamp': '2025-01-15T12:00:00'
        }

        # Backend processing
        # 1. Validate QR code and station
        assert charging_request['station_id'] in settlement_contract.stations

        # 2. Process payment (token transfer)
        payment_result = token.transfer(
            user,
            operator,
            charging_request['amount']
        )
        assert payment_result is True

        # 3. Record in contract
        tx_result = settlement_contract.record_transaction(
            station_id,
            charging_request['amount']
        )

        # 4. Generate receipt and save
        receipt = {
            **charging_request,
            'fee': tx_result['fee'],
            'net_amount': tx_result['net'],
            'status': 'completed',
            'receipt_id': f"RCP_{charging_request['timestamp']}"
        }
        backend_service.save_to_db(receipt['receipt_id'], receipt)

        # Verify
        stored_receipt = backend_service.get_from_db(receipt['receipt_id'])
        assert stored_receipt['fee'] == 2500  # 5% of 50000
        assert stored_receipt['net_amount'] == 47500

        # Verify contract state
        station = settlement_contract.stations[station_id]
        assert station['volume'] == 50000
        assert station['pending'] == 47500

    def test_settlement_process_integration(self):
        """
        Test settlement request and approval flow
        """
        admin = "ADMIN"
        operator = "OPERATOR001"
        station_id = "STATION001"

        # Initialize
        settlement_contract = SettlementSimulator(admin, 1001)
        backend_service = MockBackendService(settlement_contract)

        # Setup
        settlement_contract.register_station(station_id, operator, admin)
        settlement_contract.record_transaction(station_id, 100000)

        # Operator requests settlement
        settlement_request = {
            'operator_id': operator,
            'station_id': station_id,
            'period': '2025-01-01_2025-01-15',
            'timestamp': '2025-01-15T23:59:59'
        }

        # Backend processing
        settlement_id = f"SETTLE_{settlement_request['timestamp']}"

        # 1. Create settlement request in contract
        result = settlement_contract.request_settlement(
            station_id,
            settlement_id,
            operator
        )
        assert result is True

        # 2. Save to database
        settlement_data = {
            **settlement_request,
            'settlement_id': settlement_id,
            'amount': settlement_contract.settlements[settlement_id]['amount'],
            'status': 'pending'
        }
        backend_service.save_to_db(settlement_id, settlement_data)

        # Admin approves
        approval_result = settlement_contract.approve_settlement(settlement_id, admin)
        assert approval_result is True

        # Update database
        settlement_data['status'] = 'approved'
        backend_service.save_to_db(settlement_id, settlement_data)

        # Verify
        final_settlement = backend_service.get_from_db(settlement_id)
        assert final_settlement['status'] == 'approved'
        assert final_settlement['amount'] == 95000  # 100000 - 5%


class TestEnterpriseServiceIntegration:
    """Test integration between enterprise service and escrow contract"""

    def test_b2b_purchase_flow(self):
        """
        Test complete B2B purchase flow
        1. Enterprise creates purchase order
        2. Escrow created
        3. Payment deposited
        4. Shipment tracking
        5. Receipt confirmation
        6. Fund release
        """
        admin = "ADMIN"
        buyer = "SAMSUNG"
        seller = "FARM_COOP"

        # Initialize
        token = ESGTokenSimulator(admin)
        escrow_contract = EscrowSimulator(admin, 1001)
        backend_service = MockBackendService(escrow_contract)

        # Setup
        token.opt_in(buyer)
        token.opt_in(seller)
        token.opt_in('ESCROW_CONTRACT')
        token.mint(buyer, 10000000, admin)

        # Enterprise creates purchase order
        purchase_order = {
            'buyer_id': buyer,
            'seller_id': seller,
            'amount': 5000000,
            'products': [
                {'name': 'Organic Rice', 'quantity': 1000, 'unit': 'kg'},
                {'name': 'Fresh Vegetables', 'quantity': 500, 'unit': 'kg'}
            ],
            'delivery_date': '2025-02-01',
            'timestamp': '2025-01-15T09:00:00'
        }

        # Backend processing
        po_id = f"PO_{purchase_order['timestamp']}"
        escrow_id = f"ESC_{po_id}"

        # 1. Save PO to database
        backend_service.save_to_db(po_id, purchase_order)

        # 2. Create escrow in contract
        escrow_contract.create_escrow(
            escrow_id,
            buyer,
            seller,
            purchase_order['amount']
        )

        # 3. Update PO with escrow info
        purchase_order['escrow_id'] = escrow_id
        purchase_order['status'] = 'escrow_created'
        backend_service.save_to_db(po_id, purchase_order)

        # 4. Buyer deposits funds
        deposit_result = escrow_contract.deposit_funds(escrow_id, buyer, token)
        assert deposit_result is True

        purchase_order['status'] = 'funded'
        backend_service.save_to_db(po_id, purchase_order)

        # 5. Seller ships and confirms
        shipment_data = {
            'escrow_id': escrow_id,
            'tracking_number': 'TRACK123456',
            'carrier': 'Korea Post',
            'timestamp': '2025-01-20T10:00:00'
        }

        escrow_contract.confirm_shipment(escrow_id, seller)
        purchase_order['shipment'] = shipment_data
        purchase_order['status'] = 'shipped'
        backend_service.save_to_db(po_id, purchase_order)

        # 6. Buyer receives and confirms
        receipt_data = {
            'escrow_id': escrow_id,
            'quality_check': 'passed',
            'timestamp': '2025-01-25T14:00:00'
        }

        escrow_contract.confirm_receipt(escrow_id, buyer)
        purchase_order['receipt'] = receipt_data
        purchase_order['status'] = 'received'
        backend_service.save_to_db(po_id, purchase_order)

        # 7. Auto-release funds
        release_result = escrow_contract.release_funds(escrow_id, token)
        assert release_result is True

        purchase_order['status'] = 'completed'
        backend_service.save_to_db(po_id, purchase_order)

        # Verify complete flow
        final_po = backend_service.get_from_db(po_id)
        assert final_po['status'] == 'completed'
        assert 'shipment' in final_po
        assert 'receipt' in final_po

        # Verify contract state
        assert escrow_contract.escrows[escrow_id]['status'] == 3
        assert token.get_local(seller, 'balance') == 5000000

    def test_esg_reporting_integration(self):
        """
        Test ESG report generation with blockchain data
        """
        admin = "ADMIN"
        enterprise = "SAMSUNG"

        # Initialize
        token = ESGTokenSimulator(admin)
        escrow_contract = EscrowSimulator(admin, 1001)
        backend_service = MockBackendService(escrow_contract)

        # Setup
        token.opt_in(enterprise)
        token.opt_in('SELLER1')
        token.opt_in('SELLER2')
        token.opt_in('ESCROW_CONTRACT')
        token.mint(enterprise, 50000000, admin)

        # Simulate multiple purchases
        purchases = [
            {'seller': 'SELLER1', 'amount': 10000000, 'carbon_reduction': 500},
            {'seller': 'SELLER2', 'amount': 15000000, 'carbon_reduction': 750}
        ]

        for i, purchase in enumerate(purchases):
            escrow_id = f"ESC00{i+1}"

            # Create and complete escrow
            escrow_contract.create_escrow(
                escrow_id,
                enterprise,
                purchase['seller'],
                purchase['amount']
            )
            escrow_contract.deposit_funds(escrow_id, enterprise, token)
            escrow_contract.confirm_shipment(escrow_id, purchase['seller'])
            escrow_contract.confirm_receipt(escrow_id, enterprise)
            escrow_contract.release_funds(escrow_id, token)

            # Save purchase data
            purchase_data = {
                **purchase,
                'escrow_id': escrow_id,
                'status': 'completed'
            }
            backend_service.save_to_db(escrow_id, purchase_data)

        # Generate ESG report
        esg_report = {
            'enterprise_id': enterprise,
            'period': '2025-01',
            'total_purchases': len(purchases),
            'total_amount': sum(p['amount'] for p in purchases),
            'total_carbon_reduction': sum(p['carbon_reduction'] for p in purchases),
            'completed_escrows': []
        }

        # Collect data from blockchain
        for i in range(len(purchases)):
            escrow_id = f"ESC00{i+1}"
            purchase_data = backend_service.get_from_db(escrow_id)

            esg_report['completed_escrows'].append({
                'escrow_id': escrow_id,
                'amount': purchase_data['amount'],
                'carbon_reduction': purchase_data['carbon_reduction'],
                'seller': purchase_data['seller']
            })

        # Calculate ESG score
        esg_report['esg_score'] = min(100, (
            (esg_report['total_carbon_reduction'] / 10) +
            (esg_report['total_amount'] / 1000000)
        ))

        # Verify report
        assert esg_report['total_purchases'] == 2
        assert esg_report['total_amount'] == 25000000
        assert esg_report['total_carbon_reduction'] == 1250
        assert esg_report['esg_score'] > 0


class TestSystemWideIntegration:
    """Test system-wide integration across all components"""

    def test_complete_platform_integration(self):
        """
        Test integration across all services and contracts
        """
        admin = "ADMIN"

        # Initialize all components
        token = ESGTokenSimulator(admin)
        reward = RewardSimulator(admin, 1001)
        settlement = SettlementSimulator(admin, 1001)
        escrow = EscrowSimulator(admin, 1001)

        # Mock all backend services
        reward_service = MockBackendService(reward)
        charging_service = MockBackendService(settlement)
        enterprise_service = MockBackendService(escrow)

        # User journey
        user = "USER001"
        token.opt_in(user)
        reward.opt_in(user)

        # 1. User earns rewards
        activity_id = "ACT001"
        reward_service.save_to_db(activity_id, {'carbon_kg': 100})
        reward.register_activity(user, 100)
        reward.claim_reward(user, token)

        # Verify user has tokens
        assert token.get_local(user, 'balance') == 100000

        # 2. User uses charging station
        station_id = "STATION001"
        operator = "OPERATOR"
        token.opt_in(operator)
        settlement.register_station(station_id, operator, admin)

        charge_id = "CHARGE001"
        charging_service.save_to_db(charge_id, {'amount': 50000})
        token.transfer(user, operator, 50000)
        settlement.record_transaction(station_id, 50000)

        # 3. Enterprise makes purchase
        enterprise = "SAMSUNG"
        seller = "FARM"
        token.opt_in(enterprise)
        token.opt_in(seller)
        token.opt_in('ESCROW_CONTRACT')
        token.mint(enterprise, 10000000, admin)

        escrow_id = "ESC001"
        enterprise_service.save_to_db(escrow_id, {'amount': 5000000})
        escrow.create_escrow(escrow_id, enterprise, seller, 5000000)
        escrow.deposit_funds(escrow_id, enterprise, token)
        escrow.confirm_shipment(escrow_id, seller)
        escrow.confirm_receipt(escrow_id, enterprise)
        escrow.release_funds(escrow_id, token)

        # Verify system-wide consistency
        # User tokens: 100000 (earned) - 50000 (charging) = 50000
        assert token.get_local(user, 'balance') == 50000

        # Station pending: 50000 - 5% = 47500
        assert settlement.stations[station_id]['pending'] == 47500

        # Seller received: 5000000
        assert token.get_local(seller, 'balance') == 5000000

        # Total supply: 100000 (rewards) + 10000000 (enterprise) = 10100000
        assert token.get_global('total_supply') == 10100000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
