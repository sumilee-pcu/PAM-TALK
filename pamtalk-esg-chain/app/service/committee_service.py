import psycopg2
from app.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

def get_committee_wallet_address(committee_id):
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT wallet_address FROM committees WHERE id = %s",
                (committee_id,)
            )
            result = cur.fetchone()
            if result is None:
                raise Exception(f"Committee ID {committee_id} not found or wallet_address is null")
            wallet_address = result[0]
            if not wallet_address:
                raise Exception(f"Committee ID {committee_id} does not have a wallet_address configured")
            return wallet_address
    finally:
        conn.close()
