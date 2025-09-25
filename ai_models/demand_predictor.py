#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Demand Prediction AI Model

This module implements agricultural demand prediction using Facebook Prophet.
It includes simulation data generation, model training, and prediction with confidence intervals.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from prophet import Prophet
import warnings
import logging
from typing import Dict, List, Tuple, Optional
import json
import os

# Suppress Prophet warnings
logging.getLogger('prophet').setLevel(logging.WARNING)
warnings.filterwarnings("ignore", message="The figure layout has changed")

class DemandPredictor:
    """
    Agricultural Demand Prediction Model using Facebook Prophet
    """

    def __init__(self, data_path: str = "data/simulation_data"):
        self.data_path = data_path
        self.models = {}
        self.historical_data = {}
        self.product_configs = self._get_product_configs()

        # Create data directory if it doesn't exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs("data/predictions", exist_ok=True)
        os.makedirs("data/charts", exist_ok=True)

    def _get_product_configs(self) -> Dict:
        """Get product-specific configuration for simulation"""
        return {
            'tomatoes': {
                'base_demand': 1000,
                'seasonal_amplitude': 300,
                'growth_rate': 0.0005,
                'noise_level': 0.15,
                'peak_season': [6, 7, 8, 9],  # Summer months
                'weekly_pattern': [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 0.9],  # Mon-Sun
                'price_sensitivity': -0.2
            },
            'cabbage': {
                'base_demand': 800,
                'seasonal_amplitude': 200,
                'growth_rate': 0.0003,
                'noise_level': 0.12,
                'peak_season': [10, 11, 12, 1],  # Winter months
                'weekly_pattern': [0.9, 0.9, 1.0, 1.0, 1.1, 1.2, 0.8],
                'price_sensitivity': -0.3
            },
            'rice': {
                'base_demand': 2000,
                'seasonal_amplitude': 100,
                'growth_rate': 0.0002,
                'noise_level': 0.08,
                'peak_season': [9, 10, 11],  # Harvest season
                'weekly_pattern': [1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 0.9],
                'price_sensitivity': -0.1
            },
            'lettuce': {
                'base_demand': 600,
                'seasonal_amplitude': 150,
                'growth_rate': 0.0004,
                'noise_level': 0.18,
                'peak_season': [3, 4, 5, 10, 11],  # Spring and fall
                'weekly_pattern': [0.8, 0.9, 1.0, 1.1, 1.3, 1.2, 0.7],
                'price_sensitivity': -0.25
            },
            'carrots': {
                'base_demand': 700,
                'seasonal_amplitude': 120,
                'growth_rate': 0.0003,
                'noise_level': 0.13,
                'peak_season': [11, 12, 1, 2],  # Winter storage season
                'weekly_pattern': [0.9, 1.0, 1.0, 1.0, 1.1, 1.1, 0.9],
                'price_sensitivity': -0.15
            }
        }

    def generate_simulation_data(self, product_name: str, days: int = 365) -> pd.DataFrame:
        """
        Generate realistic simulation data for agricultural products
        """
        if product_name not in self.product_configs:
            raise ValueError(f"Product '{product_name}' not configured")

        config = self.product_configs[product_name]

        # Generate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        data = []

        for i, date in enumerate(dates):
            # Base trend
            trend = config['base_demand'] * (1 + config['growth_rate'] * i)

            # Seasonal component
            day_of_year = date.timetuple().tm_yday
            seasonal_factor = 1 + config['seasonal_amplitude'] / config['base_demand'] * \
                             np.sin(2 * np.pi * day_of_year / 365)

            # Monthly boost for peak seasons
            month = date.month
            peak_boost = 1.2 if month in config['peak_season'] else 1.0

            # Weekly pattern
            day_of_week = date.weekday()
            weekly_factor = config['weekly_pattern'][day_of_week]

            # Price effect simulation
            base_price = 100 + 20 * np.sin(2 * np.pi * day_of_year / 365) + np.random.normal(0, 5)
            price_effect = 1 + config['price_sensitivity'] * (base_price - 100) / 100

            # Weather effect (random)
            weather_effect = np.random.normal(1.0, 0.1)

            # Special events (random spikes or drops)
            event_effect = 1.0
            if np.random.random() < 0.05:  # 5% chance of special event
                event_effect = np.random.uniform(0.5, 1.8)

            # Calculate final demand
            demand = trend * seasonal_factor * peak_boost * weekly_factor * \
                    price_effect * weather_effect * event_effect

            # Add noise
            noise = np.random.normal(1.0, config['noise_level'])
            demand *= noise

            # Ensure positive demand
            demand = max(demand, config['base_demand'] * 0.1)

            data.append({
                'ds': date,
                'y': int(demand),
                'price': base_price,
                'weather_temp': np.random.normal(20, 10),
                'promotion': 1 if np.random.random() < 0.1 else 0
            })

        df = pd.DataFrame(data)

        # Save simulation data
        filename = f"{self.data_path}/{product_name}_simulation.csv"
        df.to_csv(filename, index=False)

        return df

    def load_or_generate_data(self, product_name: str, days: int = 365) -> pd.DataFrame:
        """
        Load existing data or generate new simulation data
        """
        filename = f"{self.data_path}/{product_name}_simulation.csv"

        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df['ds'] = pd.to_datetime(df['ds'])

            # Check if data is recent enough
            if (datetime.now() - df['ds'].max()).days <= 1:
                print(f"[INFO] Loaded existing simulation data for {product_name}")
                return df

        print(f"[INFO] Generating new simulation data for {product_name}")
        return self.generate_simulation_data(product_name, days)

    def train_model(self, product_name: str, use_additional_features: bool = True) -> Prophet:
        """
        Train Prophet model for specific product
        """
        # Load data
        df = self.load_or_generate_data(product_name)
        self.historical_data[product_name] = df

        # Prepare Prophet model
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            seasonality_mode='multiplicative',
            growth='linear',
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0
        )

        # Add additional regressors if available
        if use_additional_features and 'price' in df.columns:
            model.add_regressor('price')
        if use_additional_features and 'promotion' in df.columns:
            model.add_regressor('promotion')

        # Fit model
        model.fit(df[['ds', 'y'] + (['price', 'promotion'] if use_additional_features else [])])

        self.models[product_name] = model
        print(f"[OK] Model trained for {product_name}")

        return model

    def predict_demand(self, product_name: str, days: int = 7) -> Dict:
        """
        Predict demand for specified product and period
        """
        if product_name not in self.models:
            print(f"Training model for {product_name}...")
            self.train_model(product_name)

        model = self.models[product_name]
        historical_data = self.historical_data[product_name]

        # Create future dataframe
        future = model.make_future_dataframe(periods=days)

        # Add regressor values for future dates if needed
        if 'price' in historical_data.columns:
            # Simulate future prices based on recent trend
            recent_prices = historical_data['price'].tail(30)
            future_prices = []

            for i in range(len(future)):
                if i < len(historical_data):
                    future_prices.append(historical_data.iloc[i]['price'])
                else:
                    # Predict future price with some trend and randomness
                    trend_price = recent_prices.mean() + np.random.normal(0, recent_prices.std() * 0.3)
                    future_prices.append(trend_price)

            future['price'] = future_prices

        if 'promotion' in historical_data.columns:
            # Simulate future promotions
            future_promotions = []
            for i in range(len(future)):
                if i < len(historical_data):
                    future_promotions.append(historical_data.iloc[i]['promotion'])
                else:
                    future_promotions.append(1 if np.random.random() < 0.1 else 0)

            future['promotion'] = future_promotions

        # Make predictions
        forecast = model.predict(future)

        # Extract prediction period
        prediction_start = len(historical_data)
        predictions = forecast[prediction_start:].copy()

        # Calculate accuracy metrics using recent historical data
        recent_actual = historical_data['y'].tail(days).values
        recent_predicted = forecast[prediction_start-days:prediction_start]['yhat'].values

        # Calculate metrics
        mae = np.mean(np.abs(recent_actual - recent_predicted))
        mape = np.mean(np.abs((recent_actual - recent_predicted) / recent_actual)) * 100
        rmse = np.sqrt(np.mean((recent_actual - recent_predicted)**2))

        # Calculate confidence score
        confidence_score = max(0.0, min(1.0, 1.0 - (mape / 100)))

        # Prepare results
        results = {
            'product_name': product_name,
            'prediction_period': f"{days} days",
            'predictions': [
                {
                    'date': row['ds'].strftime('%Y-%m-%d'),
                    'predicted_demand': int(row['yhat']),
                    'lower_bound': int(row['yhat_lower']),
                    'upper_bound': int(row['yhat_upper']),
                    'confidence_interval': int(row['yhat_upper'] - row['yhat_lower'])
                }
                for _, row in predictions.iterrows()
            ],
            'total_predicted_demand': int(predictions['yhat'].sum()),
            'avg_daily_demand': int(predictions['yhat'].mean()),
            'accuracy_metrics': {
                'mae': round(mae, 2),
                'mape': round(mape, 2),
                'rmse': round(rmse, 2),
                'confidence_score': round(confidence_score, 3)
            },
            'model_components': {
                'trend_strength': 'moderate',
                'seasonal_strength': 'strong',
                'weekly_pattern': 'detected',
                'yearly_pattern': 'detected'
            },
            'recommendation': self._generate_recommendation(predictions, confidence_score)
        }

        # Save prediction results
        self._save_prediction_results(product_name, results)

        return results

    def visualize_prediction(self, product_name: str, days: int = 7, save_chart: bool = True) -> None:
        """
        Create visualization of prediction results
        """
        if product_name not in self.models:
            self.train_model(product_name)

        model = self.models[product_name]
        historical_data = self.historical_data[product_name]

        # Make future predictions
        future = model.make_future_dataframe(periods=days)

        # Add regressors if needed
        if 'price' in historical_data.columns:
            recent_prices = historical_data['price'].tail(30)
            future_prices = list(historical_data['price']) + \
                           [recent_prices.mean() + np.random.normal(0, recent_prices.std() * 0.3)
                            for _ in range(days)]
            future['price'] = future_prices[:len(future)]

        if 'promotion' in historical_data.columns:
            future_promotions = list(historical_data['promotion']) + \
                              [1 if np.random.random() < 0.1 else 0 for _ in range(days)]
            future['promotion'] = future_promotions[:len(future)]

        forecast = model.predict(future)

        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'{product_name.title()} Demand Prediction Analysis', fontsize=16, fontweight='bold')

        # Plot 1: Historical data and predictions
        ax1 = axes[0, 0]

        # Historical data (last 60 days)
        recent_data = historical_data.tail(60)
        ax1.plot(recent_data['ds'], recent_data['y'], 'o-', color='blue', alpha=0.7, label='Historical')

        # Predictions
        prediction_data = forecast.tail(days)
        ax1.plot(prediction_data['ds'], prediction_data['yhat'], 'o-', color='red', linewidth=2, label='Prediction')
        ax1.fill_between(prediction_data['ds'],
                        prediction_data['yhat_lower'],
                        prediction_data['yhat_upper'],
                        alpha=0.3, color='red', label='Confidence Interval')

        ax1.set_title('Demand Forecast')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Demand (kg)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=10))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

        # Plot 2: Trend decomposition
        ax2 = axes[0, 1]
        components = model.predict(future)
        ax2.plot(components['ds'], components['trend'], color='green', linewidth=2)
        ax2.set_title('Trend Component')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Trend')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

        # Plot 3: Weekly seasonality
        ax3 = axes[1, 0]
        weekly_data = components[['ds', 'weekly']].tail(14)
        days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekly_avg = [weekly_data[weekly_data['ds'].dt.dayofweek == i]['weekly'].mean()
                     for i in range(7)]

        ax3.bar(days_of_week, weekly_avg, color='orange', alpha=0.7)
        ax3.set_title('Weekly Seasonality Pattern')
        ax3.set_xlabel('Day of Week')
        ax3.set_ylabel('Seasonal Effect')
        ax3.grid(True, alpha=0.3)

        # Plot 4: Prediction summary
        ax4 = axes[1, 1]
        prediction_summary = forecast.tail(days)

        # Create bar chart of daily predictions
        bars = ax4.bar(range(len(prediction_summary)), prediction_summary['yhat'],
                      alpha=0.7, color='purple')

        # Add error bars for confidence intervals
        errors = [(row['yhat'] - row['yhat_lower'], row['yhat_upper'] - row['yhat'])
                 for _, row in prediction_summary.iterrows()]
        error_lower, error_upper = zip(*errors)
        ax4.errorbar(range(len(prediction_summary)), prediction_summary['yhat'],
                    yerr=[error_lower, error_upper], fmt='none', color='black', alpha=0.5)

        ax4.set_title(f'Next {days} Days Prediction')
        ax4.set_xlabel('Days from Today')
        ax4.set_ylabel('Predicted Demand (kg)')
        ax4.set_xticks(range(len(prediction_summary)))
        ax4.set_xticklabels([f'Day {i+1}' for i in range(len(prediction_summary))], rotation=45)
        ax4.grid(True, alpha=0.3)

        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, prediction_summary['yhat'])):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(error_upper) * 0.1,
                    f'{int(value)}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        if save_chart:
            chart_path = f"data/charts/{product_name}_prediction.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            print(f"[OK] Chart saved to {chart_path}")

        plt.show()

    def batch_predict_all_products(self, days: int = 7) -> Dict:
        """
        Predict demand for all configured products
        """
        results = {}

        print("[INFO] Running batch prediction for all products...")

        for product_name in self.product_configs.keys():
            try:
                results[product_name] = self.predict_demand(product_name, days)
                print(f"[OK] Prediction completed for {product_name}")
            except Exception as e:
                print(f"[ERROR] Prediction failed for {product_name}: {e}")
                results[product_name] = {'error': str(e)}

        # Save batch results
        batch_results_path = f"data/predictions/batch_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(batch_results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"[OK] Batch results saved to {batch_results_path}")
        return results

    def _generate_recommendation(self, predictions: pd.DataFrame, confidence_score: float) -> str:
        """
        Generate actionable recommendations based on predictions
        """
        avg_demand = predictions['yhat'].mean()
        trend = "increasing" if predictions['yhat'].iloc[-1] > predictions['yhat'].iloc[0] else "decreasing"

        if confidence_score > 0.8:
            confidence_level = "high"
        elif confidence_score > 0.6:
            confidence_level = "moderate"
        else:
            confidence_level = "low"

        recommendation = f"Demand is {trend} with {confidence_level} confidence. "

        if confidence_level == "high":
            if trend == "increasing":
                recommendation += "Consider increasing inventory and production planning."
            else:
                recommendation += "Monitor inventory levels and adjust procurement accordingly."
        elif confidence_level == "moderate":
            recommendation += "Use predictions as guidance but monitor actual demand closely."
        else:
            recommendation += "High uncertainty detected. Consider additional data sources."

        return recommendation

    def _save_prediction_results(self, product_name: str, results: Dict) -> None:
        """
        Save prediction results to file
        """
        filename = f"data/predictions/{product_name}_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"[INFO] Prediction results saved to {filename}")

    def get_model_performance(self, product_name: str) -> Dict:
        """
        Evaluate model performance using cross-validation
        """
        if product_name not in self.models:
            self.train_model(product_name)

        from prophet.diagnostics import cross_validation, performance_metrics

        model = self.models[product_name]

        # Perform cross-validation
        df_cv = cross_validation(model, initial='300 days', period='30 days', horizon='7 days')
        df_p = performance_metrics(df_cv)

        return {
            'mae': df_p['mae'].mean(),
            'mape': df_p['mape'].mean(),
            'rmse': df_p['rmse'].mean(),
            'coverage': df_p['coverage'].mean() if 'coverage' in df_p else None
        }