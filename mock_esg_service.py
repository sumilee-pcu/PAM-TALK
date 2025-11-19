#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock ESG Chain Service
PostgreSQL 없이 작동하는 간단한 ESG 서비스
"""

from flask import Flask, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Mock 데이터
mock_data = {
    "service_info": {
        "name": "PAM-TALK ESG Chain (Mock)",
        "version": "1.0.0-mock",
        "mode": "simulation",
        "started_at": datetime.now().isoformat()
    },
    "token_operations": {
        "total_minted": 1000000000,
        "total_distributed": 185000000,
        "transactions_count": 15,
        "last_transaction": datetime.now().isoformat()
    },
    "esg_metrics": {
        "carbon_credits_issued": 350,
        "eco_points_distributed": 1200000,
        "participating_users": 45,
        "environmental_impact": {
            "co2_saved": 2.5,
            "local_food_purchases": 89,
            "zero_waste_actions": 23
        }
    }
}

@app.route('/api/health')
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "service": "PAM-TALK ESG Chain",
        "mode": "mock_simulation",
        "timestamp": datetime.now().isoformat(),
        "database": "memory_based",
        "features": [
            "token_operations",
            "esg_tracking",
            "carbon_credits",
            "eco_rewards"
        ]
    })

@app.route('/api/status')
def service_status():
    """서비스 상태 상세 정보"""
    return jsonify({
        "success": True,
        "data": mock_data
    })

@app.route('/api/token/status')
def token_status():
    """토큰 상태 정보"""
    return jsonify({
        "success": True,
        "token": {
            "id": "SIM746418487",
            "name": "PAM-TALK ESG Token (Mock)",
            "total_supply": mock_data["token_operations"]["total_minted"],
            "distributed": mock_data["token_operations"]["total_distributed"],
            "transactions": mock_data["token_operations"]["transactions_count"]
        }
    })

@app.route('/api/esg/metrics')
def esg_metrics():
    """ESG 메트릭 정보"""
    return jsonify({
        "success": True,
        "metrics": mock_data["esg_metrics"]
    })

@app.route('/api/carbon/summary')
def carbon_summary():
    """탄소 절약 요약"""
    return jsonify({
        "success": True,
        "carbon_impact": {
            "total_co2_saved": mock_data["esg_metrics"]["environmental_impact"]["co2_saved"],
            "local_food_impact": mock_data["esg_metrics"]["environmental_impact"]["local_food_purchases"],
            "zero_waste_impact": mock_data["esg_metrics"]["environmental_impact"]["zero_waste_actions"],
            "credits_issued": mock_data["esg_metrics"]["carbon_credits_issued"]
        }
    })

@app.route('/api/rewards/summary')
def rewards_summary():
    """보상 시스템 요약"""
    return jsonify({
        "success": True,
        "rewards": {
            "total_eco_points": mock_data["esg_metrics"]["eco_points_distributed"],
            "active_users": mock_data["esg_metrics"]["participating_users"],
            "token_rewards": mock_data["token_operations"]["total_distributed"]
        }
    })

if __name__ == '__main__':
    print("Mock ESG Chain Service Starting...")
    print("=" * 40)
    print("Service: PAM-TALK ESG Chain (Mock)")
    print("Port: 5004")
    print("Mode: Simulation (No Database Required)")
    print("Status: Ready for Admin Dashboard")
    print("=" * 40)

    app.run(host='0.0.0.0', port=5004, debug=True)