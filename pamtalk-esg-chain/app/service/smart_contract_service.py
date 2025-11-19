# -*- coding: utf-8 -*-
"""
스마트계약 서비스 모듈
PyTeal 기반 ESG 보상 정책 스마트계약과의 연동
"""

import os
from algosdk import account, encoding
from algosdk.future import transaction
from algosdk.v2client import algod
from pyteal import *

from app.config import HCF_MNEMONIC, HCF_ADDRESS
from app.utils.algorand_utils import get_algod_client
from app.utils.wallet_utils import get_wallet_keys


class SmartContractService:
    """스마트계약 서비스 클래스"""

    def __init__(self):
        self.algod_client = get_algod_client()
        self.admin_address, self.admin_private_key = get_wallet_keys(HCF_MNEMONIC)

    def compile_contract(self, contract_teal):
        """TEAL 코드 컴파일"""
        try:
            response = self.algod_client.compile(contract_teal)
            return response['result'], response['hash']
        except Exception as e:
            raise Exception(f"컨트랙트 컴파일 실패: {str(e)}")

    def deploy_reward_policy_contract(self):
        """ESG 보상 정책 스마트계약 배포"""
        from contracts.reward_policy import reward_policy_contract

        print("[📋 스마트계약 배포 시작]")

        try:
            # 1. 컨트랙트 컴파일
            contract = reward_policy_contract()
            teal_source = compileTeal(contract, Mode.Application, version=8)
            compiled_program, program_hash = self.compile_contract(teal_source)

            print(f"[✅ 컴파일 완료] 해시: {program_hash}")

            # 2. 애플리케이션 생성 트랜잭션
            params = self.algod_client.suggested_params()

            # 스키마 정의
            global_schema = transaction.StateSchema(
                num_uints=4,  # total_supply, issued_supply, carbon_rate 등
                num_byte_slices=1  # admin
            )
            local_schema = transaction.StateSchema(
                num_uints=3,  # role, carbon_saved, tokens_earned
                num_byte_slices=0
            )

            # 애플리케이션 생성 트랜잭션
            app_create_txn = transaction.ApplicationCreateTxn(
                sender=self.admin_address,
                sp=params,
                on_complete=0,  # NoOp
                approval_program=compiled_program,
                clear_program=b"",  # Clear program (간단한 경우 비워둠)
                global_schema=global_schema,
                local_schema=local_schema
            )

            # 3. 트랜잭션 서명 및 전송
            signed_txn = app_create_txn.sign(self.admin_private_key)
            tx_id = self.algod_client.send_transaction(signed_txn)

            print(f"[📤 트랜잭션 전송] ID: {tx_id}")

            # 4. 트랜잭션 확인
            confirmed_txn = transaction.wait_for_confirmation(
                self.algod_client, tx_id, 10
            )

            app_id = confirmed_txn['application-index']
            print(f"[🎉 스마트계약 배포 완료] App ID: {app_id}")

            return {
                'success': True,
                'app_id': app_id,
                'tx_id': tx_id,
                'program_hash': program_hash
            }

        except Exception as e:
            print(f"[❌ 배포 실패] {str(e)}")
            raise Exception(f"스마트계약 배포 실패: {str(e)}")

    def call_contract_method(self, app_id, method, args=None, sender_mnemonic=None):
        """스마트계약 메서드 호출"""
        if sender_mnemonic:
            sender_address, sender_private_key = get_wallet_keys(sender_mnemonic)
        else:
            sender_address, sender_private_key = self.admin_address, self.admin_private_key

        try:
            params = self.algod_client.suggested_params()

            # 애플리케이션 호출 트랜잭션
            app_args = [method.encode()]
            if args:
                app_args.extend([arg.encode() if isinstance(arg, str) else arg for arg in args])

            app_call_txn = transaction.ApplicationCallTxn(
                sender=sender_address,
                sp=params,
                index=app_id,
                on_complete=0,  # NoOp
                app_args=app_args
            )

            # 트랜잭션 서명 및 전송
            signed_txn = app_call_txn.sign(sender_private_key)
            tx_id = self.algod_client.send_transaction(signed_txn)

            # 트랜잭션 확인
            confirmed_txn = transaction.wait_for_confirmation(
                self.algod_client, tx_id, 10
            )

            print(f"[✅ 스마트계약 호출 완료] Method: {method}, TX: {tx_id}")

            return {
                'success': True,
                'tx_id': tx_id,
                'confirmed_round': confirmed_txn['confirmed-round']
            }

        except Exception as e:
            print(f"[❌ 스마트계약 호출 실패] {str(e)}")
            raise Exception(f"스마트계약 호출 실패: {str(e)}")

    def set_user_role(self, app_id, target_address, role):
        """사용자 역할 설정"""
        return self.call_contract_method(
            app_id=app_id,
            method="set_role",
            args=[target_address, str(role)]
        )

    def record_carbon_savings(self, app_id, carbon_amount, activity_type, user_mnemonic):
        """탄소 절약량 기록"""
        return self.call_contract_method(
            app_id=app_id,
            method="record_carbon",
            args=[str(carbon_amount), activity_type],
            sender_mnemonic=user_mnemonic
        )

    def validate_token_transfer(self, app_id, sender_role, receiver_role, amount):
        """토큰 전송 검증"""
        return self.call_contract_method(
            app_id=app_id,
            method="validate_transfer",
            args=[str(sender_role), str(receiver_role), str(amount)]
        )

    def get_app_state(self, app_id):
        """애플리케이션 상태 조회"""
        try:
            app_info = self.algod_client.application_info(app_id)
            global_state = app_info['params']['global-state']

            # 상태 디코딩
            decoded_state = {}
            for item in global_state:
                key = encoding.base64.b64decode(item['key']).decode('utf-8')
                if item['value']['type'] == 1:  # bytes
                    value = encoding.base64.b64decode(item['value']['bytes']).decode('utf-8')
                else:  # uint
                    value = item['value']['uint']
                decoded_state[key] = value

            return decoded_state

        except Exception as e:
            raise Exception(f"애플리케이션 상태 조회 실패: {str(e)}")


# 사용 예시
if __name__ == "__main__":
    service = SmartContractService()

    # 스마트계약 배포
    result = service.deploy_reward_policy_contract()
    if result['success']:
        app_id = result['app_id']
        print(f"배포된 앱 ID: {app_id}")

        # 앱 상태 조회
        state = service.get_app_state(app_id)
        print(f"앱 상태: {state}")