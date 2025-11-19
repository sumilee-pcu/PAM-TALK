"""
End-to-End Scenario Tests
Tests complete user journeys through the ESG Chain system
"""

import pytest
from test_helpers import (
    ESGTokenSimulator,
    RewardSimulator,
    SettlementSimulator,
    EscrowSimulator,
    generate_test_data
)


class TestUserCarbonReductionJourney:
    """E2E test for user carbon reduction and reward cycle"""

    def test_complete_user_journey(self):
        """
        Scenario: User reduces carbon, earns rewards, and spends them

        Steps:
        1. User opts into token and reward contracts
        2. User registers multiple carbon reduction activities
        3. User claims accumulated rewards
        4. User uses tokens for transactions
        """
        # Setup
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        merchant = "MERCHANT_ADDRESS"

        token = ESGTokenSimulator(admin)
        reward = RewardSimulator(admin, 1001)

        # Step 1: Opt-in
        token.opt_in(user)
        token.opt_in(merchant)
        reward.opt_in(user)

        # Step 2: Register activities
        activities = [
            {'carbon_kg': 50, 'activity': 'public_transport'},
            {'carbon_kg': 30, 'activity': 'bicycle'},
            {'carbon_kg': 20, 'activity': 'ev_charging'}
        ]

        total_carbon = 0
        for activity in activities:
            reward.register_activity(user, activity['carbon_kg'])
            total_carbon += activity['carbon_kg']

        # Verify pending rewards
        expected_rewards = total_carbon * 1000  # 100 kg * 1000 rate
        assert reward.get_local(user, 'pending_rewards') == expected_rewards
        assert reward.get_local(user, 'total_carbon_reduction') == total_carbon

        # Step 3: Claim rewards
        claimed = reward.claim_reward(user, token)

        assert claimed == expected_rewards
        assert token.get_local(user, 'balance') == expected_rewards
        assert reward.get_local(user, 'pending_rewards') == 0
        assert reward.get_local(user, 'claimed_rewards') == expected_rewards

        # Step 4: Use tokens for purchase
        purchase_amount = 50000
        result = token.transfer(user, merchant, purchase_amount)

        assert result is True
        assert token.get_local(user, 'balance') == expected_rewards - purchase_amount
        assert token.get_local(merchant, 'balance') == purchase_amount

    def test_multiple_users_concurrent(self):
        """
        Scenario: Multiple users earning rewards simultaneously
        """
        admin = "ADMIN_ADDRESS"
        users = ["USER1", "USER2", "USER3"]

        token = ESGTokenSimulator(admin)
        reward = RewardSimulator(admin, 1001)

        # All users opt-in
        for user in users:
            token.opt_in(user)
            reward.opt_in(user)

        # Users register different amounts of activities
        activities_per_user = {
            "USER1": 100,
            "USER2": 50,
            "USER3": 75
        }

        for user, carbon_kg in activities_per_user.items():
            reward.register_activity(user, carbon_kg)

        # Verify independent balances
        for user, carbon_kg in activities_per_user.items():
            expected = carbon_kg * 1000
            assert reward.get_local(user, 'pending_rewards') == expected

        # Users claim at different times
        for user in users:
            reward.claim_reward(user, token)

        # Verify final balances
        for user, carbon_kg in activities_per_user.items():
            expected = carbon_kg * 1000
            assert token.get_local(user, 'balance') == expected

        # Verify total distribution
        total_expected = sum(activities_per_user.values()) * 1000
        assert reward.get_global('total_distributed') == total_expected
        assert token.get_global('total_supply') == total_expected


