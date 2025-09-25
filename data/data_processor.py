#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Integrated Data Processing System

This module provides comprehensive data processing capabilities that integrate
AI models, blockchain operations, and data management for the PAM-TALK platform.
"""

import os
import json
import shutil
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import logging
import zipfile
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FarmInfo:
    """Farm information data structure"""
    farm_id: str
    farm_name: str
    owner_name: str
    location: str
    size_hectares: float
    established_date: str
    contact_info: Dict
    certifications: List[str]
    products: List[str]
    esg_data: Dict
    blockchain_address: str
    status: str  # active, inactive, suspended
    created_at: str
    updated_at: str

@dataclass
class ProcessingResult:
    """Data processing result structure"""
    process_date: str
    farms_processed: int
    predictions_generated: int
    esg_scores_updated: int
    anomalies_detected: int
    blockchain_records: int
    processing_time_seconds: float
    errors: List[str]
    summary: Dict

class DataProcessor:
    """
    Integrated Data Processing System for PAM-TALK Platform
    """

    def __init__(self, base_data_path: str = "data"):
        self.base_path = base_data_path
        self.setup_directories()

        # Data file paths
        self.farms_file = os.path.join(self.base_path, "farms", "farms_registry.json")
        self.transactions_file = os.path.join(self.base_path, "transactions", "transaction_history.json")
        self.daily_reports_path = os.path.join(self.base_path, "daily_reports")
        self.backups_path = os.path.join(self.base_path, "backups")

        # Initialize AI models
        self.demand_predictor = None
        self.esg_calculator = None
        self.anomaly_detector = None
        self.smart_contract = None

        # Processing configuration
        self.config = {
            'prediction_days': 7,
            'esg_update_threshold_days': 30,
            'anomaly_check_enabled': True,
            'backup_retention_days': 30,
            'batch_size': 100
        }

    def setup_directories(self):
        """Create necessary directory structure"""
        directories = [
            self.base_path,
            os.path.join(self.base_path, "farms"),
            os.path.join(self.base_path, "transactions"),
            os.path.join(self.base_path, "daily_reports"),
            os.path.join(self.base_path, "backups"),
            os.path.join(self.base_path, "ai_results"),
            os.path.join(self.base_path, "blockchain_sync"),
            os.path.join(self.base_path, "logs")
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def initialize_models(self):
        """Initialize AI models and blockchain connection"""
        try:
            # Import AI models
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            from ai_models.demand_predictor import DemandPredictor
            from ai_models.esg_calculator import ESGCalculator
            from ai_models.anomaly_detector import AnomalyDetector
            from contracts.pam_talk_contract import pam_talk_contract

            self.demand_predictor = DemandPredictor()
            self.esg_calculator = ESGCalculator()
            self.anomaly_detector = AnomalyDetector()
            self.smart_contract = pam_talk_contract

            logger.info("All AI models and blockchain connection initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            return False

    def load_farms_registry(self) -> Dict[str, FarmInfo]:
        """Load farms registry from JSON file"""
        if os.path.exists(self.farms_file):
            try:
                with open(self.farms_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                farms = {}
                for farm_id, farm_data in data.items():
                    farms[farm_id] = FarmInfo(**farm_data)

                return farms
            except Exception as e:
                logger.error(f"Failed to load farms registry: {e}")
                return {}
        else:
            return {}

    def save_farms_registry(self, farms: Dict[str, FarmInfo]):
        """Save farms registry to JSON file"""
        try:
            data = {}
            for farm_id, farm_info in farms.items():
                data[farm_id] = asdict(farm_info)

            with open(self.farms_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Farms registry saved with {len(farms)} farms")

        except Exception as e:
            logger.error(f"Failed to save farms registry: {e}")

    def register_farm(self, farm_info: Union[FarmInfo, Dict]) -> bool:
        """Register a new farm"""
        try:
            if isinstance(farm_info, dict):
                farm_info = FarmInfo(**farm_info)

            farms = self.load_farms_registry()

            # Check if farm already exists
            if farm_info.farm_id in farms:
                logger.warning(f"Farm {farm_info.farm_id} already exists")
                return False

            # Add timestamps
            farm_info.created_at = datetime.now().isoformat()
            farm_info.updated_at = datetime.now().isoformat()

            farms[farm_info.farm_id] = farm_info
            self.save_farms_registry(farms)

            logger.info(f"Farm {farm_info.farm_id} registered successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to register farm: {e}")
            return False

    def update_farm_info(self, farm_id: str, updates: Dict) -> bool:
        """Update farm information"""
        try:
            farms = self.load_farms_registry()

            if farm_id not in farms:
                logger.error(f"Farm {farm_id} not found")
                return False

            # Update fields
            for key, value in updates.items():
                if hasattr(farms[farm_id], key):
                    setattr(farms[farm_id], key, value)

            farms[farm_id].updated_at = datetime.now().isoformat()

            self.save_farms_registry(farms)
            logger.info(f"Farm {farm_id} updated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to update farm {farm_id}: {e}")
            return False

    def load_transaction_history(self) -> List[Dict]:
        """Load transaction history from JSON file"""
        if os.path.exists(self.transactions_file):
            try:
                with open(self.transactions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load transaction history: {e}")
                return []
        else:
            return []

    def save_transaction_history(self, transactions: List[Dict]):
        """Save transaction history to JSON file"""
        try:
            with open(self.transactions_file, 'w', encoding='utf-8') as f:
                json.dump(transactions, f, indent=2, default=str)

            logger.info(f"Transaction history saved with {len(transactions)} transactions")

        except Exception as e:
            logger.error(f"Failed to save transaction history: {e}")

    def add_transaction(self, transaction: Dict) -> bool:
        """Add a new transaction to history"""
        try:
            transactions = self.load_transaction_history()

            # Add timestamp and ID if not present
            if 'transaction_id' not in transaction:
                transaction['transaction_id'] = f"TXN_{int(datetime.now().timestamp())}"

            if 'timestamp' not in transaction:
                transaction['timestamp'] = datetime.now().isoformat()

            transactions.append(transaction)
            self.save_transaction_history(transactions)

            logger.info(f"Transaction {transaction['transaction_id']} added")
            return True

        except Exception as e:
            logger.error(f"Failed to add transaction: {e}")
            return False

    def get_transactions(self, farm_id: Optional[str] = None,
                        product_type: Optional[str] = None,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        limit: int = 1000) -> List[Dict]:
        """Get filtered transaction history"""
        transactions = self.load_transaction_history()

        # Apply filters
        if farm_id:
            transactions = [t for t in transactions
                          if t.get('producer_id') == farm_id or t.get('consumer_id') == farm_id]

        if product_type:
            transactions = [t for t in transactions if t.get('product_type') == product_type]

        if start_date:
            transactions = [t for t in transactions
                          if t.get('timestamp', '') >= start_date]

        if end_date:
            transactions = [t for t in transactions
                          if t.get('timestamp', '') <= end_date]

        # Sort by timestamp (newest first) and limit
        transactions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return transactions[:limit]

    def sync_with_blockchain(self) -> Dict:
        """Synchronize local data with blockchain records"""
        if not self.smart_contract:
            return {'success': False, 'error': 'Blockchain not initialized'}

        try:
            sync_result = {
                'agriculture_records_synced': 0,
                'demand_predictions_synced': 0,
                'new_transactions_added': 0,
                'errors': []
            }

            # Get blockchain agriculture records
            blockchain_records = self.smart_contract.get_agriculture_records(limit=500)
            local_transactions = self.load_transaction_history()

            # Get existing transaction IDs
            existing_ids = {t.get('record_id') or t.get('transaction_id') for t in local_transactions}

            # Sync new blockchain records to local storage
            for record in blockchain_records:
                if record['record_id'] not in existing_ids:
                    local_transaction = {
                        'transaction_id': record['record_id'],
                        'record_id': record['record_id'],
                        'producer_id': record['producer'],
                        'consumer_id': record['consumer'],
                        'product_type': record['product_type'],
                        'quantity': record['quantity'],
                        'price_per_unit': record['price_per_unit'],
                        'total_value': record['total_value'],
                        'quality_score': record['quality_score'],
                        'esg_score': record['esg_score'],
                        'location': record['location'],
                        'timestamp': datetime.fromtimestamp(record['timestamp']).isoformat(),
                        'source': 'blockchain',
                        'metadata': record.get('metadata', {})
                    }

                    local_transactions.append(local_transaction)
                    sync_result['agriculture_records_synced'] += 1

            # Save updated transactions
            if sync_result['agriculture_records_synced'] > 0:
                self.save_transaction_history(local_transactions)

            # Get blockchain demand predictions
            predictions = self.smart_contract.get_demand_predictions(limit=100)
            sync_result['demand_predictions_synced'] = len(predictions)

            # Save predictions to local storage
            predictions_file = os.path.join(self.base_path, "ai_results", "blockchain_predictions.json")
            with open(predictions_file, 'w') as f:
                json.dump(predictions, f, indent=2, default=str)

            logger.info(f"Blockchain sync completed: {sync_result}")
            return {'success': True, 'result': sync_result}

        except Exception as e:
            logger.error(f"Blockchain sync failed: {e}")
            return {'success': False, 'error': str(e)}

    def generate_demand_predictions(self, farms: Dict[str, FarmInfo]) -> Dict:
        """Generate demand predictions for all farm products"""
        if not self.demand_predictor:
            return {'success': False, 'error': 'Demand predictor not initialized'}

        try:
            predictions_result = {
                'predictions_generated': 0,
                'products_analyzed': set(),
                'total_predicted_demand': 0,
                'predictions': {},
                'errors': []
            }

            # Get unique products from farms
            all_products = set()
            for farm in farms.values():
                all_products.update(farm.products)

            # Generate predictions for each product
            for product in all_products:
                try:
                    prediction = self.demand_predictor.predict_demand(
                        product, days=self.config['prediction_days']
                    )

                    predictions_result['predictions'][product] = prediction
                    predictions_result['predictions_generated'] += 1
                    predictions_result['products_analyzed'].add(product)
                    predictions_result['total_predicted_demand'] += prediction['total_predicted_demand']

                    # Store in blockchain
                    if self.smart_contract:
                        prediction_id = self.smart_contract.store_demand_prediction(
                            product_type=product,
                            predicted_demand=prediction['total_predicted_demand'],
                            confidence_score=prediction['accuracy_metrics']['confidence_score'],
                            prediction_period=f"{self.config['prediction_days']}_days",
                            created_by="DATA_PROCESSOR",
                            features_used=['historical_data', 'seasonality', 'market_trends'],
                            metadata={
                                'mae': prediction['accuracy_metrics']['mae'],
                                'mape': prediction['accuracy_metrics']['mape'],
                                'model': 'prophet'
                            }
                        )

                        logger.info(f"Prediction for {product} stored in blockchain: {prediction_id}")

                except Exception as e:
                    logger.error(f"Failed to generate prediction for {product}: {e}")
                    predictions_result['errors'].append(f"{product}: {str(e)}")

            # Save predictions locally
            predictions_file = os.path.join(self.base_path, "ai_results",
                                          f"demand_predictions_{datetime.now().strftime('%Y%m%d')}.json")
            with open(predictions_file, 'w') as f:
                json.dump(predictions_result, f, indent=2, default=str)

            return {'success': True, 'result': predictions_result}

        except Exception as e:
            logger.error(f"Demand prediction generation failed: {e}")
            return {'success': False, 'error': str(e)}

    def update_esg_scores(self, farms: Dict[str, FarmInfo]) -> Dict:
        """Update ESG scores for all farms"""
        if not self.esg_calculator:
            return {'success': False, 'error': 'ESG calculator not initialized'}

        try:
            esg_result = {
                'farms_processed': 0,
                'scores_updated': 0,
                'total_esg_tokens': 0,
                'esg_scores': {},
                'errors': []
            }

            for farm_id, farm_info in farms.items():
                try:
                    # Convert farm info to ESG calculator format
                    from ai_models.esg_calculator import FarmData

                    farm_data = FarmData(
                        farm_id=farm_id,
                        farm_name=farm_info.farm_name,
                        location=farm_info.location,
                        size_hectares=farm_info.size_hectares,

                        # Environmental data from farm ESG data
                        organic_certified=farm_info.esg_data.get('organic_certified', False),
                        water_usage_per_hectare=farm_info.esg_data.get('water_usage_per_hectare', 10000),
                        carbon_emissions=farm_info.esg_data.get('carbon_emissions', 5.0),
                        renewable_energy_percentage=farm_info.esg_data.get('renewable_energy_percentage', 20.0),
                        biodiversity_score=farm_info.esg_data.get('biodiversity_score', 6),
                        soil_health_score=farm_info.esg_data.get('soil_health_score', 6),
                        waste_management_score=farm_info.esg_data.get('waste_management_score', 6),

                        # Social data
                        fair_wage_certification=farm_info.esg_data.get('fair_wage_certification', False),
                        community_investment_percentage=farm_info.esg_data.get('community_investment_percentage', 1.0),
                        worker_safety_score=farm_info.esg_data.get('worker_safety_score', 6),
                        local_employment_percentage=farm_info.esg_data.get('local_employment_percentage', 70.0),
                        training_programs=farm_info.esg_data.get('training_programs', False),
                        healthcare_provided=farm_info.esg_data.get('healthcare_provided', False),

                        # Governance data
                        transparency_score=farm_info.esg_data.get('transparency_score', 6),
                        certifications=farm_info.certifications,
                        record_keeping_score=farm_info.esg_data.get('record_keeping_score', 6),
                        stakeholder_engagement_score=farm_info.esg_data.get('stakeholder_engagement_score', 6),
                        ethical_practices_score=farm_info.esg_data.get('ethical_practices_score', 6),
                        supply_chain_traceability=farm_info.esg_data.get('supply_chain_traceability', False)
                    )

                    # Calculate ESG score
                    esg_score = self.esg_calculator.calculate_score(farm_data)

                    esg_result['esg_scores'][farm_id] = {
                        'overall_score': esg_score.overall_score,
                        'environmental_score': esg_score.environmental_score,
                        'social_score': esg_score.social_score,
                        'governance_score': esg_score.governance_score,
                        'certification_level': esg_score.certification_level,
                        'esg_gold_tokens': esg_score.esg_gold_tokens,
                        'calculated_at': esg_score.calculated_at
                    }

                    esg_result['farms_processed'] += 1
                    esg_result['scores_updated'] += 1
                    esg_result['total_esg_tokens'] += esg_score.esg_gold_tokens

                    # Update farm with new ESG data
                    farms[farm_id].esg_data['last_esg_score'] = esg_score.overall_score
                    farms[farm_id].esg_data['last_esg_update'] = datetime.now().isoformat()
                    farms[farm_id].updated_at = datetime.now().isoformat()

                except Exception as e:
                    logger.error(f"Failed to calculate ESG score for {farm_id}: {e}")
                    esg_result['errors'].append(f"{farm_id}: {str(e)}")

            # Save updated farms
            self.save_farms_registry(farms)

            # Save ESG results
            esg_file = os.path.join(self.base_path, "ai_results",
                                  f"esg_scores_{datetime.now().strftime('%Y%m%d')}.json")
            with open(esg_file, 'w') as f:
                json.dump(esg_result, f, indent=2, default=str)

            return {'success': True, 'result': esg_result}

        except Exception as e:
            logger.error(f"ESG score update failed: {e}")
            return {'success': False, 'error': str(e)}

    def check_transaction_anomalies(self) -> Dict:
        """Check recent transactions for anomalies"""
        if not self.anomaly_detector:
            return {'success': False, 'error': 'Anomaly detector not initialized'}

        try:
            # Get recent transactions (last 7 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            recent_transactions = self.get_transactions(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                limit=500
            )

            if not recent_transactions:
                return {'success': True, 'result': {'anomalies_detected': 0, 'message': 'No recent transactions'}}

            # Prepare historical data for anomaly detection
            historical_transactions = self.get_transactions(limit=2000)
            historical_df = pd.DataFrame(historical_transactions)

            if len(historical_df) < 100:
                # Generate simulation data if not enough historical data
                historical_df = self.anomaly_detector.generate_simulation_data(1000)

            # Train anomaly detector
            if not self.anomaly_detector.is_trained:
                normal_data = historical_df[~historical_df.get('is_anomaly', False)] if 'is_anomaly' in historical_df.columns else historical_df
                self.anomaly_detector.train_isolation_forest(normal_data)

            # Check recent transactions for anomalies
            anomalies_result = {
                'transactions_checked': len(recent_transactions),
                'anomalies_detected': 0,
                'high_risk_transactions': 0,
                'anomalous_transactions': [],
                'errors': []
            }

            for transaction in recent_transactions:
                try:
                    # Convert to anomaly detector format
                    from ai_models.anomaly_detector import TransactionData

                    transaction_data = TransactionData(
                        transaction_id=transaction.get('transaction_id', 'UNKNOWN'),
                        timestamp=transaction.get('timestamp', datetime.now().isoformat()),
                        producer_id=transaction.get('producer_id', 'UNKNOWN'),
                        consumer_id=transaction.get('consumer_id', 'UNKNOWN'),
                        product_type=transaction.get('product_type', 'unknown'),
                        quantity=float(transaction.get('quantity', 0)),
                        price_per_unit=float(transaction.get('price_per_unit', 0)),
                        total_value=float(transaction.get('total_value', 0)),
                        location=transaction.get('location', 'unknown'),
                        quality_score=int(transaction.get('quality_score', 70)),
                        esg_score=int(transaction.get('esg_score', 70)),
                        payment_method=transaction.get('payment_method', 'PAMT_TRANSFER'),
                        delivery_time_hours=float(transaction.get('delivery_time_hours', 48)),
                        producer_reputation=float(transaction.get('producer_reputation', 0.8)),
                        consumer_reputation=float(transaction.get('consumer_reputation', 0.8)),
                        season_factor=float(transaction.get('season_factor', 1.0)),
                        market_volatility=float(transaction.get('market_volatility', 0.2))
                    )

                    # Detect anomaly
                    result = self.anomaly_detector.detect_anomaly(transaction_data, historical_df)

                    if result.is_anomaly:
                        anomalies_result['anomalies_detected'] += 1

                        if result.risk_level in ['HIGH', 'CRITICAL']:
                            anomalies_result['high_risk_transactions'] += 1

                        anomalies_result['anomalous_transactions'].append({
                            'transaction_id': result.transaction_id,
                            'risk_level': result.risk_level,
                            'anomaly_score': result.anomaly_score,
                            'anomaly_types': result.anomaly_types,
                            'recommendations': result.recommendations[:2]  # Top 2 recommendations
                        })

                except Exception as e:
                    logger.error(f"Failed to check transaction for anomalies: {e}")
                    anomalies_result['errors'].append(str(e))

            # Save anomaly results
            anomaly_file = os.path.join(self.base_path, "ai_results",
                                      f"anomaly_check_{datetime.now().strftime('%Y%m%d')}.json")
            with open(anomaly_file, 'w') as f:
                json.dump(anomalies_result, f, indent=2, default=str)

            return {'success': True, 'result': anomalies_result}

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {'success': False, 'error': str(e)}

    def process_daily_data(self) -> ProcessingResult:
        """
        Main method to process daily data - runs all AI models and updates blockchain
        """
        start_time = datetime.now()
        logger.info("Starting daily data processing...")

        # Initialize models
        if not self.initialize_models():
            return ProcessingResult(
                process_date=start_time.isoformat(),
                farms_processed=0,
                predictions_generated=0,
                esg_scores_updated=0,
                anomalies_detected=0,
                blockchain_records=0,
                processing_time_seconds=0,
                errors=["Failed to initialize AI models"],
                summary={"status": "failed"}
            )

        errors = []
        farms_processed = 0
        predictions_generated = 0
        esg_scores_updated = 0
        anomalies_detected = 0
        blockchain_records = 0

        try:
            # 1. Load farm data
            logger.info("Loading farms registry...")
            farms = self.load_farms_registry()
            farms_processed = len(farms)
            logger.info(f"Loaded {farms_processed} farms")

            # 2. Sync with blockchain
            logger.info("Syncing with blockchain...")
            sync_result = self.sync_with_blockchain()
            if sync_result['success']:
                blockchain_records = sync_result['result']['agriculture_records_synced']
                logger.info(f"Synced {blockchain_records} blockchain records")
            else:
                errors.append(f"Blockchain sync failed: {sync_result['error']}")

            # 3. Generate demand predictions
            logger.info("Generating demand predictions...")
            prediction_result = self.generate_demand_predictions(farms)
            if prediction_result['success']:
                predictions_generated = prediction_result['result']['predictions_generated']
                logger.info(f"Generated {predictions_generated} demand predictions")
            else:
                errors.append(f"Demand prediction failed: {prediction_result['error']}")

            # 4. Update ESG scores
            logger.info("Updating ESG scores...")
            esg_result = self.update_esg_scores(farms)
            if esg_result['success']:
                esg_scores_updated = esg_result['result']['scores_updated']
                logger.info(f"Updated {esg_scores_updated} ESG scores")
            else:
                errors.append(f"ESG update failed: {esg_result['error']}")

            # 5. Check for transaction anomalies
            logger.info("Checking for transaction anomalies...")
            anomaly_result = self.check_transaction_anomalies()
            if anomaly_result['success']:
                anomalies_detected = anomaly_result['result']['anomalies_detected']
                logger.info(f"Detected {anomalies_detected} anomalies")
            else:
                errors.append(f"Anomaly detection failed: {anomaly_result['error']}")

            # 6. Create daily backup
            logger.info("Creating daily backup...")
            backup_result = self.create_backup()
            if not backup_result['success']:
                errors.append(f"Backup failed: {backup_result['error']}")

            # 7. Generate daily report
            processing_time = (datetime.now() - start_time).total_seconds()

            summary = {
                "status": "completed" if not errors else "completed_with_errors",
                "farms_processed": farms_processed,
                "predictions_generated": predictions_generated,
                "esg_scores_updated": esg_scores_updated,
                "anomalies_detected": anomalies_detected,
                "blockchain_records_synced": blockchain_records,
                "processing_time_minutes": round(processing_time / 60, 2),
                "total_predicted_demand": prediction_result.get('result', {}).get('total_predicted_demand', 0) if prediction_result.get('success') else 0,
                "total_esg_tokens": esg_result.get('result', {}).get('total_esg_tokens', 0) if esg_result.get('success') else 0
            }

            result = ProcessingResult(
                process_date=start_time.isoformat(),
                farms_processed=farms_processed,
                predictions_generated=predictions_generated,
                esg_scores_updated=esg_scores_updated,
                anomalies_detected=anomalies_detected,
                blockchain_records=blockchain_records,
                processing_time_seconds=processing_time,
                errors=errors,
                summary=summary
            )

            # Save daily report
            self.save_daily_report(result)

            logger.info(f"Daily processing completed in {processing_time:.2f} seconds")
            logger.info(f"Summary: {summary}")

            return result

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Daily processing failed: {e}")

            return ProcessingResult(
                process_date=start_time.isoformat(),
                farms_processed=farms_processed,
                predictions_generated=predictions_generated,
                esg_scores_updated=esg_scores_updated,
                anomalies_detected=anomalies_detected,
                blockchain_records=blockchain_records,
                processing_time_seconds=processing_time,
                errors=errors + [str(e)],
                summary={"status": "failed", "error": str(e)}
            )

    def save_daily_report(self, result: ProcessingResult):
        """Save daily processing report"""
        try:
            report_date = datetime.fromisoformat(result.process_date).strftime('%Y%m%d')
            report_file = os.path.join(self.daily_reports_path, f"daily_report_{report_date}.json")

            with open(report_file, 'w') as f:
                json.dump(asdict(result), f, indent=2, default=str)

            logger.info(f"Daily report saved: {report_file}")

        except Exception as e:
            logger.error(f"Failed to save daily report: {e}")

    def create_backup(self) -> Dict:
        """Create backup of all data files"""
        try:
            backup_date = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(self.backups_path, f"backup_{backup_date}")

            # Create backup directory
            os.makedirs(backup_dir, exist_ok=True)

            # Files to backup
            backup_files = [
                (self.farms_file, "farms_registry.json"),
                (self.transactions_file, "transaction_history.json")
            ]

            # Copy data files
            for src_file, dst_name in backup_files:
                if os.path.exists(src_file):
                    shutil.copy2(src_file, os.path.join(backup_dir, dst_name))

            # Copy AI results directory
            ai_results_src = os.path.join(self.base_path, "ai_results")
            ai_results_dst = os.path.join(backup_dir, "ai_results")
            if os.path.exists(ai_results_src):
                shutil.copytree(ai_results_src, ai_results_dst, dirs_exist_ok=True)

            # Create compressed backup
            zip_file = f"{backup_dir}.zip"
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, backup_dir)
                        zipf.write(file_path, arcname)

            # Remove uncompressed backup directory
            shutil.rmtree(backup_dir)

            # Clean old backups
            self.cleanup_old_backups()

            backup_size = os.path.getsize(zip_file)
            logger.info(f"Backup created: {zip_file} ({backup_size} bytes)")

            return {
                'success': True,
                'backup_file': zip_file,
                'backup_size': backup_size
            }

        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {'success': False, 'error': str(e)}

    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config['backup_retention_days'])

            for file in os.listdir(self.backups_path):
                if file.startswith('backup_') and file.endswith('.zip'):
                    file_path = os.path.join(self.backups_path, file)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                    if file_mtime < cutoff_date:
                        os.remove(file_path)
                        logger.info(f"Removed old backup: {file}")

        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")

    def restore_backup(self, backup_file: str) -> Dict:
        """Restore data from backup file"""
        try:
            if not os.path.exists(backup_file):
                return {'success': False, 'error': 'Backup file not found'}

            # Create temporary restore directory
            restore_dir = os.path.join(self.base_path, "temp_restore")
            os.makedirs(restore_dir, exist_ok=True)

            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(restore_dir)

            # Restore files
            restored_files = []

            # Restore farms registry
            farms_backup = os.path.join(restore_dir, "farms_registry.json")
            if os.path.exists(farms_backup):
                shutil.copy2(farms_backup, self.farms_file)
                restored_files.append("farms_registry.json")

            # Restore transaction history
            transactions_backup = os.path.join(restore_dir, "transaction_history.json")
            if os.path.exists(transactions_backup):
                shutil.copy2(transactions_backup, self.transactions_file)
                restored_files.append("transaction_history.json")

            # Restore AI results
            ai_results_backup = os.path.join(restore_dir, "ai_results")
            ai_results_target = os.path.join(self.base_path, "ai_results")
            if os.path.exists(ai_results_backup):
                if os.path.exists(ai_results_target):
                    shutil.rmtree(ai_results_target)
                shutil.copytree(ai_results_backup, ai_results_target)
                restored_files.append("ai_results/")

            # Cleanup temporary directory
            shutil.rmtree(restore_dir)

            logger.info(f"Backup restored: {restored_files}")

            return {
                'success': True,
                'restored_files': restored_files
            }

        except Exception as e:
            logger.error(f"Backup restoration failed: {e}")
            return {'success': False, 'error': str(e)}

    def get_processing_statistics(self, days: int = 30) -> Dict:
        """Get processing statistics for the last N days"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            stats = {
                'period_days': days,
                'reports_found': 0,
                'total_farms_processed': 0,
                'total_predictions_generated': 0,
                'total_esg_scores_updated': 0,
                'total_anomalies_detected': 0,
                'total_processing_time': 0,
                'error_count': 0,
                'success_rate': 0,
                'daily_stats': []
            }

            # Scan daily reports
            for file in os.listdir(self.daily_reports_path):
                if file.startswith('daily_report_') and file.endswith('.json'):
                    try:
                        # Extract date from filename
                        date_str = file[13:21]  # daily_report_YYYYMMDD.json
                        report_date = datetime.strptime(date_str, '%Y%m%d')

                        if start_date <= report_date <= end_date:
                            report_path = os.path.join(self.daily_reports_path, file)
                            with open(report_path, 'r') as f:
                                report = json.load(f)

                            stats['reports_found'] += 1
                            stats['total_farms_processed'] += report.get('farms_processed', 0)
                            stats['total_predictions_generated'] += report.get('predictions_generated', 0)
                            stats['total_esg_scores_updated'] += report.get('esg_scores_updated', 0)
                            stats['total_anomalies_detected'] += report.get('anomalies_detected', 0)
                            stats['total_processing_time'] += report.get('processing_time_seconds', 0)

                            if report.get('errors'):
                                stats['error_count'] += len(report['errors'])

                            stats['daily_stats'].append({
                                'date': date_str,
                                'status': report.get('summary', {}).get('status', 'unknown'),
                                'farms_processed': report.get('farms_processed', 0),
                                'processing_time': report.get('processing_time_seconds', 0)
                            })

                    except Exception as e:
                        logger.error(f"Error processing report {file}: {e}")

            # Calculate success rate
            if stats['reports_found'] > 0:
                successful_runs = len([d for d in stats['daily_stats'] if d['status'] in ['completed', 'completed_with_errors']])
                stats['success_rate'] = successful_runs / stats['reports_found']
                stats['average_processing_time'] = stats['total_processing_time'] / stats['reports_found']

            return stats

        except Exception as e:
            logger.error(f"Failed to get processing statistics: {e}")
            return {'error': str(e)}

    def create_sample_farms(self) -> bool:
        """Create sample farms for testing"""
        sample_farms = [
            {
                'farm_id': 'FARM_DEMO_001',
                'farm_name': 'Green Valley Organic Farm',
                'owner_name': 'Kim Min-jun',
                'location': 'Gyeonggi-do, South Korea',
                'size_hectares': 25.5,
                'established_date': '2015-03-15',
                'contact_info': {
                    'phone': '+82-31-123-4567',
                    'email': 'info@greenvalley.co.kr'
                },
                'certifications': ['organic', 'fair_trade', 'carbon_neutral'],
                'products': ['tomatoes', 'lettuce', 'carrots'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'esg_data': {
                    'organic_certified': True,
                    'water_usage_per_hectare': 4000,
                    'carbon_emissions': 1.8,
                    'renewable_energy_percentage': 75.0,
                    'biodiversity_score': 8,
                    'soil_health_score': 9,
                    'waste_management_score': 8,
                    'fair_wage_certification': True,
                    'community_investment_percentage': 3.2,
                    'worker_safety_score': 9,
                    'local_employment_percentage': 85.0,
                    'training_programs': True,
                    'healthcare_provided': True,
                    'transparency_score': 8,
                    'record_keeping_score': 9,
                    'stakeholder_engagement_score': 8,
                    'ethical_practices_score': 9,
                    'supply_chain_traceability': True
                },
                'blockchain_address': 'ALGO_ADDR_001',
                'status': 'active'
            },
            {
                'farm_id': 'FARM_DEMO_002',
                'farm_name': 'Sunrise Agricultural Cooperative',
                'owner_name': 'Park So-young',
                'location': 'Jeolla-do, South Korea',
                'size_hectares': 45.0,
                'established_date': '2010-08-20',
                'contact_info': {
                    'phone': '+82-61-987-6543',
                    'email': 'contact@sunrise-coop.kr'
                },
                'certifications': ['global_gap'],
                'products': ['rice', 'cabbage'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'esg_data': {
                    'organic_certified': False,
                    'water_usage_per_hectare': 11000,
                    'carbon_emissions': 4.2,
                    'renewable_energy_percentage': 30.0,
                    'biodiversity_score': 5,
                    'soil_health_score': 6,
                    'waste_management_score': 7,
                    'fair_wage_certification': False,
                    'community_investment_percentage': 1.5,
                    'worker_safety_score': 7,
                    'local_employment_percentage': 65.0,
                    'training_programs': True,
                    'healthcare_provided': False,
                    'transparency_score': 6,
                    'record_keeping_score': 7,
                    'stakeholder_engagement_score': 5,
                    'ethical_practices_score': 6,
                    'supply_chain_traceability': False
                },
                'blockchain_address': 'ALGO_ADDR_002',
                'status': 'active'
            }
        ]

        success_count = 0
        for farm_data in sample_farms:
            if self.register_farm(farm_data):
                success_count += 1

        logger.info(f"Created {success_count} sample farms")
        return success_count == len(sample_farms)