import psycopg2
from app.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST
from datetime import datetime

def get_db_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port="5432"
    )

def get_undistributed_coupons(limit: int):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM esg_coupons
        WHERE status = 'ISSUED'
        ORDER BY id
        LIMIT %s
    """, (limit,))
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ids

def update_coupons_as_distributed(coupon_ids: list, committee_id: int, tx_hash: str):
    if not coupon_ids:
        return

    conn = get_db_conn()
    cursor = conn.cursor()
    now = datetime.now()

    sql = """
        UPDATE esg_coupons
        SET status = 'DISTRIBUTED',
            committee_id = %s,
            committee_assigned_at = %s,
            tx_hash = %s,
            updated_at = %s
        WHERE id = ANY(%s)
    """
    cursor.execute(sql, (committee_id, now, tx_hash, now, coupon_ids))
    conn.commit()
    cursor.close()
    conn.close()