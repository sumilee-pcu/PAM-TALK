#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK 플랫폼을 실제 토큰 ID로 업데이트
시뮬레이션에서 실제 블록체인으로 전환
"""

import json
import os
from datetime import datetime

def update_platform_config():
    """플랫폼 설정을 실제 토큰으로 업데이트"""

    print("Updating PAM-TALK Platform Configuration")
    print("=" * 45)

    # 새 토큰 정보
    new_token_config = {
        "mode": "blockchain",  # simulation에서 blockchain으로 변경
        "token_id": "746506198",  # 새로 생성된 토큰 ID
        "token_name": "PAM-TALK ESG Token",
        "token_symbol": "PAM",
        "total_supply": 1000000000,
        "decimals": 3,
        "creator_account": "3MKYZNK57LRFLWUBJG33KJZJTX4WX2EJAJNHQQSWUZ6QVTEM4DEI4Y2AF4",
        "network": "testnet",
        "algod_endpoint": "https://testnet-api.algonode.cloud",
        "updated_at": datetime.now().isoformat()
    }

    print("New Token Configuration:")
    print(f"Mode: {new_token_config['mode']}")
    print(f"Token ID: {new_token_config['token_id']}")
    print(f"Symbol: {new_token_config['token_symbol']}")
    print(f"Supply: {new_token_config['total_supply']:,}")

    # 설정 파일 생성
    config_filename = "pam_token_config.json"
    with open(config_filename, 'w') as f:
        json.dump(new_token_config, f, indent=2)

    print(f"\nConfiguration saved to: {config_filename}")

    # 환경 변수 업데이트 스크립트 생성
    env_script = f"""# PAM-TALK Environment Variables
# Generated on {datetime.now().isoformat()}

export PAM_TOKEN_MODE=blockchain
export PAM_TOKEN_ID=746506198
export PAM_TOKEN_SYMBOL=PAM
export PAM_CREATOR_ACCOUNT=3MKYZNK57LRFLWUBJG33KJZJTX4WX2EJAJNHQQSWUZ6QVTEM4DEI4Y2AF4
export PAM_ALGOD_ENDPOINT=https://testnet-api.algonode.cloud
export PAM_NETWORK=testnet

# Windows CMD version
set PAM_TOKEN_MODE=blockchain
set PAM_TOKEN_ID=746506198
set PAM_TOKEN_SYMBOL=PAM
set PAM_CREATOR_ACCOUNT=3MKYZNK57LRFLWUBJG33KJZJTX4WX2EJAJNHQQSWUZ6QVTEM4DEI4Y2AF4
set PAM_ALGOD_ENDPOINT=https://testnet-api.algonode.cloud
set PAM_NETWORK=testnet
"""

    with open("pam_env_vars.sh", 'w') as f:
        f.write(env_script)

    print("Environment variables saved to: pam_env_vars.sh")

    return new_token_config

def verify_token_status():
    """새 토큰 상태 확인"""

    print("\nVerifying New Token Status")
    print("-" * 30)

    import requests

    try:
        # 알고노드 API로 토큰 정보 확인
        token_id = "746506198"
        api_url = f"https://testnet-api.algonode.cloud/v2/assets/{token_id}"

        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            token_data = response.json()

            print("[SUCCESS] Token verification successful!")
            print(f"Asset ID: {token_data['index']}")
            print(f"Name: {token_data['params']['name']}")
            print(f"Unit Name: {token_data['params']['unit-name']}")
            print(f"Total: {token_data['params']['total']:,}")
            print(f"Decimals: {token_data['params']['decimals']}")
            print(f"Creator: {token_data['params']['creator']}")

            return True

        else:
            print(f"[ERROR] Token verification failed: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] Token verification error: {e}")
        return False

def create_blockchain_adapter():
    """실제 블록체인과 연동하는 어댑터 생성"""

    adapter_code = '''#!/usr/bin/env python3
"""
PAM Token Blockchain Adapter
실제 알고랜드 블록체인과 연동
"""

import json
import requests
from algosdk.v2client import algod
from algosdk import account, transaction

class PAMTokenAdapter:
    def __init__(self):
        # 설정 로드
        with open('pam_token_config.json', 'r') as f:
            self.config = json.load(f)

        self.algod_client = algod.AlgodClient("", self.config['algod_endpoint'])
        self.token_id = int(self.config['token_id'])

    def get_token_info(self):
        """토큰 정보 조회"""
        try:
            response = self.algod_client.asset_info(self.token_id)
            return {
                "success": True,
                "token": {
                    "id": response['index'],
                    "name": response['params']['name'],
                    "symbol": response['params']['unit-name'],
                    "total_supply": response['params']['total'],
                    "decimals": response['params']['decimals'],
                    "creator": response['params']['creator']
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_account_balance(self, address: str):
        """계정의 PAM 토큰 잔액 조회"""
        try:
            account_info = self.algod_client.account_info(address)
            assets = account_info.get('assets', [])

            for asset in assets:
                if asset['asset-id'] == self.token_id:
                    return {
                        "success": True,
                        "balance": asset['amount'] / (10 ** self.config['decimals'])
                    }

            return {"success": True, "balance": 0.0}

        except Exception as e:
            return {"success": False, "error": str(e)}

# 전역 어댑터 인스턴스
pam_adapter = PAMTokenAdapter()
'''

    with open("pam_blockchain_adapter.py", 'w') as f:
        f.write(adapter_code)

    print("Blockchain adapter created: pam_blockchain_adapter.py")

def main():
    """메인 업데이트 프로세스"""

    print("PAM-TALK BLOCKCHAIN INTEGRATION")
    print("=" * 50)

    # 1. 설정 업데이트
    config = update_platform_config()

    # 2. 토큰 상태 확인
    token_verified = verify_token_status()

    # 3. 블록체인 어댑터 생성
    create_blockchain_adapter()

    print("\n" + "=" * 50)
    print("INTEGRATION COMPLETE!")
    print("=" * 50)

    if token_verified:
        print("[SUCCESS] Real PAM token is now active")
        print("[SUCCESS] Platform ready for blockchain operations")
        print()
        print("Next Steps:")
        print("1. Restart PAM-TALK platform")
        print("2. Test token operations through admin dashboard")
        print("3. Initialize token distribution to users")
        print()
        print("Admin Dashboard: http://localhost:5001/admin")
        print("Platform API: http://localhost:5003/api/token/info")
    else:
        print("[WARNING] Token verification failed")
        print("[INFO] Platform will continue in simulation mode")

if __name__ == "__main__":
    main()