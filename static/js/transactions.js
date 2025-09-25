// Transactions page specific JavaScript
class TransactionsManager {
    constructor() {
        this.api = window.pamtalkAPI;
        this.utils = window.pamtalkUtils;
        this.chartUtils = window.pamtalkChart;
        this.transactions = [];
        this.transactionChart = null;

        this.init();
    }

    async init() {
        await this.loadTransactions();
        this.setupEventListeners();
        this.updateStatistics();
        this.loadTransactionChart();
        this.loadAnomalyStatus();
    }

    async loadTransactions() {
        try {
            this.utils.showLoading('transactions-table');

            const filters = this.getFilterParams();
            const transactionsData = await this.api.getTransactions(filters);

            if (transactionsData.success) {
                this.transactions = transactionsData.data.transactions || [];
                this.renderTransactionsTable();
            } else {
                throw new Error('거래 데이터 로딩 실패');
            }
        } catch (error) {
            console.error('거래 데이터 로딩 오류:', error);
            this.utils.showError('transactions-table', '거래 데이터를 불러올 수 없습니다.');
        }
    }

    getFilterParams() {
        const params = {};

        const farmId = document.getElementById('farm-filter').value;
        if (farmId) params.farm_id = farmId;

        const productType = document.getElementById('product-filter').value;
        if (productType) params.product_type = productType;

        const startDate = document.getElementById('start-date').value;
        if (startDate) params.start_date = startDate;

        const endDate = document.getElementById('end-date').value;
        if (endDate) params.end_date = endDate;

        const limit = document.getElementById('limit-filter').value;
        if (limit) params.limit = parseInt(limit);

        return params;
    }

    updateStatistics() {
        const totalTransactions = this.transactions.length;
        const totalValue = this.transactions.reduce((sum, tx) =>
            sum + (tx.quantity * tx.price_per_unit || 0), 0);
        const avgTransaction = totalTransactions > 0 ? totalValue / totalTransactions : 0;

        // Simulate anomaly rate (in real app, this would come from API)
        const anomalyRate = Math.random() * 5; // 0-5%

        document.getElementById('total-transactions').textContent =
            this.utils.formatNumber(totalTransactions);

        document.getElementById('total-volume').textContent =
            this.utils.formatCurrency(totalValue);

        document.getElementById('avg-transaction').textContent =
            this.utils.formatCurrency(avgTransaction);

        document.getElementById('anomaly-rate').textContent =
            anomalyRate.toFixed(1) + '%';
    }

