# -*- coding: utf-8 -*-
# app/service/token_service.py
import time

import psycopg2
from algosdk import account
from algosdk.transaction import AssetTransferTxn, PaymentTxn, ApplicationCallTxn
from algosdk.v2client import algod

from app.config import HCF_MNEMONIC, ASA_ID, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from app.utils.algorand_utils import get_algod_client
from app.utils.wallet_utils import get_wallet_keys, get_wallet_keys_from_address


def opt_in_asset(algod_client: algod.AlgodClient, receiver_address: str, asset_id: int, table_name: str):
    MIN_BALANCE_FOR_OPTIN = 210_000  # Opt-In + 수수료 + 여유

    print(f"\n[Opt-In 상태 확인] 수신자가 아직 Opt-In 하지 않음. 자동 Opt-In 수행.")
    print(f"[지갑 키 조회] 주소: {receiver_address}")

    # 1. 수신자 지갑 키 가져오기
    rec_address, rec_private_key = get_wallet_keys_from_address(receiver_address, table_name)
    print(f"[지갑 키 반환] 주소: {rec_address}")

    # 2. 협회 지갑 키 (충전용)
    sender_address, sender_private_key = get_wallet_keys(HCF_MNEMONIC)

    # 3. 수신자 잔액 확인
    rec_info = algod_client.account_info(receiver_address)
    rec_balance = rec_info.get("amount", 0)
    print(f"[수신자 현재 잔액] {rec_balance} microAlgos")

    if rec_balance < MIN_BALANCE_FOR_OPTIN:
        print("[잔액 부족] 수신자에게 ALGO 자동 충전 중...")

        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = 1000

        top_up_amount = MIN_BALANCE_FOR_OPTIN - rec_balance + 10_000  # 0.01 Algo 여유
        pay_txn = PaymentTxn(
            sender=sender_address,
            sp=params,
            receiver=receiver_address,
            amt=top_up_amount
        )
        signed_pay_txn = pay_txn.sign(sender_private_key)
        pay_tx_id = algod_client.send_transaction(signed_pay_txn)
        print(f"[충전 전송] TXID: {pay_tx_id}")
        wait_for_confirmation(algod_client, pay_tx_id)
        print("[충전 완료]")

        # 충전 후 잔액 재확인 (최대 5초 대기)
        for i in range(5):
            rec_info = algod_client.account_info(receiver_address)
            rec_balance = rec_info.get("amount", 0)
            print(f"[충전 후 잔액 확인] {rec_balance}")
            if rec_balance >= MIN_BALANCE_FOR_OPTIN:
                break
            print(f"[잔액 대기 중... {i+1}s]")
            time.sleep(1)

        if rec_balance < MIN_BALANCE_FOR_OPTIN:
            raise Exception(f"[충전 실패 또는 지연] 현재 잔액 {rec_balance} < 필요 {MIN_BALANCE_FOR_OPTIN}")
    else:
        print("[충전 생략] 충분한 잔액이 있습니다.")

    # 4. Opt-In 여부 확인 (이미 되어 있으면 생략)
    rec_info = algod_client.account_info(receiver_address)
    already_opted_in = any(asset['asset-id'] == asset_id for asset in rec_info.get('assets', []))

    if already_opted_in:
        print("[이미 Opt-In 되어 있음] 트랜잭션 생략")
        return "already_opted_in"

    # 5. Opt-In 트랜잭션 전송
    print("[📤 Opt-In 트랜잭션 전송 중...]")
    params = algod_client.suggested_params()
    params.flat_fee = True
    params.fee = 1000

    optin_txn = AssetTransferTxn(
        sender=receiver_address,
        sp=params,
        receiver=receiver_address,
        amt=0,
        index=asset_id
    )
    signed_optin_txn = optin_txn.sign(rec_private_key)
    optin_tx_id = algod_client.send_transaction(signed_optin_txn)
    wait_for_confirmation(algod_client, optin_tx_id)

    print(f"[Opt-In 성공] TXID: {optin_tx_id}")
    return optin_tx_id


