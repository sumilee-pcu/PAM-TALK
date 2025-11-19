"""
PyTest Configuration and Fixtures for Integration Tests
"""

import pytest
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        "network": "testnet",
        "algod_address": "https://testnet-api.algonode.cloud",
        "algod_token": "",
        "test_accounts": [],
        "test_mode": True
    }


@pytest.fixture(scope="session")
def mock_algod_client():
    """Mock Algorand client for testing"""
    class MockAlgodClient:
        def __init__(self):
            self.apps = {}
            self.accounts = {}
            self.next_app_id = 1000

        def suggested_params(self):
            class Params:
                fee = 1000
                first = 1000
                last = 2000
                gh = "testnet"
                genesis_id = "testnet-v1.0"
                genesis_hash = "SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI="
            return Params()

        def compile(self, source):
            """Mock compile - returns dummy bytecode"""
            import base64
            dummy_bytecode = b"dummy_compiled_teal"
            return {
                'result': base64.b64encode(dummy_bytecode).decode(),
                'hash': 'DUMMYHASH'
            }

        def send_transaction(self, signed_txn):
            """Mock transaction send"""
            return f"TX-{datetime.now().timestamp()}"

        def pending_transaction_info(self, tx_id):
            """Mock transaction confirmation"""
            return {
                'confirmed-round': 1000,
                'application-index': self.next_app_id,
                'pool-error': '',
                'txn': {}
            }

    return MockAlgodClient()


@pytest.fixture(scope="session")
def test_accounts():
    """Generate test accounts"""
    from algosdk import account

    accounts = []
    for i in range(5):
        private_key, address = account.generate_account()
        accounts.append({
            'name': f'TestAccount{i+1}',
            'address': address,
            'private_key': private_key,
            'role': ['admin', 'committee', 'user', 'station', 'enterprise'][i]
        })

    return accounts


@pytest.fixture
def esg_token_contract():
    """Mock ESG-Gold Token contract state"""
    return {
        'app_id': 1001,
        'global_state': {
            'total_supply': 0,
            'admin_address': 'TEST_ADMIN',
            'is_paused': 0
        },
        'local_state': {}
    }


@pytest.fixture
def reward_contract():
    """Mock Auto Reward contract state"""
    return {
        'app_id': 1002,
        'global_state': {
            'admin_address': 'TEST_ADMIN',
            'reward_rate': 1000,
            'total_distributed': 0,
            'token_app_id': 1001
        },
        'local_state': {}
    }


@pytest.fixture
def committee_contract():
    """Mock Committee Multi-Sig contract state"""
    return {
        'app_id': 1003,
        'global_state': {
            'admin_address': 'TEST_ADMIN',
            'required_approvals': 3,
            'committee_count': 5
        },
        'proposals': {}
    }


@pytest.fixture
def settlement_contract():
    """Mock Charging Settlement contract state"""
    return {
        'app_id': 1004,
        'global_state': {
            'admin_address': 'TEST_ADMIN',
            'platform_fee_rate': 500,
            'total_volume': 0,
            'token_app_id': 1001
        },
        'stations': {}
    }


@pytest.fixture
def escrow_contract():
    """Mock Enterprise Escrow contract state"""
    return {
        'app_id': 1005,
        'global_state': {
            'admin_address': 'TEST_ADMIN',
            'arbitration_fee': 1000000,
            'total_escrowed': 0,
            'token_app_id': 1001
        },
        'escrows': {}
    }


@pytest.fixture
def db_connection():
    """Test database connection"""
    import sqlite3

    # Create in-memory database for testing
    conn = sqlite3.connect(':memory:')

    yield conn

    conn.close()


@pytest.fixture
def mock_blockchain_state():
    """Mock blockchain state for integration testing"""
    return {
        'current_round': 1000,
        'apps': {},
        'accounts': {},
        'transactions': [],
        'inner_transactions': []
    }


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for multiple components"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end scenario tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests that interact with real blockchain"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add 'unit' marker to all tests in test_unit_*.py files
        if "test_unit_" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Add 'integration' marker to all tests in test_integration_*.py files
        elif "test_integration_" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Add 'e2e' marker to all tests in test_e2e_*.py files
        elif "test_e2e_" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
