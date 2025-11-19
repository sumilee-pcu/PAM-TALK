"""
Local Government Service
Handles all local government operations including dashboard data, carbon stats,
ESG programs, and regional management.
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
import json


class LocalGovernmentService:
    """Service for managing local government operations"""

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
    # Local Government Management
    # ===================================================================

    def get_government_dashboard(self, government_id: str) -> Optional[Dict]:
        """Get complete dashboard data for a local government"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM v_local_government_dashboard
                WHERE government_id = ?
            """, (government_id,))

            dashboard = cursor.fetchone()

            if not dashboard:
                return None

            # Add recent trends
            dashboard['trends'] = self._get_carbon_trends(government_id, cursor)
            dashboard['recent_achievements'] = self._get_recent_achievements(government_id, cursor)
            dashboard['upcoming_programs'] = self._get_upcoming_programs(government_id, cursor)

            return dashboard

        finally:
            conn.close()

    def get_all_governments(self, government_type: Optional[str] = None) -> List[Dict]:
        """Get all local governments with optional filter by type"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            if government_type:
                cursor.execute("""
                    SELECT * FROM local_governments
                    WHERE is_active = TRUE AND government_type = ?
                    ORDER BY government_name
                """, (government_type,))
            else:
                cursor.execute("""
                    SELECT * FROM local_governments
                    WHERE is_active = TRUE
                    ORDER BY government_name
                """)

            return cursor.fetchall()

        finally:
            conn.close()

    def _get_carbon_trends(self, government_id: str, cursor) -> List[Dict]:
        """Get carbon reduction trends for the past 30 days"""
        cursor.execute("""
            SELECT
                stat_date,
                total_carbon_reduction,
                active_residents,
                active_businesses
            FROM local_carbon_stats
            WHERE government_id = ? AND stat_period = 'daily'
            ORDER BY stat_date DESC
            LIMIT 30
        """, (government_id,))

        return cursor.fetchall()

    def _get_recent_achievements(self, government_id: str, cursor) -> List[Dict]:
        """Get recent achievements"""
        cursor.execute("""
            SELECT * FROM regional_achievements
            WHERE government_id = ?
            ORDER BY achieved_date DESC
            LIMIT 5
        """, (government_id,))

        return cursor.fetchall()

    def _get_upcoming_programs(self, government_id: str, cursor) -> List[Dict]:
        """Get upcoming or ongoing ESG programs"""
        cursor.execute("""
            SELECT * FROM regional_esg_programs
            WHERE government_id = ?
            AND status IN ('recruiting', 'ongoing')
            AND (end_date IS NULL OR end_date >= DATE('now'))
            ORDER BY start_date DESC
            LIMIT 5
        """, (government_id,))

        return cursor.fetchall()

    # ===================================================================
    # Carbon Statistics
    # ===================================================================

    def get_carbon_stats(
        self,
        government_id: str,
        period: str = 'monthly',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """Get carbon reduction statistics for a period"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = """
                SELECT * FROM local_carbon_stats
                WHERE government_id = ? AND stat_period = ?
            """
            params = [government_id, period]

            if start_date:
                query += " AND stat_date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND stat_date <= ?"
                params.append(end_date)

            query += " ORDER BY stat_date DESC"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            conn.close()

    def update_daily_carbon_stats(self, government_id: str) -> Dict:
        """Update daily carbon statistics from various sources"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            today = date.today().isoformat()

            # Aggregate carbon reduction from charging stations
            cursor.execute("""
                SELECT
                    COALESCE(SUM(carbon_reduction_kg), 0) as ev_reduction
                FROM charging_station_usage csu
                JOIN charging_stations cs ON csu.station_id = cs.station_id
                WHERE cs.government_id = ?
                AND DATE(csu.start_time) = ?
                AND csu.session_status = 'completed'
            """, (government_id, today))

            ev_reduction = cursor.fetchone()[0]

            # Aggregate from carbon activities (from main carbon tracking)
            cursor.execute("""
                SELECT
                    COALESCE(SUM(carbon_saved_kg), 0) as other_reduction
                FROM carbon_activities ca
                JOIN users u ON ca.user_id = u.user_id
                WHERE u.region = ?
                AND DATE(ca.activity_date) = ?
            """, (government_id, today))

            other_reduction = cursor.fetchone()[0]

            total_reduction = ev_reduction + other_reduction

            # Count active participants
            cursor.execute("""
                SELECT COUNT(DISTINCT u.user_id) as active_residents
                FROM carbon_activities ca
                JOIN users u ON ca.user_id = u.user_id
                WHERE u.region = ?
                AND DATE(ca.activity_date) = ?
            """, (government_id, today))

            active_residents = cursor.fetchone()[0]

            # Upsert daily stats
            cursor.execute("""
                INSERT INTO local_carbon_stats (
                    government_id, stat_date, stat_period,
                    total_carbon_reduction, ev_usage_reduction,
                    active_residents, updated_at
                ) VALUES (?, ?, 'daily', ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(government_id, stat_date, stat_period)
                DO UPDATE SET
                    total_carbon_reduction = excluded.total_carbon_reduction,
                    ev_usage_reduction = excluded.ev_usage_reduction,
                    active_residents = excluded.active_residents,
                    updated_at = CURRENT_TIMESTAMP
            """, (government_id, today, total_reduction, ev_reduction, active_residents))

            conn.commit()

            return {
                'government_id': government_id,
                'stat_date': today,
                'total_carbon_reduction': total_reduction,
                'ev_reduction': ev_reduction,
                'active_residents': active_residents
            }

        finally:
            conn.close()

    def get_regional_rankings(self, region_type: str = 'all') -> List[Dict]:
        """Get carbon reduction rankings of local governments"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = """
                SELECT
                    lg.government_id,
                    lg.government_name,
                    lg.government_type,
                    lg.region_code,
                    lcs.total_carbon_reduction,
                    lcs.reduction_percentage,
                    lcs.active_residents,
                    lcs.national_rank
                FROM local_governments lg
                JOIN local_carbon_stats lcs ON lg.government_id = lcs.government_id
                WHERE lcs.stat_period = 'monthly'
                AND lcs.stat_date >= DATE('now', 'start of month')
            """

            if region_type != 'all':
                query += " AND lg.government_type = ?"
                cursor.execute(query + " ORDER BY lcs.total_carbon_reduction DESC", (region_type,))
            else:
                cursor.execute(query + " ORDER BY lcs.total_carbon_reduction DESC")

            return cursor.fetchall()

        finally:
            conn.close()

    # ===================================================================
    # Regional ESG Programs
    # ===================================================================

    def get_esg_programs(
        self,
        government_id: Optional[str] = None,
        program_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get ESG programs with filters"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM regional_esg_programs WHERE 1=1"
            params = []

            if government_id:
                query += " AND government_id = ?"
                params.append(government_id)

            if program_type:
                query += " AND program_type = ?"
                params.append(program_type)

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY start_date DESC"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            conn.close()

    def create_esg_program(self, program_data: Dict) -> str:
        """Create a new ESG program"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            program_id = f"PROG-{program_data['government_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute("""
                INSERT INTO regional_esg_programs (
                    program_id, government_id, program_name, program_type,
                    description, objectives, target_group, budget_amount,
                    support_type, start_date, end_date, application_start,
                    application_deadline, max_participants, eligibility_criteria,
                    required_documents, status, expected_carbon_reduction,
                    manager_name, manager_email, manager_phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                program_id,
                program_data['government_id'],
                program_data['program_name'],
                program_data['program_type'],
                program_data.get('description'),
                program_data.get('objectives'),
                program_data.get('target_group'),
                program_data.get('budget_amount'),
                program_data.get('support_type'),
                program_data['start_date'],
                program_data.get('end_date'),
                program_data.get('application_start'),
                program_data.get('application_deadline'),
                program_data.get('max_participants'),
                program_data.get('eligibility_criteria'),
                program_data.get('required_documents'),
                program_data.get('status', 'planned'),
                program_data.get('expected_carbon_reduction'),
                program_data.get('manager_name'),
                program_data.get('manager_email'),
                program_data.get('manager_phone')
            ))

            conn.commit()
            return program_id

        finally:
            conn.close()

    def update_esg_program(self, program_id: str, update_data: Dict) -> bool:
        """Update an ESG program"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build dynamic update query
            set_clauses = []
            params = []

            for key, value in update_data.items():
                set_clauses.append(f"{key} = ?")
                params.append(value)

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            params.append(program_id)

            query = f"""
                UPDATE regional_esg_programs
                SET {', '.join(set_clauses)}
                WHERE program_id = ?
            """

            cursor.execute(query, params)
            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()