class TestChargingStationBusinessFlow:
    """E2E test for charging station operations"""

    def test_station_complete_flow(self):
        """
        Scenario: Charging station from registration to settlement

        Steps:
        1. Admin registers charging station
        2. Users charge at station (multiple transactions)
        3. Station operator requests settlement
        4. Admin approves settlement
        5. Operator receives funds
        """
        admin = "ADMIN_ADDRESS"
        operator = "OPERATOR_ADDRESS"
        users = ["USER1", "USER2", "USER3"]

        token = ESGTokenSimulator(admin)
        settlement = SettlementSimulator(admin, 1001)

        # Setup token balances for users
        token.opt_in(operator)
        for user in users:
            token.opt_in(user)
            token.mint(user, 100000, admin)

        # Step 1: Register station
        station_id = "STATION001"
        result = settlement.register_station(station_id, operator, admin)
        assert result is True

        # Step 2: Process charging transactions
        charging_transactions = [
            {'user': 'USER1', 'amount': 50000},
            {'user': 'USER2', 'amount': 30000},
            {'user': 'USER3', 'amount': 20000}
        ]

        total_volume = 0
        total_fees = 0
        total_net = 0

        for txn in charging_transactions:
            result = settlement.record_transaction(station_id, txn['amount'])
            assert result['success'] is True

            total_volume += result['amount']
            total_fees += result['fee']
            total_net += result['net']

        # Verify station stats
        station = settlement.stations[station_id]
        assert station['volume'] == total_volume
        assert station['fees_paid'] == total_fees
        assert station['pending'] == total_net

        # Step 3: Request settlement
        settlement_id = "SETTLE001"
        result = settlement.request_settlement(station_id, settlement_id, operator)
        assert result is True

        settle_record = settlement.settlements[settlement_id]
        assert settle_record['amount'] == total_net
        assert settle_record['status'] == 0  # Pending

        # Step 4: Admin approves
        result = settlement.approve_settlement(settlement_id, admin)
        assert result is True
        assert settlement.settlements[settlement_id]['status'] == 1  # Approved

        # Verify settlement amounts
        # Total: 100,000, Fee (5%): 5,000, Net: 95,000
        assert total_volume == 100000
        assert total_fees == 5000
        assert total_net == 95000

    def test_multiple_stations_parallel(self):
        """
        Scenario: Multiple stations operating in parallel
        """
        admin = "ADMIN_ADDRESS"
        operators = ["OP1", "OP2", "OP3"]
        settlement = SettlementSimulator(admin, 1001)

        # Register multiple stations
        for i, operator in enumerate(operators):
            station_id = f"STATION00{i+1}"
            settlement.register_station(station_id, operator, admin)

        # Each station processes transactions
        for i, operator in enumerate(operators):
            station_id = f"STATION00{i+1}"
            amount = (i + 1) * 10000  # 10k, 20k, 30k

            settlement.record_transaction(station_id, amount)

        # Verify independent accounting
        assert settlement.stations["STATION001"]['pending'] == 9500
        assert settlement.stations["STATION002"]['pending'] == 19000
        assert settlement.stations["STATION003"]['pending'] == 28500

        # Verify total volume
        assert settlement.get_global('total_volume') == 60000


