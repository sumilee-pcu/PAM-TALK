#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESG-Gold ASA Token Deployment Script
Creates ESG-GOLD token on Algorand blockchain
1 ESG-GOLD = 1 DC (Digital Carbon) = 1kg CO2 reduction
"""

import json
import os
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, wait_for_confirmation


def load_config(config_path='esg_gold_config.json'):
    """Load ESG-Gold configuration"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_algod_client(config):
    """Create Algorand client"""
    algod_address = config['algod_endpoint']
    algod_token = ""  # Public API requires no token
    return algod.AlgodClient(algod_token, algod_address)


def create_esg_gold_asset(client, creator_address, creator_private_key, config):
    """
    Create ESG-GOLD ASA token on Algorand

    Parameters:
    - client: Algorand client
    - creator_address: Creator wallet address
    - creator_private_key: Creator private key
    - config: ESG-GOLD configuration

    Returns:
    - asset_id: Created asset ID
    """
    params = client.suggested_params()

    # Asset creation transaction
    txn = AssetConfigTxn(
        sender=creator_address,
        sp=params,
        total=config['total_supply'],
        default_frozen=False,
        unit_name=config['unit_name'],
        asset_name=config['token_name'],
        manager=creator_address,  # Can change asset configuration
        reserve=creator_address,  # Can receive reserved tokens
        freeze=creator_address,   # Can freeze accounts
        clawback=creator_address, # Can revoke tokens (for compliance)
        url=config['url'],
        decimals=config['decimals'],
        note=config['description'].encode()
    )

    # Sign transaction
    signed_txn = txn.sign(creator_private_key)

    # Submit transaction
    tx_id = client.send_transaction(signed_txn)
    print(f"Transaction ID: {tx_id}")
    print("Waiting for confirmation...")

    # Wait for confirmation
    confirmed_txn = wait_for_confirmation(client, tx_id, 4)

    # Get asset ID
    asset_id = confirmed_txn['asset-index']
    print(f"\n✅ ESG-GOLD Token Created Successfully!")
    print(f"Asset ID: {asset_id}")
    print(f"Transaction ID: {tx_id}")
    print(f"Block: {confirmed_txn['confirmed-round']}")

    return asset_id


def update_config_with_asset_id(config_path, asset_id):
    """Update configuration file with new asset ID"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    config['token_id'] = str(asset_id)

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Configuration updated with Asset ID: {asset_id}")


def display_token_info(client, asset_id, config):
    """Display created token information"""
    asset_info = client.asset_info(asset_id)

    print("\n" + "="*60)
    print("ESG-GOLD TOKEN INFORMATION")
    print("="*60)
    print(f"Asset ID: {asset_id}")
    print(f"Name: {asset_info['params']['name']}")
    print(f"Symbol: {config['token_symbol']}")
    print(f"Unit: {asset_info['params']['unit-name']}")
    print(f"Total Supply: {asset_info['params']['total']:,}")
    print(f"Decimals: {asset_info['params']['decimals']}")
    print(f"Actual Supply: {asset_info['params']['total'] / (10 ** asset_info['params']['decimals']):,.2f} ESG-GOLD")
    print(f"URL: {asset_info['params'].get('url', 'N/A')}")
    print(f"Creator: {asset_info['params']['creator']}")
    print(f"\nConversion Rate:")
    print(f"  1 DC = 1 kg CO2 reduction")
    print(f"  1 ESG-GOLD = 1 DC = 1 kg CO2")
    print(f"\nExplorer URL:")
    print(f"  https://testnet.algoexplorer.io/asset/{asset_id}")
    print("="*60)


def main():
    """Main deployment function"""
    print("ESG-GOLD Token Deployment")
    print("="*60)

    # Load configuration
    config = load_config()
    print(f"✓ Configuration loaded")

    # Check if already deployed
    if config.get('token_id'):
        print(f"\n⚠️  ESG-GOLD token already deployed!")
        print(f"Asset ID: {config['token_id']}")
        print(f"Network: {config['network']}")

        response = input("\nDeploy a new token? (yes/no): ")
        if response.lower() != 'yes':
            print("Deployment cancelled.")
            return

    # Get creator account
    print("\n" + "="*60)
    print("CREATOR ACCOUNT SETUP")
    print("="*60)
    print("Options:")
    print("1. Use existing account (provide mnemonic)")
    print("2. Generate new account")

    choice = input("\nSelect option (1 or 2): ").strip()

    if choice == '1':
        # Use existing account
        creator_mnemonic = input("Enter creator account mnemonic (25 words): ").strip()
        try:
            creator_private_key = mnemonic.to_private_key(creator_mnemonic)
            creator_address = account.address_from_private_key(creator_private_key)
            print(f"\n✓ Creator address: {creator_address}")
        except Exception as e:
            print(f"\n❌ Invalid mnemonic: {e}")
            return

    elif choice == '2':
        # Generate new account
        creator_private_key, creator_address = account.generate_account()
        creator_mnemonic = mnemonic.from_private_key(creator_private_key)

        print(f"\n✓ New account generated!")
        print(f"Address: {creator_address}")
        print(f"\n⚠️  SAVE THIS MNEMONIC (25 words):")
        print(f"{creator_mnemonic}")
        print("\n⚠️  Fund this account with ALGO before proceeding:")
        print(f"https://testnet.algoexplorer.io/address/{creator_address}")
        print("Get testnet ALGO from: https://bank.testnet.algorand.network/")

        input("\nPress Enter after funding the account...")

    else:
        print("Invalid option")
        return

    # Create client
    client = create_algod_client(config)
    print("✓ Connected to Algorand network")

    # Check balance
    try:
        account_info = client.account_info(creator_address)
        balance = account_info.get('amount', 0) / 1_000_000
        print(f"✓ Account balance: {balance:.6f} ALGO")

        if balance < 0.2:
            print("\n⚠️  Warning: Low balance. Asset creation requires ~0.2 ALGO")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != 'yes':
                return
    except Exception as e:
        print(f"\n❌ Error checking balance: {e}")
        return

    # Create ESG-GOLD asset
    print("\n" + "="*60)
    print("CREATING ESG-GOLD TOKEN")
    print("="*60)

    try:
        asset_id = create_esg_gold_asset(client, creator_address, creator_private_key, config)

        # Update config
        update_config_with_asset_id('esg_gold_config.json', asset_id)

        # Display token info
        display_token_info(client, asset_id, config)

        print("\n✅ Deployment completed successfully!")
        print("\nNext steps:")
        print("1. Save the Asset ID and creator account details securely")
        print("2. Configure ESG-Gold service with this Asset ID")
        print("3. Set up automatic minting for carbon reduction activities")
        print("4. Integrate with marketplace payment system")

    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
