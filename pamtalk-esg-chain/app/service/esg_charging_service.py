"""
ESG-Gold Charging Station Service
Manages ESG-Gold token charging stations and transactions
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import secrets
import hashlib
import json


class ESGChargingService:
    """Service for managing ESG-Gold charging stations"""

    def __init__(self, db_path: str = "pamtalk_esg.db"):
        self.db_path = db_path

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def _dict_factory(self, cursor, row):
        """Convert database rows to dictionaries"""
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}

    # ===================================================================
    # Charging Station Management
    # ===================================================================

    def create_station(self, station_data: Dict) -> str:
        """Create a new charging station"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            station_id = f"STN-{station_data['station_type'].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute("""
                INSERT INTO esg_charging_stations (
                    station_id, station_name, station_type, location,
                    latitude, longitude, operating_hours, is_active,
                    api_key, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                station_id,
                station_data['station_name'],
                station_data['station_type'],  # online, kiosk, partner
                station_data.get('location'),
                station_data.get('latitude'),
                station_data.get('longitude'),
                station_data.get('operating_hours', '24/7'),
                True,
                secrets.token_urlsafe(32) if station_data['station_type'] == 'partner' else None,
                datetime.now().isoformat()
            ))

            conn.commit()
            return station_id

        finally:
            conn.close()

    def get_all_stations(
        self,
        station_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get all charging stations"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = """
                SELECT
                    s.*,
                    COUNT(DISTINCT t.transaction_id) as total_charges,
                    SUM(t.amount) as total_amount,
                    AVG(t.processing_time_ms) as avg_processing_time
                FROM esg_charging_stations s
                LEFT JOIN esg_charging_transactions t ON s.station_id = t.station_id
                WHERE 1=1
            """
            params = []

            if station_type:
                query += " AND s.station_type = ?"
                params.append(station_type)

            if status:
                is_active = status == 'online'
                query += " AND s.is_active = ?"
                params.append(is_active)

            query += " GROUP BY s.station_id ORDER BY s.created_at DESC"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            conn.close()

    def get_station_detail(self, station_id: str) -> Optional[Dict]:
        """Get detailed station information"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM esg_charging_stations WHERE station_id = ?
            """, (station_id,))

            station = cursor.fetchone()

            if not station:
                return None

            # Get today's statistics
            cursor.execute("""
                SELECT
                    COUNT(*) as today_charges,
                    SUM(amount) as today_amount,
                    SUM(esg_gold_amount) as today_gold
                FROM esg_charging_transactions
                WHERE station_id = ?
                AND DATE(created_at) = DATE('now')
                AND status = 'completed'
            """, (station_id,))

            station['today_stats'] = cursor.fetchone()

            return station

        finally:
            conn.close()

    def update_station_status(self, station_id: str, is_active: bool) -> bool:
        """Update station active status"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE esg_charging_stations
                SET is_active = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE station_id = ?
            """, (is_active, station_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    # ===================================================================
    # Charging Transaction Processing
    # ===================================================================

    def initiate_charge(self, charge_data: Dict) -> Dict:
        """Initiate a charging transaction"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            # Verify station is active
            cursor.execute("""
                SELECT is_active FROM esg_charging_stations WHERE station_id = ?
            """, (charge_data['station_id'],))

            station = cursor.fetchone()
            if not station or not station['is_active']:
                raise ValueError("Station is not available")

            # Calculate amounts
            amount = charge_data['amount']
            fee_percentage = self._get_fee_percentage(charge_data['station_type'])
            fee = int(amount * fee_percentage / 100)
            total_amount = amount + fee
            esg_gold_amount = amount * 1000  # 1 KRW = 1000 ESG-Gold

            # Create transaction
            transaction_id = f"TX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4)}"

            cursor.execute("""
                INSERT INTO esg_charging_transactions (
                    transaction_id, station_id, user_algorand_address,
                    amount, fee, total_amount, esg_gold_amount,
                    payment_method, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (
                transaction_id,
                charge_data['station_id'],
                charge_data['user_address'],
                amount,
                fee,
                total_amount,
                esg_gold_amount,
                charge_data['payment_method'],
                datetime.now().isoformat()
            ))

            conn.commit()

            return {
                'transaction_id': transaction_id,
                'amount': amount,
                'fee': fee,
                'total_amount': total_amount,
                'esg_gold_amount': esg_gold_amount,
                'status': 'pending'
            }

        finally:
            conn.close()

    def complete_charge(
        self,
        transaction_id: str,
        payment_reference: str,
        blockchain_tx_id: Optional[str] = None
    ) -> Dict:
        """Complete a charging transaction"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            start_time = datetime.now()

            # Get transaction details
            cursor.execute("""
                SELECT * FROM esg_charging_transactions WHERE transaction_id = ?
            """, (transaction_id,))

            transaction = cursor.fetchone()

            if not transaction:
                raise ValueError("Transaction not found")

            if transaction['status'] != 'pending':
                raise ValueError("Transaction already processed")

            # Update transaction
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            cursor.execute("""
                UPDATE esg_charging_transactions
                SET status = 'completed',
                    payment_reference = ?,
                    blockchain_tx_id = ?,
                    processing_time_ms = ?,
                    completed_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE transaction_id = ?
            """, (
                payment_reference,
                blockchain_tx_id,
                processing_time,
                datetime.now().isoformat(),
                transaction_id
            ))

            # Here you would:
            # 1. Call blockchain smart contract to mint ESG-Gold
            # 2. Update user's balance in the database
            # 3. Create blockchain receipt

            conn.commit()

            return {
                'transaction_id': transaction_id,
                'status': 'completed',
                'esg_gold_amount': transaction['esg_gold_amount'],
                'blockchain_tx_id': blockchain_tx_id,
                'receipt_url': f"/receipts/{transaction_id}"
            }

        finally:
            conn.close()

    def fail_charge(self, transaction_id: str, error_message: str) -> bool:
        """Mark a charging transaction as failed"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE esg_charging_transactions
                SET status = 'failed',
                    error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE transaction_id = ?
            """, (error_message, transaction_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    # ===================================================================
    # QR Code System
    # ===================================================================

    def generate_qr_code(self, station_id: str, amount: int) -> Dict:
        """Generate a QR code for charging"""
        qr_id = f"QR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4)}"

        # Create QR code data
        qr_data = {
            'qr_id': qr_id,
            'station_id': station_id,
            'amount': amount,
            'expires_at': (datetime.now() + timedelta(minutes=5)).isoformat()
        }

        # Generate verification hash
        verification_hash = hashlib.sha256(
            f"{qr_id}{station_id}{amount}".encode()
        ).hexdigest()

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO esg_qr_codes (
                    qr_id, station_id, amount, verification_hash,
                    expires_at, is_used, created_at
                ) VALUES (?, ?, ?, ?, ?, FALSE, ?)
            """, (
                qr_id,
                station_id,
                amount,
                verification_hash,
                qr_data['expires_at'],
                datetime.now().isoformat()
            ))

            conn.commit()

            return {
                'qr_id': qr_id,
                'qr_data': json.dumps(qr_data),
                'verification_hash': verification_hash,
                'expires_at': qr_data['expires_at']
            }

        finally:
            conn.close()

    def verify_qr_code(self, qr_id: str) -> Optional[Dict]:
        """Verify and retrieve QR code data"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM esg_qr_codes WHERE qr_id = ?
            """, (qr_id,))

            qr_code = cursor.fetchone()

            if not qr_code:
                return None

            # Check if expired
            if datetime.fromisoformat(qr_code['expires_at']) < datetime.now():
                return None

            # Check if already used
            if qr_code['is_used']:
                return None

            return qr_code

        finally:
            conn.close()

    def mark_qr_used(self, qr_id: str, transaction_id: str) -> bool:
        """Mark QR code as used"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE esg_qr_codes
                SET is_used = TRUE,
                    transaction_id = ?,
                    used_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE qr_id = ?
            """, (transaction_id, datetime.now().isoformat(), qr_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    # ===================================================================
    # Transaction History
    # ===================================================================

    def get_user_charging_history(
        self,
        user_address: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get charging history for a user"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    t.*,
                    s.station_name,
                    s.station_type
                FROM esg_charging_transactions t
                JOIN esg_charging_stations s ON t.station_id = s.station_id
                WHERE t.user_algorand_address = ?
                ORDER BY t.created_at DESC
                LIMIT ?
            """, (user_address, limit))

            return cursor.fetchall()

        finally:
            conn.close()

    def get_station_transactions(
        self,
        station_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """Get transactions for a station"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = """
                SELECT * FROM esg_charging_transactions
                WHERE station_id = ?
            """
            params = [station_id]

            if start_date:
                query += " AND DATE(created_at) >= ?"
                params.append(start_date)

            if end_date:
                query += " AND DATE(created_at) <= ?"
                params.append(end_date)

            query += " ORDER BY created_at DESC"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            conn.close()

    # ===================================================================
    # Statistics and Analytics
    # ===================================================================

    def get_charging_statistics(self, days: int = 30) -> Dict:
        """Get overall charging statistics"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            start_date = (datetime.now() - timedelta(days=days)).date().isoformat()

            # Overall stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total_transactions,
                    SUM(amount) as total_amount,
                    SUM(fee) as total_fee,
                    SUM(esg_gold_amount) as total_gold,
                    AVG(processing_time_ms) as avg_processing_time,
                    COUNT(DISTINCT user_algorand_address) as unique_users
                FROM esg_charging_transactions
                WHERE DATE(created_at) >= ?
                AND status = 'completed'
            """, (start_date,))

            overall = cursor.fetchone()

            # By station type
            cursor.execute("""
                SELECT
                    s.station_type,
                    COUNT(t.transaction_id) as transactions,
                    SUM(t.amount) as amount
                FROM esg_charging_transactions t
                JOIN esg_charging_stations s ON t.station_id = s.station_id
                WHERE DATE(t.created_at) >= ?
                AND t.status = 'completed'
                GROUP BY s.station_type
            """, (start_date,))

            by_type = cursor.fetchall()

            # Daily trend
            cursor.execute("""
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as transactions,
                    SUM(amount) as amount,
                    SUM(esg_gold_amount) as gold_issued
                FROM esg_charging_transactions
                WHERE DATE(created_at) >= ?
                AND status = 'completed'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """, (start_date,))

            daily_trend = cursor.fetchall()

            return {
                'overall': overall,
                'by_station_type': by_type,
                'daily_trend': daily_trend
            }

        finally:
            conn.close()

    # ===================================================================
    # Helper Methods
    # ===================================================================

    def _get_fee_percentage(self, station_type: str) -> float:
        """Get fee percentage for station type"""
        fees = {
            'online': 1.5,
            'kiosk': 2.0,
            'partner': 2.5
        }
        return fees.get(station_type, 2.0)

    def get_user_balance(self, user_address: str) -> int:
        """Get user's current ESG-Gold balance"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT balance FROM user_balances
                WHERE algorand_address = ?
            """, (user_address,))

            result = cursor.fetchone()
            return result[0] if result else 0

        finally:
            conn.close()

    def update_user_balance(
        self,
        user_address: str,
        amount: int,
        transaction_id: str
    ) -> bool:
        """Update user's ESG-Gold balance"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO user_balances (algorand_address, balance, last_transaction_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(algorand_address)
                DO UPDATE SET
                    balance = balance + ?,
                    last_transaction_id = ?,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_address, amount, transaction_id, amount, transaction_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()