    renderTransactionsTable() {
        const tbody = document.getElementById('transactions-table');

        if (this.transactions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="11" class="text-center text-muted">거래 내역이 없습니다</td>
                </tr>
            `;
            return;
        }

        const rows = this.transactions.map(tx => {
            const totalAmount = (tx.quantity || 0) * (tx.price_per_unit || 0);

            return `
                <tr>
                    <td>
                        <small class="text-muted">${tx.transaction_id || 'N/A'}</small>
                    </td>
                    <td>
                        <small>${this.utils.formatDateTime(tx.timestamp || new Date().toISOString())}</small>
                    </td>
                    <td>${tx.producer_id || 'N/A'}</td>
                    <td>${tx.consumer_id || 'N/A'}</td>
                    <td>
                        <span class="badge bg-success">${tx.product_type || 'N/A'}</span>
                    </td>
                    <td>${this.utils.formatNumber(tx.quantity || 0)}kg</td>
                    <td>${this.utils.formatCurrency(tx.price_per_unit || 0)}</td>
                    <td><strong>${this.utils.formatCurrency(totalAmount)}</strong></td>
                    <td>
                        <div class="esg-score-circle ${this.utils.getESGColor(tx.esg_score || 0)}"
                             style="width: 30px; height: 30px; font-size: 0.7rem;">
                            ${(tx.esg_score || 0).toFixed(0)}
                        </div>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-warning"
                                onclick="window.transactionsManager.checkTransactionAnomaly('${tx.transaction_id || ''}')"
                                title="이상 탐지 확인">
                            <i class="fas fa-search"></i>
                        </button>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1"
                                onclick="window.transactionsManager.viewTransactionDetails('${tx.transaction_id || ''}')"
                                title="상세 보기">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info"
                                onclick="window.transactionsManager.getESGScore('${tx.transaction_id || ''}')"
                                title="ESG 점수">
                            <i class="fas fa-leaf"></i>
                        </button>
                    </td>
                </tr>
            `;
        });

        tbody.innerHTML = rows.join('');
    }

    loadTransactionChart() {
        // Generate sample monthly transaction data
        const months = [];
        const transactionCounts = [];
        const now = new Date();

        for (let i = 5; i >= 0; i--) {
            const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
            months.push(date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'short' }));
            transactionCounts.push(Math.floor(Math.random() * 50) + 20);
        }

        const chartData = {
            labels: months,
            datasets: [{
                label: '거래 건수',
                data: transactionCounts,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2
            }]
        };

        this.transactionChart = this.chartUtils.createTransactionChart('transaction-chart', chartData);
    }

    async loadAnomalyStatus() {
        try {
            const container = document.getElementById('anomaly-summary');

            // Sample anomaly status
            const anomalyStats = {
                total_checks: Math.floor(Math.random() * 100) + 50,
                anomalies_detected: Math.floor(Math.random() * 5),
                risk_levels: {
                    high: Math.floor(Math.random() * 2),
                    medium: Math.floor(Math.random() * 3),
                    low: Math.floor(Math.random() * 10)
                }
            };

            container.innerHTML = `
                <div class="row text-center">
                    <div class="col-12 mb-3">
                        <h6>총 검사: ${anomalyStats.total_checks}건</h6>
                        <h6>이상 탐지: ${anomalyStats.anomalies_detected}건</h6>
                    </div>
                </div>
                <div class="row text-center">
                    <div class="col-4">
                        <div class="text-danger">
                            <strong>${anomalyStats.risk_levels.high}</strong>
                            <br><small>고위험</small>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="text-warning">
                            <strong>${anomalyStats.risk_levels.medium}</strong>
                            <br><small>중위험</small>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="text-info">
                            <strong>${anomalyStats.risk_levels.low}</strong>
                            <br><small>저위험</small>
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <div class="progress">
                        <div class="progress-bar bg-success" role="progressbar"
                             style="width: ${((anomalyStats.total_checks - anomalyStats.anomalies_detected) / anomalyStats.total_checks * 100).toFixed(1)}%">
                            정상
                        </div>
                        <div class="progress-bar bg-warning" role="progressbar"
                             style="width: ${(anomalyStats.anomalies_detected / anomalyStats.total_checks * 100).toFixed(1)}%">
                            이상
                        </div>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('이상 탐지 현황 로딩 오류:', error);
            document.getElementById('anomaly-summary').innerHTML = `
                <div class="alert alert-warning">
                    이상 탐지 현황을 불러올 수 없습니다.
                </div>
            `;
        }
    }

    async createTransaction() {
        try {
            const transactionData = {
                producer_id: document.getElementById('producer-id').value,
                consumer_id: document.getElementById('consumer-id').value,
                product_type: document.getElementById('transaction-product').value,
                quantity: parseInt(document.getElementById('quantity').value),
                price_per_unit: parseInt(document.getElementById('price-per-unit').value),
                quality_score: parseInt(document.getElementById('quality-score').value) || 85,
                esg_score: parseInt(document.getElementById('esg-score').value) || 75,
                location: document.getElementById('transaction-location').value || 'Seoul',
                payment_method: document.getElementById('payment-method').value,
                delivery_time_hours: parseInt(document.getElementById('delivery-time').value) || 24,
                metadata: {
                    note: document.getElementById('transaction-note').value
                }
            };

            const result = await this.api.createTransaction(transactionData);

            if (result.success) {
                this.utils.showAlert('거래가 성공적으로 생성되었습니다.', 'success');

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
                modal.hide();

                // Reset form
                document.getElementById('transaction-form').reset();

                // Reload transactions
                await this.loadTransactions();
                this.updateStatistics();
            } else {
                throw new Error(result.error?.message || '거래 생성에 실패했습니다');
            }
        } catch (error) {
            console.error('거래 생성 오류:', error);
            this.utils.showAlert('거래 생성 중 오류가 발생했습니다: ' + error.message, 'danger');
        }
    }

