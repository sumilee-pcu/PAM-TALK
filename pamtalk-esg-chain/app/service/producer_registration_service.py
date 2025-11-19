"""
Producer Registration Service
Handles registration and verification of agricultural and fisheries producers
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import json


class ProducerRegistrationService:
    """Service for managing local producer registration"""

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
    # Producer Registration
    # ===================================================================

    def register_producer(self, producer_data: Dict) -> str:
        """Register a new producer"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            producer_id = f"PROD-{producer_data['government_id']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute("""
                INSERT INTO local_producers (
                    producer_id, government_id, producer_name, producer_type,
                    business_registration_number, contact_person, contact_phone,
                    contact_email, farm_address, farm_latitude, farm_longitude,
                    farm_area_sqm, organic_certified, gap_certified, haccp_certified,
                    other_certifications, verification_status, algorand_address,
                    is_active, registration_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, TRUE, ?)
            """, (
                producer_id,
                producer_data['government_id'],
                producer_data['producer_name'],
                producer_data['producer_type'],
                producer_data.get('business_registration_number'),
                producer_data['contact_person'],
                producer_data['contact_phone'],
                producer_data.get('contact_email'),
                producer_data['farm_address'],
                producer_data.get('farm_latitude'),
                producer_data.get('farm_longitude'),
                producer_data.get('farm_area_sqm'),
                producer_data.get('organic_certified', False),
                producer_data.get('gap_certified', False),
                producer_data.get('haccp_certified', False),
                producer_data.get('other_certifications'),
                producer_data.get('algorand_address'),
                date.today().isoformat()
            ))

            conn.commit()
            return producer_id

        finally:
            conn.close()

    def get_producers(
        self,
        government_id: Optional[str] = None,
        producer_type: Optional[str] = None,
        verification_status: Optional[str] = None,
        organic_only: bool = False
    ) -> List[Dict]:
        """Get producers with filters"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM v_producer_directory WHERE 1=1"
            params = []

            if government_id:
                query += " AND government_id = ?"
                params.append(government_id)

            if producer_type:
                query += " AND producer_type = ?"
                params.append(producer_type)

            if verification_status:
                query += " AND verification_status = ?"
                params.append(verification_status)

            if organic_only:
                query += " AND organic_certified = TRUE"

            query += " ORDER BY producer_name"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            conn.close()

    def get_producer_detail(self, producer_id: str) -> Optional[Dict]:
        """Get detailed producer information"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM local_producers WHERE producer_id = ?
            """, (producer_id,))

            producer = cursor.fetchone()

            if not producer:
                return None

            # Get products
            cursor.execute("""
                SELECT * FROM producer_products
                WHERE producer_id = ?
                ORDER BY is_available DESC, product_name
            """, (producer_id,))

            producer['products'] = cursor.fetchall()

            # Get verification documents
            cursor.execute("""
                SELECT * FROM producer_verification_documents
                WHERE producer_id = ?
                ORDER BY uploaded_at DESC
            """, (producer_id,))

            producer['verification_documents'] = cursor.fetchall()

            return producer

        finally:
            conn.close()

    def verify_producer(
        self,
        producer_id: str,
        verifier_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """Verify or reject a producer registration"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE local_producers
                SET verification_status = ?,
                    verified_by = ?,
                    verified_at = CURRENT_TIMESTAMP,
                    verification_notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE producer_id = ?
            """, (status, verifier_id, notes, producer_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    def upload_verification_document(
        self,
        producer_id: str,
        document_data: Dict
    ) -> int:
        """Upload a verification document"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO producer_verification_documents (
                    producer_id, document_type, document_name,
                    file_url, file_type, file_size
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                producer_id,
                document_data['document_type'],
                document_data['document_name'],
                document_data['file_url'],
                document_data.get('file_type'),
                document_data.get('file_size')
            ))

            conn.commit()
            return cursor.lastrowid

        finally:
            conn.close()

    # ===================================================================
    # Producer Products
    # ===================================================================

    def add_product(self, product_data: Dict) -> str:
        """Add a product for a producer"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            product_id = f"PROD-ITEM-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            cursor.execute("""
                INSERT INTO producer_products (
                    product_id, producer_id, product_name, product_category,
                    product_type, description, harvest_season, production_method,
                    unit_type, unit_price, minimum_order, carbon_footprint_per_unit,
                    is_available, stock_quantity, product_image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                product_data['producer_id'],
                product_data['product_name'],
                product_data['product_category'],
                product_data.get('product_type'),
                product_data.get('description'),
                product_data.get('harvest_season'),
                product_data.get('production_method'),
                product_data['unit_type'],
                product_data.get('unit_price'),
                product_data.get('minimum_order'),
                product_data.get('carbon_footprint_per_unit'),
                product_data.get('is_available', True),
                product_data.get('stock_quantity'),
                product_data.get('product_image_url')
            ))

            conn.commit()
            return product_id

        finally:
            conn.close()

    def update_product(self, product_id: str, update_data: Dict) -> bool:
        """Update product information"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            set_clauses = []
            params = []

            for key, value in update_data.items():
                set_clauses.append(f"{key} = ?")
                params.append(value)

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            params.append(product_id)

            query = f"""
                UPDATE producer_products
                SET {', '.join(set_clauses)}
                WHERE product_id = ?
            """

            cursor.execute(query, params)
            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()

    def search_products(
        self,
        government_id: Optional[str] = None,
        product_category: Optional[str] = None,
        product_type: Optional[str] = None,
        organic_only: bool = False,
        available_only: bool = True
    ) -> List[Dict]:
        """Search for products"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            query = """
                SELECT
                    pp.*,
                    lp.producer_name,
                    lp.government_id,
                    lp.farm_address,
                    lp.organic_certified,
                    lp.gap_certified,
                    lp.verification_status
                FROM producer_products pp
                JOIN local_producers lp ON pp.producer_id = lp.producer_id
                WHERE lp.is_active = TRUE
            """
            params = []

            if government_id:
                query += " AND lp.government_id = ?"
                params.append(government_id)

            if product_category:
                query += " AND pp.product_category = ?"
                params.append(product_category)

            if product_type:
                query += " AND pp.product_type = ?"
                params.append(product_type)

            if organic_only:
                query += " AND lp.organic_certified = TRUE"

            if available_only:
                query += " AND pp.is_available = TRUE"

            query += " ORDER BY pp.product_name"

            cursor.execute(query, params)
            return cursor.fetchall()

        finally:
            conn.close()

    # ===================================================================
    # Statistics
    # ===================================================================

    def get_producer_statistics(self, government_id: str) -> Dict:
        """Get producer statistics for a government"""
        conn = self._get_connection()
        conn.row_factory = self._dict_factory
        cursor = conn.cursor()

        try:
            # Total producers
            cursor.execute("""
                SELECT COUNT(*) as total FROM local_producers
                WHERE government_id = ? AND is_active = TRUE
            """, (government_id,))
            total = cursor.fetchone()['total']

            # Verified producers
            cursor.execute("""
                SELECT COUNT(*) as verified FROM local_producers
                WHERE government_id = ? AND verification_status = 'verified'
            """, (government_id,))
            verified = cursor.fetchone()['verified']

            # By producer type
            cursor.execute("""
                SELECT producer_type, COUNT(*) as count
                FROM local_producers
                WHERE government_id = ? AND is_active = TRUE
                GROUP BY producer_type
            """, (government_id,))
            by_type = cursor.fetchall()

            # Certified producers
            cursor.execute("""
                SELECT
                    SUM(CASE WHEN organic_certified THEN 1 ELSE 0 END) as organic,
                    SUM(CASE WHEN gap_certified THEN 1 ELSE 0 END) as gap,
                    SUM(CASE WHEN haccp_certified THEN 1 ELSE 0 END) as haccp
                FROM local_producers
                WHERE government_id = ? AND is_active = TRUE
            """, (government_id,))
            certifications = cursor.fetchone()

            # Total products
            cursor.execute("""
                SELECT COUNT(*) as total_products
                FROM producer_products pp
                JOIN local_producers lp ON pp.producer_id = lp.producer_id
                WHERE lp.government_id = ? AND pp.is_available = TRUE
            """, (government_id,))
            products = cursor.fetchone()['total_products']

            return {
                'total_producers': total,
                'verified_producers': verified,
                'pending_verification': total - verified,
                'by_producer_type': by_type,
                'certifications': certifications,
                'total_available_products': products
            }

        finally:
            conn.close()
