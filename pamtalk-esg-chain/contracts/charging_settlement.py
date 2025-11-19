# -*- coding: utf-8 -*-
"""
Charging Station Settlement Smart Contract (PyTeal)
Handles automated settlement and payment distribution for charging stations
"""

from pyteal import *


def approval_program():
    """
    Charging Station Settlement Contract

    Operations:
    - register_station: Register new charging station
    - record_transaction: Record charging transaction
    - request_settlement: Request settlement for a period
    - approve_settlement: Approve settlement (admin only)
    - withdraw: Station operator withdraws settled funds
    """

    # Global state
    admin_address = Bytes("admin")
    token_app_id = Bytes("token_app_id")
    platform_fee_rate = Bytes("platform_fee")  # Basis points (e.g., 500 = 5%)
    total_volume = Bytes("total_volume")
    total_fees_collected = Bytes("total_fees")

    # Station state (using station_id as key prefix)
    station_operator = Bytes("station_op_")
    station_status = Bytes("station_status_")  # 0: inactive, 1: active
    station_volume = Bytes("station_vol_")
    station_fees_paid = Bytes("station_fees_")
    station_pending = Bytes("station_pending_")
    station_settled = Bytes("station_settled_")

    # Settlement state (using settlement_id as key prefix)
    settlement_station = Bytes("settle_station_")
    settlement_amount = Bytes("settle_amount_")
    settlement_fee = Bytes("settle_fee_")
    settlement_period = Bytes("settle_period_")
    settlement_status = Bytes("settle_status_")  # 0: pending, 1: approved, 2: completed
    settlement_timestamp = Bytes("settle_time_")

    on_creation = Seq([
        App.globalPut(admin_address, Txn.sender()),
        App.globalPut(platform_fee_rate, Int(500)),  # Default: 5%
        App.globalPut(total_volume, Int(0)),
        App.globalPut(total_fees_collected, Int(0)),
        Return(Int(1))
    ])

    on_opt_in = Return(Int(1))

    scratch_station_id = ScratchVar(TealType.bytes)
    scratch_amount = ScratchVar(TealType.uint64)
    scratch_fee = ScratchVar(TealType.uint64)
    scratch_net = ScratchVar(TealType.uint64)

    # Register charging station
    register_station = Seq([
        # Args: [register_station, station_id, operator_address]
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(3)),
        scratch_station_id.store(Txn.application_args[1]),

        # Register station
        App.globalPut(
            Concat(station_operator, scratch_station_id.load()),
            Txn.application_args[2]
        ),
        App.globalPut(
            Concat(station_status, scratch_station_id.load()),
            Int(1)  # Active
        ),
        App.globalPut(
            Concat(station_volume, scratch_station_id.load()),
            Int(0)
        ),
        App.globalPut(
            Concat(station_fees_paid, scratch_station_id.load()),
            Int(0)
        ),
        App.globalPut(
            Concat(station_pending, scratch_station_id.load()),
            Int(0)
        ),
        App.globalPut(
            Concat(station_settled, scratch_station_id.load()),
            Int(0)
        ),

        Return(Int(1))
    ])

    # Record charging transaction
    record_transaction = Seq([
        # Args: [record_transaction, station_id, amount, tx_hash]
        Assert(Txn.application_args.length() == Int(4)),
        scratch_station_id.store(Txn.application_args[1]),
        scratch_amount.store(Btoi(Txn.application_args[2])),

        # Check station is active
        Assert(
            App.globalGet(Concat(station_status, scratch_station_id.load())) == Int(1)
        ),

        # Calculate platform fee
        scratch_fee.store(
            (scratch_amount.load() * App.globalGet(platform_fee_rate)) / Int(10000)
        ),
        scratch_net.store(scratch_amount.load() - scratch_fee.load()),

        # Update station stats
        App.globalPut(
            Concat(station_volume, scratch_station_id.load()),
            App.globalGet(Concat(station_volume, scratch_station_id.load())) + scratch_amount.load()
        ),
        App.globalPut(
            Concat(station_fees_paid, scratch_station_id.load()),
            App.globalGet(Concat(station_fees_paid, scratch_station_id.load())) + scratch_fee.load()
        ),
        App.globalPut(
            Concat(station_pending, scratch_station_id.load()),
            App.globalGet(Concat(station_pending, scratch_station_id.load())) + scratch_net.load()
        ),

        # Update global stats
        App.globalPut(
            total_volume,
            App.globalGet(total_volume) + scratch_amount.load()
        ),
        App.globalPut(
            total_fees_collected,
            App.globalGet(total_fees_collected) + scratch_fee.load()
        ),

        Return(Int(1))
    ])

    scratch_settlement_id = ScratchVar(TealType.bytes)

    # Request settlement
    request_settlement = Seq([
        # Args: [request_settlement, station_id, settlement_id, period]
        Assert(Txn.application_args.length() == Int(4)),
        scratch_station_id.store(Txn.application_args[1]),
        scratch_settlement_id.store(Txn.application_args[2]),

        # Verify sender is station operator
        Assert(
            Txn.sender() == App.globalGet(Concat(station_operator, scratch_station_id.load()))
        ),

        # Get pending amount
        scratch_amount.store(
            App.globalGet(Concat(station_pending, scratch_station_id.load()))
        ),
        Assert(scratch_amount.load() > Int(0)),

        # Calculate fee already paid
        scratch_fee.store(
            (scratch_amount.load() * App.globalGet(platform_fee_rate)) / (Int(10000) - App.globalGet(platform_fee_rate))
        ),

        # Create settlement record
        App.globalPut(
            Concat(settlement_station, scratch_settlement_id.load()),
            scratch_station_id.load()
        ),
        App.globalPut(
            Concat(settlement_amount, scratch_settlement_id.load()),
            scratch_amount.load()
        ),
        App.globalPut(
            Concat(settlement_fee, scratch_settlement_id.load()),
            scratch_fee.load()
        ),
        App.globalPut(
            Concat(settlement_period, scratch_settlement_id.load()),
            Txn.application_args[3]
        ),
        App.globalPut(
            Concat(settlement_status, scratch_settlement_id.load()),
            Int(0)  # Pending
        ),
        App.globalPut(
            Concat(settlement_timestamp, scratch_settlement_id.load()),
            Global.latest_timestamp()
        ),

        Return(Int(1))
    ])

    # Approve settlement (admin only)
    approve_settlement = Seq([
        # Args: [approve_settlement, settlement_id]
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        scratch_settlement_id.store(Txn.application_args[1]),

        # Check settlement exists and is pending
        Assert(
            App.globalGet(Concat(settlement_status, scratch_settlement_id.load())) == Int(0)
        ),

        # Mark as approved
        App.globalPut(
            Concat(settlement_status, scratch_settlement_id.load()),
            Int(1)  # Approved
        ),

        Return(Int(1))
    ])

    # Withdraw settled funds
    withdraw = Seq([
        # Args: [withdraw, settlement_id]
        Assert(Txn.application_args.length() == Int(2)),
        scratch_settlement_id.store(Txn.application_args[1]),

        # Get settlement details
        scratch_station_id.store(
            App.globalGet(Concat(settlement_station, scratch_settlement_id.load()))
        ),
        scratch_amount.store(
            App.globalGet(Concat(settlement_amount, scratch_settlement_id.load()))
        ),

        # Verify sender is station operator
        Assert(
            Txn.sender() == App.globalGet(Concat(station_operator, scratch_station_id.load()))
        ),

        # Check settlement is approved
        Assert(
            App.globalGet(Concat(settlement_status, scratch_settlement_id.load())) == Int(1)
        ),

        # Transfer funds via inner transaction
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.ApplicationCall,
            TxnField.application_id: App.globalGet(token_app_id),
            TxnField.application_args: [Bytes("transfer"), Txn.sender(), Itob(scratch_amount.load())],
            TxnField.accounts: [Txn.sender()],
        }),
        InnerTxnBuilder.Submit(),

        # Update station balances
        App.globalPut(
            Concat(station_pending, scratch_station_id.load()),
            App.globalGet(Concat(station_pending, scratch_station_id.load())) - scratch_amount.load()
        ),
        App.globalPut(
            Concat(station_settled, scratch_station_id.load()),
            App.globalGet(Concat(station_settled, scratch_station_id.load())) + scratch_amount.load()
        ),

        # Mark settlement as completed
        App.globalPut(
            Concat(settlement_status, scratch_settlement_id.load()),
            Int(2)  # Completed
        ),

        Return(Int(1))
    ])

    # Set platform fee rate (admin only)
    set_fee_rate = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(platform_fee_rate, Btoi(Txn.application_args[1])),
        Return(Int(1))
    ])

    # Set token app ID (admin only)
    set_token_app = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        App.globalPut(token_app_id, Btoi(Txn.application_args[1])),
        Return(Int(1))
    ])

    # Deactivate station (admin only)
    deactivate_station = Seq([
        Assert(Txn.sender() == App.globalGet(admin_address)),
        Assert(Txn.application_args.length() == Int(2)),
        scratch_station_id.store(Txn.application_args[1]),
        App.globalPut(
            Concat(station_status, scratch_station_id.load()),
            Int(0)
        ),
        Return(Int(1))
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
        [Txn.application_args[0] == Bytes("register_station"), register_station],
        [Txn.application_args[0] == Bytes("record_transaction"), record_transaction],
        [Txn.application_args[0] == Bytes("request_settlement"), request_settlement],
        [Txn.application_args[0] == Bytes("approve_settlement"), approve_settlement],
        [Txn.application_args[0] == Bytes("withdraw"), withdraw],
        [Txn.application_args[0] == Bytes("set_fee_rate"), set_fee_rate],
        [Txn.application_args[0] == Bytes("set_token_app"), set_token_app],
        [Txn.application_args[0] == Bytes("deactivate_station"), deactivate_station],
    )

    return program


def clear_state_program():
    return Return(Int(1))


if __name__ == "__main__":
    with open("charging_settlement_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    with open("charging_settlement_clear.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=8)
        f.write(compiled)

    print("✅ Charging Settlement Contract compiled!")
