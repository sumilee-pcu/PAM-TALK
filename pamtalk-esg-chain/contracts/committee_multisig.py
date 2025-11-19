# -*- coding: utf-8 -*-
"""
Committee Multi-Signature Verification Contract (PyTeal)
Requires multiple committee members to approve critical operations
"""

from pyteal import *


def approval_program():
    """
    Committee Multi-Sig Contract

    Operations:
    - propose: Create new proposal
    - vote: Vote on proposal (committee members only)
    - execute: Execute approved proposal
    """

    # Global state
    admin_address = Bytes("admin")
    required_approvals = Bytes("required_approvals")
    committee_count = Bytes("committee_count")

    # Proposal state (using proposal_id as key prefix)
    proposal_creator = Bytes("prop_creator_")
    proposal_type = Bytes("prop_type_")
    proposal_data = Bytes("prop_data_")
    proposal_votes = Bytes("prop_votes_")
    proposal_executed = Bytes("prop_executed_")
    proposal_expiry = Bytes("prop_expiry_")

    on_creation = Seq([
        App.globalPut(admin_address, Txn.sender()),
        App.globalPut(required_approvals, Int(3)),  # Default: 3 of 5
        App.globalPut(committee_count, Int(0)),
        Return(Int(1))
    ])

    # Committee member opt-in
    on_opt_in = Return(Int(1))

    scratch_proposal_id = ScratchVar(TealType.bytes)
    scratch_votes = ScratchVar(TealType.uint64)

    # Create new proposal
    propose = Seq([
        # Args: [propose, proposal_id, type, data]
        Assert(Txn.application_args.length() == Int(4)),
        scratch_proposal_id.store(Txn.application_args[1]),

        # Save proposal details
        App.globalPut(
            Concat(proposal_creator, scratch_proposal_id.load()),
            Txn.sender()
        ),
        App.globalPut(
            Concat(proposal_type, scratch_proposal_id.load()),
            Txn.application_args[2]
        ),
        App.globalPut(
            Concat(proposal_data, scratch_proposal_id.load()),
            Txn.application_args[3]
        ),
        App.globalPut(
            Concat(proposal_votes, scratch_proposal_id.load()),
            Int(1)  # Creator's vote
        ),
        App.globalPut(
            Concat(proposal_executed, scratch_proposal_id.load()),
            Int(0)
        ),
        App.globalPut(
            Concat(proposal_expiry, scratch_proposal_id.load()),
            Global.latest_timestamp() + Int(604800)  # 7 days
        ),

        Return(Int(1))
    ])

    # Vote on proposal
    vote = Seq([
        # Args: [vote, proposal_id, approve]
        Assert(Txn.application_args.length() == Int(3)),
        scratch_proposal_id.store(Txn.application_args[1]),

        # Check proposal exists and not executed
        Assert(
            App.globalGet(Concat(proposal_executed, scratch_proposal_id.load())) == Int(0)
        ),

        # Check not expired
        Assert(
            Global.latest_timestamp() < App.globalGet(Concat(proposal_expiry, scratch_proposal_id.load()))
        ),

        # If approving, increment vote count
        If(
            Btoi(Txn.application_args[2]) == Int(1),
            Seq([
                scratch_votes.store(
                    App.globalGet(Concat(proposal_votes, scratch_proposal_id.load()))
                ),
                App.globalPut(
                    Concat(proposal_votes, scratch_proposal_id.load()),
                    scratch_votes.load() + Int(1)
                ),
            ])
        ),

        Return(Int(1))
    ])

    # Execute approved proposal
    execute = Seq([
        # Args: [execute, proposal_id]
        Assert(Txn.application_args.length() == Int(2)),
        scratch_proposal_id.store(Txn.application_args[1]),

        # Check proposal has enough votes
        scratch_votes.store(
            App.globalGet(Concat(proposal_votes, scratch_proposal_id.load()))
        ),
        Assert(scratch_votes.load() >= App.globalGet(required_approvals)),

        # Check not already executed
        Assert(
            App.globalGet(Concat(proposal_executed, scratch_proposal_id.load())) == Int(0)
        ),

        # Mark as executed
        App.globalPut(
            Concat(proposal_executed, scratch_proposal_id.load()),
            Int(1)
        ),

        # Execute based on proposal type
        # (In practice, this would trigger the actual operation)

        Return(Int(1))
    ])

    # Set required approvals (admin only)
    set_required_approvals = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(required_approvals, Btoi(Txn.application_args[1])),
        Return(Int(1))
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
        [Txn.application_args[0] == Bytes("propose"), propose],
        [Txn.application_args[0] == Bytes("vote"), vote],
        [Txn.application_args[0] == Bytes("execute"), execute],
        [Txn.application_args[0] == Bytes("set_required_approvals"), set_required_approvals],
    )

    return program


def clear_state_program():
    return Return(Int(1))


if __name__ == "__main__":
    with open("committee_multisig_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    with open("committee_multisig_clear.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    print("✅ Committee Multi-Sig Contract compiled!")
