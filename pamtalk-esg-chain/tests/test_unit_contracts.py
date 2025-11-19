"""
Unit Tests for Smart Contracts
Tests individual contract functionality using simulators
"""

import pytest
from test_helpers import (
    ESGTokenSimulator,
    RewardSimulator,
    SettlementSimulator,
    EscrowSimulator,
    generate_test_data
)


class TestESGTokenContract:
    """Unit tests for ESG-Gold Token contract"""

    def test_token_creation(self):
        """Test token contract initialization"""
        admin = "ADMIN_ADDRESS"
        token = ESGTokenSimulator(admin)

        assert token.get_global('total_supply') == 0
        assert token.get_global('admin_address') == admin
        assert token.get_global('is_paused') == 0

    def test_opt_in(self):
        """Test user opt-in"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        token = ESGTokenSimulator(admin)

        result = token.opt_in(user)

        assert result is True
        assert token.get_local(user, 'balance') == 0
        assert token.get_local(user, 'frozen') == 0

    def test_mint_tokens(self):
        """Test minting tokens"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        token = ESGTokenSimulator(admin)

        token.opt_in(user)
        result = token.mint(user, 10000, admin)

        assert result is True
        assert token.get_local(user, 'balance') == 10000
        assert token.get_global('total_supply') == 10000

    def test_burn_tokens(self):
        """Test burning tokens"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        token = ESGTokenSimulator(admin)

        token.opt_in(user)
        token.mint(user, 10000, admin)

        result = token.burn(user, 3000)

        assert result is True
        assert token.get_local(user, 'balance') == 7000
        assert token.get_global('total_supply') == 7000

    def test_burn_insufficient_balance(self):
        """Test burning more than balance"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        token = ESGTokenSimulator(admin)

        token.opt_in(user)
        token.mint(user, 1000, admin)

        result = token.burn(user, 5000)

        assert result is False
        assert token.get_local(user, 'balance') == 1000

    def test_transfer_tokens(self):
        """Test transferring tokens"""
        admin = "ADMIN_ADDRESS"
        sender = "SENDER_ADDRESS"
        recipient = "RECIPIENT_ADDRESS"
        token = ESGTokenSimulator(admin)

        token.opt_in(sender)
        token.opt_in(recipient)
        token.mint(sender, 10000, admin)

        result = token.transfer(sender, recipient, 3000)

        assert result is True
        assert token.get_local(sender, 'balance') == 7000
        assert token.get_local(recipient, 'balance') == 3000

    def test_transfer_insufficient_balance(self):
        """Test transfer with insufficient balance"""
        admin = "ADMIN_ADDRESS"
        sender = "SENDER_ADDRESS"
        recipient = "RECIPIENT_ADDRESS"
        token = ESGTokenSimulator(admin)

        token.opt_in(sender)
        token.opt_in(recipient)
        token.mint(sender, 1000, admin)

        result = token.transfer(sender, recipient, 5000)

        assert result is False
        assert token.get_local(sender, 'balance') == 1000
        assert token.get_local(recipient, 'balance') == 0

    def test_paused_contract(self):
        """Test operations when contract is paused"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        token = ESGTokenSimulator(admin)

        token.opt_in(user)
        token.mint(user, 10000, admin)

        # Pause contract
        token.put_global('is_paused', 1)

        # Try operations
        assert token.mint(user, 1000, admin) is False
        assert token.burn(user, 1000) is False
        assert token.transfer(user, "OTHER", 1000) is False

    def test_frozen_account_transfer(self):
        """Test transfer from frozen account"""
        admin = "ADMIN_ADDRESS"
        sender = "SENDER_ADDRESS"
        recipient = "RECIPIENT_ADDRESS"
        token = ESGTokenSimulator(admin)

        token.opt_in(sender)
        token.opt_in(recipient)
        token.mint(sender, 10000, admin)

        # Freeze sender
        token.put_local(sender, 'frozen', 1)

        result = token.transfer(sender, recipient, 1000)

        assert result is False
        assert token.get_local(sender, 'balance') == 10000


class TestAutoRewardContract:
    """Unit tests for Auto Reward contract"""

    def test_reward_creation(self):
        """Test reward contract initialization"""
        admin = "ADMIN_ADDRESS"
        token_app_id = 1001
        reward = RewardSimulator(admin, token_app_id)

        assert reward.get_global('admin_address') == admin
        assert reward.get_global('token_app_id') == token_app_id
        assert reward.get_global('reward_rate') == 1000
        assert reward.get_global('total_distributed') == 0

    def test_register_activity(self):
        """Test registering carbon reduction activity"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        reward = RewardSimulator(admin, 1001)

        reward.opt_in(user)
        reward_amount = reward.register_activity(user, 100)  # 100 kg CO2

        assert reward_amount == 100000  # 100 kg * 1000 rate
        assert reward.get_local(user, 'pending_rewards') == 100000
        assert reward.get_local(user, 'total_carbon_reduction') == 100

    def test_multiple_activities(self):
        """Test registering multiple activities"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        reward = RewardSimulator(admin, 1001)

        reward.opt_in(user)
        reward.register_activity(user, 50)
        reward.register_activity(user, 30)
        reward.register_activity(user, 20)

        assert reward.get_local(user, 'pending_rewards') == 100000  # 100 kg * 1000
        assert reward.get_local(user, 'total_carbon_reduction') == 100

    def test_claim_reward(self):
        """Test claiming rewards"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        token = ESGTokenSimulator(admin)
        reward = RewardSimulator(admin, 1001)

        token.opt_in(user)
        reward.opt_in(user)

        reward.register_activity(user, 100)
        claimed = reward.claim_reward(user, token)

        assert claimed == 100000
        assert reward.get_local(user, 'pending_rewards') == 0
        assert reward.get_local(user, 'claimed_rewards') == 100000
        assert reward.get_global('total_distributed') == 100000
        assert token.get_local(user, 'balance') == 100000

    def test_claim_no_pending(self):
        """Test claiming when no pending rewards"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        token = ESGTokenSimulator(admin)
        reward = RewardSimulator(admin, 1001)

        token.opt_in(user)
        reward.opt_in(user)

        claimed = reward.claim_reward(user, token)

        assert claimed == 0

    def test_custom_reward_rate(self):
        """Test with custom reward rate"""
        admin = "ADMIN_ADDRESS"
        user = "USER_ADDRESS"
        reward = RewardSimulator(admin, 1001)

        reward.opt_in(user)
        reward.put_global('reward_rate', 2000)

        reward_amount = reward.register_activity(user, 50)

        assert reward_amount == 100000  # 50 kg * 2000 rate


class TestChargingSettlementContract:
    """Unit tests for Charging Settlement contract"""

    def test_settlement_creation(self):
        """Test settlement contract initialization"""
        admin = "ADMIN_ADDRESS"
        token_app_id = 1001
        settlement = SettlementSimulator(admin, token_app_id)

        assert settlement.get_global('admin_address') == admin
        assert settlement.get_global('token_app_id') == token_app_id
        assert settlement.get_global('platform_fee_rate') == 500
        assert settlement.get_global('total_volume') == 0

    def test_register_station(self):
        """Test registering charging station"""
        admin = "ADMIN_ADDRESS"
        operator = "OPERATOR_ADDRESS"
        settlement = SettlementSimulator(admin, 1001)

        result = settlement.register_station("STATION001", operator, admin)

        assert result is True
        assert "STATION001" in settlement.stations
        assert settlement.stations["STATION001"]['operator'] == operator
        assert settlement.stations["STATION001"]['status'] == 1

    def test_register_station_unauthorized(self):
        """Test registering station without admin"""
        admin = "ADMIN_ADDRESS"
        operator = "OPERATOR_ADDRESS"
        settlement = SettlementSimulator(admin, 1001)

        result = settlement.register_station("STATION001", operator, "UNAUTHORIZED")

        assert result is False

    def test_record_transaction(self):
        """Test recording charging transaction"""
        admin = "ADMIN_ADDRESS"
        operator = "OPERATOR_ADDRESS"
        settlement = SettlementSimulator(admin, 1001)

        settlement.register_station("STATION001", operator, admin)
        result = settlement.record_transaction("STATION001", 10000)

        assert result['success'] is True
        assert result['amount'] == 10000
        assert result['fee'] == 500  # 5% of 10000
        assert result['net'] == 9500
        assert settlement.stations["STATION001"]['pending'] == 9500

    def test_multiple_transactions(self):
        """Test multiple charging transactions"""
        admin = "ADMIN_ADDRESS"
        operator = "OPERATOR_ADDRESS"
        settlement = SettlementSimulator(admin, 1001)

        settlement.register_station("STATION001", operator, admin)
        settlement.record_transaction("STATION001", 10000)
        settlement.record_transaction("STATION001", 20000)

        station = settlement.stations["STATION001"]
        assert station['volume'] == 30000
        assert station['fees_paid'] == 1500  # 500 + 1000
        assert station['pending'] == 28500  # 9500 + 19000

    def test_request_settlement(self):
        """Test requesting settlement"""
        admin = "ADMIN_ADDRESS"
        operator = "OPERATOR_ADDRESS"
        settlement = SettlementSimulator(admin, 1001)

        settlement.register_station("STATION001", operator, admin)
        settlement.record_transaction("STATION001", 10000)

        result = settlement.request_settlement("STATION001", "SETTLE001", operator)

        assert result is True
        assert "SETTLE001" in settlement.settlements
        assert settlement.settlements["SETTLE001"]['amount'] == 9500
        assert settlement.settlements["SETTLE001"]['status'] == 0

    def test_request_settlement_no_pending(self):
        """Test requesting settlement with no pending amount"""
        admin = "ADMIN_ADDRESS"
        operator = "OPERATOR_ADDRESS"
        settlement = SettlementSimulator(admin, 1001)

        settlement.register_station("STATION001", operator, admin)

        result = settlement.request_settlement("STATION001", "SETTLE001", operator)

        assert result is False

    def test_approve_settlement(self):
        """Test approving settlement"""
        admin = "ADMIN_ADDRESS"
        operator = "OPERATOR_ADDRESS"
        settlement = SettlementSimulator(admin, 1001)

        settlement.register_station("STATION001", operator, admin)
        settlement.record_transaction("STATION001", 10000)
        settlement.request_settlement("STATION001", "SETTLE001", operator)

        result = settlement.approve_settlement("SETTLE001", admin)

        assert result is True
        assert settlement.settlements["SETTLE001"]['status'] == 1


class TestEnterpriseEscrowContract:
    """Unit tests for Enterprise Escrow contract"""

    def test_escrow_creation(self):
        """Test escrow contract initialization"""
        admin = "ADMIN_ADDRESS"
        token_app_id = 1001
        escrow = EscrowSimulator(admin, token_app_id)

        assert escrow.get_global('admin_address') == admin
        assert escrow.get_global('token_app_id') == token_app_id
        assert escrow.get_global('total_escrowed') == 0

    def test_create_escrow(self):
        """Test creating escrow"""
        admin = "ADMIN_ADDRESS"
        buyer = "BUYER_ADDRESS"
        seller = "SELLER_ADDRESS"
        escrow = EscrowSimulator(admin, 1001)

        result = escrow.create_escrow("ESC001", buyer, seller, 1000000)

        assert result is True
        assert "ESC001" in escrow.escrows
        assert escrow.escrows["ESC001"]['buyer'] == buyer
        assert escrow.escrows["ESC001"]['seller'] == seller
        assert escrow.escrows["ESC001"]['amount'] == 1000000
        assert escrow.escrows["ESC001"]['status'] == 0

    def test_deposit_funds(self):
        """Test depositing funds to escrow"""
        admin = "ADMIN_ADDRESS"
        buyer = "BUYER_ADDRESS"
        seller = "SELLER_ADDRESS"
        token = ESGTokenSimulator(admin)
        escrow = EscrowSimulator(admin, 1001)

        # Setup
        token.opt_in(buyer)
        token.opt_in('ESCROW_CONTRACT')
        token.mint(buyer, 2000000, admin)

        escrow.create_escrow("ESC001", buyer, seller, 1000000)
        result = escrow.deposit_funds("ESC001", buyer, token)

        assert result is True
        assert escrow.escrows["ESC001"]['status'] == 1
        assert escrow.escrows["ESC001"]['deposit_amount'] == 1000000
        assert token.get_local(buyer, 'balance') == 1000000

    def test_confirm_shipment(self):
        """Test seller confirming shipment"""
        admin = "ADMIN_ADDRESS"
        buyer = "BUYER_ADDRESS"
        seller = "SELLER_ADDRESS"
        token = ESGTokenSimulator(admin)
        escrow = EscrowSimulator(admin, 1001)

        # Setup
        token.opt_in(buyer)
        token.opt_in('ESCROW_CONTRACT')
        token.mint(buyer, 1000000, admin)

        escrow.create_escrow("ESC001", buyer, seller, 1000000)
        escrow.deposit_funds("ESC001", buyer, token)

        result = escrow.confirm_shipment("ESC001", seller)

        assert result is True
        assert escrow.escrows["ESC001"]['status'] == 2
        assert escrow.escrows["ESC001"]['seller_confirmed'] is True

    def test_confirm_receipt(self):
        """Test buyer confirming receipt"""
        admin = "ADMIN_ADDRESS"
        buyer = "BUYER_ADDRESS"
        seller = "SELLER_ADDRESS"
        token = ESGTokenSimulator(admin)
        escrow = EscrowSimulator(admin, 1001)

        # Setup
        token.opt_in(buyer)
        token.opt_in(seller)
        token.opt_in('ESCROW_CONTRACT')
        token.mint(buyer, 1000000, admin)

        escrow.create_escrow("ESC001", buyer, seller, 1000000)
        escrow.deposit_funds("ESC001", buyer, token)
        escrow.confirm_shipment("ESC001", seller)

        result = escrow.confirm_receipt("ESC001", buyer)

        assert result is True
        assert escrow.escrows["ESC001"]['buyer_confirmed'] is True

    def test_full_escrow_flow(self):
        """Test complete escrow flow"""
        admin = "ADMIN_ADDRESS"
        buyer = "BUYER_ADDRESS"
        seller = "SELLER_ADDRESS"
        token = ESGTokenSimulator(admin)
        escrow = EscrowSimulator(admin, 1001)

        # Setup
        token.opt_in(buyer)
        token.opt_in(seller)
        token.opt_in('ESCROW_CONTRACT')
        token.mint(buyer, 1000000, admin)

        # Create and fund escrow
        escrow.create_escrow("ESC001", buyer, seller, 1000000)
        escrow.deposit_funds("ESC001", buyer, token)

        # Confirm shipment and receipt
        escrow.confirm_shipment("ESC001", seller)
        escrow.confirm_receipt("ESC001", buyer)

        # Release funds
        result = escrow.release_funds("ESC001", token)

        assert result is True
        assert escrow.escrows["ESC001"]['status'] == 3
        assert token.get_local(seller, 'balance') == 1000000
        assert escrow.get_global('total_escrowed') == 0

    def test_release_without_confirmation(self):
        """Test releasing funds without both confirmations"""
        admin = "ADMIN_ADDRESS"
        buyer = "BUYER_ADDRESS"
        seller = "SELLER_ADDRESS"
        token = ESGTokenSimulator(admin)
        escrow = EscrowSimulator(admin, 1001)

        # Setup
        token.opt_in(buyer)
        token.opt_in(seller)
        token.opt_in('ESCROW_CONTRACT')
        token.mint(buyer, 1000000, admin)

        escrow.create_escrow("ESC001", buyer, seller, 1000000)
        escrow.deposit_funds("ESC001", buyer, token)

        # Only confirm shipment, not receipt
        escrow.confirm_shipment("ESC001", seller)

        result = escrow.release_funds("ESC001", token)

        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
