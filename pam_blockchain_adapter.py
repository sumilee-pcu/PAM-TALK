#!/usr/bin/env python3
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
