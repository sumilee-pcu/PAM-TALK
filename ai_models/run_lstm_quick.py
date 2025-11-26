#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick LSTM Test - Simple version without emojis
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_models.lstm_demand_predictor import LSTMDemandPredictor

# Create necessary directories
os.makedirs("data/models", exist_ok=True)
os.makedirs("data/predictions", exist_ok=True)
os.makedirs("data/charts", exist_ok=True)

print("\n" + "="*70)
print("LSTM Demand Predictor - Quick Test")
print("="*70)

# Initialize predictor
predictor = LSTMDemandPredictor()

# Configure for quick test
predictor.config['training_parameters']['epochs'] = 20
predictor.config['data_parameters']['training_days'] = 90

print("\n[1/3] Training LSTM model for tomatoes...")
results = predictor.train('tomatoes', save_model=True)

print("\n[2/3] Making predictions for next 7 days...")
predictions = predictor.predict('tomatoes', days_ahead=7)

print("\nPredictions:")
print(predictions.to_string(index=False))

# Save predictions
pred_file = "data/predictions/lstm_tomatoes_forecast.csv"
predictions.to_csv(pred_file, index=False)
print(f"\n[3/3] Predictions saved to: {pred_file}")

print("\n" + "="*70)
print("Test completed successfully!")
print("="*70)
