# PAM-TALK ESG Chain - Integration Tests

Comprehensive test suite for smart contracts and backend integration.

## 📋 Test Structure

```
tests/
├── __init__.py                      # Package initialization
├── conftest.py                      # PyTest configuration and fixtures
├── test_helpers.py                  # Test utilities and simulators
├── test_unit_contracts.py           # Unit tests for smart contracts
├── test_integration_backend.py      # Backend-contract integration tests
├── test_e2e_scenarios.py           # End-to-end scenario tests
├── run_tests.py                     # Test runner script
├── requirements.txt                 # Test dependencies
└── README.md                        # This file
```

## 🚀 Quick Start

### Installation

```bash
# Install test dependencies
cd tests
pip install -r requirements.txt
```

### Running Tests

**Run all tests:**
```bash
python run_tests.py
```

**Run specific test suite:**
```bash
python run_tests.py unit           # Unit tests only
python run_tests.py integration    # Integration tests only
python run_tests.py e2e           # E2E tests only
python run_tests.py all           # All tests with HTML report
```

**Using pytest directly:**
```bash
# Run all tests
pytest -v

# Run specific test file
pytest test_unit_contracts.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run tests matching pattern
pytest -k "token" -v

# Run with markers
pytest -m unit -v
pytest -m integration -v
pytest -m e2e -v
```

## 📊 Test Categories

### 1. Unit Tests (`test_unit_contracts.py`)

Tests individual smart contract functionality using simulators.

**Test Classes:**
- `TestESGTokenContract` - ESG-Gold token operations
- `TestAutoRewardContract` - Reward distribution logic
- `TestChargingSettlementContract` - Charging station settlements
- `TestEnterpriseEscrowContract` - B2B escrow functionality

**Example:**
```python
def test_mint_tokens(self):
    """Test minting tokens"""
    admin = "ADMIN_ADDRESS"
    user = "USER_ADDRESS"
    token = ESGTokenSimulator(admin)

    token.opt_in(user)
    result = token.mint(user, 10000, admin)

    assert result is True
    assert token.get_local(user, 'balance') == 10000
```

**Coverage:**
- ✅ Token minting, burning, transferring
- ✅ Reward calculation and claiming
- ✅ Settlement creation and approval
- ✅ Escrow lifecycle (create → fund → release)
- ✅ Edge cases and error handling

### 2. Integration Tests (`test_integration_backend.py`)

Tests integration between backend services and smart contracts.

**Test Classes:**
- `TestRewardServiceIntegration` - Reward service + contract
- `TestChargingServiceIntegration` - Charging service + settlement
- `TestEnterpriseServiceIntegration` - Enterprise service + escrow
- `TestSystemWideIntegration` - Complete platform integration

**Example:**
```python
def test_activity_registration_flow(self):
    """Test complete flow from API to contract"""
    # 1. User submits activity via API
    # 2. Backend validates and stores in DB
    # 3. Backend calls contract
    # 4. Rewards calculated and stored
```

**Coverage:**
- ✅ API → Backend → Contract flow
- ✅ Database synchronization
- ✅ Transaction receipt generation
- ✅ ESG report generation
- ✅ Multi-contract coordination

### 3. E2E Scenario Tests (`test_e2e_scenarios.py`)

Tests complete user journeys through the system.

**Test Classes:**
- `TestUserCarbonReductionJourney` - User earning and spending rewards
- `TestChargingStationBusinessFlow` - Station operations
- `TestEnterpriseB2BTransaction` - Enterprise purchases
- `TestIntegratedEcosystem` - Full ecosystem simulation

**Scenarios:**
- ✅ User reduces carbon → earns rewards → spends tokens
- ✅ Charging station registration → transactions → settlement
- ✅ Enterprise creates PO → escrow → shipment → completion
- ✅ Multi-party circular economy flow

**Example:**
```python
def test_complete_user_journey(self):
    """User reduces carbon, earns rewards, spends them"""
    # 1. User opts into contracts
    # 2. Registers carbon reduction activities
    # 3. Claims accumulated rewards
    # 4. Uses tokens for transactions
```

## 🛠️ Test Helpers

### Contract Simulators

Mock smart contract execution without blockchain:

**`ESGTokenSimulator`**
- Simulates token contract (mint, burn, transfer)
- Tracks global and local state
- Validates pause/freeze logic

**`RewardSimulator`**
- Simulates reward calculation
- Tracks carbon reduction activities
- Handles reward claiming

**`SettlementSimulator`**
- Simulates charging settlements
- Calculates platform fees
- Manages station accounting

**`EscrowSimulator`**
- Simulates escrow lifecycle
- Tracks multi-party confirmations
- Handles fund releases