    async checkTransactionAnomaly(transactionId) {
        try {
            // Get transaction data for anomaly check
            const transaction = this.transactions.find(tx => tx.transaction_id === transactionId);
            if (!transaction) {
                this.utils.showAlert('거래 정보를 찾을 수 없습니다.', 'warning');
                return;
            }

            const anomalyData = {
                producer_id: transaction.producer_id,
                consumer_id: transaction.consumer_id,
                product_type: transaction.product_type,
                quantity: transaction.quantity,
                price_per_unit: transaction.price_per_unit,
                quality_score: transaction.quality_score,
                esg_score: transaction.esg_score
            };

            const result = await this.api.checkAnomalies(anomalyData);

            if (result.success) {
                const isAnomaly = result.data.is_anomaly;
                const riskLevel = result.data.risk_level;
                const score = result.data.anomaly_score;

                const alertType = isAnomaly ? 'warning' : 'success';
                const message = isAnomaly
                    ? `이상 거래 탐지! 위험도: ${riskLevel}, 점수: ${score.toFixed(3)}`
                    : `정상 거래입니다. 점수: ${score.toFixed(3)}`;

                this.utils.showAlert(message, alertType);
            } else {
                throw new Error('이상 탐지 검사에 실패했습니다');
            }
        } catch (error) {
            console.error('이상 탐지 오류:', error);
            this.utils.showAlert('이상 탐지 검사 중 오류가 발생했습니다.', 'danger');
        }
    }

    async checkAnomalyFromForm() {
        try {
            const transactionData = {
                producer_id: document.getElementById('producer-id').value,
                consumer_id: document.getElementById('consumer-id').value,
                product_type: document.getElementById('transaction-product').value,
                quantity: parseInt(document.getElementById('quantity').value),
                price_per_unit: parseInt(document.getElementById('price-per-unit').value),
                quality_score: parseInt(document.getElementById('quality-score').value) || 85,
                esg_score: parseInt(document.getElementById('esg-score').value) || 75
            };

            const result = await this.api.checkAnomalies(transactionData);

            if (result.success) {
                const isAnomaly = result.data.is_anomaly;
                const riskLevel = result.data.risk_level;
                const score = result.data.anomaly_score;

                const alertClass = isAnomaly ? 'alert-warning' : 'alert-success';
                const icon = isAnomaly ? 'fa-exclamation-triangle' : 'fa-check-circle';
                const message = isAnomaly
                    ? `⚠️ 이상 거래 의심 (위험도: ${riskLevel}, 점수: ${score.toFixed(3)})`
                    : `✅ 정상 거래 (점수: ${score.toFixed(3)})`;

                // Show result in modal
                const existingAlert = document.querySelector('#transactionModal .anomaly-result');
                if (existingAlert) {
                    existingAlert.remove();
                }

                const alertDiv = document.createElement('div');
                alertDiv.className = `alert ${alertClass} anomaly-result mt-3`;
                alertDiv.innerHTML = `<i class="fas ${icon}"></i> ${message}`;

                document.querySelector('#transactionModal .modal-body').appendChild(alertDiv);
            } else {
                throw new Error('이상 탐지 검사에 실패했습니다');
            }
        } catch (error) {
            console.error('이상 탐지 오류:', error);
            this.utils.showAlert('이상 탐지 검사 중 오류가 발생했습니다.', 'danger');
        }
    }

    async viewTransactionDetails(transactionId) {
        try {
            const transaction = this.transactions.find(tx => tx.transaction_id === transactionId);
            if (!transaction) {
                this.utils.showAlert('거래 정보를 찾을 수 없습니다.', 'warning');
                return;
            }

            this.renderTransactionDetailsModal(transaction);
            const modal = new bootstrap.Modal(document.getElementById('transactionDetailsModal'));
            modal.show();
        } catch (error) {
            console.error('거래 상세 정보 오류:', error);
            this.utils.showAlert('거래 상세 정보를 불러올 수 없습니다.', 'danger');
        }
    }

