#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Anomaly Detection System

This module implements comprehensive anomaly detection for agricultural transactions
using machine learning and statistical methods to identify suspicious trading patterns.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import json
import warnings
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import math
import os

warnings.filterwarnings("ignore", category=UserWarning)

@dataclass
class TransactionData:
    """Transaction data structure for anomaly detection"""
    transaction_id: str
    timestamp: str
    producer_id: str
    consumer_id: str
    product_type: str
    quantity: float  # kg
    price_per_unit: float  # PAMT per kg
    total_value: float  # PAMT
    location: str
    quality_score: int  # 0-100
    esg_score: int  # 0-100
    payment_method: str
    delivery_time_hours: float
    producer_reputation: float  # 0-1
    consumer_reputation: float  # 0-1
    season_factor: float  # seasonal adjustment factor
    market_volatility: float  # current market volatility

@dataclass
class AnomalyResult:
    """Anomaly detection result structure"""
    transaction_id: str
    is_anomaly: bool
    anomaly_score: float  # 0-1, higher = more anomalous
    confidence: float  # 0-1, higher = more confident
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    anomaly_types: List[str]
    detailed_analysis: Dict
    recommendations: List[str]
    detection_methods: Dict  # scores from different methods

class AnomalyDetector:
    """
    Comprehensive Anomaly Detection System for Agricultural Transactions
    """

    def __init__(self, contamination_rate: float = 0.1):
        self.contamination_rate = contamination_rate
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.is_trained = False

        # Anomaly thresholds
        self.thresholds = {
            'price_zscore': 2.5,
            'quantity_zscore': 2.0,
            'volume_zscore': 2.5,
            'time_pattern': 3.0,
            'isolation_forest': -0.1,
            'reputation_threshold': 0.3
        }

        # Risk level mapping
        self.risk_levels = {
            'LOW': (0.0, 0.3),
            'MEDIUM': (0.3, 0.6),
            'HIGH': (0.6, 0.8),
            'CRITICAL': (0.8, 1.0)
        }

        # Anomaly type patterns
        self.anomaly_patterns = {
            'price_manipulation': {
                'indicators': ['extreme_price_deviation', 'volume_price_mismatch'],
                'threshold': 0.7
            },
            'wash_trading': {
                'indicators': ['circular_trading', 'artificial_volume'],
                'threshold': 0.6
            },
            'market_cornering': {
                'indicators': ['large_volume_concentration', 'price_suppression'],
                'threshold': 0.8
            },
            'quality_fraud': {
                'indicators': ['quality_score_mismatch', 'unrealistic_quality'],
                'threshold': 0.6
            },
            'timing_manipulation': {
                'indicators': ['unusual_trading_hours', 'coordinated_timing'],
                'threshold': 0.5
            }
        }

    def generate_simulation_data(self, num_transactions: int = 1000,
                               anomaly_percentage: float = 0.1) -> pd.DataFrame:
        """Generate realistic transaction simulation data with anomalies"""

        np.random.seed(42)  # For reproducible results

        transactions = []
        num_anomalies = int(num_transactions * anomaly_percentage)
        num_normal = num_transactions - num_anomalies

        # Generate normal transactions
        for i in range(num_normal):
            # Base values for normal transactions
            product_types = ['tomatoes', 'cabbage', 'rice', 'lettuce', 'carrots']
            product = np.random.choice(product_types)

            # Normal price ranges per product type
            price_ranges = {
                'tomatoes': (3000, 7000),
                'cabbage': (2000, 5000),
                'rice': (1500, 3500),
                'lettuce': (4000, 8000),
                'carrots': (2500, 4500)
            }

            base_price = np.random.uniform(*price_ranges[product])

            # Normal quantity ranges
            quantity = np.random.uniform(100, 2000)

            # Add some natural variation
            seasonal_factor = 1.0 + 0.3 * np.sin(i / 100)  # Seasonal variation
            price = base_price * seasonal_factor * np.random.normal(1.0, 0.1)

            transaction = TransactionData(
                transaction_id=f"TXN_{i:06d}",
                timestamp=(datetime.now() - timedelta(days=np.random.randint(0, 365))).isoformat(),
                producer_id=f"PRODUCER_{np.random.randint(1, 50):03d}",
                consumer_id=f"CONSUMER_{np.random.randint(1, 100):03d}",
                product_type=product,
                quantity=quantity,
                price_per_unit=price,
                total_value=quantity * price,
                location=np.random.choice(['Seoul', 'Busan', 'Daegu', 'Incheon', 'Gwangju']),
                quality_score=np.random.randint(70, 98),
                esg_score=np.random.randint(60, 95),
                payment_method=np.random.choice(['PAMT_TRANSFER', 'CRYPTO', 'BANK_TRANSFER']),
                delivery_time_hours=np.random.uniform(24, 168),  # 1-7 days
                producer_reputation=np.random.uniform(0.6, 1.0),
                consumer_reputation=np.random.uniform(0.6, 1.0),
                season_factor=seasonal_factor,
                market_volatility=np.random.uniform(0.1, 0.3)
            )

            transactions.append(transaction)

        # Generate anomalous transactions
        for i in range(num_anomalies):
            idx = num_normal + i
            product = np.random.choice(['tomatoes', 'cabbage', 'rice', 'lettuce', 'carrots'])

            # Create various types of anomalies
            anomaly_type = np.random.choice([
                'price_manipulation', 'wash_trading', 'quality_fraud',
                'volume_manipulation', 'timing_anomaly'
            ])

            if anomaly_type == 'price_manipulation':
                # Extremely high or low prices
                base_price = np.random.uniform(2000, 6000)
                price = base_price * np.random.choice([0.2, 5.0])  # 80% below or 500% above normal
                quantity = np.random.uniform(100, 1000)
                quality_score = np.random.randint(60, 100)

            elif anomaly_type == 'wash_trading':
                # High volume, normal price, same actors
                price = np.random.uniform(3000, 6000)
                quantity = np.random.uniform(5000, 20000)  # Unusually large volume
                quality_score = np.random.randint(70, 90)

            elif anomaly_type == 'quality_fraud':
                # High price with low quality or vice versa
                price = np.random.uniform(8000, 15000)  # Premium price
                quantity = np.random.uniform(200, 800)
                quality_score = np.random.randint(20, 50)  # But low quality

            elif anomaly_type == 'volume_manipulation':
                # Extreme quantities
                price = np.random.uniform(3000, 7000)
                quantity = np.random.choice([np.random.uniform(10, 50), np.random.uniform(10000, 50000)])
                quality_score = np.random.randint(60, 90)

            else:  # timing_anomaly
                price = np.random.uniform(3000, 7000)
                quantity = np.random.uniform(500, 2000)
                quality_score = np.random.randint(60, 90)

            transaction = TransactionData(
                transaction_id=f"TXN_{idx:06d}_ANOMALY",
                timestamp=(datetime.now() - timedelta(days=np.random.randint(0, 30))).isoformat(),
                producer_id=f"PRODUCER_{np.random.randint(1, 50):03d}",
                consumer_id=f"CONSUMER_{np.random.randint(1, 100):03d}",
                product_type=product,
                quantity=quantity,
                price_per_unit=price,
                total_value=quantity * price,
                location=np.random.choice(['Seoul', 'Busan', 'Daegu', 'Incheon', 'Gwangju']),
                quality_score=quality_score,
                esg_score=np.random.randint(30, 80),  # Lower ESG for anomalous transactions
                payment_method=np.random.choice(['CRYPTO', 'BANK_TRANSFER', 'CASH']),
                delivery_time_hours=np.random.uniform(1, 240),  # Wider range
                producer_reputation=np.random.uniform(0.1, 0.8),  # Lower reputation
                consumer_reputation=np.random.uniform(0.1, 0.8),
                season_factor=np.random.uniform(0.5, 2.0),
                market_volatility=np.random.uniform(0.3, 0.8)  # Higher volatility
            )

            transactions.append(transaction)

        # Convert to DataFrame
        df = pd.DataFrame([asdict(t) for t in transactions])
        df['is_anomaly'] = df['transaction_id'].str.contains('ANOMALY')

        return df

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for machine learning models"""

        features_df = df.copy()

        # Convert timestamp to numerical features
        features_df['timestamp'] = pd.to_datetime(features_df['timestamp'])
        features_df['hour'] = features_df['timestamp'].dt.hour
        features_df['day_of_week'] = features_df['timestamp'].dt.dayofweek
        features_df['day_of_month'] = features_df['timestamp'].dt.day

        # Price-related features
        features_df['price_per_kg'] = features_df['price_per_unit']
        features_df['log_total_value'] = np.log1p(features_df['total_value'])
        features_df['log_quantity'] = np.log1p(features_df['quantity'])

        # Ratio features
        features_df['quality_price_ratio'] = features_df['quality_score'] / features_df['price_per_unit']
        features_df['esg_price_ratio'] = features_df['esg_score'] / features_df['price_per_unit']
        features_df['reputation_avg'] = (features_df['producer_reputation'] + features_df['consumer_reputation']) / 2

        # Product type encoding
        product_dummies = pd.get_dummies(features_df['product_type'].astype(str), prefix='product')
        features_df = pd.concat([features_df, product_dummies], axis=1)

        # Location encoding
        location_dummies = pd.get_dummies(features_df['location'].astype(str), prefix='location')
        features_df = pd.concat([features_df, location_dummies], axis=1)

        # Payment method encoding
        payment_dummies = pd.get_dummies(features_df['payment_method'].astype(str), prefix='payment')
        features_df = pd.concat([features_df, payment_dummies], axis=1)

        return features_df

    def train_isolation_forest(self, historical_data: pd.DataFrame):
        """Train Isolation Forest model on historical data"""

        # Prepare features
        features_df = self.prepare_features(historical_data)

        # Select numerical features for isolation forest
        feature_columns = [
            'quantity', 'price_per_unit', 'total_value', 'quality_score', 'esg_score',
            'delivery_time_hours', 'producer_reputation', 'consumer_reputation',
            'season_factor', 'market_volatility', 'hour', 'day_of_week', 'day_of_month',
            'log_total_value', 'log_quantity', 'quality_price_ratio', 'esg_price_ratio',
            'reputation_avg'
        ]

        # Add dummy columns
        feature_columns.extend([col for col in features_df.columns if col.startswith(('product_', 'location_', 'payment_'))])

        # Select available columns (in case some categories are missing)
        available_features = [col for col in feature_columns if col in features_df.columns]

        X = features_df[available_features].fillna(0)

        # Ensure all data is numeric
        for col in X.columns:
            if X[col].dtype == 'object' or X[col].dtype.name.startswith('string'):
                X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=self.contamination_rate,
            random_state=42,
            n_estimators=100
        )

        self.isolation_forest.fit(X_scaled)
        self.feature_columns = available_features
        self.is_trained = True

        print(f"[OK] Isolation Forest trained with {len(available_features)} features")

    def calculate_statistical_anomalies(self, transaction: TransactionData,
                                      historical_data: pd.DataFrame) -> Dict:
        """Calculate Z-scores and statistical anomalies"""

        # Filter historical data for same product type
        product_data = historical_data[
            historical_data['product_type'] == transaction.product_type
        ]

        if len(product_data) < 10:
            # Use all data if not enough product-specific data
            product_data = historical_data

        anomaly_scores = {}

        # Price Z-score
        price_mean = product_data['price_per_unit'].mean()
        price_std = product_data['price_per_unit'].std()
        if price_std > 0:
            price_zscore = abs((transaction.price_per_unit - price_mean) / price_std)
            anomaly_scores['price_zscore'] = price_zscore
            anomaly_scores['price_anomaly'] = price_zscore > self.thresholds['price_zscore']

        # Quantity Z-score
        quantity_mean = product_data['quantity'].mean()
        quantity_std = product_data['quantity'].std()
        if quantity_std > 0:
            quantity_zscore = abs((transaction.quantity - quantity_mean) / quantity_std)
            anomaly_scores['quantity_zscore'] = quantity_zscore
            anomaly_scores['quantity_anomaly'] = quantity_zscore > self.thresholds['quantity_zscore']

        # Total value Z-score
        value_mean = product_data['total_value'].mean()
        value_std = product_data['total_value'].std()
        if value_std > 0:
            value_zscore = abs((transaction.total_value - value_mean) / value_std)
            anomaly_scores['value_zscore'] = value_zscore
            anomaly_scores['value_anomaly'] = value_zscore > self.thresholds['volume_zscore']

        # Quality-price relationship anomaly
        if len(product_data) > 5:
            quality_price_correlation = product_data[['quality_score', 'price_per_unit']].corr().iloc[0,1]
            expected_price = price_mean + quality_price_correlation * (transaction.quality_score - product_data['quality_score'].mean())
            quality_price_deviation = abs(transaction.price_per_unit - expected_price) / price_mean
            anomaly_scores['quality_price_anomaly'] = quality_price_deviation > 0.5

        return anomaly_scores

    def analyze_transaction_patterns(self, transaction: TransactionData,
                                   historical_data: pd.DataFrame) -> Dict:
        """Analyze transaction patterns for anomaly detection"""

        pattern_analysis = {}

        # Time pattern analysis
        transaction_time = pd.to_datetime(transaction.timestamp)
        hour = transaction_time.hour

        # Check for unusual trading hours (e.g., very late night or very early morning)
        unusual_hours = [0, 1, 2, 3, 4, 5, 23]
        pattern_analysis['unusual_trading_hour'] = hour in unusual_hours

        # Reputation analysis
        avg_reputation = (transaction.producer_reputation + transaction.consumer_reputation) / 2
        pattern_analysis['low_reputation'] = avg_reputation < self.thresholds['reputation_threshold']

        # ESG-Quality consistency
        esg_quality_ratio = transaction.esg_score / max(transaction.quality_score, 1)
        pattern_analysis['esg_quality_mismatch'] = abs(esg_quality_ratio - 1.0) > 0.5

        # Price volatility vs market volatility
        if transaction.market_volatility > 0:
            # High price with low market volatility might be suspicious
            if transaction.price_per_unit > historical_data['price_per_unit'].quantile(0.8):
                pattern_analysis['price_volatility_mismatch'] = transaction.market_volatility < 0.2

        # Delivery time analysis
        normal_delivery_range = (24, 168)  # 1-7 days
        pattern_analysis['unusual_delivery_time'] = (
            transaction.delivery_time_hours < normal_delivery_range[0] or
            transaction.delivery_time_hours > normal_delivery_range[1]
        )

        return pattern_analysis

    def classify_anomaly_type(self, statistical_scores: Dict, pattern_analysis: Dict,
                            isolation_score: float) -> List[str]:
        """Classify the type of anomaly based on detection results"""

        anomaly_types = []

        # Price manipulation detection
        price_indicators = [
            statistical_scores.get('price_anomaly', False),
            statistical_scores.get('quality_price_anomaly', False),
            pattern_analysis.get('price_volatility_mismatch', False)
        ]
        if sum(price_indicators) >= 2:
            anomaly_types.append('price_manipulation')

        # Quality fraud detection
        quality_indicators = [
            statistical_scores.get('quality_price_anomaly', False),
            pattern_analysis.get('esg_quality_mismatch', False)
        ]
        if any(quality_indicators):
            anomaly_types.append('quality_fraud')

        # Wash trading / artificial volume
        volume_indicators = [
            statistical_scores.get('quantity_anomaly', False),
            statistical_scores.get('value_anomaly', False),
            pattern_analysis.get('low_reputation', False)
        ]
        if sum(volume_indicators) >= 2:
            anomaly_types.append('wash_trading')

        # Timing manipulation
        timing_indicators = [
            pattern_analysis.get('unusual_trading_hour', False),
            pattern_analysis.get('unusual_delivery_time', False)
        ]
        if any(timing_indicators):
            anomaly_types.append('timing_manipulation')

        # General suspicious activity (high isolation forest score)
        if isolation_score < -0.3:
            anomaly_types.append('general_suspicious')

        return anomaly_types if anomaly_types else ['unknown']

    def calculate_confidence_and_risk(self, statistical_scores: Dict, pattern_analysis: Dict,
                                    isolation_score: float, anomaly_types: List[str]) -> Tuple[float, str]:
        """Calculate confidence score and risk level"""

        # Count positive indicators
        statistical_indicators = sum([
            statistical_scores.get('price_anomaly', False),
            statistical_scores.get('quantity_anomaly', False),
            statistical_scores.get('value_anomaly', False),
            statistical_scores.get('quality_price_anomaly', False)
        ])

        pattern_indicators = sum([
            pattern_analysis.get('unusual_trading_hour', False),
            pattern_analysis.get('low_reputation', False),
            pattern_analysis.get('esg_quality_mismatch', False),
            pattern_analysis.get('price_volatility_mismatch', False),
            pattern_analysis.get('unusual_delivery_time', False)
        ])

        # Isolation forest contribution
        isolation_contribution = max(0, (-isolation_score - 0.1) * 2)  # Scale to 0-1

        # Calculate overall anomaly score
        total_indicators = statistical_indicators + pattern_indicators
        max_indicators = 4 + 5  # max statistical + max pattern indicators

        anomaly_score = (
            (statistical_indicators / 4) * 0.4 +
            (pattern_indicators / 5) * 0.3 +
            isolation_contribution * 0.3
        )

        # Confidence based on consistency of indicators
        if total_indicators >= 4:
            confidence = 0.9
        elif total_indicators >= 2:
            confidence = 0.7
        elif total_indicators >= 1:
            confidence = 0.5
        else:
            confidence = 0.3

        # Determine risk level
        risk_level = 'LOW'
        for level, (min_score, max_score) in self.risk_levels.items():
            if min_score <= anomaly_score < max_score:
                risk_level = level
                break

        return min(1.0, anomaly_score), risk_level

    def generate_recommendations(self, anomaly_types: List[str], risk_level: str,
                               statistical_scores: Dict, pattern_analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on anomaly detection results"""

        recommendations = []

        if 'price_manipulation' in anomaly_types:
            recommendations.append("URGENT: Investigate potential price manipulation - verify market conditions")
            recommendations.append("Cross-check with other similar transactions in the same time period")

        if 'quality_fraud' in anomaly_types:
            recommendations.append("Verify product quality claims and ESG certifications")
            recommendations.append("Request additional documentation for quality scores")

        if 'wash_trading' in anomaly_types:
            recommendations.append("Investigate relationship between trading parties")
            recommendations.append("Check for circular trading patterns and artificial volume")

        if 'timing_manipulation' in anomaly_types:
            recommendations.append("Review trading time patterns for coordination")
            recommendations.append("Verify delivery schedules and logistics")

        if pattern_analysis.get('low_reputation', False):
            recommendations.append("Enhanced due diligence required for low-reputation parties")
            recommendations.append("Consider requiring additional collateral or guarantees")

        if risk_level in ['HIGH', 'CRITICAL']:
            recommendations.append("IMMEDIATE ACTION: Suspend transaction pending investigation")
            recommendations.append("Notify regulatory authorities if required")
            recommendations.append("Implement additional monitoring for involved parties")
        elif risk_level == 'MEDIUM':
            recommendations.append("Enhanced monitoring recommended")
            recommendations.append("Request additional transaction documentation")

        return recommendations

    def detect_anomaly(self, transaction_data: Union[TransactionData, Dict],
                      historical_data: pd.DataFrame) -> AnomalyResult:
        """
        Main method to detect anomalies in a transaction

        Args:
            transaction_data: Current transaction to analyze
            historical_data: Historical transaction data for comparison

        Returns:
            AnomalyResult with comprehensive anomaly analysis
        """

        # Convert dict to TransactionData if needed
        if isinstance(transaction_data, dict):
            transaction = TransactionData(**transaction_data)
        else:
            transaction = transaction_data

        # Ensure isolation forest is trained
        if not self.is_trained:
            print("[INFO] Training Isolation Forest with historical data...")
            self.train_isolation_forest(historical_data)

        # Statistical anomaly detection
        statistical_scores = self.calculate_statistical_anomalies(transaction, historical_data)

        # Pattern analysis
        pattern_analysis = self.analyze_transaction_patterns(transaction, historical_data)

        # Isolation Forest prediction
        isolation_score = -1.0  # Default if prediction fails
        if self.isolation_forest is not None:
            try:
                # Prepare transaction for ML model
                transaction_df = pd.DataFrame([asdict(transaction)])
                features_df = self.prepare_features(transaction_df)

                # Select same features as training
                available_features = [col for col in self.feature_columns if col in features_df.columns]
                X = features_df[available_features].fillna(0)

                # Scale and predict
                X_scaled = self.scaler.transform(X)
                isolation_score = self.isolation_forest.decision_function(X_scaled)[0]

            except Exception as e:
                print(f"[WARNING] Isolation Forest prediction failed: {e}")

        # Classify anomaly types
        anomaly_types = self.classify_anomaly_type(statistical_scores, pattern_analysis, isolation_score)

        # Calculate confidence and risk level
        anomaly_score, risk_level = self.calculate_confidence_and_risk(
            statistical_scores, pattern_analysis, isolation_score, anomaly_types
        )

        # Determine if transaction is anomalous
        is_anomaly = (
            anomaly_score > 0.5 or
            isolation_score < self.thresholds['isolation_forest'] or
            any([
                statistical_scores.get('price_anomaly', False),
                statistical_scores.get('quantity_anomaly', False),
                statistical_scores.get('value_anomaly', False)
            ])
        )

        # Generate recommendations
        recommendations = self.generate_recommendations(
            anomaly_types, risk_level, statistical_scores, pattern_analysis
        )

        # Create detailed analysis
        detailed_analysis = {
            'statistical_analysis': statistical_scores,
            'pattern_analysis': pattern_analysis,
            'isolation_forest_score': isolation_score,
            'feature_contributions': {
                'price_deviation': statistical_scores.get('price_zscore', 0),
                'quantity_deviation': statistical_scores.get('quantity_zscore', 0),
                'value_deviation': statistical_scores.get('value_zscore', 0),
                'reputation_factor': (transaction.producer_reputation + transaction.consumer_reputation) / 2,
                'time_factor': pattern_analysis.get('unusual_trading_hour', False)
            }
        }

        # Detection methods scores
        detection_methods = {
            'z_score_analysis': max([
                statistical_scores.get('price_zscore', 0) / 5,
                statistical_scores.get('quantity_zscore', 0) / 5,
                statistical_scores.get('value_zscore', 0) / 5
            ]),
            'isolation_forest': max(0, (-isolation_score - 0.1) * 2),
            'pattern_analysis': sum(pattern_analysis.values()) / len(pattern_analysis)
        }

        # Create result
        result = AnomalyResult(
            transaction_id=transaction.transaction_id,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            confidence=min(1.0, anomaly_score + 0.1),  # Slight confidence boost
            risk_level=risk_level,
            anomaly_types=anomaly_types,
            detailed_analysis=detailed_analysis,
            recommendations=recommendations,
            detection_methods=detection_methods
        )

        return result

    def batch_anomaly_detection(self, transactions: List[Union[TransactionData, Dict]],
                              historical_data: pd.DataFrame) -> List[AnomalyResult]:
        """Run anomaly detection on multiple transactions"""

        results = []

        print(f"[INFO] Running batch anomaly detection on {len(transactions)} transactions...")

        for i, transaction in enumerate(transactions):
            try:
                result = self.detect_anomaly(transaction, historical_data)
                results.append(result)

                if (i + 1) % 100 == 0:
                    print(f"[INFO] Processed {i + 1}/{len(transactions)} transactions")

            except Exception as e:
                print(f"[ERROR] Failed to process transaction {i}: {e}")

        return results

    def save_anomaly_results(self, results: List[AnomalyResult],
                           filename: Optional[str] = None) -> str:
        """Save anomaly detection results to file"""

        if not filename:
            filename = f"data/anomaly_results/anomaly_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Convert results to dictionary format
        results_data = [asdict(result) for result in results]

        # Add summary statistics
        summary = {
            'total_transactions': len(results),
            'anomalies_detected': sum(1 for r in results if r.is_anomaly),
            'risk_level_distribution': {},
            'anomaly_type_distribution': {},
            'average_anomaly_score': np.mean([r.anomaly_score for r in results])
        }

        # Calculate distributions
        for result in results:
            # Risk level distribution
            if result.risk_level in summary['risk_level_distribution']:
                summary['risk_level_distribution'][result.risk_level] += 1
            else:
                summary['risk_level_distribution'][result.risk_level] = 1

            # Anomaly type distribution
            for anomaly_type in result.anomaly_types:
                if anomaly_type in summary['anomaly_type_distribution']:
                    summary['anomaly_type_distribution'][anomaly_type] += 1
                else:
                    summary['anomaly_type_distribution'][anomaly_type] = 1

        # Save to file
        output_data = {
            'summary': summary,
            'results': results_data,
            'generated_at': datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)

        print(f"[OK] Anomaly results saved to {filename}")
        return filename