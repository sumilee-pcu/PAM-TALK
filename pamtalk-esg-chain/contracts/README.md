# PAM-TALK ESG Chain - Smart Contracts

Algorand smart contracts for the PAM-TALK ESG blockchain platform, written in PyTeal.

## 📋 Contracts Overview

### 1. ESG-Gold Token Contract (`esg_gold_token.py`)
Main token contract for ESG-Gold, the native currency of the platform.

**Features:**
- Mint tokens with committee approval
- Burn tokens
- Transfer tokens between accounts
- Pause/unpause contract
- Freeze/unfreeze accounts
- Admin controls

**Operations:**
- `mint` - Issue new tokens (requires committee approval)
- `burn` - Destroy tokens
- `transfer` - Transfer tokens between accounts
- `set_committee` - Set committee address (admin only)
- `set_pause` - Pause/unpause contract (admin only)
- `set_freeze` - Freeze/unfreeze account (admin only)

**State Schema:**
- Global: 3 uints, 3 byte slices
- Local: 2 uints, 0 byte slices

---

### 2. Auto Reward Contract (`auto_reward.py`)
Automatically distributes rewards based on carbon reduction activities.

**Features:**
- Register carbon reduction activities
- Calculate rewards based on CO2 reduction
- Claim accumulated rewards
- Track user statistics
- Configurable reward rates

**Operations:**
- `register_activity` - Register carbon reduction (carbon_kg, activity_hash)
- `claim_reward` - Claim pending rewards
- `set_reward_rate` - Set reward rate (admin only)
- `set_token_app` - Link to token contract (admin only)

**State Schema:**
- Global: 3 uints, 2 byte slices
- Local: 3 uints, 0 byte slices

**Default Reward Rate:** 1000 ESG-Gold per kg CO2 reduced

---

### 3. Committee Multi-Sig Contract (`committee_multisig.py`)
Multi-signature verification for critical operations requiring committee approval.

**Features:**
- Create proposals
- Vote on proposals
- Execute approved proposals
- Proposal expiry (7 days default)
- Configurable approval threshold

**Operations:**
- `propose` - Create new proposal (proposal_id, type, data)
- `vote` - Vote on proposal (proposal_id, approve)
- `execute` - Execute approved proposal (proposal_id)
- `set_required_approvals` - Set approval threshold (admin only)

**State Schema:**
- Global: 3 uints, 50 byte slices
- Local: 0 uints, 0 byte slices

**Default Threshold:** 3 of 5 committee members

---

### 4. Charging Settlement Contract (`charging_settlement.py`)
Handles automated settlement and payment distribution for charging stations.

**Features:**
- Register charging stations
- Record charging transactions
- Request settlement
- Approve settlements
- Withdraw settled funds
- Platform fee collection

**Operations:**
- `register_station` - Register new station (station_id, operator_address)
- `record_transaction` - Record charging (station_id, amount, tx_hash)
- `request_settlement` - Request settlement (station_id, settlement_id, period)
- `approve_settlement` - Approve settlement (admin only)
- `withdraw` - Withdraw settled funds (settlement_id)
- `set_fee_rate` - Set platform fee rate (admin only)
- `deactivate_station` - Deactivate station (admin only)

**State Schema:**
- Global: 4 uints, 50 byte slices
- Local: 0 uints, 0 byte slices

**Default Platform Fee:** 5% (500 basis points)

---

### 5. Enterprise Escrow Contract (`enterprise_escrow.py`)
Secure escrow for large B2B enterprise purchases with multi-party approval.

**Features:**
- Create escrow for transactions
- Buyer deposits funds
- Seller confirms shipment
- Buyer confirms receipt
- Automated fund release
- Dispute resolution
- Cancellation with refund

**Operations:**
- `create_escrow` - Create escrow (escrow_id, buyer, seller, amount, contract_hash, deadline)
- `deposit_funds` - Buyer deposits (escrow_id)
- `confirm_shipment` - Seller confirms (escrow_id, tracking_hash)
- `confirm_receipt` - Buyer confirms (escrow_id, receipt_hash)
- `release_funds` - Release to seller (escrow_id)
- `raise_dispute` - Raise dispute (escrow_id, reason_hash)
- `resolve_dispute` - Admin resolves (escrow_id, resolution)
- `cancel_escrow` - Cancel and refund (escrow_id)

**State Schema:**
- Global: 4 uints, 50 byte slices
- Local: 0 uints, 0 byte slices

**Escrow States:**
- 0: Created
- 1: Funded
- 2: Shipped
- 3: Completed
- 4: Disputed
- 5: Cancelled

---

## 🚀 Deployment

### Prerequisites

```bash
# Install required packages
pip install pyteal py-algorand-sdk

# Ensure you have:
# - PyTeal >= 0.20.0
# - py-algorand-sdk >= 2.0.0
```

### Option 1: Compile Only

Compile all contracts to TEAL without deploying:

```bash
cd contracts
export COMPILE_ONLY=true
python deploy_contracts.py
```

This generates `.teal` files for each contract.

### Option 2: Full Deployment

Deploy all contracts to Algorand blockchain:

```bash
cd contracts
python deploy_contracts.py
```

Follow the interactive prompts:
1. Select network (testnet/mainnet)
2. Provide Algod API endpoint (or use default)
3. Choose to generate new account or use existing mnemonic
4. Fund the creator account with ALGO
5. Deployment proceeds automatically

**Output:**
- Compiled `.teal` files
- `deployment_testnet.json` or `deployment_mainnet.json` with contract IDs

