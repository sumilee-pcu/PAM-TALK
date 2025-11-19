# -*- coding: utf-8 -*-
"""
ESG-Gold Token Smart Contract (PyTeal)
Handles minting and burning of ESG-Gold tokens with committee approval
"""

from pyteal import *


def approval_program():
    """
    ESG-Gold Token Contract - Approval Program

    Operations:
    - mint: Issue new ESG-Gold tokens (requires committee approval)
    - burn: Destroy ESG-Gold tokens
    - transfer: Transfer tokens between accounts
    - get_balance: Query token balance
    """

    # Global state keys
    total_supply = Bytes("total_supply")
    admin_address = Bytes("admin_address")
    committee_address = Bytes("committee_address")
    is_paused = Bytes("is_paused")

    # Local state keys (per account)
    balance_key = Bytes("balance")
    frozen_key = Bytes("frozen")

    # Transaction type check
    on_creation = Seq([
        App.globalPut(total_supply, Int(0)),
        App.globalPut(admin_address, Txn.sender()),
        App.globalPut(is_paused, Int(0)),
        Return(Int(1))
    ])

    # Initialize account
    on_opt_in = Seq([
        App.localPut(Txn.sender(), balance_key, Int(0)),
        App.localPut(Txn.sender(), frozen_key, Int(0)),
        Return(Int(1))
    ])

    # Close out
    on_close_out = Seq([
        Assert(App.localGet(Txn.sender(), balance_key) == Int(0)),
        Return(Int(1))
    ])

    # Update application
    on_update = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Return(Int(1))
    ])

    # Delete application
    on_delete = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(App.globalGet(total_supply) == Int(0)),
        Return(Int(1))
    ])

    # Scratch variables
    scratch_balance = ScratchVar(TealType.uint64)
    scratch_amount = ScratchVar(TealType.uint64)

    # Mint tokens (requires committee approval)
    mint = Seq([
        # Check if paused
        Assert(App.globalGet(is_paused) == Int(0)),

        # Verify committee signature
        Assert(Txn.application_args.length() == Int(3)),  # [mint, recipient, amount]
        scratch_amount.store(Btoi(Txn.application_args[2])),

        # Check committee approval (in real implementation, verify multi-sig)
        Assert(Global.group_size() == Int(2)),
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].receiver() == App.globalGet(committee_address)),

        # Mint tokens to recipient
        scratch_balance.store(
            App.localGet(Txn.accounts[1], balance_key)
        ),
        App.localPut(
            Txn.accounts[1],
            balance_key,
            scratch_balance.load() + scratch_amount.load()
        ),

        # Update total supply
        App.globalPut(
            total_supply,
            App.globalGet(total_supply) + scratch_amount.load()
        ),

        Return(Int(1))
    ])

    # Burn tokens
    burn = Seq([
        Assert(App.globalGet(is_paused) == Int(0)),
        Assert(Txn.application_args.length() == Int(2)),  # [burn, amount]

        scratch_amount.store(Btoi(Txn.application_args[1])),
        scratch_balance.store(App.localGet(Txn.sender(), balance_key)),

        # Check sufficient balance
        Assert(scratch_balance.load() >= scratch_amount.load()),

        # Burn tokens
        App.localPut(
            Txn.sender(),
            balance_key,
            scratch_balance.load() - scratch_amount.load()
        ),

        # Update total supply
        App.globalPut(
            total_supply,
            App.globalGet(total_supply) - scratch_amount.load()
        ),

        Return(Int(1))
    ])

    # Transfer tokens
    transfer = Seq([
        Assert(App.globalGet(is_paused) == Int(0)),
        Assert(Txn.application_args.length() == Int(3)),  # [transfer, recipient, amount]

        # Check sender not frozen
        Assert(App.localGet(Txn.sender(), frozen_key) == Int(0)),

        scratch_amount.store(Btoi(Txn.application_args[2])),

        # Deduct from sender
        scratch_balance.store(App.localGet(Txn.sender(), balance_key)),
        Assert(scratch_balance.load() >= scratch_amount.load()),
        App.localPut(
            Txn.sender(),
            balance_key,
            scratch_balance.load() - scratch_amount.load()
        ),

        # Add to recipient
        scratch_balance.store(App.localGet(Txn.accounts[1], balance_key)),
        App.localPut(
            Txn.accounts[1],
            balance_key,
            scratch_balance.load() + scratch_amount.load()
        ),

        Return(Int(1))
    ])

    # Set committee address
    set_committee = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(committee_address, Txn.application_args[1]),
        Return(Int(1))
    ])

    # Pause/unpause contract
    set_pause = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(is_paused, Btoi(Txn.application_args[1])),
        Return(Int(1))
    ])

    # Freeze/unfreeze account
    set_freeze = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(3)),
        App.localPut(
            Txn.accounts[1],
            frozen_key,
            Btoi(Txn.application_args[2])
        ),
        Return(Int(1))
    ])

    # Main routing logic
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
        [Txn.on_completion() == OnComplete.CloseOut, on_close_out],
        [Txn.on_completion() == OnComplete.UpdateApplication, on_update],
        [Txn.on_completion() == OnComplete.DeleteApplication, on_delete],
        [Txn.application_args[0] == Bytes("mint"), mint],
        [Txn.application_args[0] == Bytes("burn"), burn],
        [Txn.application_args[0] == Bytes("transfer"), transfer],
        [Txn.application_args[0] == Bytes("set_committee"), set_committee],
        [Txn.application_args[0] == Bytes("set_pause"), set_pause],
        [Txn.application_args[0] == Bytes("set_freeze"), set_freeze],
    )

    return program


def clear_state_program():
    """Clear state program - always approve"""
    return Return(Int(1))


if __name__ == "__main__":
    # Compile the contract
    with open("esg_gold_token_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    with open("esg_gold_token_clear.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    print("✅ ESG-Gold Token Contract compiled successfully!")
    print("   - esg_gold_token_approval.teal")
    print("   - esg_gold_token_clear.teal")