def transfer_committee_token(committee_id, amount):
    algod_client = get_algod_client()

    # 1. 협회 지갑 키 로드 및 유효성 확인
    sender_address, sender_private_key = get_wallet_keys(HCF_MNEMONIC)
    if sender_address != account.address_from_private_key(sender_private_key):
        raise Exception("HCF 지갑 주소와 프라이빗 키가 일치하지 않습니다.")

    # 2. 위원회 지갑 주소 조회
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT wallet_address FROM committees WHERE id = %s", (committee_id,))
            result = cur.fetchone()
            if not result:
                raise Exception("해당 committee_id에 대한 지갑 주소가 없습니다.")
            receiver_address = result[0]

        # 3. 수신자 지갑 Opt-in 확인 및 처리
        receiver_info = algod_client.account_info(receiver_address)
        opted_in = any(asset['asset-id'] == ASA_ID for asset in receiver_info.get("assets", []))
        if not opted_in:
            print("[Opt-In] 미등록 상태 → 자동 Opt-In 수행")
            opt_in_asset(algod_client, receiver_address, ASA_ID, "committees")
        else:
            print("[Opt-In] 이미 등록됨")

        # 4. 트랜잭션 생성 및 전송
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = 1000

        txn = AssetTransferTxn(
            sender=sender_address,
            sp=params,
            receiver=receiver_address,
            amt=amount,
            index=ASA_ID
        )
        signed_txn = txn.sign(sender_private_key)
        if signed_txn.transaction.sender != sender_address:
            raise Exception("트랜잭션 서명자 주소 불일치")

        tx_id = algod_client.send_transaction(signed_txn)
        wait_for_confirmation(algod_client, tx_id)
        print(f"[온체인 전송 완료] TX ID: {tx_id}")

        # 5. 오프체인 DB 상태 업데이트
        with conn.cursor() as cur:
            cur.execute("""
                WITH to_update AS (
                    SELECT id
                    FROM esg_coupons
                    WHERE status = 'ISSUED'
                    ORDER BY id
                    LIMIT %s
                )
                UPDATE esg_coupons
                SET status = 'COMMITTEE',
                    committee_id = %s,
                    tx_hash = %s,
                    committee_assigned_at = NOW(),
                    updated_at = NOW()
                WHERE id IN (SELECT id FROM to_update)
                RETURNING id
            """, (amount, committee_id, tx_id))
            updated_rows = cur.fetchall()
            updated_ids = [row[0] for row in updated_rows]
            print(f"[DB 업데이트 완료] 쿠폰 ID: {updated_ids}")

        conn.commit()
        return tx_id

    except Exception as e:
        print(f"[오류 발생] {str(e)}")
        raise Exception(f"토큰 전송 실패: {str(e)}")

    finally:
        conn.close()

def transfer_provider_token(provider_id, amount):
    algod_client = get_algod_client()

    # 1. 위원회 지갑 키 로드 및 유효성 확인
    sender_address, sender_private_key = get_wallet_keys(HCF_MNEMONIC)
    if sender_address != account.address_from_private_key(sender_private_key):
        raise Exception("위원회 지갑 주소와 프라이빗 키가 일치하지 않습니다.")

    # 2. 공급자 지갑 주소 조회
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT wallet_address FROM providers WHERE id = %s", (provider_id,))
            result = cur.fetchone()
            if not result:
                raise Exception("해당 provider_id에 대한 지갑 주소가 없습니다.")
            receiver_address = result[0]

        # 3. 수신자 지갑 Opt-in 확인 및 처리
        receiver_info = algod_client.account_info(receiver_address)
        opted_in = any(asset['asset-id'] == ASA_ID for asset in receiver_info.get("assets", []))
        if not opted_in:
            print("[Opt-In] 미등록 상태 → 자동 Opt-In 수행")
            opt_in_asset(algod_client, receiver_address, ASA_ID, "providers")
        else:
            print("[Opt-In] 이미 등록됨")

        # 4. 트랜잭션 생성 및 전송
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = 1000

        txn = AssetTransferTxn(
            sender=sender_address,
            sp=params,
            receiver=receiver_address,
            amt=amount,
            index=ASA_ID
        )
        signed_txn = txn.sign(sender_private_key)
        if signed_txn.transaction.sender != sender_address:
            raise Exception("트랜잭션 서명자 주소 불일치")

        tx_id = algod_client.send_transaction(signed_txn)
        wait_for_confirmation(algod_client, tx_id)
        print(f"[온체인 전송 완료] TX ID: {tx_id}")

        # 5. 오프체인 DB 상태 업데이트
        with conn.cursor() as cur:
            cur.execute("""
                WITH to_update AS (
                    SELECT id
                    FROM esg_coupons
                    WHERE status = 'COMMITTEE'
                    ORDER BY id
                    LIMIT %s
                )
                UPDATE esg_coupons
                SET status = 'PROVIDER',
                    provider_id = %s,
                    tx_hash = %s,
                    provider_assigned_at = NOW(),
                    updated_at = NOW()
                WHERE id IN (SELECT id FROM to_update)
                RETURNING id
            """, (amount, provider_id, tx_id))
            updated_rows = cur.fetchall()
            updated_ids = [row[0] for row in updated_rows]
            print(f"[DB 업데이트 완료] 쿠폰 ID: {updated_ids}")

        conn.commit()
        return tx_id

    except Exception as e:
        print(f"[오류 발생] {str(e)}")
        raise Exception(f"토큰 전송 실패: {str(e)}")

    finally:
        conn.close()

