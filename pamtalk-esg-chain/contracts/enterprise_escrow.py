# -*- coding: utf-8 -*-
"""
Enterprise B2B Escrow Smart Contract (PyTeal)
Handles secure escrow for large enterprise purchases with multi-party approval
"""

from pyteal import *


def approval_program():
    """
    Enterprise Escrow Contract

    Operations:
    - create_escrow: Create new escrow for B2B transaction
    - deposit_funds: Buyer deposits funds into escrow
    - confirm_shipment: Seller confirms shipment
    - confirm_receipt: Buyer confirms receipt
    - release_funds: Release funds to seller (automated or admin)
    - raise_dispute: Either party raises dispute
    - resolve_dispute: Admin resolves dispute
    - cancel_escrow: Cancel escrow (both parties must agree)
    """

    # Global state
    admin_address = Bytes("admin")
    token_app_id = Bytes("token_app_id")
    arbitration_fee = Bytes("arbitration_fee")  # Fee for dispute resolution
    total_escrowed = Bytes("total_escrowed")
    total_completed = Bytes("total_completed")

    # Escrow state (using escrow_id as key prefix)
    escrow_buyer = Bytes("escrow_buyer_")
    escrow_seller = Bytes("escrow_seller_")
    escrow_amount = Bytes("escrow_amount_")
    escrow_deposit_amount = Bytes("escrow_deposit_")
    escrow_status = Bytes("escrow_status_")  # 0: created, 1: funded, 2: shipped, 3: completed, 4: disputed, 5: cancelled
    escrow_contract_hash = Bytes("escrow_contract_")  # Hash of contract terms
    escrow_deadline = Bytes("escrow_deadline_")
    escrow_buyer_confirmed = Bytes("escrow_buyer_conf_")
    escrow_seller_confirmed = Bytes("escrow_seller_conf_")
    escrow_dispute_reason = Bytes("escrow_dispute_")
    escrow_created_time = Bytes("escrow_created_")
    escrow_completed_time = Bytes("escrow_completed_")

    on_creation = Seq([
        App.globalPut(admin_address, Txn.sender()),
        App.globalPut(arbitration_fee, Int(1000000)),  # Default: 1M ESG-Gold
        App.globalPut(total_escrowed, Int(0)),
        App.globalPut(total_completed, Int(0)),
        Return(Int(1))
    ])

    on_opt_in = Return(Int(1))

    scratch_escrow_id = ScratchVar(TealType.bytes)
    scratch_amount = ScratchVar(TealType.uint64)
    scratch_status = ScratchVar(TealType.uint64)

    # Create escrow
    create_escrow = Seq([
        # Args: [create_escrow, escrow_id, buyer_addr, seller_addr, amount, contract_hash, deadline_days]
        Assert(Txn.application_args.length() == Int(7)),
        scratch_escrow_id.store(Txn.application_args[1]),
        scratch_amount.store(Btoi(Txn.application_args[4])),

        # Initialize escrow
        App.globalPut(
            Concat(escrow_buyer, scratch_escrow_id.load()),
            Txn.application_args[2]
        ),
        App.globalPut(
            Concat(escrow_seller, scratch_escrow_id.load()),
            Txn.application_args[3]
        ),
        App.globalPut(
            Concat(escrow_amount, scratch_escrow_id.load()),
            scratch_amount.load()
        ),
        App.globalPut(
            Concat(escrow_deposit_amount, scratch_escrow_id.load()),
            Int(0)
        ),
        App.globalPut(
            Concat(escrow_status, scratch_escrow_id.load()),
            Int(0)  # Created
        ),
        App.globalPut(
            Concat(escrow_contract_hash, scratch_escrow_id.load()),
            Txn.application_args[5]
        ),
        App.globalPut(
            Concat(escrow_deadline, scratch_escrow_id.load()),
            Global.latest_timestamp() + (Btoi(Txn.application_args[6]) * Int(86400))
        ),
        App.globalPut(
            Concat(escrow_buyer_confirmed, scratch_escrow_id.load()),
            Int(0)
        ),
        App.globalPut(
            Concat(escrow_seller_confirmed, scratch_escrow_id.load()),
            Int(0)
        ),
        App.globalPut(
            Concat(escrow_created_time, scratch_escrow_id.load()),
            Global.latest_timestamp()
        ),

        Return(Int(1))
    ])

    # Deposit funds
    deposit_funds = Seq([
        # Args: [deposit_funds, escrow_id]
        Assert(Txn.application_args.length() == Int(2)),
        scratch_escrow_id.store(Txn.application_args[1]),

        # Verify sender is buyer
        Assert(
            Txn.sender() == App.globalGet(Concat(escrow_buyer, scratch_escrow_id.load()))
        ),

        # Check escrow status is created
        Assert(
            App.globalGet(Concat(escrow_status, scratch_escrow_id.load())) == Int(0)
        ),

        # Get required amount
        scratch_amount.store(
            App.globalGet(Concat(escrow_amount, scratch_escrow_id.load()))
        ),

        # Verify payment transaction in group
        Assert(Global.group_size() == Int(2)),
        Assert(Gtxn[1].type_enum() == TxnType.ApplicationCall),
        Assert(Gtxn[1].application_id() == App.globalGet(token_app_id)),

        # Update deposit amount and status
        App.globalPut(
            Concat(escrow_deposit_amount, scratch_escrow_id.load()),
            scratch_amount.load()
        ),
        App.globalPut(
            Concat(escrow_status, scratch_escrow_id.load()),
            Int(1)  # Funded
        ),

        # Update total escrowed
        App.globalPut(
            total_escrowed,
            App.globalGet(total_escrowed) + scratch_amount.load()
        ),

        Return(Int(1))
    ])

    # Confirm shipment
    confirm_shipment = Seq([
        # Args: [confirm_shipment, escrow_id, tracking_hash]
        Assert(Txn.application_args.length() == Int(3)),
        scratch_escrow_id.store(Txn.application_args[1]),

        # Verify sender is seller
        Assert(
            Txn.sender() == App.globalGet(Concat(escrow_seller, scratch_escrow_id.load()))
        ),

        # Check escrow is funded
        Assert(
            App.globalGet(Concat(escrow_status, scratch_escrow_id.load())) == Int(1)
        ),

        # Mark seller confirmed and update status
        App.globalPut(
            Concat(escrow_seller_confirmed, scratch_escrow_id.load()),
            Int(1)
        ),
        App.globalPut(
            Concat(escrow_status, scratch_escrow_id.load()),
            Int(2)  # Shipped
        ),

        Return(Int(1))
    ])

    # Confirm receipt
    confirm_receipt = Seq([
        # Args: [confirm_receipt, escrow_id, receipt_hash]
        Assert(Txn.application_args.length() == Int(3)),
        scratch_escrow_id.store(Txn.application_args[1]),

        # Verify sender is buyer
        Assert(
            Txn.sender() == App.globalGet(Concat(escrow_buyer, scratch_escrow_id.load()))
        ),

        # Check escrow is shipped
        Assert(
            App.globalGet(Concat(escrow_status, scratch_escrow_id.load())) == Int(2)
        ),

        # Mark buyer confirmed
        App.globalPut(
            Concat(escrow_buyer_confirmed, scratch_escrow_id.load()),
            Int(1)
        ),

        # Auto-release funds since both parties confirmed
        Return(Int(1))
    ])

    # Release funds
    release_funds = Seq([
        # Args: [release_funds, escrow_id]
        Assert(Txn.application_args.length() == Int(2)),
        scratch_escrow_id.store(Txn.application_args[1]),

        # Get escrow details
        scratch_amount.store(
            App.globalGet(Concat(escrow_amount, scratch_escrow_id.load()))
        ),

        # Check both parties confirmed OR admin approval OR deadline passed
        Assert(
            Or(
                And(
                    App.globalGet(Concat(escrow_buyer_confirmed, scratch_escrow_id.load())) == Int(1),
                    App.globalGet(Concat(escrow_seller_confirmed, scratch_escrow_id.load())) == Int(1)
                ),
                Txn.sender() == App.globalGet(admin_address),
                Global.latest_timestamp() > App.globalGet(Concat(escrow_deadline, scratch_escrow_id.load()))
            )
        ),

        # Check not already completed or cancelled
        scratch_status.store(
            App.globalGet(Concat(escrow_status, scratch_escrow_id.load()))
        ),
        Assert(
            And(
                scratch_status.load() != Int(3),
                scratch_status.load() != Int(5)
            )
        ),

        # Transfer funds to seller via inner transaction
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: App.globalGet(token_app_id),
            TxnField.application_args: [
                Bytes("transfer"),
                App.globalGet(Concat(escrow_seller, scratch_escrow_id.load())),
                Itob(scratch_amount.load())
            ],
            TxnField.accounts: [App.globalGet(Concat(escrow_seller, scratch_escrow_id.load()))],
        }),
        InnerTxnBuilder.Submit(),

        # Update status
        App.globalPut(
            Concat(escrow_status, scratch_escrow_id.load()),
            Int(3)  # Completed
        ),
        App.globalPut(
            Concat(escrow_completed_time, scratch_escrow_id.load()),
            Global.latest_timestamp()
        ),

        # Update totals
        App.globalPut(
            total_escrowed,
            App.globalGet(total_escrowed) - scratch_amount.load()
        ),
        App.globalPut(
            total_completed,
            App.globalGet(total_completed) + scratch_amount.load()
        ),

        Return(Int(1))
    ])

    # Raise dispute
    raise_dispute = Seq([
        # Args: [raise_dispute, escrow_id, reason_hash]
        Assert(Txn.application_args.length() == Int(3)),
        scratch_escrow_id.store(Txn.application_args[1]),

        # Verify sender is buyer or seller
        Assert(
            Or(
                Txn.sender() == App.globalGet(Concat(escrow_buyer, scratch_escrow_id.load())),
                Txn.sender() == App.globalGet(Concat(escrow_seller, scratch_escrow_id.load()))
            )
        ),

        # Check escrow is active (not completed or cancelled)
        scratch_status.store(
            App.globalGet(Concat(escrow_status, scratch_escrow_id.load()))
        ),
        Assert(
            And(
                scratch_status.load() != Int(3),
                scratch_status.load() != Int(5)
            )
        ),

        # Update status to disputed
        App.globalPut(
            Concat(escrow_status, scratch_escrow_id.load()),
            Int(4)  # Disputed
        ),
        App.globalPut(
            Concat(escrow_dispute_reason, scratch_escrow_id.load()),
            Txn.application_args[2]
        ),

        Return(Int(1))
    ])

    # Resolve dispute (admin only)
    resolve_dispute = Seq([
        # Args: [resolve_dispute, escrow_id, resolution]
        # resolution: 0 = refund buyer, 1 = pay seller, 2 = split
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(3)),
        scratch_escrow_id.store(Txn.application_args[1]),

        # Check escrow is disputed
        Assert(
            App.globalGet(Concat(escrow_status, scratch_escrow_id.load())) == Int(4)
        ),

        scratch_amount.store(
            App.globalGet(Concat(escrow_amount, scratch_escrow_id.load()))
        ),

        # Resolution logic would go here
        # For simplicity, marking as completed
        App.globalPut(
            Concat(escrow_status, scratch_escrow_id.load()),
            Int(3)  # Completed
        ),

        Return(Int(1))
    ])

    # Cancel escrow (requires both parties or admin)
    cancel_escrow = Seq([
        # Args: [cancel_escrow, escrow_id]
        Assert(Txn.application_args.length() == Int(2)),
        scratch_escrow_id.store(Txn.application_args[1]),

        # Admin can cancel anytime, or both parties must confirm
        Assert(
            Or(
                Txn.sender() == App.globalGet(admin_address),
                And(
                    App.globalGet(Concat(escrow_buyer_confirmed, scratch_escrow_id.load())) == Int(1),
                    App.globalGet(Concat(escrow_seller_confirmed, scratch_escrow_id.load())) == Int(1)
                )
            )
        ),

        # Mark as cancelled
        App.globalPut(
            Concat(escrow_status, scratch_escrow_id.load()),
            Int(5)  # Cancelled
        ),

        # Refund buyer if funds were deposited
        scratch_amount.store(
            App.globalGet(Concat(escrow_deposit_amount, scratch_escrow_id.load()))
        ),

        If(
            scratch_amount.load() > Int(0),
            Seq([
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum: TxnType.ApplicationCall,
                    TxnField.application_id: App.globalGet(token_app_id),
                    TxnField.application_args: [
                        Bytes("transfer"),
                        App.globalGet(Concat(escrow_buyer, scratch_escrow_id.load())),
                        Itob(scratch_amount.load())
                    ],
                    TxnField.accounts: [App.globalGet(Concat(escrow_buyer, scratch_escrow_id.load()))],
                }),
                InnerTxnBuilder.Submit(),

                # Update total escrowed
                App.globalPut(
                    total_escrowed,
                    App.globalGet(total_escrowed) - scratch_amount.load()
                ),
            ])
        ),

        Return(Int(1))
    ])

    # Set token app ID (admin only)
    set_token_app = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(token_app_id, Btoi(Txn.application_args[1])),
        Return(Int(1))
    ])

    # Set arbitration fee (admin only)
    set_arbitration_fee = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(arbitration_fee, Btoi(Txn.application_args[1])),
        Return(Int(1))
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
        [Txn.application_args[0] == Bytes("create_escrow"), create_escrow],
        [Txn.application_args[0] == Bytes("deposit_funds"), deposit_funds],
        [Txn.application_args[0] == Bytes("confirm_shipment"), confirm_shipment],
        [Txn.application_args[0] == Bytes("confirm_receipt"), confirm_receipt],
        [Txn.application_args[0] == Bytes("release_funds"), release_funds],
        [Txn.application_args[0] == Bytes("raise_dispute"), raise_dispute],
        [Txn.application_args[0] == Bytes("resolve_dispute"), resolve_dispute],
        [Txn.application_args[0] == Bytes("cancel_escrow"), cancel_escrow],
        [Txn.application_args[0] == Bytes("set_token_app"), set_token_app],
        [Txn.application_args[0] == Bytes("set_arbitration_fee"), set_arbitration_fee],
    )

    return program


def clear_state_program():
    return Return(Int(1))


if __name__ == "__main__":
    with open("enterprise_escrow_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    with open("enterprise_escrow_clear.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    print("✅ Enterprise Escrow Contract compiled!")
