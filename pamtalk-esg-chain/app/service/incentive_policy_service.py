"""
Incentive Policy Service
Manages local government incentive policies and applications
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional
import json


class IncentivePolicyService:
    """Service for managing incentive policies and applications"""

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
    # Policy Management
    # ===================================================================

    def create_policy(self, policy_data: Dict) -> str:
        """Create a new incentive policy"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            policy_id = f"POL-{policy_data['government_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute("""
                INSERT INTO local_incentive_policies (
                    policy_id, government_id, policy_name, policy_type,
                    description, target_group, eligibility_criteria,
                    benefit_amount, benefit_unit, esg_gold_bonus_percentage,
                    total_budget, remaining_budget, application_start_date,
                    application_end_date, required_documents, required_activities,
                    minimum_carbon_reduction, review_period_days, approval_authority,
                    status, legal_basis, regulation_url, contact_department,
                    contact_phone, contact_email, effective_date, expiry_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                policy_id,
                policy_data['government_id'],
                policy_data['policy_name'],
                policy_data['policy_type'],
                policy_data['description'],
                policy_data['target_group'],
                policy_data['eligibility_criteria'],
                policy_data.get('benefit_amount'),
                policy_data.get('benefit_unit'),
                policy_data.get('esg_gold_bonus_percentage'),
                policy_data.get('total_budget'),
                policy_data.get('total_budget'),  # Initially, remaining = total
                policy_data['application_start_date'],
                policy_data.get('application_end_date'),
                policy_data.get('required_documents'),
                policy_data.get('required_activities'),
                policy_data.get('minimum_carbon_reduction'),
                policy_data.get('review_period_days', 14),
                policy_data.get('approval_authority'),
                policy_data.get('status', 'active'),
                policy_data.get('legal_basis'),
                policy_data.get('regulation_url'),
                policy_data.get('contact_department'),
                policy_data.get('contact_phone'),
                policy_data.get('contact_email'),
                policy_data['effective_date'],
                policy_data.get('expiry_date')
            ))

            conn.commit()
            return policy_id

        finally:
            conn.close()

    def get_policies(
        self,
        government_id: Optional[str] = None,
        policy_type: Optional[str] = None,
        status: str = 'active',
        target_group: Optional[str] = None
    ) -> List[Dict]:
        """Get incentive policies with filters"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM local_incentive_policies WHERE 1=1"
            params = []

            if government_id:
                query += " AND government_id = ?"
                params.append(government_id)

            if policy_type:
                query += " AND policy_type = ?"
                params.append(policy_type)

            if status:
                query += " AND status = ?"
                params.append(status)

            if target_group:
                query += " AND target_group LIKE ?"
                params.append(f"%{target_group}%")

            # Check if still within application period
            query += " AND (application_end_date IS NULL OR application_end_date >= DATE('now'))"
            query += " ORDER BY created_at DESC"

            cursor.execute(query, params)
            policies = cursor.fetchall()

            # Add application counts for each policy
            for policy in policies:
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_applications,
                        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                        SUM(CASE WHEN status = 'under_review' THEN 1 ELSE 0 END) as under_review,
                        SUM(CASE WHEN status IN ('approved', 'paid') THEN approved_amount ELSE 0 END) as total_paid
                    FROM incentive_applications
                    WHERE policy_id = ?
                """, (policy['policy_id'],))

                stats = cursor.fetchone()
                policy['application_stats'] = stats

            return policies

        finally:
            conn.close()

    def get_policy_detail(self, policy_id: str) -> Optional[Dict]:
        """Get detailed policy information"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM local_incentive_policies WHERE policy_id = ?
            """, (policy_id,))

            policy = cursor.fetchone()

            if not policy:
                return None

            # Get application statistics
            cursor.execute("""
                SELECT
                    status,
                    COUNT(*) as count,
                    SUM(requested_amount) as total_requested,
                    SUM(approved_amount) as total_approved
                FROM incentive_applications
                WHERE policy_id = ?
                GROUP BY status
            """, (policy_id,))

            policy['status_breakdown'] = cursor.fetchall()

            # Get recent applications
            cursor.execute("""
                SELECT * FROM incentive_applications
                WHERE policy_id = ?
                ORDER BY application_date DESC
                LIMIT 10
            """, (policy_id,))

            policy['recent_applications'] = cursor.fetchall()

            return policy

        finally:
            conn.close()

    def update_policy(self, policy_id: str, update_data: Dict) -> bool:
        """Update policy information"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            set_clauses = []
            params = []

            for key, value in update_data.items():
                set_clauses.append(f"{key} = ?")
                params.append(value)

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            params.append(policy_id)

            query = f"""
                UPDATE local_incentive_policies
                SET {', '.join(set_clauses)}
                WHERE policy_id = ?
            """

            cursor.execute(query, params)
            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()

    # ===================================================================
    # Application Management
    # ===================================================================

    def submit_application(self, application_data: Dict) -> str:
        """Submit a new incentive application"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Verify policy exists and is active
            cursor.execute("""
                SELECT status, remaining_budget FROM local_incentive_policies
                WHERE policy_id = ?
            """, (application_data['policy_id'],))

            policy = cursor.fetchone()

            if not policy:
                raise ValueError("Policy not found")

            if policy[0] != 'active':
                raise ValueError("Policy is not active")

            if policy[1] is not None and policy[1] <= 0:
                raise ValueError("Policy budget exhausted")

            # Create application
            application_id = f"APP-{application_data['policy_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute("""
                INSERT INTO incentive_applications (
                    application_id, policy_id, government_id,
                    applicant_type, applicant_id, applicant_name,
                    applicant_email, applicant_phone, application_date,
                    requested_amount, carbon_reduction_achieved,
                    activities_completed, supporting_documents,
                    recipient_algorand_address, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'submitted')
            """, (
                application_id,
                application_data['policy_id'],
                application_data['government_id'],
                application_data['applicant_type'],
                application_data['applicant_id'],
                application_data['applicant_name'],
                application_data['applicant_email'],
                application_data['applicant_phone'],
                date.today().isoformat(),
                application_data.get('requested_amount'),
                application_data.get('carbon_reduction_achieved'),
                application_data.get('activities_completed'),
                application_data.get('supporting_documents'),
                application_data.get('recipient_algorand_address')
            ))

            conn.commit()
            return application_id

        finally:
            conn.close()

    def get_applications(
        self,
        government_id: Optional[str] = None,
        policy_id: Optional[str] = None,
        applicant_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get applications with filters"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = """
                SELECT
                    ia.*,
                    lip.policy_name,
                    lip.policy_type
                FROM incentive_applications ia
                JOIN local_incentive_policies lip ON ia.policy_id = lip.policy_id
                WHERE 1=1
            """
            params = []

            if government_id:
                query += " AND ia.government_id = ?"
                params.append(government_id)

            if policy_id:
                query += " AND ia.policy_id = ?"
                params.append(policy_id)

            if applicant_id:
                query += " AND ia.applicant_id = ?"
                params.append(applicant_id)

            if status:
                query += " AND ia.status = ?"
                params.append(status)

            query += " ORDER BY ia.application_date DESC"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            conn.close()

    def get_application_detail(self, application_id: str) -> Optional[Dict]:
        """Get detailed application information"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    ia.*,
                    lip.policy_name,
                    lip.policy_type,
                    lip.benefit_amount,
                    lip.benefit_unit,
                    lip.esg_gold_bonus_percentage,
                    lip.review_period_days
                FROM incentive_applications ia
                JOIN local_incentive_policies lip ON ia.policy_id = lip.policy_id
                WHERE ia.application_id = ?
            """, (application_id,))

            return cursor.fetchone()

        finally:
            conn.close()

    def review_application(
        self,
        application_id: str,
        reviewer_id: str,
        decision: str,
        approved_amount: Optional[float] = None,
        review_notes: Optional[str] = None
    ) -> bool:
        """Review and approve/reject an application"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if decision not in ['approved', 'rejected']:
                raise ValueError("Decision must be 'approved' or 'rejected'")

            update_data = {
                'status': decision,
                'reviewer_id': reviewer_id,
                'review_date': date.today().isoformat(),
                'review_notes': review_notes
            }

            if decision == 'approved':
                update_data['approved_amount'] = approved_amount
                update_data['approval_date'] = date.today().isoformat()

            # Update application
            set_clauses = []
            params = []

            for key, value in update_data.items():
                set_clauses.append(f"{key} = ?")
                params.append(value)

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            params.append(application_id)

            query = f"""
                UPDATE incentive_applications
                SET {', '.join(set_clauses)}
                WHERE application_id = ?
            """

            cursor.execute(query, params)
            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()

    def mark_application_paid(
        self,
        application_id: str,
        payment_reference: str,
        blockchain_tx_id: Optional[str] = None
    ) -> bool:
        """Mark an application as paid"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE incentive_applications
                SET status = 'paid',
                    payment_date = ?,
                    payment_reference = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE application_id = ?
                AND status = 'approved'
            """, (date.today().isoformat(), payment_reference, application_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    # ===================================================================
    # Statistics and Reports
    # ===================================================================

    def get_policy_statistics(self, government_id: str) -> Dict:
        """Get policy statistics for a government"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            # Active policies
            cursor.execute("""
                SELECT COUNT(*) as count FROM local_incentive_policies
                WHERE government_id = ? AND status = 'active'
            """, (government_id,))
            active_policies = cursor.fetchone()['count']

            # Total budget
            cursor.execute("""
                SELECT
                    SUM(total_budget) as total_budget,
                    SUM(remaining_budget) as remaining_budget
                FROM local_incentive_policies
                WHERE government_id = ? AND status = 'active'
            """, (government_id,))
            budget = cursor.fetchone()

            # Applications by status
            cursor.execute("""
                SELECT
                    ia.status,
                    COUNT(*) as count,
                    SUM(ia.approved_amount) as total_amount
                FROM incentive_applications ia
                JOIN local_incentive_policies lip ON ia.policy_id = lip.policy_id
                WHERE lip.government_id = ?
                GROUP BY ia.status
            """, (government_id,))
            applications = cursor.fetchall()

            # Recent activity
            cursor.execute("""
                SELECT
                    DATE(ia.application_date) as date,
                    COUNT(*) as application_count
                FROM incentive_applications ia
                JOIN local_incentive_policies lip ON ia.policy_id = lip.policy_id
                WHERE lip.government_id = ?
                AND ia.application_date >= DATE('now', '-30 days')
                GROUP BY DATE(ia.application_date)
                ORDER BY date DESC
            """, (government_id,))
            recent_activity = cursor.fetchall()

            # Policy effectiveness
            cursor.execute("""
                SELECT
                    lip.policy_type,
                    COUNT(ia.application_id) as applications,
                    SUM(CASE WHEN ia.status = 'approved' THEN 1 ELSE 0 END) as approved,
                    SUM(ia.carbon_reduction_achieved) as total_carbon_reduction
                FROM local_incentive_policies lip
                LEFT JOIN incentive_applications ia ON lip.policy_id = ia.policy_id
                WHERE lip.government_id = ?
                GROUP BY lip.policy_type
            """, (government_id,))
            by_policy_type = cursor.fetchall()

            return {
                'active_policies': active_policies,
                'budget': budget,
                'applications_by_status': applications,
                'recent_activity': recent_activity,
                'effectiveness_by_type': by_policy_type
            }

        finally:
            conn.close()

    def get_applicant_history(self, applicant_id: str) -> Dict:
        """Get application history for an applicant"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    ia.*,
                    lip.policy_name,
                    lip.policy_type,
                    lg.government_name
                FROM incentive_applications ia
                JOIN local_incentive_policies lip ON ia.policy_id = lip.policy_id
                JOIN local_governments lg ON ia.government_id = lg.government_id
                WHERE ia.applicant_id = ?
                ORDER BY ia.application_date DESC
            """, (applicant_id,))

            applications = cursor.fetchall()

            # Summary statistics
            cursor.execute("""
                SELECT
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
                    SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid_count,
                    SUM(requested_amount) as total_requested,
                    SUM(approved_amount) as total_approved,
                    SUM(carbon_reduction_achieved) as total_carbon_reduction
                FROM incentive_applications
                WHERE applicant_id = ?
            """, (applicant_id,))

            summary = cursor.fetchone()

            return {
                'applications': applications,
                'summary': summary
            }

        finally:
            conn.close()
