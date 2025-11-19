# -*- coding: utf-8 -*-
"""
Smart Contract Deployment Script for PAM-TALK ESG Chain
Compiles and deploys all TEAL contracts to Algorand blockchain
"""

import os
import json
import base64
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import (
    ApplicationCreateTxn,
    ApplicationCallTxn,
    StateSchema,
    OnComplete,
    wait_for_confirmation
)
from pyteal import compileTeal, Mode

# Import contract programs
from esg_gold_token import approval_program as token_approval, clear_state_program as token_clear
from auto_reward import approval_program as reward_approval, clear_state_program as reward_clear
from committee_multisig import approval_program as committee_approval, clear_state_program as committee_clear
from charging_settlement import approval_program as settlement_approval, clear_state_program as settlement_clear
from enterprise_escrow import approval_program as escrow_approval, clear_state_program as escrow_clear


class ContractDeployer:
    """Handles compilation and deployment of all ESG Chain contracts"""

    def __init__(self, algod_address, algod_token, network="testnet"):
        """
        Initialize deployer

        Args:
            algod_address: Algorand node address
            algod_token: Algorand node API token
            network: 'testnet' or 'mainnet'
        """
        self.client = algod.AlgodClient(algod_token, algod_address)
        self.network = network
        self.deployed_apps = {}

    def compile_contract(self, approval_fn, clear_fn, name):
        """
        Compile PyTeal contract to TEAL

        Args:
            approval_fn: Approval program function
            clear_fn: Clear state program function
            name: Contract name

        Returns:
            tuple: (approval_teal, clear_teal)
        """
        print(f"📝 Compiling {name}...")

        approval_teal = compileTeal(approval_fn(), mode=Mode.Application, version=8)
        clear_teal = compileTeal(clear_fn(), mode=Mode.Application, version=8)

        # Save to files
        with open(f"{name}_approval.teal", "w") as f:
            f.write(approval_teal)
        with open(f"{name}_clear.teal", "w") as f:
            f.write(clear_teal)

        print(f"✅ {name} compiled successfully")
        return approval_teal, clear_teal

    def compile_teal_to_bytecode(self, teal_source):
        """
        Compile TEAL source to bytecode using algod

        Args:
            teal_source: TEAL source code string

        Returns:
            bytes: Compiled bytecode
        """
        compile_response = self.client.compile(teal_source)
        return base64.b64decode(compile_response['result'])

    def deploy_contract(self, creator_private_key, approval_teal, clear_teal,
                       global_schema, local_schema, name, app_args=None):
        """
        Deploy contract to Algorand

        Args:
            creator_private_key: Private key of creator account
            approval_teal: Approval program TEAL
            clear_teal: Clear state program TEAL
            global_schema: StateSchema for global state
            local_schema: StateSchema for local state
            name: Contract name
            app_args: Optional application arguments

        Returns:
            int: Application ID
        """
        print(f"🚀 Deploying {name}...")

        # Compile to bytecode
        approval_program = self.compile_teal_to_bytecode(approval_teal)
        clear_program = self.compile_teal_to_bytecode(clear_teal)

        # Get creator address
        creator_address = account.address_from_private_key(creator_private_key)

        # Get suggested params
        params = self.client.suggested_params()

        # Create transaction
        txn = ApplicationCreateTxn(
            sender=creator_address,
            sp=params,
            on_complete=OnComplete.NoOpOC,
            approval_program=approval_program,
            clear_program=clear_program,
            global_schema=global_schema,
            local_schema=local_schema,
            app_args=app_args or []
        )

        # Sign transaction
        signed_txn = txn.sign(creator_private_key)

        # Send transaction
        tx_id = self.client.send_transaction(signed_txn)
        print(f"Transaction ID: {tx_id}")

        # Wait for confirmation
        confirmed_txn = wait_for_confirmation(self.client, tx_id, 4)

        # Get application ID
        app_id = confirmed_txn['application-index']
        print(f"✅ {name} deployed! App ID: {app_id}")

        self.deployed_apps[name] = app_id
        return app_id

    def call_application(self, caller_private_key, app_id, app_args):
        """
        Call application method

        Args:
            caller_private_key: Private key of caller
            app_id: Application ID
            app_args: Application arguments

        Returns:
            str: Transaction ID
        """
        caller_address = account.address_from_private_key(caller_private_key)
        params = self.client.suggested_params()

        txn = ApplicationCallTxn(
            sender=caller_address,
            sp=params,
            index=app_id,
            on_complete=OnComplete.NoOpOC,
            app_args=app_args
        )

        signed_txn = txn.sign(caller_private_key)
        tx_id = self.client.send_transaction(signed_txn)
        wait_for_confirmation(self.client, tx_id, 4)

        return tx_id

    def deploy_all_contracts(self, creator_private_key):
        """
        Deploy all ESG Chain contracts in correct order

        Args:
            creator_private_key: Creator's private key

        Returns:
            dict: Mapping of contract names to app IDs
        """
        print("\n" + "="*60)
        print("🌱 PAM-TALK ESG Chain - Contract Deployment")
        print("="*60 + "\n")

        # 1. Deploy ESG-Gold Token Contract
        print("\n1️⃣  ESG-Gold Token Contract")
        approval, clear = self.compile_contract(token_approval, token_clear, "esg_gold_token")
        token_app_id = self.deploy_contract(
            creator_private_key,
            approval,
            clear,
            global_schema=StateSchema(num_uints=3, num_byte_slices=3),
            local_schema=StateSchema(num_uints=2, num_byte_slices=0),
            name="ESG-Gold Token"
        )

        # 2. Deploy Committee Multi-Sig Contract
        print("\n2️⃣  Committee Multi-Sig Contract")
        approval, clear = self.compile_contract(committee_approval, committee_clear, "committee_multisig")
        committee_app_id = self.deploy_contract(
            creator_private_key,
            approval,
            clear,
            global_schema=StateSchema(num_uints=3, num_byte_slices=50),
            local_schema=StateSchema(num_uints=0, num_byte_slices=0),
            name="Committee Multi-Sig"
        )

        # 3. Deploy Auto Reward Contract
        print("\n3️⃣  Auto Reward Contract")
        approval, clear = self.compile_contract(reward_approval, reward_clear, "auto_reward")
        reward_app_id = self.deploy_contract(
            creator_private_key,
            approval,
            clear,
            global_schema=StateSchema(num_uints=3, num_byte_slices=2),
            local_schema=StateSchema(num_uints=3, num_byte_slices=0),
            name="Auto Reward"
        )

        # Configure reward contract with token app ID
        print("   Configuring Auto Reward with Token contract...")
        self.call_application(
            creator_private_key,
            reward_app_id,
            [b"set_token_app", token_app_id.to_bytes(8, 'big')]
        )

        # 4. Deploy Charging Settlement Contract
        print("\n4️⃣  Charging Settlement Contract")
        approval, clear = self.compile_contract(settlement_approval, settlement_clear, "charging_settlement")
        settlement_app_id = self.deploy_contract(
            creator_private_key,
            approval,
            clear,
            global_schema=StateSchema(num_uints=4, num_byte_slices=50),
            local_schema=StateSchema(num_uints=0, num_byte_slices=0),
            name="Charging Settlement"
        )

        # Configure settlement contract with token app ID
        print("   Configuring Charging Settlement with Token contract...")
        self.call_application(
            creator_private_key,
            settlement_app_id,
            [b"set_token_app", token_app_id.to_bytes(8, 'big')]
        )

        # 5. Deploy Enterprise Escrow Contract
        print("\n5️⃣  Enterprise Escrow Contract")
        approval, clear = self.compile_contract(escrow_approval, escrow_clear, "enterprise_escrow")
        escrow_app_id = self.deploy_contract(
            creator_private_key,
            approval,
            clear,
            global_schema=StateSchema(num_uints=4, num_byte_slices=50),
            local_schema=StateSchema(num_uints=0, num_byte_slices=0),
            name="Enterprise Escrow"
        )

        # Configure escrow contract with token app ID
        print("   Configuring Enterprise Escrow with Token contract...")
        self.call_application(
            creator_private_key,
            escrow_app_id,
            [b"set_token_app", token_app_id.to_bytes(8, 'big')]
        )

        # Save deployment info
        deployment_info = {
            "network": self.network,
            "contracts": {
                "esg_gold_token": token_app_id,
                "committee_multisig": committee_app_id,
                "auto_reward": reward_app_id,
                "charging_settlement": settlement_app_id,
                "enterprise_escrow": escrow_app_id
            },
            "creator": account.address_from_private_key(creator_private_key)
        }

        with open(f"deployment_{self.network}.json", "w") as f:
            json.dump(deployment_info, f, indent=2)

        print("\n" + "="*60)
        print("✅ All contracts deployed successfully!")
        print("="*60)
        print(f"\n📄 Deployment info saved to: deployment_{self.network}.json")

        print("\n📊 Deployed Contract IDs:")
        for name, app_id in deployment_info["contracts"].items():
            print(f"   {name}: {app_id}")

        return deployment_info


