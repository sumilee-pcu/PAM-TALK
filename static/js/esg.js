// ESG page specific JavaScript
class ESGManager {
    constructor() {
        this.api = window.pamtalkAPI;
        this.utils = window.pamtalkUtils;
        this.chartUtils = window.pamtalkChart;
        this.farms = [];
        this.esgDistributionChart = null;
        this.esgTrendChart = null;

        this.init();
    }

    async init() {
        await this.loadESGData();
        await this.loadFarms();
        this.setupEventListeners();
        this.createESGCharts();
        this.loadESGSuggestions();
    }

    async loadESGData() {
        try {
            // Load dashboard data for overall ESG statistics
            const dashboardData = await this.api.getDashboard();

            if (dashboardData.success) {
                this.updateESGStatistics(dashboardData.data);
                this.updateTokenStatistics();
            }
        } catch (error) {
            console.error('ESG 데이터 로딩 오류:', error);
            this.utils.showAlert('ESG 데이터를 불러올 수 없습니다.', 'danger');
        }
    }

    async loadFarms() {
        try {
            const farmsData = await this.api.getFarms();

            if (farmsData.success) {
                this.farms = farmsData.data.farms || [];
                this.renderESGFarmsTable();
                this.populateFarmSelector();
            }
        } catch (error) {
            console.error('농장 데이터 로딩 오류:', error);
            this.utils.showError('esg-farms-table', '농장 데이터를 불러올 수 없습니다.');
        }
    }

    updateESGStatistics(data) {
        const overallESG = data.ai_insights?.esg_average || 0;

        // Calculate component scores (simulate for demo)
        const environmentalScore = overallESG + (Math.random() - 0.5) * 10;
        const socialScore = overallESG + (Math.random() - 0.5) * 8;
        const governanceScore = overallESG + (Math.random() - 0.5) * 6;

        document.getElementById('overall-esg').textContent = overallESG.toFixed(1);
        document.getElementById('environmental-score').textContent = Math.max(0, environmentalScore).toFixed(1);
        document.getElementById('social-score').textContent = Math.max(0, socialScore).toFixed(1);
        document.getElementById('governance-score').textContent = Math.max(0, governanceScore).toFixed(1);
    }

    updateTokenStatistics() {
        // Simulate token statistics
        const totalTokens = Math.floor(Math.random() * 50000) + 10000;
        const monthlyTokens = Math.floor(Math.random() * 2000) + 500;
        const rewardFarms = Math.floor(Math.random() * 15) + 5;
        const avgReward = Math.floor(totalTokens / rewardFarms);

        document.getElementById('total-tokens').textContent = this.utils.formatNumber(totalTokens);
        document.getElementById('monthly-tokens').textContent = this.utils.formatNumber(monthlyTokens);
        document.getElementById('reward-farms').textContent = rewardFarms;
        document.getElementById('avg-reward').textContent = this.utils.formatNumber(avgReward);
    }

    createESGCharts() {
        this.createESGDistributionChart();
        this.createESGTrendChart();
    }

    createESGDistributionChart() {
        const ctx = document.getElementById('esg-distribution-chart').getContext('2d');

        // Simulate ESG score distribution
        const distributionData = {
            labels: ['우수 (80-100)', '양호 (70-79)', '보통 (60-69)', '미흡 (0-59)'],
            datasets: [{
                label: '농장 수',
                data: [3, 7, 4, 1],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',   // 우수 - 녹색
                    'rgba(23, 162, 184, 0.8)',  // 양호 - 청색
                    'rgba(255, 193, 7, 0.8)',   // 보통 - 황색
                    'rgba(220, 53, 69, 0.8)'    // 미흡 - 적색
                ],
                borderColor: [
                    'rgba(40, 167, 69, 1)',
                    'rgba(23, 162, 184, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 2
            }]
        };

        this.esgDistributionChart = this.chartUtils.createESGChart('esg-distribution-chart', distributionData);
    }

