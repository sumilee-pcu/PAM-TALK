// Dashboard specific JavaScript
class Dashboard {
    constructor() {
        this.api = window.pamtalkAPI;
        this.utils = window.pamtalkUtils;
        this.chartUtils = window.pamtalkChart;
        this.demandChart = null;
        this.refreshInterval = null;

        this.init();
    }

    async init() {
        await this.loadDashboardData();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    async loadDashboardData() {
        try {
            // Load main dashboard data
            const dashboardData = await this.api.getDashboard();

            if (dashboardData.success) {
                this.updateStatistics(dashboardData.data);
                this.updateRecentTransactions(dashboardData.data.transactions);
                await this.loadDemandPrediction();
                this.loadAnomalyAlerts();
            }
        } catch (error) {
            console.error('대시보드 데이터 로딩 실패:', error);
            this.utils.showAlert('대시보드 데이터를 불러올 수 없습니다.', 'danger');
        }
    }

    updateStatistics(data) {
        // Update overview statistics
        document.getElementById('total-farms').textContent =
            this.utils.formatNumber(data.overview.total_farms || 0);

        document.getElementById('total-transactions').textContent =
            this.utils.formatNumber(data.overview.total_transactions || 0);

        document.getElementById('avg-esg').textContent =
            (data.ai_insights.esg_average || 0).toFixed(1);

        document.getElementById('total-revenue').textContent =
            this.utils.formatCurrency(data.transactions.total_value || 0);

        // Update ESG circle
        const esgScore = data.ai_insights.esg_average || 0;
        const esgCircle = document.getElementById('esg-circle');
        const esgDisplay = document.getElementById('esg-score-display');
        const esgDescription = document.getElementById('esg-description');

        esgDisplay.textContent = esgScore.toFixed(1);
        esgCircle.className = `esg-score-circle ${this.utils.getESGColor(esgScore)}`;
        esgDescription.textContent = `${this.utils.getESGLabel(esgScore)} ESG 성과`;
    }

    updateRecentTransactions(transactionData) {
        const tbody = document.getElementById('recent-transactions');

        if (!transactionData.recent_activity || transactionData.recent_activity.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted">최근 거래가 없습니다</td>
                </tr>
            `;
            return;
        }

        const rows = transactionData.recent_activity.slice(0, 5).map(tx => {
            return `
                <tr>
                    <td>${this.utils.formatDateTime(tx.timestamp || new Date().toISOString())}</td>
                    <td>
                        <span class="badge bg-primary">거래</span>
                    </td>
                    <td>${tx.producer_id || 'N/A'}</td>
                    <td>${tx.product_type || 'N/A'}</td>
                    <td>${this.utils.formatNumber(tx.quantity || 0)}kg</td>
                    <td>${this.utils.formatCurrency(tx.total_value || 0)}</td>
                    <td>
                        <span class="badge ${this.utils.getStatusBadge(tx.status || 'completed')}">
                            ${tx.status || '완료'}
                        </span>
                    </td>
                </tr>
            `;
        });

        tbody.innerHTML = rows.join('');
    }

    async loadDemandPrediction() {
        try {
            const currentProduct = document.getElementById('product-selector').value;

            // Get a sample farm for prediction
            const farmsData = await this.api.getFarms();
            if (farmsData.success && farmsData.data.farms.length > 0) {
                const farmId = farmsData.data.farms[0].farm_id;
                const predictionData = await this.api.getFarmPrediction(farmId, 14);

                if (predictionData.success) {
                    this.renderDemandChart(predictionData.data);
                }
            } else {
                // Create sample data for demo
                this.renderSampleDemandChart();
            }
        } catch (error) {
            console.error('수요 예측 데이터 로딩 실패:', error);
            this.renderSampleDemandChart();
        }
    }

    renderDemandChart(predictionData) {
        const ctx = document.getElementById('demand-chart').getContext('2d');

        // Destroy existing chart
        if (this.demandChart) {
            this.demandChart.destroy();
        }

        const chartData = {
            labels: predictionData.predictions.map(p =>
                new Date(p.date).toLocaleDateString('ko-KR')
            ),
            datasets: [
                {
                    label: '예측 수요',
                    data: predictionData.predictions.map(p => p.predicted_demand),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '신뢰구간 (상한)',
                    data: predictionData.predictions.map(p => p.confidence_upper),
                    borderColor: 'rgba(255, 99, 132, 0.5)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false
                },
                {
                    label: '신뢰구간 (하한)',
                    data: predictionData.predictions.map(p => p.confidence_lower),
                    borderColor: 'rgba(255, 99, 132, 0.5)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false
                }
            ]
        };

        this.demandChart = this.chartUtils.createDemandChart('demand-chart', chartData);
    }

    renderSampleDemandChart() {
        const ctx = document.getElementById('demand-chart').getContext('2d');

        if (this.demandChart) {
            this.demandChart.destroy();
        }

        // Generate sample data for the next 14 days
        const dates = [];
        const predictions = [];
        const upperBounds = [];
        const lowerBounds = [];

        for (let i = 0; i < 14; i++) {
            const date = new Date();
            date.setDate(date.getDate() + i);
            dates.push(date.toLocaleDateString('ko-KR'));

            const baseDemand = 1000 + Math.sin(i * 0.5) * 200 + Math.random() * 100;
            predictions.push(Math.round(baseDemand));
            upperBounds.push(Math.round(baseDemand * 1.2));
            lowerBounds.push(Math.round(baseDemand * 0.8));
        }

        const chartData = {
            labels: dates,
            datasets: [
                {
                    label: '예측 수요',
                    data: predictions,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '신뢰구간 (상한)',
                    data: upperBounds,
                    borderColor: 'rgba(255, 99, 132, 0.5)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false
                },
                {
                    label: '신뢰구간 (하한)',
                    data: lowerBounds,
                    borderColor: 'rgba(255, 99, 132, 0.5)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false
                }
            ]
        };

        this.demandChart = this.chartUtils.createDemandChart('demand-chart', chartData);
    }

    async loadAnomalyAlerts() {
        try {
            const alertContainer = document.getElementById('anomaly-alerts');

            // Get recent transactions to check for anomalies
            const transactionsData = await this.api.getTransactions({limit: 10});

            if (transactionsData.success && transactionsData.data.transactions.length > 0) {
                const alerts = [];

                // Check some transactions for anomalies
                for (const tx of transactionsData.data.transactions.slice(0, 3)) {
                    try {
                        const anomalyResult = await this.api.checkAnomalies({
                            producer_id: tx.producer_id,
                            consumer_id: tx.consumer_id,
                            product_type: tx.product_type,
                            quantity: tx.quantity,
                            price_per_unit: tx.price_per_unit
                        });

                        if (anomalyResult.success && anomalyResult.data.is_anomaly) {
                            alerts.push({
                                type: 'anomaly',
                                message: `이상 거래 탐지: ${tx.product_type} (${tx.producer_id})`,
                                risk: anomalyResult.data.risk_level,
                                time: tx.timestamp
                            });
                        }
                    } catch (error) {
                        // Skip this transaction if anomaly check fails
                        continue;
                    }
                }

                // Add some sample alerts for demo
                if (alerts.length === 0) {
                    alerts.push(
                        {
                            type: 'info',
                            message: '모든 거래가 정상 범위 내에 있습니다.',
                            risk: 'LOW',
                            time: new Date().toISOString()
                        }
                    );
                }

                this.renderAnomalyAlerts(alerts);
            } else {
                this.renderNoAnomalyAlerts();
            }
        } catch (error) {
            console.error('이상 거래 알림 로딩 실패:', error);
            this.renderNoAnomalyAlerts();
        }
    }

    renderAnomalyAlerts(alerts) {
        const container = document.getElementById('anomaly-alerts');

        const alertHtml = alerts.map(alert => {
            const alertClass = alert.type === 'anomaly' ? 'alert-warning' : 'alert-info';
            const icon = alert.type === 'anomaly' ? 'fa-exclamation-triangle' : 'fa-info-circle';

            return `
                <div class="alert ${alertClass} py-2 mb-2">
                    <div class="d-flex align-items-center">
                        <i class="fas ${icon} me-2"></i>
                        <div class="flex-grow-1">
                            <small class="fw-bold">${alert.message}</small>
                            <br>
                            <small class="text-muted">
                                위험도: ${alert.risk} |
                                ${this.utils.formatDateTime(alert.time)}
                            </small>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = alertHtml;
    }

    renderNoAnomalyAlerts() {
        const container = document.getElementById('anomaly-alerts');
        container.innerHTML = `
            <div class="alert alert-success py-2">
                <div class="d-flex align-items-center">
                    <i class="fas fa-check-circle me-2"></i>
                    <small>현재 이상 거래가 감지되지 않았습니다.</small>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        // Product selector change
        document.getElementById('product-selector').addEventListener('change', () => {
            this.loadDemandPrediction();
        });

        // Role change handler
        window.addEventListener('roleChanged', (e) => {
            this.handleRoleChange(e.detail.role);
        });
    }

    handleRoleChange(role) {
        console.log('대시보드 역할 변경:', role);

        // Refresh data based on role
        this.loadDashboardData();

        // Update UI elements based on role
        const roleSpecificElements = document.querySelectorAll('[data-role]');
        roleSpecificElements.forEach(element => {
            const allowedRoles = element.dataset.role.split(',');
            element.style.display = allowedRoles.includes(role) ? 'block' : 'none';
        });
    }

    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new Dashboard();
});

// Clean up when leaving page
window.addEventListener('beforeunload', function() {
    if (window.dashboard) {
        window.dashboard.stopAutoRefresh();
    }
});