class TestEnterpriseB2BTransaction:
    """E2E test for enterprise B2B transactions"""

    def test_successful_b2b_purchase(self):
        """
        Scenario: Complete enterprise purchase with escrow

        Steps:
        1. Create escrow for B2B transaction
        2. Buyer deposits funds
        3. Seller confirms shipment
        4. Buyer confirms receipt
        5. Funds released to seller
        """
        admin = "ADMIN_ADDRESS"
        buyer = "SAMSUNG"
        seller = "LOCAL_COOP"
        amount = 10000000  # 10M ESG-Gold

        token = ESGTokenSimulator(admin)
        escrow = EscrowSimulator(admin, 1001)

        # Setup
        token.opt_in(buyer)
        token.opt_in(seller)
        token.opt_in('ESCROW_CONTRACT')
        token.mint(buyer, amount * 2, admin)  # Give buyer enough funds

        # Step 1: Create escrow
        escrow_id = "ESC_B2B_001"
        result = escrow.create_escrow(escrow_id, buyer, seller, amount)
        assert result is True

        # Step 2: Buyer deposits
        initial_buyer_balance = token.get_local(buyer, 'balance')
        result = escrow.deposit_funds(escrow_id, buyer, token)
        assert result is True
        assert token.get_local(buyer, 'balance') == initial_buyer_balance - amount

        # Step 3: Seller confirms shipment
        result = escrow.confirm_shipment(escrow_id, seller)
        assert result is True
        assert escrow.escrows[escrow_id]['status'] == 2  # Shipped

        # Step 4: Buyer confirms receipt
        result = escrow.confirm_receipt(escrow_id, buyer)
        assert result is True
        assert escrow.escrows[escrow_id]['buyer_confirmed'] is True

        # Step 5: Release funds
        result = escrow.release_funds(escrow_id, token)
        assert result is True

        # Verify final state
        assert escrow.escrows[escrow_id]['status'] == 3  # Completed
        assert token.get_local(seller, 'balance') == amount
        assert escrow.get_global('total_escrowed') == 0

    def test_multiple_concurrent_escrows(self):
        """
        Scenario: Multiple B2B transactions in parallel
        """
        admin = "ADMIN_ADDRESS"
        token = ESGTokenSimulator(admin)
        escrow = EscrowSimulator(admin, 1001)

        # Setup multiple buyers and sellers
        buyers = ["SAMSUNG", "LG", "HYUNDAI"]
        sellers = ["COOP1", "COOP2", "COOP3"]
        amounts = [5000000, 7000000, 3000000]

        # Initialize all accounts
        token.opt_in('ESCROW_CONTRACT')
        for buyer in buyers:
            token.opt_in(buyer)
            token.mint(buyer, 20000000, admin)

        for seller in sellers:
            token.opt_in(seller)

        # Create and process multiple escrows
        for i, (buyer, seller, amount) in enumerate(zip(buyers, sellers, amounts)):
            escrow_id = f"ESC00{i+1}"

            # Create and fund
            escrow.create_escrow(escrow_id, buyer, seller, amount)
            escrow.deposit_funds(escrow_id, buyer, token)

            # Confirm and release
            escrow.confirm_shipment(escrow_id, seller)
            escrow.confirm_receipt(escrow_id, buyer)
            escrow.release_funds(escrow_id, token)

        # Verify all completed
        for i in range(3):
            escrow_id = f"ESC00{i+1}"
            assert escrow.escrows[escrow_id]['status'] == 3

        # Verify seller balances
        for seller, amount in zip(sellers, amounts):
            assert token.get_local(seller, 'balance') == amount


