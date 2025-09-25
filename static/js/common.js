// PAM-TALK Dashboard Common JavaScript
class PAMTalkAPI {
    constructor() {
        this.baseURL = 'http://localhost:5000';
        this.currentRole = localStorage.getItem('pamtalk_role') || 'farmer';
    }

    // Generic API request method
    async request(endpoint, method = 'GET', data = null) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error?.message || 'API request failed');
            }

            return result;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // Health check
    async getHealth() {
        return await this.request('/api/health');
    }

    // Dashboard data
    async getDashboard() {
        return await this.request('/api/dashboard');
    }

    // Farm management
    async getFarms(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/api/farms?${queryString}` : '/api/farms';
        return await this.request(endpoint);
    }

    async getFarm(farmId) {
        return await this.request(`/api/farms/${farmId}`);
    }

    async registerFarm(farmData) {
        return await this.request('/api/farms', 'POST', farmData);
    }

    async getFarmPrediction(farmId, days = 7) {
        return await this.request(`/api/farms/${farmId}/predict?days=${days}`);
    }

    // Transaction management
    async getTransactions(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/api/transactions?${queryString}` : '/api/transactions';
        return await this.request(endpoint);
    }

    async createTransaction(transactionData) {
        return await this.request('/api/transactions', 'POST', transactionData);
    }

    async checkAnomalies(transactionData) {
        return await this.request('/api/transactions/check', 'POST', transactionData);
    }

    async getESGScore(transactionId, participant = 'producer') {
        return await this.request(`/api/transactions/${transactionId}/esg?participant=${participant}`);
    }

    // Role management
    setRole(role) {
        this.currentRole = role;
        localStorage.setItem('pamtalk_role', role);
        window.dispatchEvent(new CustomEvent('roleChanged', { detail: { role } }));
    }

    getRole() {
        return this.currentRole;
    }
}

// Utility functions
class Utils {
    static formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    }

    static formatCurrency(amount) {
        return '₩' + amount.toLocaleString();
    }

    static formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('ko-KR');
    }

    static formatDateTime(dateString) {
        return new Date(dateString).toLocaleString('ko-KR');
    }

    static getStatusBadge(status) {
        const statusMap = {
            'active': 'status-active',
            'inactive': 'status-inactive',
            'pending': 'status-pending',
            'completed': 'status-completed'
        };
        return statusMap[status] || 'secondary';
    }

    static getESGColor(score) {
        if (score >= 80) return 'esg-excellent';
        if (score >= 70) return 'esg-good';
        if (score >= 60) return 'esg-fair';
        return 'esg-poor';
    }

    static getESGLabel(score) {
        if (score >= 80) return '우수';
        if (score >= 70) return '양호';
        if (score >= 60) return '보통';
        return '미흡';
    }

    static showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            `;
        }
    }

    static showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle"></i>
                    오류: ${message}
                </div>
            `;
        }
    }

    static showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-info-circle"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = alertHtml;
            setTimeout(() => {
                alertContainer.innerHTML = '';
            }, 5000);
        }
    }
}

// Chart utilities
class ChartUtils {
    static createDemandChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');

        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '수요 예측 그래프'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '수요량 (kg)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '날짜'
                    }
                }
            }
        };

        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: { ...defaultOptions, ...options }
        });
    }

    static createESGChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');

        return new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'ESG 점수 분포'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    static createTransactionChart(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');

        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '월별 거래량'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '거래 건수'
                        }
                    }
                }
            }
        });
    }
}

// Role-based view controller
class RoleController {
    constructor() {
        this.api = new PAMTalkAPI();
        this.initializeRoleSelector();
        this.setupEventListeners();
    }

    initializeRoleSelector() {
        const roleSelector = document.getElementById('role-selector');
        if (roleSelector) {
            const currentRole = this.api.getRole();
            roleSelector.innerHTML = `
                <div class="d-flex justify-content-center">
                    <button class="role-btn ${currentRole === 'farmer' ? 'active' : ''}"
                            data-role="farmer">
                        <i class="fas fa-tractor"></i> 농장주
                    </button>
                    <button class="role-btn ${currentRole === 'consumer' ? 'active' : ''}"
                            data-role="consumer">
                        <i class="fas fa-shopping-cart"></i> 소비자
                    </button>
                    <button class="role-btn ${currentRole === 'admin' ? 'active' : ''}"
                            data-role="admin">
                        <i class="fas fa-cog"></i> 관리자
                    </button>
                </div>
            `;
        }
    }

    setupEventListeners() {
        // Role button click handlers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('role-btn')) {
                const role = e.target.dataset.role;
                this.switchRole(role);
            }
        });

        // Listen for role changes
        window.addEventListener('roleChanged', (e) => {
            this.updateView(e.detail.role);
        });
    }

    switchRole(role) {
        this.api.setRole(role);

        // Update active button
        document.querySelectorAll('.role-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-role="${role}"]`).classList.add('active');
    }

    updateView(role) {
        // This method should be overridden by each page
        console.log('Role switched to:', role);
    }
}

// Initialize common functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize API and utilities
    window.pamtalkAPI = new PAMTalkAPI();
    window.pamtalkUtils = Utils;
    window.pamtalkChart = ChartUtils;

    // Initialize role controller
    window.roleController = new RoleController();

    // Add current year to footer
    const yearSpan = document.getElementById('current-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Add fade-in animation to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }

    // Health check on page load
    pamtalkAPI.getHealth().then(result => {
        if (result.success) {
            console.log('API 서버 연결됨:', result.data.status);
        }
    }).catch(error => {
        console.error('API 서버 연결 실패:', error);
        pamtalkUtils.showAlert('API 서버에 연결할 수 없습니다. 서버를 확인해주세요.', 'danger');
    });
});