    createESGTrendChart() {
        const ctx = document.getElementById('esg-trend-chart').getContext('2d');

        // Generate monthly ESG trend data
        const months = [];
        const trendData = [];
        const now = new Date();

        for (let i = 5; i >= 0; i--) {
            const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
            months.push(date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'short' }));
            trendData.push((70 + Math.random() * 15).toFixed(1));
        }

        const chartData = {
            labels: months,
            datasets: [{
                label: '평균 ESG 점수',
                data: trendData,
                borderColor: 'rgb(40, 167, 69)',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgb(40, 167, 69)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        };

        const config = {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '월별 ESG 점수 추이'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 60,
                        max: 90,
                        title: {
                            display: true,
                            text: 'ESG 점수'
                        }
                    }
                }
            }
        };

        this.esgTrendChart = new Chart(ctx, config);
    }

    renderESGFarmsTable() {
        const tbody = document.getElementById('esg-farms-table');

        if (this.farms.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted">등록된 농장이 없습니다</td>
                </tr>
            `;
            return;
        }

        // Add simulated ESG data to farms
        const farmsWithESG = this.farms.map(farm => {
            const baseScore = 70 + Math.random() * 20;
            return {
                ...farm,
                esg_scores: {
                    overall: baseScore,
                    environmental: baseScore + (Math.random() - 0.5) * 10,
                    social: baseScore + (Math.random() - 0.5) * 8,
                    governance: baseScore + (Math.random() - 0.5) * 6
                },
                tokens_earned: Math.floor(Math.random() * 1000) + 100,
                last_updated: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
            };
        });

        // Sort farms based on selected criteria
        this.sortFarms(farmsWithESG);

        const rows = farmsWithESG.map(farm => {
            const esgScore = farm.esg_scores.overall;
            const certifications = farm.certifications || [];

            return `
                <tr>
                    <td>
                        <strong>${farm.farm_name}</strong>
                        <br>
                        <small class="text-muted">${farm.farm_id}</small>
                    </td>
                    <td>
                        <div class="esg-score-circle ${this.utils.getESGColor(esgScore)}"
                             style="width: 50px; height: 50px; font-size: 0.9rem;">
                            ${esgScore.toFixed(1)}
                        </div>
                    </td>
                    <td>
                        <div class="progress">
                            <div class="progress-bar bg-success" style="width: ${farm.esg_scores.environmental}%">
                                ${farm.esg_scores.environmental.toFixed(1)}
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="progress">
                            <div class="progress-bar bg-info" style="width: ${farm.esg_scores.social}%">
                                ${farm.esg_scores.social.toFixed(1)}
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="progress">
                            <div class="progress-bar bg-warning" style="width: ${farm.esg_scores.governance}%">
                                ${farm.esg_scores.governance.toFixed(1)}
                            </div>
                        </div>
                    </td>
                    <td>
                        <span class="badge bg-success">
                            <i class="fas fa-coins"></i> ${this.utils.formatNumber(farm.tokens_earned)}
                        </span>
                    </td>
                    <td>
                        ${certifications.map(cert =>
                            `<span class="badge bg-primary me-1">${cert}</span>`
                        ).join('')}
                    </td>
                    <td>
                        <small>${this.utils.formatDate(farm.last_updated)}</small>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1"
                                onclick="window.esgManager.viewESGDetails('${farm.farm_id}')"
                                title="상세 점수">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" data-role="admin"
                                onclick="window.esgManager.showTokenModal('${farm.farm_id}')"
                                title="토큰 발행">
                            <i class="fas fa-coins"></i>
                        </button>
                    </td>
                </tr>
            `;
        });

        tbody.innerHTML = rows.join('');

        // Apply role-based visibility
        this.applyRoleVisibility();
    }

    sortFarms(farms) {
        const sortBy = document.getElementById('esg-sort').value;

        switch (sortBy) {
            case 'score_desc':
                farms.sort((a, b) => (b.esg_scores?.overall || 0) - (a.esg_scores?.overall || 0));
                break;
            case 'score_asc':
                farms.sort((a, b) => (a.esg_scores?.overall || 0) - (b.esg_scores?.overall || 0));
                break;
            case 'name':
                farms.sort((a, b) => (a.farm_name || '').localeCompare(b.farm_name || ''));
                break;
            case 'tokens':
                farms.sort((a, b) => (b.tokens_earned || 0) - (a.tokens_earned || 0));
                break;
        }
    }

    populateFarmSelector() {
        const selector = document.getElementById('token-farm-id');
        selector.innerHTML = '<option value="">농장을 선택하세요</option>';

        this.farms.forEach(farm => {
            const option = document.createElement('option');
            option.value = farm.farm_id;
            option.textContent = `${farm.farm_name} (${farm.farm_id})`;
            selector.appendChild(option);
        });
    }

    loadESGSuggestions() {
        const container = document.getElementById('esg-suggestions');

        // Generate sample ESG improvement suggestions
        const suggestions = [
            {
                category: '환경 (Environmental)',
                icon: 'fas fa-leaf',
                color: 'success',
                items: [
                    '물 사용량을 10% 줄이면 환경 점수가 5점 향상됩니다.',
                    '재생에너지 비율을 80%까지 늘리면 추가 토큰 보상을 받을 수 있습니다.',
                    '유기농 인증을 받으면 환경 점수가 크게 향상됩니다.'
                ]
            },
            {
                category: '사회 (Social)',
                icon: 'fas fa-users',
                color: 'info',
                items: [
                    '지역 사회와의 협력 프로그램을 운영하면 사회 점수가 향상됩니다.',
                    '근로자 복지 개선을 통해 사회적 책임을 강화할 수 있습니다.',
                    '농산물 기부 활동으로 사회 기여도를 높일 수 있습니다.'
                ]
            },
            {
                category: '지배구조 (Governance)',
                icon: 'fas fa-balance-scale',
                color: 'warning',
                items: [
                    '투명한 재무 관리 시스템 도입으로 지배구조 점수를 높일 수 있습니다.',
                    '정기적인 감사 및 보고서 작성으로 신뢰성을 높일 수 있습니다.',
                    '이해관계자와의 소통 채널 확대가 필요합니다.'
                ]
            }
        ];

        const suggestionsHTML = suggestions.map(category => `
            <div class="row mb-3">
                <div class="col-12">
                    <h6 class="text-${category.color}">
                        <i class="${category.icon}"></i> ${category.category}
                    </h6>
                    <ul class="list-group list-group-flush">
                        ${category.items.map(item => `
                            <li class="list-group-item border-0 ps-0">
                                <i class="fas fa-arrow-right text-${category.color} me-2"></i>
                                ${item}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `).join('');

        container.innerHTML = suggestionsHTML;
    }

    async viewESGDetails(farmId) {
        try {
            const farm = this.farms.find(f => f.farm_id === farmId);
            if (!farm) {
                this.utils.showAlert('농장 정보를 찾을 수 없습니다.', 'warning');
                return;
            }

            this.renderESGDetailsModal(farm);
            const modal = new bootstrap.Modal(document.getElementById('esgDetailsModal'));
            modal.show();
        } catch (error) {
            console.error('ESG 상세 정보 오류:', error);
            this.utils.showAlert('ESG 상세 정보를 불러올 수 없습니다.', 'danger');
        }
    }

    renderESGDetailsModal(farm) {
        const content = document.getElementById('esg-details-content');

        // Simulate detailed ESG scores
        const esgDetails = {
            overall: 75.8,
            environmental: {
                score: 78.5,
                water_usage: 4800,
                carbon_emissions: 2.2,
                renewable_energy: 65,
                organic_certified: true
            },
            social: {
                score: 74.2,
                worker_welfare: 80,
                community_engagement: 70,
                fair_trade: true
            },
            governance: {
                score: 74.8,
                transparency: 75,
                compliance: 80,
                stakeholder_engagement: 70
            }
        };

        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>농장 기본 정보</h6>
                    <table class="table table-sm">
                        <tbody>
                            <tr><th>농장명:</th><td>${farm.farm_name}</td></tr>
                            <tr><th>소유자:</th><td>${farm.owner_name}</td></tr>
                            <tr><th>위치:</th><td>${farm.location}</td></tr>
                            <tr><th>면적:</th><td>${farm.size_hectares} ha</td></tr>
                        </tbody>
                    </table>

                    <h6>전체 ESG 점수</h6>
                    <div class="text-center mb-3">
                        <div class="esg-score-circle ${this.utils.getESGColor(esgDetails.overall)}"
                             style="width: 100px; height: 100px; font-size: 1.5rem;">
                            ${esgDetails.overall}
                        </div>
                        <p class="mt-2">${this.utils.getESGLabel(esgDetails.overall)} 성과</p>
                    </div>
                </div>

                <div class="col-md-6">
                    <h6>ESG 구성 점수</h6>

                    <div class="mb-3">
                        <div class="d-flex justify-content-between">
                            <span><i class="fas fa-leaf text-success"></i> 환경 (E)</span>
                            <strong>${esgDetails.environmental.score}</strong>
                        </div>
                        <div class="progress">
                            <div class="progress-bar bg-success" style="width: ${esgDetails.environmental.score}%"></div>
                        </div>
                        <small class="text-muted">
                            물 사용: ${esgDetails.environmental.water_usage}L/ha,
                            탄소: ${esgDetails.environmental.carbon_emissions}t/ha,
                            재생에너지: ${esgDetails.environmental.renewable_energy}%
                        </small>
                    </div>

                    <div class="mb-3">
                        <div class="d-flex justify-content-between">
                            <span><i class="fas fa-users text-info"></i> 사회 (S)</span>
                            <strong>${esgDetails.social.score}</strong>
                        </div>
                        <div class="progress">
                            <div class="progress-bar bg-info" style="width: ${esgDetails.social.score}%"></div>
                        </div>
                        <small class="text-muted">
                            근로자 복지: ${esgDetails.social.worker_welfare}/100,
                            지역사회 참여: ${esgDetails.social.community_engagement}/100
                        </small>
                    </div>

                    <div class="mb-3">
                        <div class="d-flex justify-content-between">
                            <span><i class="fas fa-balance-scale text-warning"></i> 지배구조 (G)</span>
                            <strong>${esgDetails.governance.score}</strong>
                        </div>
                        <div class="progress">
                            <div class="progress-bar bg-warning" style="width: ${esgDetails.governance.score}%"></div>
                        </div>
                        <small class="text-muted">
                            투명성: ${esgDetails.governance.transparency}/100,
                            컴플라이언스: ${esgDetails.governance.compliance}/100
                        </small>
                    </div>
                </div>
            </div>

            <div class="row mt-4">
                <div class="col-12">
                    <h6>인증 및 토큰</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="small">보유 인증</h6>
                            ${(farm.certifications || []).map(cert =>
                                `<span class="badge bg-primary me-1">${cert}</span>`
                            ).join('')}
                            ${esgDetails.environmental.organic_certified ?
                                '<span class="badge bg-success">유기농 인증</span>' : ''}
                            ${esgDetails.social.fair_trade ?
                                '<span class="badge bg-info">공정무역</span>' : ''}
                        </div>
                        <div class="col-md-6">
                            <h6 class="small">토큰 보상</h6>
                            <p class="mb-0">
                                <i class="fas fa-coins text-warning"></i>
                                총 ${Math.floor(Math.random() * 1000) + 500} ESG-GOLD 토큰 보유
                            </p>
                            <small class="text-muted">
                                마지막 보상: ${new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toLocaleDateString('ko-KR')}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    showTokenModal(farmId) {
        const farm = this.farms.find(f => f.farm_id === farmId);
        if (farm) {
            document.getElementById('token-farm-id').value = farmId;
            const modal = new bootstrap.Modal(document.getElementById('esgTokenModal'));
            modal.show();
        }
    }

    async issueTokens() {
        try {
            const farmId = document.getElementById('token-farm-id').value;
            const amount = parseInt(document.getElementById('token-amount').value);
            const reason = document.getElementById('token-reason').value;
            const memo = document.getElementById('token-memo').value;

            if (!farmId || !amount || amount <= 0) {
                this.utils.showAlert('모든 필수 정보를 입력해주세요.', 'warning');
                return;
            }

            // In a real application, this would call an API to issue tokens
            // For demo, we'll simulate the process
            await new Promise(resolve => setTimeout(resolve, 1000));

            this.utils.showAlert(
                `${farmId}에 ${amount} ESG-GOLD 토큰이 성공적으로 발행되었습니다.`,
                'success'
            );

            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('esgTokenModal'));
            modal.hide();
            document.getElementById('esg-token-form').reset();

            // Refresh data
            this.updateTokenStatistics();

        } catch (error) {
            console.error('토큰 발행 오류:', error);
            this.utils.showAlert('토큰 발행 중 오류가 발생했습니다.', 'danger');
        }
    }

    applyRoleVisibility() {
        const currentRole = this.api.getRole();
        const roleElements = document.querySelectorAll('[data-role]');

        roleElements.forEach(element => {
            const allowedRoles = element.dataset.role.split(',');
            element.style.display = allowedRoles.includes(currentRole) ? '' : 'none';
        });
    }

    setupEventListeners() {
        // ESG sort change
        document.getElementById('esg-sort').addEventListener('change', () => {
            this.renderESGFarmsTable();
        });

        // Token issuance
        document.getElementById('issue-tokens').addEventListener('click', () => {
            this.issueTokens();
        });

        // Role change handler
        window.addEventListener('roleChanged', (e) => {
            this.handleRoleChange(e.detail.role);
        });
    }

    handleRoleChange(role) {
        console.log('ESG 페이지 역할 변경:', role);
        this.applyRoleVisibility();

        // Reload data if needed based on role
        this.loadESGData();
    }
}

// Initialize ESG manager when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.esgManager = new ESGManager();
});