def transfer_consumer_token(consumer_id, amount):
    algod_client = get_algod_client()

    # 1. 위원회 지갑 키 로드 및 유효성 확인
    sender_address, sender_private_key = get_wallet_keys(HCF_MNEMONIC)
    if sender_address != account.address_from_private_key(sender_private_key):
        raise Exception("위원회 지갑 주소와 프라이빗 키가 일치하지 않습니다.")

    # 2. 공급자 지갑 주소 조회
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT wallet_address FROM consumers WHERE id = %s", (consumer_id,))
            result = cur.fetchone()
            if not result:
                raise Exception("해당 consumer_id에 대한 지갑 주소가 없습니다.")
            receiver_address = result[0]

        # 3. 수신자 지갑 Opt-in 확인 및 처리
        receiver_info = algod_client.account_info(receiver_address)
        opted_in = any(asset['asset-id'] == ASA_ID for asset in receiver_info.get("assets", []))
        if not opted_in:
            print("[Opt-In] 미등록 상태 → 자동 Opt-In 수행")
            opt_in_asset(algod_client, receiver_address, ASA_ID, "consumers")
        else:
            print("[Opt-In] 이미 등록됨")

        # 4. 트랜잭션 생성 및 전송
        params = algod_client.suggested_params()
        params.flat_fee = True
        params.fee = 1000

        txn = AssetTransferTxn(
            sender=sender_address,
            sp=params,
            receiver=receiver_address,
            amt=amount,
            index=ASA_ID
        )
        signed_txn = txn.sign(sender_private_key)
        if signed_txn.transaction.sender != sender_address:
            raise Exception("트랜잭션 서명자 주소 불일치")

        tx_id = algod_client.send_transaction(signed_txn)
        wait_for_confirmation(algod_client, tx_id)
        print(f"[온체인 전송 완료] TX ID: {tx_id}")

        # 5. 오프체인 DB 상태 업데이트
        with conn.cursor() as cur:
            cur.execute("""
                WITH to_update AS (
                    SELECT id
                    FROM esg_coupons
                    WHERE status = 'PROVIDER'
                    ORDER BY id
                    LIMIT %s
                )
                UPDATE esg_coupons
                SET status = 'CONSUMER',
                    consumer_id = %s,
                    tx_hash = %s,
                    consumer_assigned_at = NOW(),
                    updated_at = NOW()
                WHERE id IN (SELECT id FROM to_update)
                RETURNING id
            """, (amount, consumer_id, tx_id))
            updated_rows = cur.fetchall()
            updated_ids = [row[0] for row in updated_rows]
            print(f"[📝 DB 업데이트 완료] 쿠폰 ID: {updated_ids}")

        conn.commit()
        return tx_id

    except Exception as e:
        print(f"[오류 발생] {str(e)}")
        raise Exception(f"토큰 전송 실패: {str(e)}")

    finally:
        conn.close()

def wait_for_confirmation(client, txid, timeout=10):
    """
    주어진 txid가 블록에 포함될 때까지 최대 timeout초간 대기
    """
    start_time = time.time()
    last_round = client.status()["last-round"]

    while time.time() - start_time < timeout:
        try:
            pending_txn = client.pending_transaction_info(txid)
            if pending_txn.get("confirmed-round", 0) > 0:
                print(f"[확인됨] 트랜잭션 {txid} 이 블록 {pending_txn['confirmed-round']}에 포함됨")
                return pending_txn
        except Exception:
            pass

        print(f"[⌛ 대기 중] 블록 round: {last_round + 1}")
        client.status_after_block(last_round + 1)
        last_round += 1

    raise Exception(f"[타임아웃] {timeout}초 안에 트랜잭션 {txid} 확인 실패")
