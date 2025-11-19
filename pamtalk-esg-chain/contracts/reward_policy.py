# -*- coding: utf-8 -*-
"""
PAM-TALK ESG Reward Policy Smart Contract
PyTeal-based smart contract for on-chain reward verification
"""

from pyteal import *

def reward_policy_contract():
    """
    ESG 보상 정책 스마트계약

    목적:
    1. 탄소 절약량 기반 토큰 발행 정책 검증
    2. 위원회 → 공급자 → 소비자 배분 규칙 검증
    3. 부정행위 방지 및 투명성 확보
    """

    # 글로벌 상태 키
    admin_key = Bytes("admin")
    total_supply_key = Bytes("total_supply")
    issued_supply_key = Bytes("issued_supply")
    carbon_rate_key = Bytes("carbon_rate")  # kg당 토큰 비율

    # 로컬 상태 키 (각 계정별)
    role_key = Bytes("role")  # COMMITTEE(1), PROVIDER(2), CONSUMER(3)
    carbon_saved_key = Bytes("carbon_saved")  # 누적 탄소 절약량
    tokens_earned_key = Bytes("tokens_earned")  # 획득한 토큰량

    # 애플리케이션 호출 처리
    program = Cond(
        [Txn.application_id() == Int(0), init_contract()],
        [Txn.on_completion() == OnCall.NoOp, handle_noop()],
        [Txn.on_completion() == OnCall.OptIn, handle_opt_in()],
        [Txn.on_completion() == OnCall.CloseOut, Return(Int(1))],
        [Txn.on_completion() == OnCall.UpdateApplication, handle_update()],
        [Txn.on_completion() == OnCall.DeleteApplication, handle_delete()]
    )

    return program

def init_contract():
    """컨트랙트 초기화"""
    return Seq([
        App.globalPut(admin_key, Txn.sender()),
        App.globalPut(total_supply_key, Int(1000000)),  # 총 공급량 100만개
        App.globalPut(issued_supply_key, Int(0)),
        App.globalPut(carbon_rate_key, Int(10)),  # 1kg CO2 절약 = 10토큰
        Return(Int(1))
    ])

def handle_noop():
    """애플리케이션 호출 처리"""
    method = Txn.application_args[0]

    return Cond(
        [method == Bytes("set_role"), set_user_role()],
        [method == Bytes("record_carbon"), record_carbon_savings()],
        [method == Bytes("calculate_reward"), calculate_token_reward()],
        [method == Bytes("validate_transfer"), validate_token_transfer()],
        [Return(Int(0))]
    )

def handle_opt_in():
    """사용자 등록"""
    return Seq([
        App.localPut(Txn.sender(), role_key, Int(0)),  # 미설정
        App.localPut(Txn.sender(), carbon_saved_key, Int(0)),
        App.localPut(Txn.sender(), tokens_earned_key, Int(0)),
        Return(Int(1))
    ])

def set_user_role():
    """사용자 역할 설정 (관리자만 가능)"""
    target_address = Txn.application_args[1]
    new_role = Btoi(Txn.application_args[2])  # 1=위원회, 2=공급자, 3=소비자

    return Seq([
        Assert(Txn.sender() == App.globalGet(admin_key)),  # 관리자 확인
        Assert(And(new_role >= Int(1), new_role <= Int(3))),  # 유효한 역할
        App.localPutEx(target_address, role_key, new_role),
        Return(Int(1))
    ])

def record_carbon_savings():
    """탄소 절약량 기록"""
    carbon_amount = Btoi(Txn.application_args[1])  # kg 단위
    activity_type = Txn.application_args[2]  # "local_food", "transport", "renewable"

    current_saved = App.localGet(Txn.sender(), carbon_saved_key)

    return Seq([
        Assert(carbon_amount > Int(0)),
        Assert(App.localGet(Txn.sender(), role_key) > Int(0)),  # 등록된 사용자
        App.localPut(Txn.sender(), carbon_saved_key, current_saved + carbon_amount),
        Return(Int(1))
    ])

def calculate_token_reward():
    """토큰 보상량 계산"""
    user_carbon_saved = App.localGet(Txn.sender(), carbon_saved_key)
    carbon_rate = App.globalGet(carbon_rate_key)

    reward_amount = user_carbon_saved * carbon_rate
    current_issued = App.globalGet(issued_supply_key)
    total_supply = App.globalGet(total_supply_key)

    return Seq([
        Assert(current_issued + reward_amount <= total_supply),  # 공급량 초과 방지
        App.globalPut(issued_supply_key, current_issued + reward_amount),
        App.localPut(Txn.sender(), tokens_earned_key,
                     App.localGet(Txn.sender(), tokens_earned_key) + reward_amount),
        Return(reward_amount)
    ])

def validate_token_transfer():
    """토큰 전송 유효성 검증"""
    sender_role = Btoi(Txn.application_args[1])
    receiver_role = Btoi(Txn.application_args[2])
    transfer_amount = Btoi(Txn.application_args[3])

    # 배분 규칙: 위원회(1) → 공급자(2) → 소비자(3)
    valid_transfer = Or(
        And(sender_role == Int(1), receiver_role == Int(2)),  # 위원회 → 공급자
        And(sender_role == Int(2), receiver_role == Int(3)),  # 공급자 → 소비자
        sender_role == Int(1)  # 위원회는 직접 발행 가능
    )

    return Seq([
        Assert(valid_transfer),
        Assert(transfer_amount > Int(0)),
        Return(Int(1))
    ])

def handle_update():
    """컨트랙트 업데이트 (관리자만)"""
    return If(
        Txn.sender() == App.globalGet(admin_key),
        Return(Int(1)),
        Return(Int(0))
    )

def handle_delete():
    """컨트랙트 삭제 (관리자만)"""
    return If(
        Txn.sender() == App.globalGet(admin_key),
        Return(Int(1)),
        Return(Int(0))
    )

if __name__ == "__main__":
    # 컨트랙트 컴파일
    contract = reward_policy_contract()

    # TEAL 코드 출력
    print("=== PAM-TALK ESG Reward Policy Contract ===")
    print(compileTeal(contract, Mode.Application, version=8))