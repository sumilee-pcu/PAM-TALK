"""
ESG-GOLD (DC) Token Creation Script
알고랜드 TestNet에 ESG-GOLD(DC) 토큰 ASA 생성
"""

import json
import os
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import AssetConfigTxn, wait_for_confirmation

# Algorand TestNet 설정
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

# ESG-GOLD 토큰 설정
ESG_GOLD_CONFIG = {
    "asset_name": "ESG-Gold Digital Carbon Credit",
    "unit_name": "DC",
    "total": 10_000_000_000,  # 100억 DC (base units with 6 decimals)
    "decimals": 6,
    "default_frozen": False,
    "url": "https://pam-talk.com/esg-gold",
    "metadata_hash": None,  # 32 bytes, optional
}


def create_algod_client():
    """Algorand 클라이언트 생성"""
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


def create_or_load_creator_account():
    """
    Creator 계정 생성 또는 로드
    .env 파일에서 니모닉을 읽거나, 없으면 새로 생성
    """
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')

    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('ESG_GOLD_CREATOR_MNEMONIC='):
                    creator_mnemonic = line.split('=', 1)[1].strip().strip('"').strip("'")
                    private_key = mnemonic.to_private_key(creator_mnemonic)
                    address = account.address_from_private_key(private_key)
                    print(f"✓ Loaded creator account from .env")
                    print(f"  Address: {address}")
                    return private_key, address, creator_mnemonic

    # 새 계정 생성
    print("Creating new creator account...")
    private_key, address = account.generate_account()
    creator_mnemonic = mnemonic.from_private_key(private_key)

    print(f"\n{'='*60}")
    print("🔐 NEW CREATOR ACCOUNT GENERATED")
    print(f"{'='*60}")
    print(f"Address: {address}")
    print(f"Mnemonic: {creator_mnemonic}")
    print(f"{'='*60}")
    print("\n⚠️  IMPORTANT: Save this mnemonic securely!")
    print("⚠️  Add to .env file: ESG_GOLD_CREATOR_MNEMONIC=\"...\"")
    print(f"\n💰 Fund this account with ALGO at:")
    print(f"   https://testnet.algoexplorer.io/dispenser")
    print(f"   Address: {address}\n")

    # .env 파일에 저장
    with open(env_file, 'a') as f:
        f.write(f'\nESG_GOLD_CREATOR_MNEMONIC="{creator_mnemonic}"\n')

    input("Press Enter after funding the account...")

    return private_key, address, creator_mnemonic


def check_account_balance(client, address):
    """계정 잔액 확인"""
    account_info = client.account_info(address)
    balance = account_info.get('amount', 0) / 1_000_000  # microALGO to ALGO
    return balance


def create_esg_gold_asset(client, creator_private_key, creator_address):
    """ESG-GOLD ASA 생성"""

    # 계정 잔액 확인
    balance = check_account_balance(client, creator_address)
    print(f"\n💰 Account Balance: {balance} ALGO")

    if balance < 0.1:
        print("❌ Insufficient balance. Need at least 0.1 ALGO for transaction.")
        print(f"   Fund account: {creator_address}")
        return None

    # 트랜잭션 파라미터 가져오기
    params = client.suggested_params()

    # Asset Creation Transaction
    txn = AssetConfigTxn(
        sender=creator_address,
        sp=params,
        total=ESG_GOLD_CONFIG["total"],
        default_frozen=ESG_GOLD_CONFIG["default_frozen"],
        unit_name=ESG_GOLD_CONFIG["unit_name"],
        asset_name=ESG_GOLD_CONFIG["asset_name"],
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address,
        url=ESG_GOLD_CONFIG["url"],
        decimals=ESG_GOLD_CONFIG["decimals"]
    )

    # 트랜잭션 서명
    signed_txn = txn.sign(creator_private_key)

    # 트랜잭션 전송
    print("\n📤 Sending asset creation transaction...")
    tx_id = client.send_transaction(signed_txn)
    print(f"   Transaction ID: {tx_id}")

    # 확인 대기
    print("⏳ Waiting for confirmation...")
    confirmed_txn = wait_for_confirmation(client, tx_id, 4)

    # Asset ID 추출
    asset_id = confirmed_txn['asset-index']

    print(f"\n{'='*60}")
    print("✅ ESG-GOLD (DC) TOKEN CREATED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"Asset ID: {asset_id}")
    print(f"Asset Name: {ESG_GOLD_CONFIG['asset_name']}")
    print(f"Unit Name: {ESG_GOLD_CONFIG['unit_name']}")
    print(f"Total Supply: {ESG_GOLD_CONFIG['total'] / 10**ESG_GOLD_CONFIG['decimals']:,.0f} DC")
    print(f"Decimals: {ESG_GOLD_CONFIG['decimals']}")
    print(f"Creator: {creator_address}")
    print(f"Transaction ID: {tx_id}")
    print(f"{'='*60}")

    # 검증 링크
    print(f"\n🔗 Verify on AlgoExplorer:")
    print(f"   Asset: https://testnet.algoexplorer.io/asset/{asset_id}")
    print(f"   Transaction: https://testnet.algoexplorer.io/tx/{tx_id}")

    return {
        "success": True,
        "asset_id": asset_id,
        "asset_name": ESG_GOLD_CONFIG["asset_name"],
        "unit_name": ESG_GOLD_CONFIG["unit_name"],
        "total_supply": ESG_GOLD_CONFIG["total"],
        "decimals": ESG_GOLD_CONFIG["decimals"],
        "creator": creator_address,
        "tx_id": tx_id,
        "created_at": confirmed_txn.get("confirmed-round")
    }


def save_token_info(token_info):
    """토큰 정보를 파일로 저장"""
    output_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'esg_gold_token_created.json'
    )

    with open(output_file, 'w') as f:
        json.dump(token_info, f, indent=2)

    print(f"\n💾 Token info saved to: {output_file}")

    # .env 파일에 asset_id 추가
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    with open(env_file, 'a') as f:
        f.write(f'ESG_GOLD_ASSET_ID={token_info["asset_id"]}\n')

    print(f"💾 Asset ID added to .env file")


def main():
    """메인 실행 함수"""
    print("\n" + "="*60)
    print("ESG-GOLD (DC) TOKEN CREATION")
    print("="*60)

    # 1. Algod 클라이언트 생성
    print("\n[1/4] Connecting to Algorand TestNet...")
    client = create_algod_client()
    status = client.status()
    print(f"✓ Connected to TestNet (Round: {status['last-round']})")

    # 2. Creator 계정 로드/생성
    print("\n[2/4] Loading creator account...")
    private_key, address, mnemonic_phrase = create_or_load_creator_account()

    # 3. ESG-GOLD 토큰 생성
    print("\n[3/4] Creating ESG-GOLD (DC) asset...")
    token_info = create_esg_gold_asset(client, private_key, address)

    if not token_info:
        print("\n❌ Asset creation failed. Please check account balance and try again.")
        return

    # 4. 토큰 정보 저장
    print("\n[4/4] Saving token information...")
    save_token_info(token_info)

    print("\n" + "="*60)
    print("🎉 ESG-GOLD (DC) TOKEN SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update frontend with new asset ID")
    print("2. Update backend configuration")
    print("3. Implement collateral deposit system")
    print("4. Implement DC minting engine")
    print("\n")


if __name__ == "__main__":
    main()
