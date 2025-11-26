#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK LSTM Demand Prediction Model

This module implements agricultural demand prediction using LSTM neural networks.
Supports customizable training data configuration and hyperparameters.
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings("ignore")

class LSTMDemandPredictor:
    """
    LSTM-based Agricultural Demand Prediction Model
    """

    def __init__(self, config_path: str = "ai_models/lstm_config.json"):
        """
        Initialize LSTM Demand Predictor

        Args:
            config_path: Path to configuration JSON file
        """
        self.config = self._load_config(config_path)
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.history = None
        self.model_path = "data/models"

        # Create directories
        os.makedirs(self.model_path, exist_ok=True)
        os.makedirs("data/predictions", exist_ok=True)
        os.makedirs("data/charts", exist_ok=True)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                "model_parameters": {
                    "lookback_period": 30,  # Days to look back
                    "lstm_units": [64, 32],  # LSTM layers configuration
                    "dropout_rate": 0.2,
                    "dense_units": 16,
                    "activation": "relu",
                    "output_activation": "linear"
                },
                "training_parameters": {
                    "batch_size": 32,
                    "epochs": 100,
                    "validation_split": 0.2,
                    "learning_rate": 0.001,
                    "early_stopping_patience": 10,
                    "reduce_lr_patience": 5
                },
                "data_parameters": {
                    "training_days": 365,  # Total days of training data
                    "test_split": 0.2,
                    "features": [
                        "demand",
                        "price",
                        "day_of_week",
                        "month",
                        "is_weekend",
                        "is_holiday"
                    ],
                    "target": "demand"
                },
                "products": {
                    "tomatoes": {
                        "base_demand": 1000,
                        "seasonal_amplitude": 300,
                        "growth_rate": 0.0005,
                        "noise_level": 0.15
                    },
                    "cabbage": {
                        "base_demand": 800,
                        "seasonal_amplitude": 200,
                        "growth_rate": 0.0003,
                        "noise_level": 0.12
                    },
                    "rice": {
                        "base_demand": 2000,
                        "seasonal_amplitude": 100,
                        "growth_rate": 0.0002,
                        "noise_level": 0.08
                    }
                }
            }

            # Save default config
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

            return default_config

    def generate_training_data(self, product_name: str) -> pd.DataFrame:
        """
        Generate synthetic training data for agricultural product

        Args:
            product_name: Name of the product (e.g., 'tomatoes', 'cabbage')

        Returns:
            DataFrame with training data
        """
        if product_name not in self.config['products']:
            raise ValueError(f"Product '{product_name}' not configured")

        product_config = self.config['products'][product_name]
        days = self.config['data_parameters']['training_days']

        # Generate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # Base demand with growth trend
        base_demand = product_config['base_demand']
        growth_rate = product_config['growth_rate']
        trend = base_demand * (1 + np.arange(len(dates)) * growth_rate)

        # Seasonal component (yearly cycle)
        seasonal = product_config['seasonal_amplitude'] * np.sin(
            2 * np.pi * np.arange(len(dates)) / 365
        )

        # Weekly pattern (higher demand on weekends)
        weekly = 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)

        # Random noise
        noise = np.random.normal(0, base_demand * product_config['noise_level'], len(dates))

        # Combined demand
        demand = trend + seasonal + weekly + noise
        demand = np.maximum(demand, 0)  # Ensure non-negative

        # Generate prices (inversely correlated with demand)
        base_price = 5000  # Base price per kg
        price = base_price - (demand - base_demand) * 2 + np.random.normal(0, 500, len(dates))
        price = np.maximum(price, 1000)  # Minimum price

        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'demand': demand,
            'price': price,
            'day_of_week': dates.dayofweek,
            'month': dates.month,
            'is_weekend': dates.dayofweek.isin([5, 6]).astype(int),
            'is_holiday': np.random.binomial(1, 0.1, len(dates))  # 10% holiday rate
        })

        return df

    def prepare_sequences(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequences for LSTM training

        Args:
            data: DataFrame with features

        Returns:
            X (features), y (targets)
        """
        lookback = self.config['model_parameters']['lookback_period']
        features = self.config['data_parameters']['features']
        target = self.config['data_parameters']['target']

        # Extract feature columns
        feature_data = data[features].values

        # Normalize data
        scaled_data = self.scaler.fit_transform(feature_data)

        # Create sequences
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i])
            # Target is the demand value at time i
            target_idx = features.index(target)
            y.append(scaled_data[i, target_idx])

        return np.array(X), np.array(y)

    def build_model(self, input_shape: Tuple[int, int]) -> keras.Model:
        """
        Build LSTM model architecture

        Args:
            input_shape: Shape of input data (timesteps, features)

        Returns:
            Compiled Keras model
        """
        model_params = self.config['model_parameters']
        train_params = self.config['training_parameters']

        model = keras.Sequential()

        # LSTM layers
        lstm_units = model_params['lstm_units']
        for i, units in enumerate(lstm_units):
            return_sequences = (i < len(lstm_units) - 1)
            if i == 0:
                model.add(layers.LSTM(
                    units,
                    return_sequences=return_sequences,
                    input_shape=input_shape
                ))
            else:
                model.add(layers.LSTM(
                    units,
                    return_sequences=return_sequences
                ))
            model.add(layers.Dropout(model_params['dropout_rate']))

        # Dense layers
        model.add(layers.Dense(
            model_params['dense_units'],
            activation=model_params['activation']
        ))
        model.add(layers.Dropout(model_params['dropout_rate']))

        # Output layer
        model.add(layers.Dense(1, activation=model_params['output_activation']))

        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=train_params['learning_rate'])
        model.compile(
            optimizer=optimizer,
            loss='mse',
            metrics=['mae', 'mape']
        )

        return model

    def train(self, product_name: str, save_model: bool = True) -> Dict:
        """
        Train LSTM model on product data

        Args:
            product_name: Name of the product to train on
            save_model: Whether to save the trained model

        Returns:
            Training history and metrics
        """
        print(f"\n{'='*60}")
        print(f"🚀 LSTM 학습 시작: {product_name}")
        print(f"{'='*60}\n")

        # Generate training data
        print("📊 학습 데이터 생성 중...")
        data = self.generate_training_data(product_name)
        print(f"✅ 생성된 데이터: {len(data)} days")

        # Prepare sequences
        print("\n🔄 시퀀스 데이터 준비 중...")
        X, y = self.prepare_sequences(data)
        print(f"✅ 시퀀스 생성: X shape = {X.shape}, y shape = {y.shape}")

        # Split data
        test_split = self.config['data_parameters']['test_split']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_split, shuffle=False
        )

        print(f"\n📈 학습/테스트 분할:")
        print(f"   - 학습 데이터: {len(X_train)} samples")
        print(f"   - 테스트 데이터: {len(X_test)} samples")

        # Build model
        print("\n🏗️  LSTM 모델 구축 중...")
        input_shape = (X.shape[1], X.shape[2])
        self.model = self.build_model(input_shape)

        print("\n📋 모델 구조:")
        self.model.summary()

        # Callbacks
        train_params = self.config['training_parameters']
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=train_params['early_stopping_patience'],
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=train_params['reduce_lr_patience'],
                verbose=1
            )
        ]

        # Train model
        print(f"\n🎓 모델 학습 시작...")
        print(f"   - Batch Size: {train_params['batch_size']}")
        print(f"   - Max Epochs: {train_params['epochs']}")
        print(f"   - Learning Rate: {train_params['learning_rate']}")
        print()

        self.history = self.model.fit(
            X_train, y_train,
            batch_size=train_params['batch_size'],
            epochs=train_params['epochs'],
            validation_split=train_params['validation_split'],
            callbacks=callbacks,
            verbose=1
        )

        # Evaluate on test set
        print("\n📊 테스트 세트 평가 중...")
        test_results = self.model.evaluate(X_test, y_test, verbose=0)

        results = {
            'product': product_name,
            'test_loss': float(test_results[0]),
            'test_mae': float(test_results[1]),
            'test_mape': float(test_results[2]),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'epochs_trained': len(self.history.history['loss']),
            'timestamp': datetime.now().isoformat()
        }

        print(f"\n✅ 학습 완료!")
        print(f"   - Test Loss (MSE): {results['test_loss']:.2f}")
        print(f"   - Test MAE: {results['test_mae']:.2f}")
        print(f"   - Test MAPE: {results['test_mape']:.2f}%")
        print(f"   - Epochs: {results['epochs_trained']}")

        # Save model
        if save_model:
            model_file = os.path.join(self.model_path, f"lstm_{product_name}.h5")
            self.model.save(model_file)
            print(f"\n💾 모델 저장: {model_file}")

            # Save training history
            history_file = os.path.join(self.model_path, f"lstm_{product_name}_history.json")
            with open(history_file, 'w') as f:
                json.dump({
                    'history': {k: [float(v) for v in vals] for k, vals in self.history.history.items()},
                    'results': results
                }, f, indent=2)
            print(f"💾 학습 기록 저장: {history_file}")

        # Plot training history
        self._plot_training_history(product_name)

        return results

    def _plot_training_history(self, product_name: str):
        """Plot training history"""
        if self.history is None:
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'LSTM Training History - {product_name}', fontsize=16)

        # Loss
        axes[0, 0].plot(self.history.history['loss'], label='Training Loss')
        axes[0, 0].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[0, 0].set_title('Model Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss (MSE)')
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # MAE
        axes[0, 1].plot(self.history.history['mae'], label='Training MAE')
        axes[0, 1].plot(self.history.history['val_mae'], label='Validation MAE')
        axes[0, 1].set_title('Mean Absolute Error')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('MAE')
        axes[0, 1].legend()
        axes[0, 1].grid(True)

        # MAPE
        axes[1, 0].plot(self.history.history['mape'], label='Training MAPE')
        axes[1, 0].plot(self.history.history['val_mape'], label='Validation MAPE')
        axes[1, 0].set_title('Mean Absolute Percentage Error')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('MAPE (%)')
        axes[1, 0].legend()
        axes[1, 0].grid(True)

        # Learning Rate (if available)
        if 'lr' in self.history.history:
            axes[1, 1].plot(self.history.history['lr'])
            axes[1, 1].set_title('Learning Rate')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('LR')
            axes[1, 1].set_yscale('log')
            axes[1, 1].grid(True)
        else:
            axes[1, 1].text(0.5, 0.5, 'Learning Rate History\nNot Available',
                          ha='center', va='center')

        plt.tight_layout()

        chart_file = os.path.join("data/charts", f"lstm_training_{product_name}.png")
        plt.savefig(chart_file, dpi=150, bbox_inches='tight')
        print(f"📊 학습 차트 저장: {chart_file}")
        plt.close()

    def predict(self, product_name: str, days_ahead: int = 7) -> pd.DataFrame:
        """
        Make predictions for future demand

        Args:
            product_name: Name of the product
            days_ahead: Number of days to predict ahead

        Returns:
            DataFrame with predictions
        """
        if self.model is None:
            # Try to load saved model
            model_file = os.path.join(self.model_path, f"lstm_{product_name}.h5")
            if os.path.exists(model_file):
                self.model = keras.models.load_model(model_file, compile=False)
                print(f"✅ 저장된 모델 로드: {model_file}")
            else:
                # Auto-train if model doesn't exist
                print(f"⚠️  저장된 모델이 없습니다. 자동 학습을 시작합니다...")
                self.config['training_parameters']['epochs'] = 15
                self.config['data_parameters']['training_days'] = 90
                self.train(product_name, save_model=True)
                print(f"✅ 자동 학습 완료")

        # Generate recent data for context
        data = self.generate_training_data(product_name)

        # Use last lookback_period days as initial sequence
        lookback = self.config['model_parameters']['lookback_period']
        features = self.config['data_parameters']['features']

        recent_data = data[features].tail(lookback).values
        scaled_recent = self.scaler.transform(recent_data)

        # Make predictions
        predictions = []
        current_sequence = scaled_recent.copy()

        for _ in range(days_ahead):
            # Reshape for prediction
            X_pred = current_sequence.reshape(1, lookback, len(features))

            # Predict
            pred_scaled = self.model.predict(X_pred, verbose=0)[0, 0]

            # Create next input (shift sequence and add prediction)
            # For simplicity, we use the predicted demand and approximate other features
            next_input = current_sequence[-1].copy()
            target_idx = features.index(self.config['data_parameters']['target'])
            next_input[target_idx] = pred_scaled

            # Update sequence
            current_sequence = np.vstack([current_sequence[1:], next_input])

            # Inverse transform to get actual value
            full_features = np.zeros((1, len(features)))
            full_features[0, target_idx] = pred_scaled
            pred_actual = self.scaler.inverse_transform(full_features)[0, target_idx]

            predictions.append(pred_actual)

        # Create prediction DataFrame
        last_date = data['date'].max()
        pred_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=days_ahead,
            freq='D'
        )

        pred_df = pd.DataFrame({
            'date': pred_dates,
            'predicted_demand': predictions
        })

        return pred_df

    def update_config(self, new_config: Dict) -> None:
        """
        Update configuration parameters

        Args:
            new_config: Dictionary with new configuration values
        """
        self.config.update(new_config)

        # Save updated config
        config_path = "ai_models/lstm_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

        print(f"✅ 설정 업데이트 완료: {config_path}")


def main():
    """Example usage"""
    print("🌱 PAM-TALK LSTM Demand Predictor")
    print("="*60)

    # Initialize predictor
    predictor = LSTMDemandPredictor()

    # Train model
    product = 'tomatoes'
    results = predictor.train(product, save_model=True)

    # Make predictions
    print(f"\n🔮 {product} 수요 예측 (향후 7일)...")
    predictions = predictor.predict(product, days_ahead=7)
    print("\n예측 결과:")
    print(predictions.to_string(index=False))

    # Save predictions
    pred_file = f"data/predictions/lstm_{product}_forecast.csv"
    predictions.to_csv(pred_file, index=False)
    print(f"\n💾 예측 결과 저장: {pred_file}")


if __name__ == "__main__":
    main()