### Mock Classes

**`MockTransactionBuilder`**
- Creates mock Algorand transactions
- Supports application calls and payments
- Generates transaction IDs

**`MockBackendService`**
- Simulates backend database operations
- Integrates with contract simulators
- Tracks API → Contract flow

## 📈 Test Metrics

### Coverage Goals

- **Unit Tests:** ≥ 90% contract code coverage
- **Integration Tests:** ≥ 80% backend-contract integration
- **E2E Tests:** ≥ 100% critical user journeys

### Current Status

Run `pytest --cov` to see current coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

## 🔍 Debugging Tests

### Verbose Output

```bash
pytest -v -s  # Show print statements
```

### Stop on First Failure

```bash
pytest -x
```

### Run Specific Test

```bash
pytest test_unit_contracts.py::TestESGTokenContract::test_mint_tokens -v
```

### Debug with PDB

```python
def test_something(self):
    import pdb; pdb.set_trace()
    # Your test code
```

## 📝 Writing New Tests

### Unit Test Template

```python
class TestMyContract:
    """Unit tests for MyContract"""

    def test_basic_operation(self):
        """Test description"""
        # Setup
        admin = "ADMIN"
        contract = MyContractSimulator(admin)

        # Execute
        result = contract.do_something()

        # Verify
        assert result is True
        assert contract.get_global('key') == expected_value
```

### Integration Test Template

```python
class TestMyServiceIntegration:
    """Integration tests for MyService"""

    def test_service_flow(self):
        """Test complete service flow"""
        # Setup
        contract = MyContractSimulator(admin)
        service = MockBackendService(contract)

        # Simulate API request
        request_data = {...}

        # Backend processing
        service.save_to_db(key, request_data)
        contract.process(data)

        # Verify
        assert service.get_from_db(key) == expected
        assert contract.get_global('state') == expected
```

### E2E Test Template

```python
class TestMyScenario:
    """E2E tests for user scenario"""

    def test_complete_scenario(self):
        """Test: User does X → Y → Z"""
        # Setup all contracts
        token = ESGTokenSimulator(admin)
        my_contract = MyContractSimulator(admin)

        # Step 1: User action
        token.opt_in(user)
        my_contract.do_step_1(user)

        # Step 2: Follow-up action
        my_contract.do_step_2(user)

        # Verify end state
        assert token.get_local(user, 'balance') == expected
```

## 🎯 Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_level():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.e2e
def test_scenario():
    pass

@pytest.mark.slow
def test_blockchain_call():
    pass
```

Run by marker:
```bash
pytest -m unit          # Only unit tests
pytest -m "not slow"    # Exclude slow tests
```

## 📊 Test Reports

### HTML Report

```bash
pytest --html=report.html --self-contained-html
```

Opens in browser to view detailed results.

### Coverage Report

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### JSON Results

```bash
python run_tests.py
# Creates test_results.json
```

## 🐛 Common Issues

### Issue: Import errors

**Solution:**
```bash
# Add parent directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
```

### Issue: Pytest not found

**Solution:**
```bash
pip install pytest pytest-html pytest-cov
```

### Issue: Tests fail with "AssertionError"

**Solution:**
1. Check test logic
2. Verify simulator state
3. Use `-v` flag for details
4. Add debug print statements

### Issue: Slow test execution

**Solution:**
```bash
# Run in parallel
pip install pytest-xdist
pytest -n auto
```

## 📚 Best Practices

### 1. Test Independence
- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 2. Clear Test Names
```python
# Good
def test_mint_tokens_updates_balance_and_supply():
    pass

# Bad
def test_mint():
    pass
```

### 3. Arrange-Act-Assert Pattern
```python
def test_something(self):
    # Arrange
    setup_data()

    # Act
    result = perform_action()

    # Assert
    assert result == expected
```

### 4. Test Edge Cases
- Zero values
- Maximum values
- Negative values
- Empty inputs
- Invalid states

### 5. Use Descriptive Assertions
```python
# Good
assert balance == 100, f"Expected 100 but got {balance}"

# Also good
assert balance == 100, "Balance should be 100 after minting"
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r tests/requirements.txt
      - run: cd tests && python run_tests.py all
      - uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: tests/test_results.json
```

## 🎓 Learning Resources

- **PyTest Docs:** https://docs.pytest.org/
- **Testing Best Practices:** https://testdriven.io/blog/testing-best-practices/
- **Algorand Testing:** https://developer.algorand.org/docs/get-started/dapps/testing/

## 🤝 Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain > 80% coverage
4. Update this README if needed

---

**Last Updated:** 2025-01-15
**Test Framework:** PyTest 7.4+
**Python Version:** 3.8+
