#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK 관리자 웹 대시보드
실시간 모니터링을 위한 웹 기반 관리자 인터페이스
"""

from flask import Flask, render_template_string, jsonify, request
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# 관리자 대시보드 HTML 템플릿
ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PAM-TALK 관리자 대시보드</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
        }

        .admin-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .admin-header h1 {
            font-size: 1.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .admin-subtitle {
            opacity: 0.9;
            margin-top: 0.5rem;
        }

        .container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .dashboard-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border: 1px solid #e1e8ed;
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f0f3f7;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }

        .status-online { background: #2ecc71; }
        .status-offline { background: #e74c3c; }
        .status-warning { background: #f39c12; }

        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
            margin: 0.5rem 0;
        }

        .metric-label {
            color: #7f8c8d;
            font-size: 0.9rem;
        }

        .metric-change {
            font-size: 0.8rem;
            font-weight: 500;
        }

        .metric-up { color: #2ecc71; }
        .metric-down { color: #e74c3c; }

        .table-container {
            overflow-x: auto;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        .data-table th,
        .data-table td {
            padding: 0.8rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        .data-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }

        .data-table tr:hover {
            background: #f8f9fa;
        }

        .refresh-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .refresh-btn:hover {
            background: #2980b9;
        }

        .auto-refresh {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            color: #7f8c8d;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin: 0.5rem 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            border-radius: 4px;
            transition: width 0.3s ease;
        }

        .alert {
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            border-left: 4px solid;
        }

        .alert-success {
            background: #d4edda;
            border-left-color: #28a745;
            color: #155724;
        }

        .alert-warning {
            background: #fff3cd;
            border-left-color: #ffc107;
            color: #856404;
        }

        .alert-danger {
            background: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }

        .log-container {
            max-height: 300px;
            overflow-y: auto;
            background: #2c3e50;
            color: #ecf0f1;
            padding: 1rem;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            line-height: 1.4;
        }

        .log-entry {
            margin-bottom: 0.5rem;
            display: flex;
        }

        .log-timestamp {
            color: #95a5a6;
            margin-right: 1rem;
            flex-shrink: 0;
        }

        .log-level-info { color: #3498db; }
        .log-level-warn { color: #f39c12; }
        .log-level-error { color: #e74c3c; }
        .log-level-success { color: #2ecc71; }

        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }

            .container {
                padding: 0 1rem;
            }
        }
    </style>
</head>
<body>
    <header class="admin-header">
        <h1>
            <i class="fas fa-cogs"></i>
            PAM-TALK 관리자 대시보드
        </h1>
        <div class="admin-subtitle">실시간 시스템 모니터링 및 관리</div>
    </header>

    <div class="container">
        <!-- 시스템 상태 알림 -->
        <div id="systemAlerts"></div>

        <!-- 메인 대시보드 그리드 -->
        <div class="dashboard-grid">
            <!-- 서비스 상태 -->
            <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-server"></i>
                        서비스 상태
                    </div>
                    <button class="refresh-btn" onclick="refreshServices()">
                        <i class="fas fa-sync-alt"></i>
                        새로고침
                    </button>
                </div>
                <div id="serviceStatus">
                    <div class="metric-value">로딩 중...</div>
                </div>
            </div>

            <!-- 블록체인 계정 -->
            <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-wallet"></i>
                        알고랜드 계정
                    </div>
                    <button class="refresh-btn" onclick="refreshBlockchain()">
                        <i class="fas fa-sync-alt"></i>
                        새로고침
                    </button>
                </div>
                <div id="blockchainStatus">
                    <div class="metric-value">로딩 중...</div>
                </div>
            </div>

            <!-- PAM 토큰 -->
            <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-coins"></i>
                        PAM 토큰
                    </div>
                    <button class="refresh-btn" onclick="refreshToken()">
                        <i class="fas fa-sync-alt"></i>
                        새로고침
                    </button>
                </div>
                <div id="tokenStatus">
                    <div class="metric-value">로딩 중...</div>
                </div>
            </div>

            <!-- 플랫폼 통계 -->
            <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-chart-line"></i>
                        플랫폼 통계
                    </div>
                    <button class="refresh-btn" onclick="refreshStats()">
                        <i class="fas fa-sync-alt"></i>
                        새로고침
                    </button>
                </div>
                <div id="platformStats">
                    <div class="metric-value">로딩 중...</div>
                </div>
            </div>
        </div>

        <!-- 상세 모니터링 섹션 -->
        <div class="dashboard-grid">
            <!-- 실시간 트랜잭션 로그 -->
            <div class="dashboard-card" style="grid-column: 1 / -1;">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-list"></i>
                        실시간 시스템 로그
                    </div>
                    <div class="auto-refresh">
                        <i class="fas fa-clock"></i>
                        자동 새로고침: 10초
                    </div>
                </div>
                <div class="log-container" id="systemLogs">
                    <div class="log-entry">
                        <span class="log-timestamp">Loading...</span>
                        <span>시스템 로그를 불러오는 중...</span>
                    </div>
                </div>
            </div>

            <!-- 최근 활동 테이블 -->
            <div class="dashboard-card" style="grid-column: 1 / -1;">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-users"></i>
                        최근 사용자 활동
                    </div>
                </div>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>시간</th>
                                <th>사용자</th>
                                <th>활동</th>
                                <th>상태</th>
                                <th>세부사항</th>
                            </tr>
                        </thead>
                        <tbody id="activityTable">
                            <tr>
                                <td colspan="5" style="text-align: center;">데이터 로딩 중...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 전역 변수
        let autoRefreshInterval;
        let logUpdateInterval;

        // 페이지 로드 시 실행
        document.addEventListener('DOMContentLoaded', () => {
            refreshAllData();
            startAutoRefresh();
        });

        // 모든 데이터 새로고침
        async function refreshAllData() {
            await Promise.all([
                refreshServices(),
                refreshBlockchain(),
                refreshToken(),
                refreshStats(),
                refreshLogs()
            ]);
        }

        // 서비스 상태 새로고침
        async function refreshServices() {
            try {
                const response = await fetch('/admin/api/services');
                const data = await response.json();

                let html = '';
                let alertsHtml = '';

                data.services.forEach(service => {
                    const statusClass = service.status === 'running' ? 'status-online' : 'status-offline';
                    const statusText = service.status === 'running' ? '온라인' : '오프라인';

                    html += `
                        <div style="margin-bottom: 1rem;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span class="status-indicator ${statusClass}"></span>
                                <strong>${service.name}</strong>
                                <span style="color: #7f8c8d;">(포트 ${service.port})</span>
                            </div>
                            <div style="font-size: 0.9rem; color: #666;">
                                상태: ${statusText} | 마지막 확인: ${service.last_check}
                            </div>
                        </div>
                    `;

                    if (service.status !== 'running') {
                        alertsHtml += `
                            <div class="alert alert-warning">
                                <i class="fas fa-exclamation-triangle"></i>
                                ${service.name} 서비스가 오프라인 상태입니다.
                            </div>
                        `;
                    }
                });

                document.getElementById('serviceStatus').innerHTML = html;
                document.getElementById('systemAlerts').innerHTML = alertsHtml;

            } catch (error) {
                console.error('서비스 상태 로드 실패:', error);
                document.getElementById('serviceStatus').innerHTML =
                    '<div style="color: #e74c3c;">서비스 상태를 불러올 수 없습니다.</div>';
            }
        }

        // 블록체인 상태 새로고침
        async function refreshBlockchain() {
            try {
                const response = await fetch('/admin/api/blockchain');
                const data = await response.json();

                let html = '';
                data.accounts.forEach(account => {
                    const funded = account.balance >= 1.0;
                    const statusClass = funded ? 'status-online' : 'status-warning';
                    const statusText = funded ? '펀딩됨' : '펀딩 필요';

                    html += `
                        <div style="margin-bottom: 1rem;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span class="status-indicator ${statusClass}"></span>
                                <strong>${account.name.toUpperCase()}</strong>
                            </div>
                            <div style="font-size: 0.9rem;">
                                잔액: <strong>${account.balance.toFixed(6)} ALGO</strong><br>
                                상태: ${statusText}<br>
                                주소: ${account.address.substring(0, 20)}...
                            </div>
                        </div>
                    `;
                });

                document.getElementById('blockchainStatus').innerHTML = html;

            } catch (error) {
                console.error('블록체인 상태 로드 실패:', error);
                document.getElementById('blockchainStatus').innerHTML =
                    '<div style="color: #e74c3c;">블록체인 상태를 불러올 수 없습니다.</div>';
            }
        }

        // 토큰 상태 새로고침
        async function refreshToken() {
            try {
                const response = await fetch('/admin/api/token');
                const data = await response.json();

                const statusClass = data.status === 'active' ? 'status-online' : 'status-warning';
                const statusText = data.status === 'active' ? '활성' : '비활성';

                let html = `
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                        <span class="status-indicator ${statusClass}"></span>
                        <strong>PAM 토큰</strong>
                    </div>
                    <div style="font-size: 0.9rem;">
                        상태: ${statusText}<br>
                        ${data.token_id ? `토큰 ID: ${data.token_id}<br>` : ''}
                        ${data.total_supply ? `총 공급량: ${data.total_supply.toLocaleString()}<br>` : ''}
                        모드: ${data.mode || '실제'}
                    </div>
                `;

                document.getElementById('tokenStatus').innerHTML = html;

            } catch (error) {
                console.error('토큰 상태 로드 실패:', error);
                document.getElementById('tokenStatus').innerHTML =
                    '<div style="color: #e74c3c;">토큰 상태를 불러올 수 없습니다.</div>';
            }
        }

        // 플랫폼 통계 새로고침
        async function refreshStats() {
            try {
                const response = await fetch('http://localhost:5003/api/dashboard');
                const result = await response.json();

                if (result.success) {
                    const stats = result.data;
                    let html = `
                        <div style="margin-bottom: 1rem;">
                            <div class="metric-value">${stats.platform_stats.total_users}</div>
                            <div class="metric-label">전체 사용자</div>
                        </div>
                        <div style="margin-bottom: 1rem;">
                            <div class="metric-value">${stats.carbon_impact.total_carbon_saved.toFixed(1)}kg</div>
                            <div class="metric-label">CO₂ 절약량</div>
                        </div>
                        <div style="margin-bottom: 1rem;">
                            <div class="metric-value">${stats.economic_impact.direct_trades_value.toLocaleString()}원</div>
                            <div class="metric-label">직거래 거래액</div>
                        </div>
                    `;
                    document.getElementById('platformStats').innerHTML = html;
                } else {
                    throw new Error('API 응답 실패');
                }

            } catch (error) {
                console.error('플랫폼 통계 로드 실패:', error);
                document.getElementById('platformStats').innerHTML =
                    '<div style="color: #e74c3c;">통계를 불러올 수 없습니다.</div>';
            }
        }

        // 시스템 로그 새로고침
        async function refreshLogs() {
            try {
                const response = await fetch('/admin/api/logs');
                const data = await response.json();

                let html = '';
                data.logs.forEach(log => {
                    const levelClass = `log-level-${log.level}`;
                    html += `
                        <div class="log-entry">
                            <span class="log-timestamp">${log.timestamp}</span>
                            <span class="${levelClass}">[${log.level.toUpperCase()}]</span>
                            <span>${log.message}</span>
                        </div>
                    `;
                });

                document.getElementById('systemLogs').innerHTML = html;

                // 스크롤을 맨 아래로
                const logContainer = document.getElementById('systemLogs');
                logContainer.scrollTop = logContainer.scrollHeight;

            } catch (error) {
                console.error('로그 로드 실패:', error);
            }
        }

        // 자동 새로고침 시작
        function startAutoRefresh() {
            // 전체 새로고침: 30초마다
            autoRefreshInterval = setInterval(refreshAllData, 30000);

            // 로그만 빠르게: 10초마다
            logUpdateInterval = setInterval(refreshLogs, 10000);
        }

        // 자동 새로고침 중지
        function stopAutoRefresh() {
            if (autoRefreshInterval) clearInterval(autoRefreshInterval);
            if (logUpdateInterval) clearInterval(logUpdateInterval);
        }

        // 페이지 언로드 시 인터벌 정리
        window.addEventListener('beforeunload', stopAutoRefresh);
    </script>
</body>
</html>
"""

