#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK RESTful API Server

This Flask application provides comprehensive REST API endpoints for the PAM-TALK platform,
including farm management, transaction processing, AI predictions, and dashboard services.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import PAM-TALK modules
try:
    from data.data_processor import DataProcessor, FarmInfo
    from ai_models.demand_predictor import DemandPredictor
    from ai_models.esg_calculator import ESGCalculator, FarmData
    from ai_models.anomaly_detector import AnomalyDetector, TransactionData
    from contracts.pam_talk_contract import pam_talk_contract
except ImportError as e:
    print(f"Warning: Could not import PAM-TALK modules: {e}")
    print("Some API endpoints may not function properly.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False

# Enable CORS for all origins and methods
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Global data processor instance
data_processor = None
current_scenario_data = None

def get_data_processor():
    """Get or create data processor instance"""
    global data_processor
    if data_processor is None:
        data_processor = DataProcessor(base_data_path="data/api_data")
        # Initialize models
        try:
            data_processor.initialize_models()
        except Exception as e:
            logger.warning(f"Failed to initialize AI models: {e}")
    return data_processor

def create_error_response(message: str, status_code: int = 400, details: Dict = None) -> Dict:
    """Create standardized error response"""
    response = {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
    }
    if details:
        response["error"]["details"] = details
    return response

def create_success_response(data: Any, message: str = None) -> Dict:
    """Create standardized success response"""
    response = {
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    if message:
        response["message"] = message
    return response

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Handle HTTP exceptions"""
    return jsonify(create_error_response(e.description, e.code)), e.code

@app.errorhandler(Exception)
def handle_general_exception(e):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify(create_error_response("Internal server error", 500)), 500

@app.before_request
def log_request_info():
    """Log request information"""
    logger.info(f"{request.method} {request.url} - {request.remote_addr}")

# =============================================================================
# Health Check and System Status
# =============================================================================

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic API information"""
    return jsonify({
        "name": "PAM-TALK API Server",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "GET /api/health",
            "POST /api/farms",
            "GET /api/farms/{id}",
            "GET /api/farms/{id}/predict",
            "POST /api/transactions",
            "GET /api/transactions/{id}/esg",
            "POST /api/transactions/check",
            "GET /api/dashboard"
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    processor = get_data_processor()

    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "data_processor": "ok",
            "ai_models": "unknown",
            "blockchain": "unknown"
        }
    }

    # Check AI models
    try:
        if hasattr(processor, 'demand_predictor') and processor.demand_predictor:
            health_status["components"]["ai_models"] = "ok"
        else:
            health_status["components"]["ai_models"] = "not_initialized"
    except Exception:
        health_status["components"]["ai_models"] = "error"

    # Check blockchain
    try:
        if hasattr(processor, 'smart_contract') and processor.smart_contract:
            # Try to get contract stats
            stats = processor.smart_contract.get_contract_stats()
            health_status["components"]["blockchain"] = "ok"
            health_status["blockchain_stats"] = stats
        else:
            health_status["components"]["blockchain"] = "not_initialized"
    except Exception:
        health_status["components"]["blockchain"] = "error"

    return jsonify(create_success_response(health_status))

# =============================================================================
# Farm Management Endpoints
# =============================================================================

@app.route('/api/farms', methods=['POST'])
def register_farm():
    """Register a new farm"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("No JSON data provided")), 400

        # Validate required fields
        required_fields = ['farm_id', 'farm_name', 'location', 'size_hectares', 'owner_name']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"Missing required fields: {', '.join(missing_fields)}"
            )), 400

        # Set default values
        farm_data = {
            'farm_id': data['farm_id'],
            'farm_name': data['farm_name'],
            'owner_name': data['owner_name'],
            'location': data['location'],
            'size_hectares': float(data['size_hectares']),
            'established_date': data.get('established_date', datetime.now().strftime('%Y-%m-%d')),
            'contact_info': data.get('contact_info', {}),
            'certifications': data.get('certifications', []),
            'products': data.get('products', []),
            'esg_data': data.get('esg_data', {}),
            'blockchain_address': data.get('blockchain_address', f"ALGO_ADDR_{data['farm_id']}"),
            'status': data.get('status', 'active'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        processor = get_data_processor()
        success = processor.register_farm(farm_data)

        if success:
            return jsonify(create_success_response(
                farm_data, "Farm registered successfully"
            )), 201
        else:
            return jsonify(create_error_response(
                "Failed to register farm - farm may already exist"
            )), 400

    except Exception as e:
        logger.error(f"Farm registration error: {e}")
        return jsonify(create_error_response(f"Registration failed: {str(e)}")), 500

@app.route('/api/farms/<string:farm_id>', methods=['GET'])
def get_farm(farm_id):
    """Get farm information"""
    try:
        processor = get_data_processor()
        farms = processor.load_farms_registry()

        if farm_id not in farms:
            return jsonify(create_error_response("Farm not found")), 404

        farm_info = farms[farm_id]
        farm_data = {
            'farm_id': farm_info.farm_id,
            'farm_name': farm_info.farm_name,
            'owner_name': farm_info.owner_name,
            'location': farm_info.location,
            'size_hectares': farm_info.size_hectares,
            'established_date': farm_info.established_date,
            'contact_info': farm_info.contact_info,
            'certifications': farm_info.certifications,
            'products': farm_info.products,
            'esg_data': farm_info.esg_data,
            'blockchain_address': farm_info.blockchain_address,
            'status': farm_info.status,
            'created_at': farm_info.created_at,
            'updated_at': farm_info.updated_at
        }

        return jsonify(create_success_response(farm_data))

    except Exception as e:
        logger.error(f"Get farm error: {e}")
        return jsonify(create_error_response(f"Failed to get farm: {str(e)}")), 500

@app.route('/api/farms/<string:farm_id>/predict', methods=['GET'])
def get_demand_prediction(farm_id):
    """Get demand prediction for farm products"""
    try:
        processor = get_data_processor()
        farms = processor.load_farms_registry()

        if farm_id not in farms:
            return jsonify(create_error_response("Farm not found")), 404

        farm_info = farms[farm_id]
        days = request.args.get('days', 7, type=int)

        if not processor.demand_predictor:
            return jsonify(create_error_response(
                "Demand predictor not available"
            )), 503

        predictions = {}
        errors = []

        for product in farm_info.products:
            try:
                prediction = processor.demand_predictor.predict_demand(product, days=days)
                predictions[product] = {
                    'total_predicted_demand': prediction['total_predicted_demand'],
                    'avg_daily_demand': prediction['avg_daily_demand'],
                    'confidence_score': prediction['accuracy_metrics']['confidence_score'],
                    'prediction_period': prediction['prediction_period'],
                    'daily_predictions': prediction['predictions'][:7]  # First week only
                }
            except Exception as e:
                errors.append(f"{product}: {str(e)}")

        result = {
            'farm_id': farm_id,
            'farm_name': farm_info.farm_name,
            'predictions': predictions,
            'prediction_date': datetime.now().isoformat()
        }

        if errors:
            result['errors'] = errors

        return jsonify(create_success_response(result))

    except Exception as e:
        logger.error(f"Demand prediction error: {e}")
        return jsonify(create_error_response(f"Prediction failed: {str(e)}")), 500

# =============================================================================
# Transaction Management Endpoints
# =============================================================================

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("No JSON data provided")), 400

        # Validate required fields
        required_fields = ['producer_id', 'consumer_id', 'product_type', 'quantity', 'price_per_unit']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"Missing required fields: {', '.join(missing_fields)}"
            )), 400

        # Calculate total value
        quantity = float(data['quantity'])
        price_per_unit = float(data['price_per_unit'])
        total_value = quantity * price_per_unit

        transaction_data = {
            'producer_id': data['producer_id'],
            'consumer_id': data['consumer_id'],
            'product_type': data['product_type'],
            'quantity': quantity,
            'price_per_unit': price_per_unit,
            'total_value': total_value,
            'quality_score': data.get('quality_score', 80),
            'esg_score': data.get('esg_score', 70),
            'location': data.get('location', 'Unknown'),
            'payment_method': data.get('payment_method', 'PAMT_TRANSFER'),
            'delivery_time_hours': data.get('delivery_time_hours', 48.0),
            'metadata': data.get('metadata', {})
        }

        processor = get_data_processor()

        # Add to local storage
        success = processor.add_transaction(transaction_data)

        # Also try to add to blockchain
        blockchain_result = None
        if processor.smart_contract:
            try:
                record_id = processor.smart_contract.record_agriculture_transaction(
                    producer=transaction_data['producer_id'],
                    consumer=transaction_data['consumer_id'],
                    product_type=transaction_data['product_type'],
                    quantity=int(transaction_data['quantity']),
                    price_per_unit=int(transaction_data['price_per_unit']),
                    quality_score=transaction_data['quality_score'],
                    esg_score=transaction_data['esg_score'],
                    location=transaction_data['location'],
                    metadata=transaction_data['metadata']
                )
                blockchain_result = {'record_id': record_id}
            except Exception as e:
                logger.warning(f"Blockchain recording failed: {e}")

        if success:
            result = {
                'transaction': transaction_data,
                'blockchain_record': blockchain_result
            }
            return jsonify(create_success_response(
                result, "Transaction created successfully"
            )), 201
        else:
            return jsonify(create_error_response("Failed to create transaction")), 500

    except Exception as e:
        logger.error(f"Transaction creation error: {e}")
        return jsonify(create_error_response(f"Transaction failed: {str(e)}")), 500

@app.route('/api/transactions/<string:transaction_id>/esg', methods=['GET'])
def get_esg_score(transaction_id):
    """Get ESG score for a transaction participant"""
    try:
        processor = get_data_processor()
        transactions = processor.get_transactions()

        # Find the transaction
        transaction = None
        for t in transactions:
            if t.get('transaction_id') == transaction_id or t.get('record_id') == transaction_id:
                transaction = t
                break

        if not transaction:
            return jsonify(create_error_response("Transaction not found")), 404

        # Get participant from query parameter (producer or consumer)
        participant = request.args.get('participant', 'producer')

        if participant == 'producer':
            address = transaction.get('producer_id')
        elif participant == 'consumer':
            address = transaction.get('consumer_id')
        else:
            return jsonify(create_error_response(
                "Invalid participant. Use 'producer' or 'consumer'"
            )), 400

        if not address:
            return jsonify(create_error_response("Participant address not found")), 404

        # Calculate ESG score
        if processor.smart_contract:
            try:
                esg_result = processor.smart_contract.get_esg_score(address)
            except Exception:
                # Fallback to manual calculation
                esg_result = {
                    'address': address,
                    'esg_score': transaction.get('esg_score', 70),
                    'transactions_count': 1,
                    'period_days': 30
                }
        else:
            esg_result = {
                'address': address,
                'esg_score': transaction.get('esg_score', 70),
                'transactions_count': 1,
                'period_days': 30
            }

        result = {
            'transaction_id': transaction_id,
            'participant': participant,
            'participant_address': address,
            'esg_data': esg_result
        }

        return jsonify(create_success_response(result))

    except Exception as e:
        logger.error(f"ESG score error: {e}")
        return jsonify(create_error_response(f"ESG score failed: {str(e)}")), 500

@app.route('/api/transactions/check', methods=['POST'])
def check_transaction_anomaly():
    """Check a transaction for anomalies"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(create_error_response("No JSON data provided")), 400

        # Validate required fields
        required_fields = ['producer_id', 'consumer_id', 'product_type', 'quantity', 'price_per_unit']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(create_error_response(
                f"Missing required fields: {', '.join(missing_fields)}"
            )), 400

        processor = get_data_processor()

        if not processor.anomaly_detector:
            return jsonify(create_error_response(
                "Anomaly detector not available"
            )), 503

        # Create transaction data for anomaly detection
        transaction_data = TransactionData(
            transaction_id=data.get('transaction_id', f"CHECK_{int(datetime.now().timestamp())}"),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            producer_id=data['producer_id'],
            consumer_id=data['consumer_id'],
            product_type=data['product_type'],
            quantity=float(data['quantity']),
            price_per_unit=float(data['price_per_unit']),
            total_value=float(data['quantity']) * float(data['price_per_unit']),
            location=data.get('location', 'Unknown'),
            quality_score=data.get('quality_score', 80),
            esg_score=data.get('esg_score', 70),
            payment_method=data.get('payment_method', 'PAMT_TRANSFER'),
            delivery_time_hours=data.get('delivery_time_hours', 48.0),
            producer_reputation=data.get('producer_reputation', 0.8),
            consumer_reputation=data.get('consumer_reputation', 0.8),
            season_factor=data.get('season_factor', 1.0),
            market_volatility=data.get('market_volatility', 0.2)
        )

        # Get historical data
        historical_transactions = processor.get_transactions(limit=1000)

        if len(historical_transactions) < 100:
            # Use simulation data if not enough historical data
            import pandas as pd
            historical_df = processor.anomaly_detector.generate_simulation_data(1000)
        else:
            import pandas as pd
            historical_df = pd.DataFrame(historical_transactions)

        # Run anomaly detection
        result = processor.anomaly_detector.detect_anomaly(transaction_data, historical_df)

        anomaly_result = {
            'transaction_id': result.transaction_id,
            'is_anomaly': result.is_anomaly,
            'anomaly_score': result.anomaly_score,
            'confidence': result.confidence,
            'risk_level': result.risk_level,
            'anomaly_types': result.anomaly_types,
            'recommendations': result.recommendations[:5],  # Top 5 recommendations
            'detection_methods': result.detection_methods,
            'check_timestamp': datetime.now().isoformat()
        }

        return jsonify(create_success_response(anomaly_result))

    except Exception as e:
        logger.error(f"Anomaly check error: {e}")
        return jsonify(create_error_response(f"Anomaly check failed: {str(e)}")), 500

# =============================================================================
# Dashboard and Analytics Endpoints
# =============================================================================

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        processor = get_data_processor()

        # Get basic statistics
        farms = processor.load_farms_registry()
        transactions = processor.get_transactions(limit=1000)

        # Get recent transactions (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_transactions = processor.get_transactions(
            start_date=week_ago, limit=100
        )

        # Calculate dashboard metrics
        dashboard_data = {
            'overview': {
                'total_farms': len(farms),
                'total_transactions': len(transactions),
                'recent_transactions': len(recent_transactions),
                'active_farms': len([f for f in farms.values() if f.status == 'active']),
                'last_updated': datetime.now().isoformat()
            },
            'farms': {
                'by_status': {},
                'by_size': {'small': 0, 'medium': 0, 'large': 0},
                'by_products': {},
                'total_area': 0
            },
            'transactions': {
                'total_value': 0,
                'by_product': {},
                'recent_activity': []
            },
            'ai_insights': {
                'predictions': {},
                'anomalies_detected': 0,
                'esg_average': 0
            }
        }

        # Analyze farms
        for farm in farms.values():
            # Status distribution
            status = farm.status
            dashboard_data['farms']['by_status'][status] = dashboard_data['farms']['by_status'].get(status, 0) + 1

            # Size categories
            if farm.size_hectares < 10:
                dashboard_data['farms']['by_size']['small'] += 1
            elif farm.size_hectares < 50:
                dashboard_data['farms']['by_size']['medium'] += 1
            else:
                dashboard_data['farms']['by_size']['large'] += 1

            # Products
            for product in farm.products:
                dashboard_data['farms']['by_products'][product] = dashboard_data['farms']['by_products'].get(product, 0) + 1

            # Total area
            dashboard_data['farms']['total_area'] += farm.size_hectares

        # Analyze transactions
        total_value = 0
        esg_scores = []

        for transaction in transactions:
            value = transaction.get('total_value', 0)
            total_value += value

            product = transaction.get('product_type', 'unknown')
            dashboard_data['transactions']['by_product'][product] = dashboard_data['transactions']['by_product'].get(product, 0) + value

            esg_score = transaction.get('esg_score')
            if esg_score:
                esg_scores.append(esg_score)

        dashboard_data['transactions']['total_value'] = total_value

        # Recent activity
        dashboard_data['transactions']['recent_activity'] = [
            {
                'transaction_id': t.get('transaction_id', 'N/A'),
                'product_type': t.get('product_type', 'N/A'),
                'total_value': t.get('total_value', 0),
                'timestamp': t.get('timestamp', 'N/A')
            }
            for t in recent_transactions[:10]
        ]

        # AI insights
        if esg_scores:
            dashboard_data['ai_insights']['esg_average'] = sum(esg_scores) / len(esg_scores)

        # Get predictions if available
        if processor.demand_predictor:
            try:
                unique_products = list(dashboard_data['farms']['by_products'].keys())[:5]
                for product in unique_products:
                    prediction = processor.demand_predictor.predict_demand(product, days=7)
                    dashboard_data['ai_insights']['predictions'][product] = {
                        'total_demand': prediction['total_predicted_demand'],
                        'confidence': prediction['accuracy_metrics']['confidence_score']
                    }
            except Exception as e:
                logger.warning(f"Failed to get predictions for dashboard: {e}")

        # Get processing statistics
        try:
            stats = processor.get_processing_statistics(days=7)
            if 'error' not in stats:
                dashboard_data['processing_stats'] = {
                    'success_rate': stats['success_rate'],
                    'total_predictions': stats['total_predictions_generated'],
                    'total_anomalies': stats['total_anomalies_detected']
                }
        except Exception as e:
            logger.warning(f"Failed to get processing stats: {e}")

        return jsonify(create_success_response(dashboard_data))

    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify(create_error_response(f"Dashboard failed: {str(e)}")), 500

# =============================================================================
# Additional Utility Endpoints
# =============================================================================

@app.route('/api/farms', methods=['GET'])
def list_farms():
    """List all farms with optional filtering"""
    try:
        processor = get_data_processor()
        farms = processor.load_farms_registry()

        # Apply filters
        status_filter = request.args.get('status')
        product_filter = request.args.get('product')

        filtered_farms = []
        for farm_id, farm_info in farms.items():
            # Status filter
            if status_filter and farm_info.status != status_filter:
                continue

            # Product filter
            if product_filter and product_filter not in farm_info.products:
                continue

            farm_data = {
                'farm_id': farm_info.farm_id,
                'farm_name': farm_info.farm_name,
                'location': farm_info.location,
                'size_hectares': farm_info.size_hectares,
                'products': farm_info.products,
                'status': farm_info.status,
                'certifications': farm_info.certifications
            }
            filtered_farms.append(farm_data)

        result = {
            'farms': filtered_farms,
            'total_count': len(filtered_farms),
            'filters_applied': {
                'status': status_filter,
                'product': product_filter
            }
        }

        return jsonify(create_success_response(result))

    except Exception as e:
        logger.error(f"List farms error: {e}")
        return jsonify(create_error_response(f"Failed to list farms: {str(e)}")), 500

@app.route('/api/transactions', methods=['GET'])
def list_transactions():
    """List transactions with optional filtering"""
    try:
        processor = get_data_processor()

        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        farm_id = request.args.get('farm_id')
        product_type = request.args.get('product_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        transactions = processor.get_transactions(
            farm_id=farm_id,
            product_type=product_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        result = {
            'transactions': transactions,
            'count': len(transactions),
            'filters_applied': {
                'farm_id': farm_id,
                'product_type': product_type,
                'start_date': start_date,
                'end_date': end_date,
                'limit': limit
            }
        }

        return jsonify(create_success_response(result))

    except Exception as e:
        logger.error(f"List transactions error: {e}")
        return jsonify(create_error_response(f"Failed to list transactions: {str(e)}")), 500

# =============================================================================
# Scenario Management Endpoints
# =============================================================================

@app.route('/api/scenarios', methods=['GET'])
def list_scenarios():
    """List available demo scenarios"""
    try:
        import glob
        import os

        # Find scenario files in data directory
        scenario_files = glob.glob("../../data/scenario_*.json")

        scenarios = []
        for file_path in scenario_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    scenario_data = json.load(f)

                scenario_info = {
                    "file_path": file_path,
                    "scenario_type": scenario_data.get("scenario_type"),
                    "scenario_name": scenario_data.get("scenario_name"),
                    "description": scenario_data.get("description"),
                    "metrics": scenario_data.get("metrics", {}),
                    "file_size": os.path.getsize(file_path)
                }
                scenarios.append(scenario_info)

            except Exception as e:
                logger.warning(f"Failed to read scenario file {file_path}: {e}")

        return jsonify(create_success_response({
            "scenarios": scenarios,
            "total_count": len(scenarios)
        }))

    except Exception as e:
        logger.error(f"List scenarios error: {e}")
        return jsonify(create_error_response(f"Failed to list scenarios: {str(e)}")), 500

@app.route('/api/scenarios/<string:scenario_type>', methods=['POST'])
def load_scenario(scenario_type):
    """Load a specific demo scenario"""
    global current_scenario_data

    try:
        import glob

        # Find the most recent scenario file of the specified type
        pattern = f"../../data/scenario_{scenario_type}_*.json"
        scenario_files = glob.glob(pattern)

        if not scenario_files:
            return jsonify(create_error_response(f"No scenario found for type: {scenario_type}")), 404

        # Use the most recent file
        latest_file = max(scenario_files, key=os.path.getmtime)

        with open(latest_file, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)

        # Store the loaded scenario data
        current_scenario_data = scenario_data

        # Update data processor with scenario data
        processor = get_data_processor()

        # Load farms from scenario
        if 'farms' in scenario_data:
            # Clear existing farm registry
            processor.farms_registry = {}

            # Load scenario farms
            for farm_data in scenario_data['farms']:
                from data.data_processor import FarmInfo

                # Filter only the fields that FarmInfo accepts
                filtered_data = {
                    'farm_id': farm_data.get('farm_id'),
                    'farm_name': farm_data.get('farm_name'),
                    'owner_name': farm_data.get('owner_name'),
                    'location': farm_data.get('location'),
                    'size_hectares': farm_data.get('size_hectares'),
                    'established_date': farm_data.get('established_date'),
                    'contact_info': farm_data.get('contact_info', {}),
                    'certifications': farm_data.get('certifications', []),
                    'products': farm_data.get('products', []),
                    'esg_data': farm_data.get('esg_data', {}),
                    'blockchain_address': farm_data.get('blockchain_address'),
                    'status': farm_data.get('status', 'active'),
                    'created_at': farm_data.get('created_at'),
                    'updated_at': farm_data.get('updated_at')
                }

                farm_info = FarmInfo(**filtered_data)
                processor.farms_registry[farm_info.farm_id] = farm_info

        # Load transactions from scenario
        if 'transactions' in scenario_data:
            processor.transactions = scenario_data['transactions']

        logger.info(f"Loaded scenario: {scenario_type}")

        return jsonify(create_success_response({
            "scenario_loaded": scenario_type,
            "scenario_name": scenario_data.get("scenario_name"),
            "farms_loaded": len(scenario_data.get("farms", [])),
            "transactions_loaded": len(scenario_data.get("transactions", [])),
            "file_path": latest_file,
            "metrics": scenario_data.get("metrics", {})
        }))

    except Exception as e:
        logger.error(f"Load scenario error: {e}")
        return jsonify(create_error_response(f"Failed to load scenario: {str(e)}")), 500

@app.route('/api/scenarios/current', methods=['GET'])
def get_current_scenario():
    """Get information about currently loaded scenario"""
    global current_scenario_data

    if current_scenario_data is None:
        return jsonify(create_error_response("No scenario currently loaded")), 404

    return jsonify(create_success_response({
        "scenario_type": current_scenario_data.get("scenario_type"),
        "scenario_name": current_scenario_data.get("scenario_name"),
        "description": current_scenario_data.get("description"),
        "metrics": current_scenario_data.get("metrics", {}),
        "insights": current_scenario_data.get("insights", []),
        "alerts": current_scenario_data.get("alerts", []),
        "achievements": current_scenario_data.get("achievements", [])
    }))

@app.route('/api/scenarios/reset', methods=['POST'])
def reset_scenario():
    """Reset to default data (clear loaded scenario)"""
    global current_scenario_data

    try:
        current_scenario_data = None

        # Reset data processor to default state
        processor = get_data_processor()
        processor.farms_registry = {}
        processor.transactions = []

        # Recreate sample farms
        processor.create_sample_farms()

        return jsonify(create_success_response({
            "message": "Scenario reset to default state"
        }))

    except Exception as e:
        logger.error(f"Reset scenario error: {e}")
        return jsonify(create_error_response(f"Failed to reset scenario: {str(e)}")), 500

# =============================================================================
# Application Startup
# =============================================================================

def initialize_app():
    """Initialize application with sample data"""
    try:
        processor = get_data_processor()

        # Create sample farms if none exist
        farms = processor.load_farms_registry()
        if not farms:
            logger.info("Creating sample farms...")
            processor.create_sample_farms()

        logger.info("PAM-TALK API Server initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize app: {e}")

if __name__ == '__main__':
    # Initialize app
    initialize_app()

    # Run the Flask application
    logger.info("Starting PAM-TALK API Server on port 5000...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Avoid double initialization
    )