### Manual Compilation

Compile individual contracts:

```bash
python esg_gold_token.py
python auto_reward.py
python committee_multisig.py
python charging_settlement.py
python enterprise_escrow.py
```

---

## 📊 Contract Interactions

### Example: Registering Carbon Reduction Activity

```python
from algosdk.transaction import ApplicationCallTxn

# Prepare arguments
args = [
    b"register_activity",
    (100).to_bytes(8, 'big'),  # 100 kg CO2
    b"activity_hash_12345"
]

# Create transaction
txn = ApplicationCallTxn(
    sender=user_address,
    sp=params,
    index=reward_app_id,
    app_args=args
)

# Sign and send
signed = txn.sign(private_key)
tx_id = algod_client.send_transaction(signed)
```

### Example: Creating Escrow

```python
args = [
    b"create_escrow",
    b"ESCROW-001",
    buyer_address.encode(),
    seller_address.encode(),
    (10000000).to_bytes(8, 'big'),  # 10M ESG-Gold
    b"contract_terms_hash",
    (30).to_bytes(8, 'big')  # 30 days deadline
]

txn = ApplicationCallTxn(
    sender=creator_address,
    sp=params,
    index=escrow_app_id,
    app_args=args
)
```

---

## 🔗 Contract Dependencies

```
esg_gold_token (Token Contract)
       ↓
       ├─→ auto_reward (uses token for minting rewards)
       ├─→ charging_settlement (uses token for settlements)
       └─→ enterprise_escrow (uses token for escrow)

committee_multisig (Independent verification system)
```

**Setup Order:**
1. Deploy ESG-Gold Token
2. Deploy Committee Multi-Sig
3. Deploy Auto Reward → Link to Token
4. Deploy Charging Settlement → Link to Token
5. Deploy Enterprise Escrow → Link to Token

---

## 🔐 Security Considerations

### Admin Controls
All contracts have admin-only operations:
- Only the creator account can perform admin functions
- Admin can be transferred by updating the `admin_address` global state

### Committee Approval
ESG-Gold minting requires:
- Group transaction with committee approval
- Multi-signature verification via Committee contract

### Escrow Protection
- Funds locked until both parties confirm
- Dispute resolution by admin
- Automatic refund on cancellation

### Fee Prevention
- Platform fees calculated with basis points (10000 = 100%)
- Maximum fee validation in settlement contract

---

## 📁 File Structure

```
contracts/
├── esg_gold_token.py              # Token contract
├── auto_reward.py                  # Reward distribution
├── committee_multisig.py           # Multi-sig verification
├── charging_settlement.py          # Station settlements
├── enterprise_escrow.py            # B2B escrow
├── deploy_contracts.py             # Deployment script
├── README.md                       # This file
└── deployment_*.json               # Deployment records
```

---

## 🧪 Testing

### TestNet Resources

**Faucet:** https://testnet.algoexplorer.io/dispenser

**Explorer:** https://testnet.algoexplorer.io/

### Test Flow

1. **Deploy contracts to TestNet**
   ```bash
   python deploy_contracts.py
   # Select 'testnet'
   ```

2. **Register test accounts**
   - Opt-in users to contracts
   - Fund accounts from faucet

3. **Test operations**
   - Register activity → Claim rewards
   - Create settlement → Withdraw
   - Create escrow → Complete transaction

4. **Verify on explorer**
   - Check application state
   - View transactions
   - Inspect inner transactions

---

## 📝 Deployment Checklist

- [ ] Compile all contracts successfully
- [ ] Fund creator account with ALGO
- [ ] Deploy ESG-Gold Token contract
- [ ] Deploy Committee Multi-Sig contract
- [ ] Deploy Auto Reward contract
- [ ] Link Auto Reward to Token contract
- [ ] Deploy Charging Settlement contract
- [ ] Link Charging Settlement to Token contract
- [ ] Deploy Enterprise Escrow contract
- [ ] Link Enterprise Escrow to Token contract
- [ ] Save deployment info (`deployment_*.json`)
- [ ] Update backend services with contract IDs
- [ ] Update frontend with contract addresses
- [ ] Test each contract operation
- [ ] Set up monitoring alerts

---

## 🐛 Troubleshooting

### Compilation Errors

**Error:** `ModuleNotFoundError: No module named 'pyteal'`
```bash
pip install pyteal
```

**Error:** `TEAL version not supported`
- Ensure PyTeal >= 0.20.0
- Check `version=8` in compileTeal calls

### Deployment Errors

**Error:** `Insufficient funds`
- Fund creator account with ALGO
- TestNet: Use faucet
- MainNet: Transfer ALGO to creator

**Error:** `Application does not exist`
- Verify app ID is correct
- Check you're on the right network

**Error:** `Transaction rejected`
- Check application arguments format
- Verify account has opted-in
- Ensure sender has permission

---

## 📚 Additional Resources

- **Algorand Developer Docs:** https://developer.algorand.org/
- **PyTeal Documentation:** https://pyteal.readthedocs.io/
- **Algorand SDK:** https://py-algorand-sdk.readthedocs.io/
- **TEAL Language:** https://developer.algorand.org/docs/get-details/dapps/avm/teal/

---

## 📄 License

Part of the PAM-TALK ESG Chain platform.

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review contract code comments
3. Test on TestNet first
4. Verify all dependencies are installed

---

**Last Updated:** 2025
**TEAL Version:** 8
**PyTeal Version:** >= 0.20.0
