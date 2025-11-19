# -*- coding: utf-8 -*-
"""
Auto Reward Distribution Smart Contract (PyTeal)
Automatically distributes rewards based on carbon reduction activities
"""

from pyteal import *


def approval_program():
    """
    Auto Reward Contract - Approval Program

    Operations:
    - register_activity: Register carbon reduction activity
    - claim_reward: Claim accumulated rewards
    - set_reward_rate: Set reward rate (admin only)
    """

    # Global state
    admin_address = Bytes("admin")
    token_app_id = Bytes("token_app_id")
    reward_rate = Bytes("reward_rate")  # ESG-Gold per kg CO2
    total_distributed = Bytes("total_distributed")

    # Local state (per user)
    pending_rewards = Bytes("pending_rewards")
    claimed_rewards = Bytes("claimed_rewards")
    total_carbon_reduction = Bytes("total_carbon")

    on_creation = Seq([
        App.globalPut(admin_address, Txn.sender()),
        App.globalPut(reward_rate, Int(1000)),  # Default: 1000 ESG-Gold per kg
        App.globalPut(total_distributed, Int(0)),
        Return(Int(1))
    ])

    on_opt_in = Seq([
        App.localPut(Txn.sender(), pending_rewards, Int(0)),
        App.localPut(Txn.sender(), claimed_rewards, Int(0)),
        App.localPut(Txn.sender(), total_carbon_reduction, Int(0)),
        Return(Int(1))
    ])

    scratch_amount = ScratchVar(TealType.uint64)
    scratch_reward = ScratchVar(TealType.uint64)

    # Register carbon reduction activity
    register_activity = Seq([
        # Args: [register_activity, carbon_kg, activity_hash]
        Assert(Txn.application_args.length() == Int(3)),

        scratch_amount.store(Btoi(Txn.application_args[1])),

        # Calculate reward
        scratch_reward.store(
            scratch_amount.load() * App.globalGet(reward_rate)
        ),

        # Update user stats
        App.localPut(
            Txn.sender(),
            pending_rewards,
            App.localGet(Txn.sender(), pending_rewards) + scratch_reward.load()
        ),
        App.localPut(
            Txn.sender(),
            total_carbon_reduction,
            App.localGet(Txn.sender(), total_carbon_reduction) + scratch_amount.load()
        ),

        Return(Int(1))
    ])

    # Claim accumulated rewards
    claim_reward = Seq([
        scratch_reward.store(App.localGet(Txn.sender(), pending_rewards)),

        # Check if there are pending rewards
        Assert(scratch_reward.load() > Int(0)),

        # Transfer rewards via inner transaction
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: App.globalGet(token_app_id),
            TxnField.application_args: [Bytes("mint"), Txn.sender(), Itob(scratch_reward.load())],
            TxnField.accounts: [Txn.sender()],
        }),
        InnerTxnBuilder.Submit(),

        # Update balances
        App.localPut(Txn.sender(), pending_rewards, Int(0)),
        App.localPut(
            Txn.sender(),
            claimed_rewards,
            App.localGet(Txn.sender(), claimed_rewards) + scratch_reward.load()
        ),
        App.globalPut(
            total_distributed,
            App.globalGet(total_distributed) + scratch_reward.load()
        ),

        Return(Int(1))
    ])

    # Set reward rate (admin only)
    set_reward_rate = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(reward_rate, Btoi(Txn.application_args[1])),
        Return(Int(1))
    ])

    # Set token app ID (admin only)
    set_token_app = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(token_app_id, Btoi(Txn.application_args[1])),
        Return(Int(1))
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
        [Txn.application_args[0] == Bytes("register_activity"), register_activity],
        [Txn.application_args[0] == Bytes("claim_reward"), claim_reward],
        [Txn.application_args[0] == Bytes("set_reward_rate"), set_reward_rate],
        [Txn.application_args[0] == Bytes("set_token_app"), set_token_app],
    )

    return program


def clear_state_program():
    return Return(Int(1))


if __name__ == "__main__":
    with open("auto_reward_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    with open("auto_reward_clear.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    print("✅ Auto Reward Contract compiled!")
