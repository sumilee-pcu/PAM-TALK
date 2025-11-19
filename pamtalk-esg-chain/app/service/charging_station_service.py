"""
Charging Station Service
Manages EV charging stations, usage tracking, and location-based searches
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import json
import math


class ChargingStationService:
    """Service for managing charging stations and usage"""

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

    def get_all_stations(
        self,
        government_id: Optional[str] = None,
        station_type: Optional[str] = None,
        accepts_esg_gold: Optional[bool] = None
    ) -> List[Dict]:
        """Get all charging stations with filters"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM v_charging_station_map WHERE 1=1"
            params = []

            if government_id:
                query += " AND government_id = ?"
                params.append(government_id)

            if station_type:
                query += " AND station_type = ?"
                params.append(station_type)

            if accepts_esg_gold is not None:
                query += " AND accepts_esg_gold = ?"
                params.append(accepts_esg_gold)

            query += " ORDER BY station_name"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            conn.close()

    def get_nearby_stations(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        limit: int = 20
    ) -> List[Dict]:
        """Find charging stations near a location"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            # Using simple distance calculation (not precise for large distances)
            # For production, consider using PostGIS or more accurate geo calculations
            cursor.execute("""
                SELECT
                    *,
                    (
                        6371 * acos(
                            cos(radians(?)) * cos(radians(latitude)) *
                            cos(radians(longitude) - radians(?)) +
                            sin(radians(?)) * sin(radians(latitude))
                        )
                    ) AS distance_km
                FROM v_charging_station_map
                WHERE operational_status = 'operational'
                HAVING distance_km <= ?
                ORDER BY distance_km
                LIMIT ?
            """, (latitude, longitude, latitude, radius_km, limit))

            return cursor.fetchall()

        finally:
            conn.close()

    def get_station_detail(self, station_id: str) -> Optional[Dict]:
        """Get detailed information about a charging station"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM charging_stations WHERE station_id = ?
            """, (station_id,))

            station = cursor.fetchone()

            if not station:
                return None

            # Get recent reviews
            cursor.execute("""
                SELECT * FROM charging_station_reviews
                WHERE station_id = ? AND is_visible = TRUE
                ORDER BY created_at DESC
                LIMIT 10
            """, (station_id,))

            station['recent_reviews'] = cursor.fetchall()

            # Get usage statistics
            cursor.execute("""
                SELECT
                    COUNT(*) as total_sessions,
                    SUM(energy_delivered_kwh) as total_energy_kwh,
                    SUM(carbon_reduction_kg) as total_carbon_reduction,
                    AVG(duration_minutes) as avg_duration_minutes,
                    SUM(esg_gold_amount) as total_esg_gold_used
                FROM charging_station_usage
                WHERE station_id = ? AND session_status = 'completed'
            """, (station_id,))

            station['usage_stats'] = cursor.fetchone()

            # Parse JSON fields
            if station.get('charger_types'):
                try:
                    station['charger_types'] = json.loads(station['charger_types'])
                except:
                    pass

            if station.get('operating_hours'):
                try:
                    station['operating_hours'] = json.loads(station['operating_hours'])
                except:
                    pass

            return station

        finally:
            conn.close()

    def create_station(self, station_data: Dict) -> str:
        """Create a new charging station"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            station_id = f"CS-{station_data['government_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Convert lists/dicts to JSON strings
            charger_types = json.dumps(station_data.get('charger_types', []))
            operating_hours = json.dumps(station_data.get('operating_hours', {}))

            cursor.execute("""
                INSERT INTO charging_stations (
                    station_id, government_id, station_name, station_type,
                    operator_name, operator_contact, address, latitude, longitude,
                    total_chargers, available_chargers, charger_types, max_power_kw,
                    price_per_kwh, parking_fee_per_hour, accepts_esg_gold,
                    accepts_pam_token, accepts_credit_card, esg_gold_discount_percentage,
                    operating_hours, is_24_hours, has_wifi, has_restroom,
                    has_convenience_store, has_cafe, has_parking, parking_capacity,
                    wheelchair_accessible, operational_status, is_public, installation_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                station_id,
                station_data['government_id'],
                station_data['station_name'],
                station_data['station_type'],
                station_data['operator_name'],
                station_data.get('operator_contact'),
                station_data['address'],
                station_data['latitude'],
                station_data['longitude'],
                station_data['total_chargers'],
                station_data.get('available_chargers', station_data['total_chargers']),
                charger_types,
                station_data['max_power_kw'],
                station_data.get('price_per_kwh'),
                station_data.get('parking_fee_per_hour'),
                station_data.get('accepts_esg_gold', False),
                station_data.get('accepts_pam_token', False),
                station_data.get('accepts_credit_card', True),
                station_data.get('esg_gold_discount_percentage', 0),
                operating_hours,
                station_data.get('is_24_hours', True),
                station_data.get('has_wifi', False),
                station_data.get('has_restroom', False),
                station_data.get('has_convenience_store', False),
                station_data.get('has_cafe', False),
                station_data.get('has_parking', True),
                station_data.get('parking_capacity'),
                station_data.get('wheelchair_accessible', False),
                station_data.get('operational_status', 'operational'),
                station_data.get('is_public', True),
                station_data.get('installation_date', date.today().isoformat())
            ))

            conn.commit()
            return station_id

        finally:
            conn.close()

    def update_station(self, station_id: str, update_data: Dict) -> bool:
        """Update charging station information"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Convert lists/dicts to JSON strings if present
            if 'charger_types' in update_data and isinstance(update_data['charger_types'], list):
                update_data['charger_types'] = json.dumps(update_data['charger_types'])

            if 'operating_hours' in update_data and isinstance(update_data['operating_hours'], dict):
                update_data['operating_hours'] = json.dumps(update_data['operating_hours'])

            set_clauses = []
            params = []

            for key, value in update_data.items():
                set_clauses.append(f"{key} = ?")
                params.append(value)

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            params.append(station_id)

            query = f"""
                UPDATE charging_stations
                SET {', '.join(set_clauses)}
                WHERE station_id = ?
            """

            cursor.execute(query, params)
            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()

    # ===================================================================
    # Charging Sessions
    # ===================================================================

    def start_charging_session(self, session_data: Dict) -> str:
        """Start a new charging session"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            usage_id = f"USAGE-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            cursor.execute("""
                INSERT INTO charging_station_usage (
                    usage_id, station_id, user_algorand_address, user_id,
                    start_time, max_power_kw, payment_method, session_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'in_progress')
            """, (
                usage_id,
                session_data['station_id'],
                session_data['user_algorand_address'],
                session_data.get('user_id'),
                datetime.now().isoformat(),
                session_data.get('max_power_kw'),
                session_data.get('payment_method', 'credit_card')
            ))

            conn.commit()
            return usage_id

        finally:
            conn.close()

    def complete_charging_session(
        self,
        usage_id: str,
        energy_delivered_kwh: float,
        payment_details: Optional[Dict] = None
    ) -> Dict:
        """Complete a charging session and calculate costs"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            # Get session details
            cursor.execute("""
                SELECT csu.*, cs.price_per_kwh, cs.esg_gold_discount_percentage,
                       cs.accepts_esg_gold, cs.government_id
                FROM charging_station_usage csu
                JOIN charging_stations cs ON csu.station_id = cs.station_id
                WHERE csu.usage_id = ?
            """, (usage_id,))

            session = cursor.fetchone()

            if not session:
                raise ValueError(f"Session {usage_id} not found")

            # Calculate costs
            base_cost = energy_delivered_kwh * session['price_per_kwh']
            discount = 0
            esg_gold_used = 0

            if payment_details and payment_details.get('use_esg_gold') and session['accepts_esg_gold']:
                discount = base_cost * (session['esg_gold_discount_percentage'] / 100)
                # Assume 1 ESG-Gold = 10 KRW for calculation
                esg_gold_used = int(discount / 10)

            total_cost = base_cost - discount

            # Calculate carbon reduction (assuming 0.5 kg CO2 per kWh saved vs gasoline)
            carbon_reduction = energy_delivered_kwh * 0.5

            # Calculate duration
            start_time = datetime.fromisoformat(session['start_time'])
            end_time = datetime.now()
            duration_minutes = int((end_time - start_time).total_seconds() / 60)

            # Update session
            cursor.execute("""
                UPDATE charging_station_usage
                SET end_time = ?,
                    duration_minutes = ?,
                    energy_delivered_kwh = ?,
                    carbon_reduction_kg = ?,
                    total_cost = ?,
                    discount_applied = ?,
                    esg_gold_amount = ?,
                    session_status = 'completed',
                    updated_at = CURRENT_TIMESTAMP
                WHERE usage_id = ?
            """, (
                end_time.isoformat(),
                duration_minutes,
                energy_delivered_kwh,
                carbon_reduction,
                total_cost,
                discount,
                esg_gold_used,
                usage_id
            ))

            conn.commit()

            return {
                'usage_id': usage_id,
                'energy_delivered_kwh': energy_delivered_kwh,
                'duration_minutes': duration_minutes,
                'base_cost': base_cost,
                'discount': discount,
                'total_cost': total_cost,
                'esg_gold_used': esg_gold_used,
                'carbon_reduction_kg': carbon_reduction,
                'government_id': session['government_id']
            }

        finally:
            conn.close()

    def get_user_charging_history(
        self,
        user_algorand_address: str,
        limit: int = 50
    ) -> List[Dict]:
        """Get charging history for a user"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    csu.*,
                    cs.station_name,
                    cs.address,
                    cs.government_id
                FROM charging_station_usage csu
                JOIN charging_stations cs ON csu.station_id = cs.station_id
                WHERE csu.user_algorand_address = ?
                ORDER BY csu.start_time DESC
                LIMIT ?
            """, (user_algorand_address, limit))

            return cursor.fetchall()

        finally:
            conn.close()

    # ===================================================================
    # Reviews and Ratings
    # ===================================================================

    def add_review(self, review_data: Dict) -> int:
        """Add a review for a charging station"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO charging_station_reviews (
                    station_id, user_id, rating, review_text,
                    charger_speed_rating, facility_rating, accessibility_rating,
                    is_verified_usage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                review_data['station_id'],
                review_data['user_id'],
                review_data['rating'],
                review_data.get('review_text'),
                review_data.get('charger_speed_rating'),
                review_data.get('facility_rating'),
                review_data.get('accessibility_rating'),
                review_data.get('is_verified_usage', False)
            ))

            review_id = cursor.lastrowid

            # Update station average rating
            cursor.execute("""
                UPDATE charging_stations
                SET average_rating = (
                    SELECT AVG(rating)
                    FROM charging_station_reviews
                    WHERE station_id = ? AND is_visible = TRUE
                ),
                review_count = (
                    SELECT COUNT(*)
                    FROM charging_station_reviews
                    WHERE station_id = ? AND is_visible = TRUE
                ),
                updated_at = CURRENT_TIMESTAMP
                WHERE station_id = ?
            """, (review_data['station_id'], review_data['station_id'], review_data['station_id']))

            conn.commit()
            return review_id

        finally:
            conn.close()

    # ===================================================================
    # Statistics and Analytics
    # ===================================================================

    def get_station_statistics(self, government_id: str) -> Dict:
        """Get charging station statistics for a government"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            # Station counts by type
            cursor.execute("""
                SELECT station_type, COUNT(*) as count
                FROM charging_stations
                WHERE government_id = ?
                GROUP BY station_type
            """, (government_id,))
            by_type = cursor.fetchall()

            # Overall statistics
            cursor.execute("""
                SELECT
                    COUNT(*) as total_stations,
                    SUM(total_chargers) as total_chargers,
                    SUM(available_chargers) as available_chargers,
                    SUM(total_charging_sessions) as total_sessions,
                    SUM(total_energy_delivered_kwh) as total_energy_kwh,
                    SUM(total_carbon_reduction_kg) as total_carbon_reduction,
                    AVG(average_rating) as avg_rating
                FROM charging_stations
                WHERE government_id = ?
            """, (government_id,))
            overall = cursor.fetchone()

            # Monthly trends
            cursor.execute("""
                SELECT
                    strftime('%Y-%m', start_time) as month,
                    COUNT(*) as sessions,
                    SUM(energy_delivered_kwh) as energy_kwh,
                    SUM(carbon_reduction_kg) as carbon_reduction,
                    SUM(esg_gold_amount) as esg_gold_used
                FROM charging_station_usage csu
                JOIN charging_stations cs ON csu.station_id = cs.station_id
                WHERE cs.government_id = ?
                AND csu.session_status = 'completed'
                AND csu.start_time >= datetime('now', '-6 months')
                GROUP BY month
                ORDER BY month DESC
            """, (government_id,))
            monthly_trends = cursor.fetchall()

            return {
                'by_station_type': by_type,
                'overall_statistics': overall,
                'monthly_trends': monthly_trends
            }

        finally:
            conn.close()

    def get_popular_stations(self, government_id: str, limit: int = 10) -> List[Dict]:
        """Get most popular charging stations"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    cs.*,
                    COUNT(csu.usage_id) as recent_sessions,
                    SUM(csu.energy_delivered_kwh) as recent_energy_kwh
                FROM charging_stations cs
                LEFT JOIN charging_station_usage csu
                    ON cs.station_id = csu.station_id
                    AND csu.start_time >= datetime('now', '-30 days')
                    AND csu.session_status = 'completed'
                WHERE cs.government_id = ?
                AND cs.operational_status = 'operational'
                GROUP BY cs.station_id
                ORDER BY recent_sessions DESC, cs.average_rating DESC
                LIMIT ?
            """, (government_id, limit))

            return cursor.fetchall()

        finally:
            conn.close()