class TestIntegratedEcosystem:
    """E2E test for complete ecosystem integration"""

    def test_full_ecosystem_flow(self):
        """
        Scenario: Complete flow from carbon reduction to enterprise purchase

        Steps:
        1. User reduces carbon and earns tokens
        2. User charges EV at station
        3. Station settles earnings
        4. Enterprise buys carbon credits via escrow
        5. Verify complete circular economy
        """
        admin = "ADMIN_ADDRESS"
        user = "CITIZEN"
        station_operator = "STATION_OP"
        enterprise = "SAMSUNG"
        producer = "FARM_COOP"

        # Initialize all contracts
        token = ESGTokenSimulator(admin)
        reward = RewardSimulator(admin, 1001)
        settlement = SettlementSimulator(admin, 1001)
        escrow = EscrowSimulator(admin, 1001)

        # Setup accounts
        for account in [user, station_operator, enterprise, producer, 'ESCROW_CONTRACT']:
            token.opt_in(account)

        reward.opt_in(user)

        # Phase 1: User earns tokens from carbon reduction
        reward.register_activity(user, 100)  # 100 kg CO2
        reward.claim_reward(user, token)

        user_initial_balance = token.get_local(user, 'balance')
        assert user_initial_balance == 100000  # 100 kg * 1000 rate

        # Phase 2: User charges at station
        settlement.register_station("STATION001", station_operator, admin)
        charging_amount = 50000

        # User pays for charging (simulated)
        token.transfer(user, station_operator, charging_amount)
        settlement.record_transaction("STATION001", charging_amount)

        # Phase 3: Station settles
        settlement.request_settlement("STATION001", "SETTLE001", station_operator)
        settlement.approve_settlement("SETTLE001", admin)

        station_earnings = settlement.stations["STATION001"]['pending']
        assert station_earnings == 47500  # 50000 - 5% fee

        # Phase 4: Enterprise purchases carbon credits
        token.mint(enterprise, 10000000, admin)  # Enterprise has funds

        escrow.create_escrow("ESC001", enterprise, producer, 5000000)
        escrow.deposit_funds("ESC001", enterprise, token)
        escrow.confirm_shipment("ESC001", producer)
        escrow.confirm_receipt("ESC001", enterprise)
        escrow.release_funds("ESC001", token)

        # Verify circular economy
        assert token.get_local(user, 'balance') == user_initial_balance - charging_amount
        assert token.get_local(producer, 'balance') == 5000000
        assert reward.get_global('total_distributed') == 100000
        assert settlement.get_global('total_volume') == 50000

        # Verify total token supply consistency
        total_minted = 100000 + 10000000  # Rewards + Enterprise funds
        expected_supply = total_minted
        assert token.get_global('total_supply') == expected_supply

    def test_complex_multi_party_scenario(self):
        """
        Scenario: Complex interactions with multiple parties
        """
        admin = "ADMIN_ADDRESS"

        # Multiple users
        users = [f"USER{i}" for i in range(1, 6)]
        # Multiple stations
        stations = [f"STATION{i}" for i in range(1, 4)]
        station_ops = [f"OP{i}" for i in range(1, 4)]
        # Enterprises
        enterprises = ["SAMSUNG", "LG"]
        # Producers
        producers = ["FARM1", "FARM2"]

        # Initialize
        token = ESGTokenSimulator(admin)
        reward = RewardSimulator(admin, 1001)
        settlement = SettlementSimulator(admin, 1001)
        escrow = EscrowSimulator(admin, 1001)

        # Setup all accounts
        for user in users + station_ops + enterprises + producers + ['ESCROW_CONTRACT']:
            token.opt_in(user)

        for user in users:
            reward.opt_in(user)

        # Setup stations
        for station, operator in zip(stations, station_ops):
            settlement.register_station(station, operator, admin)

        # Phase 1: Users earn rewards
        carbon_amounts = [50, 75, 100, 60, 80]
        for user, carbon in zip(users, carbon_amounts):
            reward.register_activity(user, carbon)
            reward.claim_reward(user, token)

        # Phase 2: Users use stations
        for user, station in zip(users[:3], stations):
            amount = 30000
            token.transfer(user, station_ops[stations.index(station)], amount)
            settlement.record_transaction(station, amount)

        # Phase 3: Enterprises make purchases
        for enterprise, producer in zip(enterprises, producers):
            token.mint(enterprise, 20000000, admin)
            escrow_id = f"ESC_{enterprise}"

            escrow.create_escrow(escrow_id, enterprise, producer, 8000000)
            escrow.deposit_funds(escrow_id, enterprise, token)
            escrow.confirm_shipment(escrow_id, producer)
            escrow.confirm_receipt(escrow_id, enterprise)
            escrow.release_funds(escrow_id, token)

        # Verify system-wide metrics
        total_rewards_distributed = sum(carbon_amounts) * 1000
        assert reward.get_global('total_distributed') == total_rewards_distributed

        total_charging_volume = 30000 * 3  # 3 transactions
        assert settlement.get_global('total_volume') == total_charging_volume

        # Verify producers received payments
        for producer in producers:
            assert token.get_local(producer, 'balance') == 8000000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
