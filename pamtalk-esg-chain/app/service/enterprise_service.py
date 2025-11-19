# -*- coding: utf-8 -*-
"""
Enterprise B2B Service
Handles enterprise ESG purchasing, contracts, and reporting
"""

import sqlite3
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import secrets
import json
from decimal import Decimal


class EnterpriseService:
    """Service for managing enterprise B2B operations"""

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
    # Enterprise Registration & Management
    # ===================================================================

    def register_enterprise(self, enterprise_data: Dict) -> str:
        """Register a new enterprise client"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            enterprise_id = f"ENT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            api_key = secrets.token_urlsafe(32)
            api_secret = secrets.token_urlsafe(48)

            cursor.execute("""
                INSERT INTO enterprises (
                    enterprise_id, company_name, business_registration_number,
                    ceo_name, industry, employee_count, annual_revenue,
                    esg_manager_name, esg_manager_email, esg_manager_phone,
                    api_key, api_secret, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, TRUE, ?)
            """, (
                enterprise_id,
                enterprise_data['company_name'],
                enterprise_data['business_registration_number'],
                enterprise_data['ceo_name'],
                enterprise_data.get('industry'),
                enterprise_data.get('employee_count'),
                enterprise_data.get('annual_revenue'),
                enterprise_data['esg_manager_name'],
                enterprise_data['esg_manager_email'],
                enterprise_data['esg_manager_phone'],
                api_key,
                api_secret,
                datetime.now().isoformat()
            ))

            conn.commit()

            return {
                'enterprise_id': enterprise_id,
                'api_key': api_key,
                'api_secret': api_secret
            }

        finally:
            conn.close()

    def get_enterprise_detail(self, enterprise_id: str) -> Optional[Dict]:
        """Get enterprise details"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM enterprises WHERE enterprise_id = ?
            """, (enterprise_id,))

            return cursor.fetchone()

        finally:
            conn.close()

    def verify_api_credentials(self, api_key: str, api_secret: str) -> Optional[Dict]:
        """Verify API credentials and return enterprise info"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT enterprise_id, company_name, is_active
                FROM enterprises
                WHERE api_key = ? AND api_secret = ? AND is_active = TRUE
            """, (api_key, api_secret))

            return cursor.fetchone()

        finally:
            conn.close()

    # ===================================================================
    # Bulk Purchase Contracts
    # ===================================================================

    def create_contract(self, contract_data: Dict) -> str:
        """Create a new bulk purchase contract"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            contract_id = f"CNT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute("""
                INSERT INTO enterprise_contracts (
                    contract_id, enterprise_id, contract_name, contract_type,
                    supplier_id, contract_amount, contract_period_months,
                    start_date, end_date, delivery_schedule, payment_terms,
                    carbon_reduction_target, special_terms, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?)
            """, (
                contract_id,
                contract_data['enterprise_id'],
                contract_data['contract_name'],
                contract_data['contract_type'],  # single, recurring, framework
                contract_data['supplier_id'],
                contract_data['contract_amount'],
                contract_data.get('contract_period_months', 12),
                contract_data['start_date'],
                contract_data['end_date'],
                contract_data.get('delivery_schedule'),
                contract_data.get('payment_terms'),
                contract_data.get('carbon_reduction_target'),
                contract_data.get('special_terms'),
                datetime.now().isoformat()
            ))

            conn.commit()
            return contract_id

        finally:
            conn.close()

    def get_enterprise_contracts(
        self,
        enterprise_id: str,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get all contracts for an enterprise"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = """
                SELECT
                    c.*,
                    p.producer_name as supplier_name,
                    (SELECT COUNT(*) FROM contract_deliveries WHERE contract_id = c.contract_id) as total_deliveries,
                    (SELECT SUM(delivered_amount) FROM contract_deliveries WHERE contract_id = c.contract_id AND status = 'completed') as delivered_amount
                FROM enterprise_contracts c
                LEFT JOIN local_producers p ON c.supplier_id = p.producer_id
                WHERE c.enterprise_id = ?
            """
            params = [enterprise_id]

            if status:
                query += " AND c.status = ?"
                params.append(status)

            query += " ORDER BY c.created_at DESC"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            conn.close()

    def get_contract_detail(self, contract_id: str) -> Optional[Dict]:
        """Get detailed contract information"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    c.*,
                    p.producer_name as supplier_name,
                    p.contact_person,
                    p.contact_phone,
                    e.company_name as enterprise_name
                FROM enterprise_contracts c
                LEFT JOIN local_producers p ON c.supplier_id = p.producer_id
                LEFT JOIN enterprises e ON c.enterprise_id = e.enterprise_id
                WHERE c.contract_id = ?
            """, (contract_id,))

            contract = cursor.fetchone()

            if not contract:
                return None

            # Get deliveries
            cursor.execute("""
                SELECT * FROM contract_deliveries
                WHERE contract_id = ?
                ORDER BY delivery_date DESC
            """, (contract_id,))

            contract['deliveries'] = cursor.fetchall()

            # Get performance metrics
            cursor.execute("""
                SELECT
                    SUM(delivered_amount) as total_delivered,
                    SUM(carbon_reduction_achieved) as total_carbon_reduction,
                    AVG(quality_rating) as avg_quality_rating
                FROM contract_deliveries
                WHERE contract_id = ? AND status = 'completed'
            """, (contract_id,))

            contract['performance'] = cursor.fetchone()

            return contract

        finally:
            conn.close()

    def update_contract_status(
        self,
        contract_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update contract status"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE enterprise_contracts
                SET status = ?,
                    status_notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE contract_id = ?
            """, (status, notes, contract_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    def record_delivery(self, delivery_data: Dict) -> str:
        """Record a contract delivery"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            delivery_id = f"DEL-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute("""
                INSERT INTO contract_deliveries (
                    delivery_id, contract_id, delivery_date, delivered_amount,
                    delivered_quantity, carbon_reduction_achieved,
                    quality_rating, delivery_notes, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?)
            """, (
                delivery_id,
                delivery_data['contract_id'],
                delivery_data['delivery_date'],
                delivery_data['delivered_amount'],
                delivery_data.get('delivered_quantity'),
                delivery_data.get('carbon_reduction_achieved', 0),
                delivery_data.get('quality_rating'),
                delivery_data.get('delivery_notes'),
                datetime.now().isoformat()
            ))

            conn.commit()
            return delivery_id

        finally:
            conn.close()

    # ===================================================================
    # ESG Reporting
    # ===================================================================

    def generate_esg_report(
        self,
        enterprise_id: str,
        report_period: str,
        report_type: str = 'comprehensive'
    ) -> Dict:
        """Generate ESG report for enterprise"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            # Parse report period
            start_date, end_date = self._parse_report_period(report_period)

            # Get enterprise info
            cursor.execute("""
                SELECT * FROM enterprises WHERE enterprise_id = ?
            """, (enterprise_id,))
            enterprise = cursor.fetchone()

            # Purchase summary
            cursor.execute("""
                SELECT
                    COUNT(DISTINCT c.contract_id) as total_contracts,
                    SUM(c.contract_amount) as total_purchase_amount,
                    COUNT(DISTINCT c.supplier_id) as total_suppliers
                FROM enterprise_contracts c
                WHERE c.enterprise_id = ?
                AND DATE(c.start_date) >= ? AND DATE(c.start_date) <= ?
            """, (enterprise_id, start_date, end_date))
            purchase_summary = cursor.fetchone()

            # Carbon reduction summary
            cursor.execute("""
                SELECT
                    SUM(cd.carbon_reduction_achieved) as total_carbon_reduction,
                    AVG(cd.quality_rating) as avg_quality_rating
                FROM contract_deliveries cd
                JOIN enterprise_contracts c ON cd.contract_id = c.contract_id
                WHERE c.enterprise_id = ?
                AND DATE(cd.delivery_date) >= ? AND DATE(cd.delivery_date) <= ?
            """, (enterprise_id, start_date, end_date))
            carbon_summary = cursor.fetchone()

            # ESG certification breakdown
            cursor.execute("""
                SELECT
                    CASE
                        WHEN p.organic_certified THEN 'organic'
                        WHEN p.gap_certified THEN 'gap'
                        WHEN p.haccp_certified THEN 'haccp'
                        ELSE 'other'
                    END as certification_type,
                    COUNT(DISTINCT c.contract_id) as contract_count,
                    SUM(c.contract_amount) as total_amount
                FROM enterprise_contracts c
                JOIN local_producers p ON c.supplier_id = p.producer_id
                WHERE c.enterprise_id = ?
                AND DATE(c.start_date) >= ? AND DATE(c.start_date) <= ?
                GROUP BY certification_type
            """, (enterprise_id, start_date, end_date))
            certification_breakdown = cursor.fetchall()

            # Generate report
            report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            report = {
                'report_id': report_id,
                'enterprise_id': enterprise_id,
                'company_name': enterprise['company_name'],
                'report_period': report_period,
                'report_type': report_type,
                'generated_at': datetime.now().isoformat(),
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'purchase_summary': {
                    'total_contracts': purchase_summary['total_contracts'] or 0,
                    'total_purchase_amount': purchase_summary['total_purchase_amount'] or 0,
                    'total_suppliers': purchase_summary['total_suppliers'] or 0
                },
                'carbon_impact': {
                    'total_carbon_reduction': carbon_summary['total_carbon_reduction'] or 0,
                    'avg_quality_rating': carbon_summary['avg_quality_rating'] or 0
                },
                'certification_breakdown': certification_breakdown,
                'esg_score': self._calculate_esg_score(
                    purchase_summary,
                    carbon_summary,
                    certification_breakdown
                )
            }

            # Save report
            cursor.execute("""
                INSERT INTO esg_reports (
                    report_id, enterprise_id, report_period, report_type,
                    report_data, generated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                report_id,
                enterprise_id,
                report_period,
                report_type,
                json.dumps(report),
                datetime.now().isoformat()
            ))

            conn.commit()

            return report

        finally:
            conn.close()

    def get_enterprise_reports(
        self,
        enterprise_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get generated reports for enterprise"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM esg_reports
                WHERE enterprise_id = ?
                ORDER BY generated_at DESC
                LIMIT ?
            """, (enterprise_id, limit))

            reports = cursor.fetchall()

            # Parse JSON data
            for report in reports:
                if report['report_data']:
                    report['report_data'] = json.loads(report['report_data'])

            return reports

        finally:
            conn.close()

    # ===================================================================
    # Carbon Reduction Tracking
    # ===================================================================

    def get_carbon_contribution_dashboard(self, enterprise_id: str) -> Dict:
        """Get carbon reduction contribution dashboard data"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            # Overall stats
            cursor.execute("""
                SELECT
                    SUM(cd.carbon_reduction_achieved) as total_carbon_reduction,
                    COUNT(DISTINCT c.contract_id) as active_contracts,
                    COUNT(DISTINCT c.supplier_id) as active_suppliers
                FROM enterprise_contracts c
                LEFT JOIN contract_deliveries cd ON c.contract_id = cd.contract_id
                WHERE c.enterprise_id = ? AND c.status = 'active'
            """, (enterprise_id,))
            overall = cursor.fetchone()

            # Monthly trend (last 12 months)
            cursor.execute("""
                SELECT
                    strftime('%Y-%m', cd.delivery_date) as month,
                    SUM(cd.carbon_reduction_achieved) as carbon_reduction,
                    SUM(cd.delivered_amount) as purchase_amount,
                    COUNT(cd.delivery_id) as delivery_count
                FROM contract_deliveries cd
                JOIN enterprise_contracts c ON cd.contract_id = c.contract_id
                WHERE c.enterprise_id = ?
                AND cd.delivery_date >= DATE('now', '-12 months')
                GROUP BY month
                ORDER BY month DESC
            """, (enterprise_id,))
            monthly_trend = cursor.fetchall()

            # Category breakdown
            cursor.execute("""
                SELECT
                    pp.product_category,
                    SUM(cd.carbon_reduction_achieved) as carbon_reduction,
                    COUNT(cd.delivery_id) as delivery_count
                FROM contract_deliveries cd
                JOIN enterprise_contracts c ON cd.contract_id = c.contract_id
                JOIN producer_products pp ON c.supplier_id = pp.producer_id
                WHERE c.enterprise_id = ?
                GROUP BY pp.product_category
                ORDER BY carbon_reduction DESC
            """, (enterprise_id,))
            category_breakdown = cursor.fetchall()

            # Year-over-year comparison
            current_year = date.today().year
            cursor.execute("""
                SELECT
                    strftime('%Y', cd.delivery_date) as year,
                    SUM(cd.carbon_reduction_achieved) as carbon_reduction
                FROM contract_deliveries cd
                JOIN enterprise_contracts c ON cd.contract_id = c.contract_id
                WHERE c.enterprise_id = ?
                AND strftime('%Y', cd.delivery_date) IN (?, ?)
                GROUP BY year
            """, (enterprise_id, str(current_year), str(current_year - 1)))
            yoy_comparison = cursor.fetchall()

            # Industry ranking (mock - would need industry data)
            industry_rank = 1
            total_companies = 150

            return {
                'overall_stats': overall,
                'monthly_trend': monthly_trend,
                'category_breakdown': category_breakdown,
                'yoy_comparison': yoy_comparison,
                'industry_ranking': {
                    'rank': industry_rank,
                    'total_companies': total_companies,
                    'percentile': round((1 - industry_rank / total_companies) * 100, 1)
                }
            }

        finally:
            conn.close()

    # ===================================================================
    # B2B API Analytics
    # ===================================================================

    def log_api_request(
        self,
        enterprise_id: str,
        endpoint: str,
        method: str,
        response_status: int,
        response_time_ms: float
    ):
        """Log API request for analytics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO api_request_logs (
                    enterprise_id, endpoint, method, response_status,
                    response_time_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                enterprise_id,
                endpoint,
                method,
                response_status,
                response_time_ms,
                datetime.now().isoformat()
            ))

            conn.commit()

        finally:
            conn.close()

    def get_api_usage_stats(
        self,
        enterprise_id: str,
        days: int = 30
    ) -> Dict:
        """Get API usage statistics"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            start_date = (datetime.now() - timedelta(days=days)).date().isoformat()

            cursor.execute("""
                SELECT
                    COUNT(*) as total_requests,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(CASE WHEN response_status = 200 THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as failed_requests
                FROM api_request_logs
                WHERE enterprise_id = ?
                AND DATE(created_at) >= ?
            """, (enterprise_id, start_date))

            overall = cursor.fetchone()

            # Requests by endpoint
            cursor.execute("""
                SELECT
                    endpoint,
                    COUNT(*) as request_count,
                    AVG(response_time_ms) as avg_response_time
                FROM api_request_logs
                WHERE enterprise_id = ?
                AND DATE(created_at) >= ?
                GROUP BY endpoint
                ORDER BY request_count DESC
            """, (enterprise_id, start_date))

            by_endpoint = cursor.fetchall()

            return {
                'overall': overall,
                'by_endpoint': by_endpoint
            }

        finally:
            conn.close()

    # ===================================================================
    # Helper Methods
    # ===================================================================

    def _parse_report_period(self, report_period: str) -> tuple:
        """Parse report period string to start and end dates"""
        # Examples: "2024-11", "2024-Q3", "2024"
        today = date.today()

        if '-' in report_period:  # Monthly: "2024-11"
            year, month = report_period.split('-')
            start_date = date(int(year), int(month), 1)
            if int(month) == 12:
                end_date = date(int(year) + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(int(year), int(month) + 1, 1) - timedelta(days=1)
        elif 'Q' in report_period:  # Quarterly: "2024-Q3"
            year, quarter = report_period.split('-Q')
            quarter = int(quarter)
            start_month = (quarter - 1) * 3 + 1
            start_date = date(int(year), start_month, 1)
            end_month = start_month + 2
            if end_month == 12:
                end_date = date(int(year), 12, 31)
            else:
                end_date = date(int(year), end_month + 1, 1) - timedelta(days=1)
        else:  # Yearly: "2024"
            start_date = date(int(report_period), 1, 1)
            end_date = date(int(report_period), 12, 31)

        return start_date.isoformat(), end_date.isoformat()

    def _calculate_esg_score(
        self,
        purchase_summary: Dict,
        carbon_summary: Dict,
        certification_breakdown: List[Dict]
    ) -> Dict:
        """Calculate ESG score based on multiple factors"""
        # Purchase volume score (0-30)
        purchase_amount = purchase_summary.get('total_purchase_amount') or 0
        purchase_score = min(30, (purchase_amount / 100000000) * 10)  # 1억당 10점

        # Carbon reduction score (0-40)
        carbon_reduction = carbon_summary.get('total_carbon_reduction') or 0
        carbon_score = min(40, (carbon_reduction / 100) * 10)  # 100톤당 10점

        # Certification diversity score (0-30)
        cert_count = len(certification_breakdown)
        cert_score = min(30, cert_count * 10)

        total_score = purchase_score + carbon_score + cert_score

        # Grade based on total score
        if total_score >= 90:
            grade = 'A+'
        elif total_score >= 80:
            grade = 'A'
        elif total_score >= 70:
            grade = 'B+'
        elif total_score >= 60:
            grade = 'B'
        else:
            grade = 'C'

        return {
            'total_score': round(total_score, 1),
            'grade': grade,
            'breakdown': {
                'purchase_score': round(purchase_score, 1),
                'carbon_score': round(carbon_score, 1),
                'certification_score': round(cert_score, 1)
            }
        }

    def regenerate_api_key(self, enterprise_id: str) -> Dict:
        """Regenerate API key for enterprise"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            new_api_key = secrets.token_urlsafe(32)
            new_api_secret = secrets.token_urlsafe(48)

            cursor.execute("""
                UPDATE enterprises
                SET api_key = ?,
                    api_secret = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE enterprise_id = ?
            """, (new_api_key, new_api_secret, enterprise_id))

            conn.commit()

            return {
                'api_key': new_api_key,
                'api_secret': new_api_secret
            }

        finally:
            conn.close()