# 관리자 API 엔드포인트들
@app.route('/')
def admin_dashboard():
    """관리자 대시보드 메인 페이지"""
    return render_template_string(ADMIN_DASHBOARD_HTML)

@app.route('/admin/api/services')
def get_services_status():
    """서비스 상태 API"""
    services = [
        {"name": "PAM-TALK Main", "port": 5003, "path": "/api/health"},
        {"name": "ESG Chain", "port": 5004, "path": "/api/health"}
    ]

    service_status = []
    for service in services:
        try:
            response = requests.get(f"http://localhost:{service['port']}{service['path']}", timeout=3)
            status = "running" if response.status_code == 200 else "error"
        except:
            status = "stopped"

        service_status.append({
            "name": service["name"],
            "port": service["port"],
            "status": status,
            "last_check": datetime.now().strftime("%H:%M:%S")
        })

    return jsonify({"services": service_status})

@app.route('/admin/api/blockchain')
def get_blockchain_status():
    """블록체인 계정 상태 API"""
    accounts = [
        {
            "name": "main",
            "address": "3MKYZNK57LRFLWUBJG33KJZJTX4WX2EJAJNHQQSWUZ6QVTEM4DEI4Y2AF4"
        }
    ]

    account_status = []
    for account in accounts:
        try:
            api_url = f"https://testnet-api.algonode.cloud/v2/accounts/{account['address']}"
            response = requests.get(api_url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                balance = data.get('amount', 0) / 1000000
            else:
                balance = 0.0
        except:
            balance = 0.0

        account_status.append({
            "name": account["name"],
            "address": account["address"],
            "balance": balance
        })

    return jsonify({"accounts": account_status})

@app.route('/admin/api/token')
def get_token_status():
    """PAM 토큰 상태 API"""
    # 실제 토큰 우선 체크 (블록체인 모드)
    try:
        if os.path.exists('pam_token_config.json'):
            with open('pam_token_config.json', 'r') as f:
                config = json.load(f)

            if config.get('mode') == 'blockchain':
                token_id = config.get('token_id', '746506198')
                api_url = f"https://testnet-api.algonode.cloud/v2/assets/{token_id}"
                response = requests.get(api_url, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    params = data.get('params', {})

                    return jsonify({
                        "status": "active",
                        "mode": "blockchain",
                        "token_id": token_id,
                        "total_supply": params.get('total', 0),
                        "name": params.get('name', 'PAM-TALK ESG Token')
                    })

        # 시뮬레이션 토큰 폴백
        if os.path.exists('pam_token_simulation.json'):
            with open('pam_token_simulation.json', 'r') as f:
                sim_data = json.load(f)

            return jsonify({
                "status": "active",
                "mode": "simulation",
                "token_id": sim_data['token']['token_id'],
                "total_supply": sim_data['token']['total_supply'],
                "name": sim_data['token']['name']
            })

        return jsonify({"status": "inactive", "mode": "none"})

    except Exception as e:
        return jsonify({"status": "error", "mode": "unknown", "error": str(e)})

@app.route('/admin/api/logs')
def get_system_logs():
    """시스템 로그 API"""
    logs = [
        {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": "info",
            "message": "관리자 대시보드 접속"
        },
        {
            "timestamp": (datetime.now()).strftime("%H:%M:%S"),
            "level": "success",
            "message": "PAM-TALK 메인 서비스 정상 작동"
        },
        {
            "timestamp": (datetime.now()).strftime("%H:%M:%S"),
            "level": "warn",
            "message": "알고랜드 계정 펀딩 대기 중"
        },
        {
            "timestamp": (datetime.now()).strftime("%H:%M:%S"),
            "level": "info",
            "message": "시뮬레이션 토큰 활성화됨"
        }
    ]

    return jsonify({"logs": logs})

if __name__ == '__main__':
    print("PAM-TALK 관리자 대시보드 시작")
    print("접속 URL: http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=True)