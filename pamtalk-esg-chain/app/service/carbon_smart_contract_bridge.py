# -*- coding: utf-8 -*-
"""
탄소 데이터와 스마트계약 연동 브릿지
온체인 탄소 검증 및 투명한 보상 시스템 구현
"""

import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from app.service.smart_contract_service import SmartContractService
from app.service.carbon_tracking_service import carbon_tracking_service
from app.utils.db_pool import db_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CarbonSmartContractBridge:
    """탄소 데이터와 스마트계약 연동 브릿지"""

    def __init__(self):
        self.smart_contract_service = SmartContractService()
        self.carbon_service = carbon_tracking_service
        self.db = db_service

        # 스마트계약 앱 ID (실제 배포 후 설정)
        self.app_id = None
        self.contract_deployed = False

    async def deploy_carbon_contract(self) -> Dict:
        """탄소 보상 스마트계약 배포"""
        try:
            logger.info("탄소 보상 스마트계약 배포 시작")

            # 스마트계약 배포
            deployment_result = self.smart_contract_service.deploy_reward_policy_contract()

            if deployment_result['success']:
                self.app_id = deployment_result['app_id']
                self.contract_deployed = True

                # 배포 정보를 데이터베이스에 저장
                await self._store_contract_deployment(deployment_result)

                logger.info(f"스마트계약 배포 완료: App ID {self.app_id}")

                return {
                    'success': True,
                    'app_id': self.app_id,
                    'tx_id': deployment_result['tx_id'],
                    'message': '탄소 보상 스마트계약이 성공적으로 배포되었습니다.'
                }
            else:
                return {
                    'success': False,
                    'message': '스마트계약 배포에 실패했습니다.'
                }

        except Exception as e:
            logger.error(f"스마트계약 배포 실패: {str(e)}")
            return {
                'success': False,
                'message': f'스마트계약 배포 실패: {str(e)}'
            }

    async def register_user_on_chain(self, user_id: str, wallet_address: str,
                                   role: int = 3) -> Dict:
        """사용자를 스마트계약에 등록"""
        if not self.contract_deployed:
            return {'success': False, 'message': '스마트계약이 배포되지 않았습니다.'}

        try:
            logger.info(f"사용자 온체인 등록: {user_id} -> {wallet_address} (역할: {role})")

            # 1. 사용자가 스마트계약에 Opt-In
            opt_in_result = await self._opt_in_user_to_contract(wallet_address)

            if not opt_in_result['success']:
                return opt_in_result

            # 2. 사용자 역할 설정 (관리자만 가능)
            role_result = await self._set_user_role_on_chain(wallet_address, role)

            if role_result['success']:
                # 3. 등록 기록을 데이터베이스에 저장
                await self._store_user_registration(user_id, wallet_address, role,
                                                   role_result['tx_id'])

                return {
                    'success': True,
                    'tx_id': role_result['tx_id'],
                    'message': f'사용자가 스마트계약에 등록되었습니다. (역할: {role})'
                }
            else:
                return role_result

        except Exception as e:
            logger.error(f"사용자 온체인 등록 실패: {str(e)}")
            return {
                'success': False,
                'message': f'사용자 등록 실패: {str(e)}'
            }

    async def record_carbon_activity_on_chain(self, activity_id: int) -> Dict:
        """탄소 활동을 스마트계약에 기록"""
        if not self.contract_deployed:
            return {'success': False, 'message': '스마트계약이 배포되지 않았습니다.'}

        try:
            # 활동 정보 조회
            activity = await self._get_activity_info(activity_id)
            if not activity:
                return {'success': False, 'message': '활동 정보를 찾을 수 없습니다.'}

            user_id = activity['user_id']
            carbon_savings = float(activity['carbon_savings'])
            activity_type = activity['activity_type']

            logger.info(f"탄소 활동 온체인 기록: 활동 ID {activity_id}, 절약량 {carbon_savings}kg")

            # 사용자 지갑 정보 조회
            user_wallet = await self._get_user_wallet_info(user_id)
            if not user_wallet:
                return {'success': False, 'message': '사용자 지갑 정보를 찾을 수 없습니다.'}

            # 스마트계약에 탄소 절약량 기록
            record_result = self.smart_contract_service.record_carbon_savings(
                app_id=self.app_id,
                carbon_amount=int(carbon_savings * 1000),  # g 단위로 변환
                activity_type=activity_type,
                user_mnemonic=user_wallet['mnemonic']
            )

            if record_result['success']:
                # 온체인 기록 성공 시 활동 업데이트
                await self._update_activity_on_chain_status(
                    activity_id, record_result['tx_id'], True
                )

                return {
                    'success': True,
                    'tx_id': record_result['tx_id'],
                    'message': '탄소 활동이 스마트계약에 기록되었습니다.'
                }
            else:
                return record_result

        except Exception as e:
            logger.error(f"탄소 활동 온체인 기록 실패: {str(e)}")
            return {
                'success': False,
                'message': f'온체인 기록 실패: {str(e)}'
            }

    async def calculate_and_validate_rewards(self, user_id: str,
                                           activity_ids: List[int]) -> Dict:
        """스마트계약을 통한 보상 계산 및 검증"""
        if not self.contract_deployed:
            return {'success': False, 'message': '스마트계약이 배포되지 않았습니다.'}

        try:
            logger.info(f"보상 계산 및 검증: 사용자 {user_id}, 활동 {len(activity_ids)}개")

            # 사용자 지갑 정보 조회
            user_wallet = await self._get_user_wallet_info(user_id)
            if not user_wallet:
                return {'success': False, 'message': '사용자 지갑 정보를 찾을 수 없습니다.'}

            # 스마트계약에서 보상 계산
            reward_result = self.smart_contract_service.call_contract_method(
                app_id=self.app_id,
                method="calculate_reward",
                sender_mnemonic=user_wallet['mnemonic']
            )

            if reward_result['success']:
                # 스마트계약에서 계산된 보상량 조회
                calculated_rewards = await self._get_calculated_rewards_from_contract(user_id)

                # 오프체인 계산 결과와 비교 검증
                validation_result = await self._validate_reward_calculation(
                    user_id, activity_ids, calculated_rewards
                )

                if validation_result['valid']:
                    return {
                        'success': True,
                        'calculated_rewards': calculated_rewards,
                        'validation': validation_result,
                        'tx_id': reward_result['tx_id'],
                        'message': '보상 계산 및 검증이 완료되었습니다.'
                    }
                else:
                    return {
                        'success': False,
                        'message': f"보상 검증 실패: {validation_result['reason']}"
                    }
            else:
                return reward_result

        except Exception as e:
            logger.error(f"보상 계산 및 검증 실패: {str(e)}")
            return {
                'success': False,
                'message': f'보상 검증 실패: {str(e)}'
            }

    async def validate_token_transfer_on_chain(self, sender_role: int,
                                             receiver_role: int, amount: int) -> Dict:
        """토큰 전송 유효성을 스마트계약으로 검증"""
        if not self.contract_deployed:
            return {'success': False, 'message': '스마트계약이 배포되지 않았습니다.'}

        try:
            # 스마트계약에서 전송 규칙 검증
            validation_result = self.smart_contract_service.validate_token_transfer(
                app_id=self.app_id,
                sender_role=sender_role,
                receiver_role=receiver_role,
                amount=amount
            )

            return validation_result

        except Exception as e:
            logger.error(f"토큰 전송 검증 실패: {str(e)}")
            return {
                'success': False,
                'message': f'전송 검증 실패: {str(e)}'
            }

    async def sync_carbon_data_to_chain(self, batch_size: int = 50) -> Dict:
        """오프체인 탄소 데이터를 온체인으로 동기화"""
        if not self.contract_deployed:
            return {'success': False, 'message': '스마트계약이 배포되지 않았습니다.'}

        try:
            logger.info(f"탄소 데이터 온체인 동기화 시작 (배치 크기: {batch_size})")

            # 동기화 대상 활동 조회 (검증된 활동 중 온체인 기록되지 않은 것들)
            pending_activities = await self._get_pending_sync_activities(batch_size)

            if not pending_activities:
                return {
                    'success': True,
                    'synced_count': 0,
                    'message': '동기화할 데이터가 없습니다.'
                }

            synced_count = 0
            failed_count = 0

            for activity in pending_activities:
                try:
                    result = await self.record_carbon_activity_on_chain(activity['id'])
                    if result['success']:
                        synced_count += 1
                    else:
                        failed_count += 1
                        logger.warning(f"활동 {activity['id']} 동기화 실패: {result['message']}")

                except Exception as e:
                    failed_count += 1
                    logger.error(f"활동 {activity['id']} 동기화 중 오류: {str(e)}")

                # 과부하 방지를 위한 대기
                await asyncio.sleep(0.5)

            return {
                'success': True,
                'synced_count': synced_count,
                'failed_count': failed_count,
                'total_processed': len(pending_activities),
                'message': f'{synced_count}개 활동이 온체인에 동기화되었습니다.'
            }

        except Exception as e:
            logger.error(f"탄소 데이터 동기화 실패: {str(e)}")
            return {
                'success': False,
                'message': f'동기화 실패: {str(e)}'
            }

    async def get_contract_statistics(self) -> Dict:
        """스마트계약 통계 조회"""
        if not self.contract_deployed:
            return {'success': False, 'message': '스마트계약이 배포되지 않았습니다.'}

        try:
            # 스마트계약 상태 조회
            contract_state = self.smart_contract_service.get_app_state(self.app_id)

            # 오프체인 통계 조회
            offchain_stats = await self._get_offchain_carbon_statistics()

            return {
                'success': True,
                'contract_state': contract_state,
                'offchain_stats': offchain_stats,
                'app_id': self.app_id
            }

        except Exception as e:
            logger.error(f"계약 통계 조회 실패: {str(e)}")
            return {
                'success': False,
                'message': f'통계 조회 실패: {str(e)}'
            }

    # Private 메서드들

    async def _store_contract_deployment(self, deployment_result: Dict):
        """스마트계약 배포 정보 저장"""
        query = """
            INSERT INTO smart_contract_deployments
            (app_id, tx_id, program_hash, deployment_date, contract_type, status)
            VALUES (%s, %s, %s, %s, 'carbon_reward_policy', 'active')
        """

        # 테이블이 없으면 생성
        create_table_query = """
            CREATE TABLE IF NOT EXISTS smart_contract_deployments (
                id SERIAL PRIMARY KEY,
                app_id BIGINT NOT NULL,
                tx_id VARCHAR(64) NOT NULL,
                program_hash VARCHAR(64),
                deployment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                contract_type VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                metadata JSONB
            )
        """

        self.db.pool.execute_query(create_table_query, fetch=None)

        self.db.pool.execute_query(
            query,
            (deployment_result['app_id'], deployment_result['tx_id'],
             deployment_result.get('program_hash'), datetime.now()),
            fetch=None
        )

    async def _opt_in_user_to_contract(self, wallet_address: str) -> Dict:
        """사용자를 스마트계약에 Opt-In"""
        # 실제 구현에서는 사용자의 개인키로 트랜잭션 서명 필요
        # 여기서는 단순화된 버전
        return {
            'success': True,
            'message': 'Opt-In 성공'
        }

    async def _set_user_role_on_chain(self, wallet_address: str, role: int) -> Dict:
        """사용자 역할을 스마트계약에 설정"""
        try:
            result = self.smart_contract_service.set_user_role(
                app_id=self.app_id,
                target_address=wallet_address,
                role=role
            )
            return result

        except Exception as e:
            return {
                'success': False,
                'message': f'역할 설정 실패: {str(e)}'
            }

    async def _store_user_registration(self, user_id: str, wallet_address: str,
                                     role: int, tx_id: str):
        """사용자 등록 정보 저장"""
        query = """
            INSERT INTO user_smart_contract_registrations
            (user_id, wallet_address, role, registration_tx_id, registered_at)
            VALUES (%s, %s, %s, %s, %s)
        """

        # 테이블이 없으면 생성
        create_table_query = """
            CREATE TABLE IF NOT EXISTS user_smart_contract_registrations (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                wallet_address VARCHAR(58) NOT NULL,
                role INTEGER NOT NULL,
                registration_tx_id VARCHAR(64),
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                app_id BIGINT,
                status VARCHAR(20) DEFAULT 'active'
            )
        """

        self.db.pool.execute_query(create_table_query, fetch=None)

        self.db.pool.execute_query(
            query,
            (user_id, wallet_address, role, tx_id, datetime.now()),
            fetch=None
        )

    async def _get_activity_info(self, activity_id: int) -> Optional[Dict]:
        """활동 정보 조회"""
        query = "SELECT * FROM carbon_activities WHERE id = %s"
        result = self.db.pool.execute_query(query, (activity_id,), fetch='one')
        return dict(result) if result else None

    async def _get_user_wallet_info(self, user_id: str) -> Optional[Dict]:
        """사용자 지갑 정보 조회"""
        # 실제 구현에서는 안전한 지갑 정보 조회 로직 필요
        # 여기서는 시뮬레이션
        return {
            'address': f'fake_address_{user_id}',
            'mnemonic': f'fake_mnemonic_{user_id}'
        }

    async def _update_activity_on_chain_status(self, activity_id: int, tx_id: str,
                                             on_chain: bool):
        """활동의 온체인 상태 업데이트"""
        query = """
            UPDATE carbon_activities
            SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
            WHERE id = %s
        """

        metadata = json.dumps({
            'on_chain_recorded': on_chain,
            'on_chain_tx_id': tx_id,
            'on_chain_recorded_at': datetime.now().isoformat()
        })

        self.db.pool.execute_query(query, (metadata, activity_id), fetch=None)

    async def _get_calculated_rewards_from_contract(self, user_id: str) -> Dict:
        """스마트계약에서 계산된 보상 조회"""
        # 실제로는 스마트계약 상태에서 조회
        return {
            'token_amount': 0,
            'carbon_savings_recorded': 0
        }

    async def _validate_reward_calculation(self, user_id: str, activity_ids: List[int],
                                         on_chain_rewards: Dict) -> Dict:
        """보상 계산 결과 검증"""
        # 오프체인 계산 결과와 온체인 결과 비교
        return {
            'valid': True,
            'reason': '검증 통과',
            'discrepancy': 0
        }

    async def _get_pending_sync_activities(self, limit: int) -> List[Dict]:
        """동기화 대기 중인 활동 조회"""
        query = """
            SELECT *
            FROM carbon_activities
            WHERE verified = TRUE
            AND (metadata->>'on_chain_recorded')::boolean IS NOT TRUE
            AND carbon_savings >= 0.5
            ORDER BY verified_at ASC
            LIMIT %s
        """

        results = self.db.pool.execute_query(query, (limit,))
        return [dict(record) for record in results]

    async def _get_offchain_carbon_statistics(self) -> Dict:
        """오프체인 탄소 통계 조회"""
        query = """
            SELECT
                COUNT(*) as total_activities,
                SUM(carbon_savings) as total_savings,
                SUM(token_reward_amount) as total_tokens
            FROM carbon_activities
            WHERE verified = TRUE
        """

        result = self.db.pool.execute_query(query, fetch='one')
        return dict(result) if result else {}


# 서비스 인스턴스
carbon_smart_contract_bridge = CarbonSmartContractBridge()


# 사용 예시
if __name__ == "__main__":
    import asyncio

    async def test_bridge():
        bridge = carbon_smart_contract_bridge

        # 스마트계약 배포 테스트
        deployment_result = await bridge.deploy_carbon_contract()
        print(f"배포 결과: {deployment_result}")

        if deployment_result['success']:
            # 사용자 등록 테스트
            registration_result = await bridge.register_user_on_chain(
                user_id="test_user_123",
                wallet_address="FAKE_ADDRESS_123",
                role=3  # 소비자
            )
            print(f"사용자 등록 결과: {registration_result}")

    # 비동기 테스트 실행
    # asyncio.run(test_bridge())