    renderTransactionDetailsModal(transaction) {
        const content = document.getElementById('transaction-details-content');
        const totalAmount = (transaction.quantity || 0) * (transaction.price_per_unit || 0);

        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>거래 기본 정보</h6>
                    <table class="table table-sm">
                        <tbody>
                            <tr><th>거래 ID:</th><td>${transaction.transaction_id || 'N/A'}</td></tr>
                            <tr><th>생성 시간:</th><td>${this.utils.formatDateTime(transaction.timestamp || '')}</td></tr>
                            <tr><th>생산자:</th><td>${transaction.producer_id || 'N/A'}</td></tr>
                            <tr><th>소비자:</th><td>${transaction.consumer_id || 'N/A'}</td></tr>
                            <tr><th>품목:</th><td>
                                <span class="badge bg-success">${transaction.product_type || 'N/A'}</span>
                            </td></tr>
                            <tr><th>수량:</th><td>${this.utils.formatNumber(transaction.quantity || 0)} kg</td></tr>
                            <tr><th>단가:</th><td>${this.utils.formatCurrency(transaction.price_per_unit || 0)}</td></tr>
                            <tr><th>총액:</th><td><strong>${this.utils.formatCurrency(totalAmount)}</strong></td></tr>
                        </tbody>
                    </table>
                </div>

                <div class="col-md-6">
                    <h6>품질 및 ESG 정보</h6>
                    <table class="table table-sm">
                        <tbody>
                            <tr><th>품질 점수:</th><td>
                                <div class="progress">
                                    <div class="progress-bar" style="width: ${transaction.quality_score || 0}%">
                                        ${transaction.quality_score || 0}/100
                                    </div>
                                </div>
                            </td></tr>
                            <tr><th>ESG 점수:</th><td>
                                <div class="esg-score-circle ${this.utils.getESGColor(transaction.esg_score || 0)}"
                                     style="width: 50px; height: 50px; font-size: 0.9rem;">
                                    ${(transaction.esg_score || 0).toFixed(1)}
                                </div>
                            </td></tr>
                            <tr><th>위치:</th><td>${transaction.location || 'N/A'}</td></tr>
                            <tr><th>결제 방법:</th><td>${transaction.payment_method || 'N/A'}</td></tr>
                            <tr><th>배송 시간:</th><td>${transaction.delivery_time_hours || 'N/A'} 시간</td></tr>
                        </tbody>
                    </table>

                    <h6>추가 정보</h6>
                    <div class="alert alert-info">
                        <strong>메모:</strong> ${transaction.metadata?.note || '없음'}
                    </div>
                </div>
            </div>

            <div class="row mt-3">
                <div class="col-12">
                    <div class="d-flex justify-content-center gap-2">
                        <button class="btn btn-warning" onclick="window.transactionsManager.checkTransactionAnomaly('${transaction.transaction_id || ''}')">
                            <i class="fas fa-search"></i> 이상 탐지 검사
                        </button>
                        <button class="btn btn-info" onclick="window.transactionsManager.getESGScore('${transaction.transaction_id || ''}')">
                            <i class="fas fa-leaf"></i> ESG 상세 점수
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    async getESGScore(transactionId) {
        try {
            const esgResult = await this.api.getESGScore(transactionId, 'producer');

            if (esgResult.success) {
                const esgData = esgResult.data;
                this.utils.showAlert(
                    `ESG 점수: ${esgData.total_score || 'N/A'} (환경: ${esgData.environmental || 'N/A'}, 사회: ${esgData.social || 'N/A'}, 지배구조: ${esgData.governance || 'N/A'})`,
                    'info'
                );
            } else {
                throw new Error('ESG 점수를 불러올 수 없습니다');
            }
        } catch (error) {
            console.error('ESG 점수 오류:', error);
            this.utils.showAlert('ESG 점수를 불러오는 중 오류가 발생했습니다.', 'danger');
        }
    }

    updateTotalAmount() {
        const quantity = parseFloat(document.getElementById('quantity').value) || 0;
        const pricePerUnit = parseFloat(document.getElementById('price-per-unit').value) || 0;
        const totalAmount = quantity * pricePerUnit;

        document.getElementById('total-amount').value =
            totalAmount > 0 ? this.utils.formatCurrency(totalAmount) : '';
    }

    setupEventListeners() {
        // Filter controls
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.loadTransactions();
        });

        document.getElementById('refresh-transactions').addEventListener('click', () => {
            this.loadTransactions();
        });

        // Transaction creation
        document.getElementById('create-transaction').addEventListener('click', () => {
            this.createTransaction();
        });

        document.getElementById('check-anomaly').addEventListener('click', () => {
            this.checkAnomalyFromForm();
        });

        // Auto-calculate total amount
        ['quantity', 'price-per-unit'].forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.updateTotalAmount();
            });
        });

        // Role change handler
        window.addEventListener('roleChanged', (e) => {
            this.handleRoleChange(e.detail.role);
        });
    }

    handleRoleChange(role) {
        console.log('거래 내역 페이지 역할 변경:', role);

        // Show/hide role-specific elements
        const roleElements = document.querySelectorAll('[data-role]');
        roleElements.forEach(element => {
            const allowedRoles = element.dataset.role.split(',');
            element.style.display = allowedRoles.includes(role) ? 'block' : 'none';
        });

        // Reload data if needed based on role
        this.loadTransactions();
    }
}

// Initialize transactions manager when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.transactionsManager = new TransactionsManager();
});