def main():
    """Main deployment function"""

    print("\n🔧 PAM-TALK ESG Chain - Contract Deployment Tool\n")

    # Configuration
    print("Please provide the following information:")

    # Network selection
    network = input("Network (testnet/mainnet) [testnet]: ").strip() or "testnet"

    if network == "testnet":
        # TestNet default
        algod_address = "https://testnet-api.algonode.cloud"
        algod_token = ""  # Public node
    else:
        # MainNet
        algod_address = input("Algod address [https://mainnet-api.algonode.cloud]: ").strip() or "https://mainnet-api.algonode.cloud"
        algod_token = input("Algod token []: ").strip() or ""

    # Creator account
    print("\n🔑 Creator Account:")
    print("Option 1: Generate new account")
    print("Option 2: Use existing mnemonic")
    choice = input("Choice (1/2): ").strip()

    if choice == "1":
        # Generate new account
        private_key, address = account.generate_account()
        mn = mnemonic.from_private_key(private_key)
        print(f"\n✅ New account generated!")
        print(f"Address: {address}")
        print(f"Mnemonic: {mn}")
        print(f"\n⚠️  IMPORTANT: Save this mnemonic securely!")
        print(f"⚠️  Fund this account with ALGO before deployment")
        input("\nPress Enter when account is funded...")
    else:
        # Use existing account
        mn = input("Enter account mnemonic: ").strip()
        private_key = mnemonic.to_private_key(mn)
        address = account.address_from_private_key(private_key)
        print(f"Address: {address}")

    # Create deployer and deploy
    deployer = ContractDeployer(algod_address, algod_token, network)

    try:
        deployment_info = deployer.deploy_all_contracts(private_key)

        print("\n" + "="*60)
        print("🎉 Deployment Complete!")
        print("="*60)
        print("\nNext Steps:")
        print("1. Update backend services with contract IDs")
        print("2. Configure frontend with contract addresses")
        print("3. Test contract interactions")
        print("4. Set up monitoring and alerts")

    except Exception as e:
        print(f"\n❌ Deployment failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if running in compilation-only mode
    if os.getenv("COMPILE_ONLY") == "true":
        print("📝 Compilation-only mode\n")

        # Just compile contracts without deploying
        from esg_gold_token import approval_program as token_approval, clear_state_program as token_clear
        from auto_reward import approval_program as reward_approval, clear_state_program as reward_clear
        from committee_multisig import approval_program as committee_approval, clear_state_program as committee_clear
        from charging_settlement import approval_program as settlement_approval, clear_state_program as settlement_clear
        from enterprise_escrow import approval_program as escrow_approval, clear_state_program as escrow_clear

        contracts = [
            (token_approval, token_clear, "esg_gold_token"),
            (committee_approval, committee_clear, "committee_multisig"),
            (reward_approval, reward_clear, "auto_reward"),
            (settlement_approval, settlement_clear, "charging_settlement"),
            (escrow_approval, escrow_clear, "enterprise_escrow")
        ]

        for approval, clear, name in contracts:
            approval_teal = compileTeal(approval(), mode=Mode.Application, version=8)
            clear_teal = compileTeal(clear(), mode=Mode.Application, version=8)

            with open(f"{name}_approval.teal", "w") as f:
                f.write(approval_teal)
            with open(f"{name}_clear.teal", "w") as f:
                f.write(clear_teal)

            print(f"✅ {name} compiled")

        print("\n✅ All contracts compiled successfully!")
    else:
        main()
