// Analytics page specific JavaScript
class AnalyticsManager {
    constructor() {
        this.api = window.pamtalkAPI;
        this.utils = window.pamtalkUtils;
        this.chartUtils = window.pamtalkChart;
        this.farms = [];
        this.charts = {
            main: null,
            anomaly: null,
            esg: null
        };
        this.analysisResults = [];

        this.init();
    }

    async init() {
        await this.loadInitialData();
        this.setupEventListeners();
        this.initializeCharts();
        this.updateModelPerformance();

        // Check for URL parameters (farm filter from other pages)
        const urlParams = new URLSearchParams(window.location.search);
        const farmParam = urlParams.get('farm');
        if (farmParam) {
            document.getElementById('farm-selector').value = farmParam;
            this.runAnalysis();
        }
    }

    async loadInitialData() {
        try {
            // Load farms for selector
            const farmsData = await this.api.getFarms();
            if (farmsData.success) {
                this.farms = farmsData.data.farms || [];
                this.populateFarmSelector();
            }

            // Load dashboard data for statistics
            const dashboardData = await this.api.getDashboard();
            if (dashboardData.success) {
                this.updateAnalyticsStatistics(dashboardData.data);
            }
        } catch (error) {
            console.error('초기 데이터 로딩 오류:', error);
            this.utils.showAlert('분석 데이터를 불러올 수 없습니다.', 'danger');
        }
    }

    populateFarmSelector() {
        const selector = document.getElementById('farm-selector');
        selector.innerHTML = '<option value="">전체 농장</option>';

        this.farms.forEach(farm => {
            const option = document.createElement('option');
            option.value = farm.farm_id;
            option.textContent = `${farm.farm_name} (${farm.farm_id})`;
            selector.appendChild(option);
        });
    }

    updateAnalyticsStatistics(data) {
        // Update statistics with processing stats
        const processingStats = data.processing_stats || {};

        document.getElementById('total-predictions').textContent =
            this.utils.formatNumber(processingStats.total_predictions || 0);

        document.getElementById('prediction-accuracy').textContent =
            `${((processingStats.success_rate || 0.85) * 100).toFixed(1)}%`;

        document.getElementById('anomalies-detected').textContent =
            this.utils.formatNumber(processingStats.total_anomalies || 0);

        document.getElementById('ai-confidence').textContent =
            `${((processingStats.avg_confidence || 0.8) * 100).toFixed(1)}%`;
    }

    initializeCharts() {
        this.createMainAnalysisChart();
        this.createAnomalyChart();
        this.createESGAnalysisChart();
    }

    createMainAnalysisChart() {
        const ctx = document.getElementById('main-analysis-chart').getContext('2d');

        // Initial empty chart
        this.charts.main = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'AI 분석 결과'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    createAnomalyChart() {
        const ctx = document.getElementById('anomaly-chart').getContext('2d');

        // Sample anomaly detection data
        const anomalyData = {
            labels: ['정상', '의심', '위험'],
            datasets: [{
                label: '거래 건수',
                data: [85, 12, 3],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',   // 정상 - 녹색
                    'rgba(255, 193, 7, 0.8)',   // 의심 - 황색
                    'rgba(220, 53, 69, 0.8)'    // 위험 - 적색
                ],
                borderColor: [
                    'rgba(40, 167, 69, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 2
            }]
        };

        this.charts.anomaly = new Chart(ctx, {
            type: 'doughnut',
            data: anomalyData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '이상 탐지 분포'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    createESGAnalysisChart() {
        const ctx = document.getElementById('esg-analysis-chart').getContext('2d');

        // Sample ESG analysis data
        const esgData = {
            labels: ['환경 (E)', '사회 (S)', '지배구조 (G)'],
            datasets: [{
                label: '평균 점수',
                data: [78.5, 72.3, 75.8],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',   // 환경 - 녹색
                    'rgba(23, 162, 184, 0.8)',  // 사회 - 청색
                    'rgba(255, 193, 7, 0.8)'    // 지배구조 - 황색
                ],
                borderColor: [
                    'rgba(40, 167, 69, 1)',
                    'rgba(23, 162, 184, 1)',
                    'rgba(255, 193, 7, 1)'
                ],
                borderWidth: 2
            }]
        };

        this.charts.esg = new Chart(ctx, {
            type: 'bar',
            data: esgData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'ESG 구성 요소별 점수'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: '점수'
                        }
                    }
                }
            }
        });
    }

    async runAnalysis() {
        try {
            const analysisType = document.getElementById('analysis-type').value;
            const farmId = document.getElementById('farm-selector').value;
            const product = document.getElementById('product-selector').value;
            const period = parseInt(document.getElementById('prediction-period').value);
            const confidence = parseInt(document.getElementById('confidence-threshold').value);

            // Show loading
            this.showAnalysisLoading();

            // Simulate analysis delay
            await new Promise(resolve => setTimeout(resolve, 2000));

            switch (analysisType) {
                case 'demand':
                    await this.runDemandAnalysis(farmId, product, period, confidence);
                    break;
                case 'price':
                    await this.runPriceAnalysis(farmId, product, period, confidence);
                    break;
                case 'anomaly':
                    await this.runAnomalyAnalysis();
                    break;
                case 'esg':
                    await this.runESGAnalysis();
                    break;
            }

            this.updateMainChart(analysisType);
            this.updateAnalysisSummary(analysisType);
            this.updateAnalysisTable(analysisType);

        } catch (error) {
            console.error('분석 실행 오류:', error);
            this.utils.showAlert('AI 분석 실행 중 오류가 발생했습니다.', 'danger');
        }
    }

    async runDemandAnalysis(farmId, product, period, confidence) {
        try {
            let predictionData;

            if (farmId) {
                // Get specific farm prediction
                predictionData = await this.api.getFarmPrediction(farmId, period);
            } else {
                // Generate sample prediction data for all farms
                predictionData = this.generateSamplePredictionData(period, product);
            }

            this.analysisResults = predictionData.success ? predictionData.data.predictions : predictionData;
            document.getElementById('main-chart-title').innerHTML = '<i class="fas fa-chart-line"></i> 수요 예측 분석';

        } catch (error) {
            console.error('수요 분석 오류:', error);
            this.analysisResults = this.generateSamplePredictionData(period, product);
        }
    }

    async runPriceAnalysis(farmId, product, period, confidence) {
        // Generate sample price prediction data
        this.analysisResults = this.generateSamplePriceData(period, product);
        document.getElementById('main-chart-title').innerHTML = '<i class="fas fa-won-sign"></i> 가격 예측 분석';
    }

    async runAnomalyAnalysis() {
        // Generate sample anomaly data
        this.analysisResults = this.generateSampleAnomalyData();
        document.getElementById('main-chart-title').innerHTML = '<i class="fas fa-exclamation-triangle"></i> 이상 탐지 분석';
    }

    async runESGAnalysis() {
        // Generate sample ESG analysis data
        this.analysisResults = this.generateSampleESGData();
        document.getElementById('main-chart-title').innerHTML = '<i class="fas fa-leaf"></i> ESG 분석 결과';
    }

    generateSamplePredictionData(period, product) {
        const predictions = [];
        const baseValue = product === 'rice' ? 2000 : product === 'tomatoes' ? 1500 : 1000;

        for (let i = 0; i < period; i++) {
            const date = new Date();
            date.setDate(date.getDate() + i);

            const trend = Math.sin(i * 0.1) * 200;
            const noise = (Math.random() - 0.5) * 100;
            const seasonal = Math.sin(i * 0.3) * 150;

            const demand = Math.max(0, baseValue + trend + seasonal + noise);
            const confidence = 0.7 + Math.random() * 0.25;

            predictions.push({
                date: date.toISOString().split('T')[0],
                predicted_demand: Math.round(demand),
                confidence_upper: Math.round(demand * 1.2),
                confidence_lower: Math.round(demand * 0.8),
                confidence: confidence,
                product: product === 'all' ? ['tomatoes', 'rice', 'lettuce'][i % 3] : product
            });
        }

        return predictions;
    }

    generateSamplePriceData(period, product) {
        const prices = [];
        const basePrice = product === 'rice' ? 1800 : product === 'tomatoes' ? 3000 : 2000;

        for (let i = 0; i < period; i++) {
            const date = new Date();
            date.setDate(date.getDate() + i);

            const trend = Math.sin(i * 0.15) * 300;
            const volatility = (Math.random() - 0.5) * 200;

            const price = Math.max(1000, basePrice + trend + volatility);
            const confidence = 0.65 + Math.random() * 0.3;

            prices.push({
                date: date.toISOString().split('T')[0],
                predicted_price: Math.round(price),
                confidence_upper: Math.round(price * 1.15),
                confidence_lower: Math.round(price * 0.85),
                confidence: confidence,
                product: product === 'all' ? ['tomatoes', 'rice', 'lettuce'][i % 3] : product
            });
        }

        return prices;
    }

    generateSampleAnomalyData() {
        const anomalies = [];

        for (let i = 0; i < 20; i++) {
            const date = new Date();
            date.setDate(date.getDate() - i);

            anomalies.push({
                date: date.toISOString().split('T')[0],
                transaction_id: `TXN_${Date.now() + i}`,
                anomaly_score: Math.random(),
                is_anomaly: Math.random() > 0.8,
                risk_level: ['LOW', 'MEDIUM', 'HIGH'][Math.floor(Math.random() * 3)],
                confidence: 0.7 + Math.random() * 0.3
            });
        }

        return anomalies;
    }

    generateSampleESGData() {
        const esgData = [];

        for (let i = 0; i < 15; i++) {
            esgData.push({
                farm_id: `FARM_${String(i + 1).padStart(3, '0')}`,
                overall_esg: 60 + Math.random() * 30,
                environmental: 60 + Math.random() * 35,
                social: 65 + Math.random() * 25,
                governance: 70 + Math.random() * 20,
                tokens_earned: Math.floor(Math.random() * 1000) + 100,
                improvement_potential: Math.random() * 20
            });
        }

        return esgData;
    }

    updateMainChart(analysisType) {
        if (!this.charts.main) return;

        let chartData;
        let chartType = 'line';

        switch (analysisType) {
            case 'demand':
                chartData = this.createDemandChartData();
                break;
            case 'price':
                chartData = this.createPriceChartData();
                break;
            case 'anomaly':
                chartData = this.createAnomalyTimeSeriesData();
                chartType = 'scatter';
                break;
            case 'esg':
                chartData = this.createESGTimeSeriesData();
                chartType = 'bar';
                break;
            default:
                chartData = { labels: [], datasets: [] };
        }

        // Destroy and recreate chart with new type if needed
        if (this.charts.main.config.type !== chartType) {
            this.charts.main.destroy();
            const ctx = document.getElementById('main-analysis-chart').getContext('2d');
            this.charts.main = new Chart(ctx, {
                type: chartType,
                data: chartData,
                options: this.getChartOptions(analysisType)
            });
        } else {
            this.charts.main.data = chartData;
            this.charts.main.update();
        }
    }

    createDemandChartData() {
        return {
            labels: this.analysisResults.map(r => new Date(r.date).toLocaleDateString('ko-KR')),
            datasets: [
                {
                    label: '예측 수요',
                    data: this.analysisResults.map(r => r.predicted_demand),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '상한 신뢰구간',
                    data: this.analysisResults.map(r => r.confidence_upper),
                    borderColor: 'rgba(255, 99, 132, 0.5)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false
                },
                {
                    label: '하한 신뢰구간',
                    data: this.analysisResults.map(r => r.confidence_lower),
                    borderColor: 'rgba(255, 99, 132, 0.5)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false
                }
            ]
        };
    }

    createPriceChartData() {
        return {
            labels: this.analysisResults.map(r => new Date(r.date).toLocaleDateString('ko-KR')),
            datasets: [
                {
                    label: '예측 가격',
                    data: this.analysisResults.map(r => r.predicted_price),
                    borderColor: 'rgb(255, 159, 64)',
                    backgroundColor: 'rgba(255, 159, 64, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '상한 신뢰구간',
                    data: this.analysisResults.map(r => r.confidence_upper),
                    borderColor: 'rgba(255, 99, 132, 0.5)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false
                },
                {
                    label: '하한 신뢰구간',
                    data: this.analysisResults.map(r => r.confidence_lower),
                    borderColor: 'rgba(255, 99, 132, 0.5)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false
                }
            ]
        };
    }

    createAnomalyTimeSeriesData() {
        const normalPoints = this.analysisResults.filter(r => !r.is_anomaly);
        const anomalyPoints = this.analysisResults.filter(r => r.is_anomaly);

        return {
            datasets: [
                {
                    label: '정상 거래',
                    data: normalPoints.map((r, i) => ({ x: i, y: r.anomaly_score })),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    pointRadius: 4
                },
                {
                    label: '이상 거래',
                    data: anomalyPoints.map((r, i) => ({ x: i + normalPoints.length, y: r.anomaly_score })),
                    backgroundColor: 'rgba(255, 99, 132, 0.8)',
                    pointRadius: 6
                }
            ]
        };
    }

    createESGTimeSeriesData() {
        return {
            labels: this.analysisResults.map(r => r.farm_id),
            datasets: [
                {
                    label: '전체 ESG',
                    data: this.analysisResults.map(r => r.overall_esg),
                    backgroundColor: 'rgba(40, 167, 69, 0.8)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 1
                },
                {
                    label: '환경 (E)',
                    data: this.analysisResults.map(r => r.environmental),
                    backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: '사회 (S)',
                    data: this.analysisResults.map(r => r.social),
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: '지배구조 (G)',
                    data: this.analysisResults.map(r => r.governance),
                    backgroundColor: 'rgba(255, 206, 86, 0.8)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1
                }
            ]
        };
    }

    getChartOptions(analysisType) {
        const baseOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        };

        switch (analysisType) {
            case 'demand':
                return {
                    ...baseOptions,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '수요량 (kg)'
                            }
                        }
                    }
                };
            case 'price':
                return {
                    ...baseOptions,
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: '가격 (원)'
                            }
                        }
                    }
                };
            case 'anomaly':
                return {
                    ...baseOptions,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: '거래 순서'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            max: 1,
                            title: {
                                display: true,
                                text: '이상 점수'
                            }
                        }
                    }
                };
            case 'esg':
                return {
                    ...baseOptions,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'ESG 점수'
                            }
                        }
                    }
                };
            default:
                return baseOptions;
        }
    }

    updateAnalysisSummary(analysisType) {
        const container = document.getElementById('analysis-summary');

        if (!this.analysisResults || this.analysisResults.length === 0) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    분석 결과가 없습니다.
                </div>
            `;
            return;
        }

        let summaryHTML;

        switch (analysisType) {
            case 'demand':
                summaryHTML = this.createDemandSummary();
                break;
            case 'price':
                summaryHTML = this.createPriceSummary();
                break;
            case 'anomaly':
                summaryHTML = this.createAnomalySummary();
                break;
            case 'esg':
                summaryHTML = this.createESGSummary();
                break;
            default:
                summaryHTML = '<p class="text-muted">분석 결과 요약을 준비 중입니다.</p>';
        }

        container.innerHTML = summaryHTML;
    }

    createDemandSummary() {
        const avgDemand = this.analysisResults.reduce((sum, r) => sum + r.predicted_demand, 0) / this.analysisResults.length;
        const maxDemand = Math.max(...this.analysisResults.map(r => r.predicted_demand));
        const minDemand = Math.min(...this.analysisResults.map(r => r.predicted_demand));
        const avgConfidence = this.analysisResults.reduce((sum, r) => sum + r.confidence, 0) / this.analysisResults.length;

        return `
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="border-end">
                        <h6 class="text-primary">${this.utils.formatNumber(Math.round(avgDemand))}kg</h6>
                        <small class="text-muted">평균 예측 수요</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <h6 class="text-success">${(avgConfidence * 100).toFixed(1)}%</h6>
                    <small class="text-muted">평균 신뢰도</small>
                </div>
            </div>
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="border-end">
                        <h6 class="text-info">${this.utils.formatNumber(maxDemand)}kg</h6>
                        <small class="text-muted">최대 예측</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <h6 class="text-warning">${this.utils.formatNumber(minDemand)}kg</h6>
                    <small class="text-muted">최소 예측</small>
                </div>
            </div>
            <div class="alert alert-info">
                <i class="fas fa-lightbulb"></i>
                <strong>인사이트:</strong> 예측 기간 동안 수요가 ${avgDemand > 1500 ? '높은' : '안정적인'} 수준을 유지할 것으로 예상됩니다.
            </div>
        `;
    }

    createPriceSummary() {
        const avgPrice = this.analysisResults.reduce((sum, r) => sum + r.predicted_price, 0) / this.analysisResults.length;
        const maxPrice = Math.max(...this.analysisResults.map(r => r.predicted_price));
        const minPrice = Math.min(...this.analysisResults.map(r => r.predicted_price));
        const priceVolatility = ((maxPrice - minPrice) / avgPrice * 100).toFixed(1);

        return `
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="border-end">
                        <h6 class="text-primary">${this.utils.formatCurrency(Math.round(avgPrice))}</h6>
                        <small class="text-muted">평균 예측 가격</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <h6 class="text-warning">${priceVolatility}%</h6>
                    <small class="text-muted">가격 변동성</small>
                </div>
            </div>
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="border-end">
                        <h6 class="text-success">${this.utils.formatCurrency(maxPrice)}</h6>
                        <small class="text-muted">최고 예상가</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <h6 class="text-info">${this.utils.formatCurrency(minPrice)}</h6>
                    <small class="text-muted">최저 예상가</small>
                </div>
            </div>
            <div class="alert alert-success">
                <i class="fas fa-chart-line"></i>
                <strong>추천:</strong> 가격 변동성이 ${priceVolatility > 20 ? '높으므로 신중한' : '낮으므로 안정적인'} 거래를 고려하세요.
            </div>
        `;
    }

    createAnomalySummary() {
        const totalTransactions = this.analysisResults.length;
        const anomalies = this.analysisResults.filter(r => r.is_anomaly).length;
        const anomalyRate = (anomalies / totalTransactions * 100).toFixed(1);
        const highRiskCount = this.analysisResults.filter(r => r.risk_level === 'HIGH').length;

        return `
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="border-end">
                        <h6 class="text-danger">${anomalies}</h6>
                        <small class="text-muted">이상 거래 탐지</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <h6 class="text-warning">${anomalyRate}%</h6>
                    <small class="text-muted">이상 탐지율</small>
                </div>
            </div>
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="border-end">
                        <h6 class="text-info">${highRiskCount}</h6>
                        <small class="text-muted">고위험 거래</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <h6 class="text-success">${totalTransactions - anomalies}</h6>
                    <small class="text-muted">정상 거래</small>
                </div>
            </div>
            <div class="alert ${anomalyRate > 5 ? 'alert-warning' : 'alert-success'}">
                <i class="fas fa-shield-alt"></i>
                <strong>보안 상태:</strong> ${anomalyRate > 5 ? '주의 필요' : '양호'}한 수준입니다.
            </div>
        `;
    }

    createESGSummary() {
        const avgESG = this.analysisResults.reduce((sum, r) => sum + r.overall_esg, 0) / this.analysisResults.length;
        const topPerformers = this.analysisResults.filter(r => r.overall_esg >= 80).length;
        const improvementNeeded = this.analysisResults.filter(r => r.overall_esg < 60).length;
        const totalTokens = this.analysisResults.reduce((sum, r) => sum + r.tokens_earned, 0);

        return `
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="border-end">
                        <h6 class="text-success">${avgESG.toFixed(1)}</h6>
                        <small class="text-muted">평균 ESG 점수</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <h6 class="text-primary">${topPerformers}</h6>
                    <small class="text-muted">우수 농장 수</small>
                </div>
            </div>
            <div class="row text-center">
                <div class="col-6 mb-3">
                    <div class="border-end">
                        <h6 class="text-warning">${improvementNeeded}</h6>
                        <small class="text-muted">개선 필요</small>
                    </div>
                </div>
                <div class="col-6 mb-3">
                    <h6 class="text-info">${this.utils.formatNumber(totalTokens)}</h6>
                    <small class="text-muted">총 토큰 발행</small>
                </div>
            </div>
            <div class="alert alert-info">
                <i class="fas fa-leaf"></i>
                <strong>ESG 현황:</strong> 전체적으로 ${avgESG >= 70 ? '양호한' : '개선이 필요한'} ESG 성과를 보이고 있습니다.
            </div>
        `;
    }

    updateAnalysisTable(analysisType) {
        const tbody = document.getElementById('analysis-results-table');
        const thead = document.getElementById('analysis-table-header');

        if (!this.analysisResults || this.analysisResults.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">분석 결과가 없습니다</td>
                </tr>
            `;
            return;
        }

        // Update table header based on analysis type
        thead.innerHTML = this.getTableHeader(analysisType);

        // Update table rows
        const rows = this.analysisResults.slice(0, 10).map(result => {
            return this.createTableRow(result, analysisType);
        }).join('');

        tbody.innerHTML = rows;
    }

    getTableHeader(analysisType) {
        switch (analysisType) {
            case 'demand':
                return `
                    <th>날짜</th>
                    <th>품목</th>
                    <th>예측 수요</th>
                    <th>신뢰도</th>
                    <th>신뢰구간</th>
                `;
            case 'price':
                return `
                    <th>날짜</th>
                    <th>품목</th>
                    <th>예측 가격</th>
                    <th>신뢰도</th>
                    <th>가격 범위</th>
                `;
            case 'anomaly':
                return `
                    <th>날짜</th>
                    <th>거래 ID</th>
                    <th>이상 점수</th>
                    <th>위험도</th>
                    <th>상태</th>
                `;
            case 'esg':
                return `
                    <th>농장 ID</th>
                    <th>전체 ESG</th>
                    <th>환경 점수</th>
                    <th>사회 점수</th>
                    <th>지배구조 점수</th>
                `;
            default:
                return `
                    <th>날짜</th>
                    <th>항목</th>
                    <th>값</th>
                    <th>신뢰도</th>
                    <th>상태</th>
                `;
        }
    }

    createTableRow(result, analysisType) {
        switch (analysisType) {
            case 'demand':
                return `
                    <tr>
                        <td>${new Date(result.date).toLocaleDateString('ko-KR')}</td>
                        <td><span class="badge bg-success">${result.product || 'N/A'}</span></td>
                        <td>${this.utils.formatNumber(result.predicted_demand)}kg</td>
                        <td>
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar" style="width: ${result.confidence * 100}%">
                                    ${(result.confidence * 100).toFixed(1)}%
                                </div>
                            </div>
                        </td>
                        <td>
                            <small class="text-muted">
                                ${this.utils.formatNumber(result.confidence_lower)} ~
                                ${this.utils.formatNumber(result.confidence_upper)}kg
                            </small>
                        </td>
                    </tr>
                `;
            case 'price':
                return `
                    <tr>
                        <td>${new Date(result.date).toLocaleDateString('ko-KR')}</td>
                        <td><span class="badge bg-warning">${result.product || 'N/A'}</span></td>
                        <td>${this.utils.formatCurrency(result.predicted_price)}</td>
                        <td>
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar bg-warning" style="width: ${result.confidence * 100}%">
                                    ${(result.confidence * 100).toFixed(1)}%
                                </div>
                            </div>
                        </td>
                        <td>
                            <small class="text-muted">
                                ${this.utils.formatCurrency(result.confidence_lower)} ~
                                ${this.utils.formatCurrency(result.confidence_upper)}
                            </small>
                        </td>
                    </tr>
                `;
            case 'anomaly':
                return `
                    <tr>
                        <td>${new Date(result.date).toLocaleDateString('ko-KR')}</td>
                        <td><small class="text-muted">${result.transaction_id}</small></td>
                        <td>${result.anomaly_score.toFixed(3)}</td>
                        <td>
                            <span class="badge ${result.risk_level === 'HIGH' ? 'bg-danger' :
                                               result.risk_level === 'MEDIUM' ? 'bg-warning' : 'bg-success'}">
                                ${result.risk_level}
                            </span>
                        </td>
                        <td>
                            <span class="badge ${result.is_anomaly ? 'bg-warning' : 'bg-success'}">
                                ${result.is_anomaly ? '이상' : '정상'}
                            </span>
                        </td>
                    </tr>
                `;
            case 'esg':
                return `
                    <tr>
                        <td>${result.farm_id}</td>
                        <td>
                            <div class="esg-score-circle ${this.utils.getESGColor(result.overall_esg)}"
                                 style="width: 30px; height: 30px; font-size: 0.7rem;">
                                ${result.overall_esg.toFixed(1)}
                            </div>
                        </td>
                        <td>
                            <div class="progress">
                                <div class="progress-bar bg-success" style="width: ${result.environmental}%">
                                    ${result.environmental.toFixed(1)}
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="progress">
                                <div class="progress-bar bg-info" style="width: ${result.social}%">
                                    ${result.social.toFixed(1)}
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="progress">
                                <div class="progress-bar bg-warning" style="width: ${result.governance}%">
                                    ${result.governance.toFixed(1)}
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
            default:
                return `<tr><td colspan="5">지원하지 않는 분석 유형입니다.</td></tr>`;
        }
    }

    updateModelPerformance() {
        // Simulate model performance metrics
        const metrics = {
            demand: 87.5,
            price: 82.3,
            anomaly: 91.2,
            esg: 79.8
        };

        Object.entries(metrics).forEach(([model, accuracy]) => {
            const progressBar = document.getElementById(`${model === 'esg' ? 'esg-model' : model}-accuracy`);
            const textElement = document.getElementById(`${model === 'esg' ? 'esg-model' : model}-accuracy-text`);

            if (progressBar) {
                progressBar.style.width = `${accuracy}%`;
                progressBar.setAttribute('aria-valuenow', accuracy);
            }

            if (textElement) {
                textElement.textContent = `정확도: ${accuracy.toFixed(1)}%`;
            }
        });
    }

    showAnalysisLoading() {
        const container = document.getElementById('analysis-summary');
        container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p class="mt-2">AI 분석 실행 중...</p>
            </div>
        `;

        const tbody = document.getElementById('analysis-results-table');
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">
                    <div class="spinner"></div>
                </td>
            </tr>
        `;
    }

    setupEventListeners() {
        // Analysis controls
        document.getElementById('run-analysis').addEventListener('click', () => {
            this.runAnalysis();
        });

        document.getElementById('refresh-chart').addEventListener('click', () => {
            this.runAnalysis();
        });

        // Confidence threshold slider
        const confidenceSlider = document.getElementById('confidence-threshold');
        const confidenceValue = document.getElementById('confidence-value');

        confidenceSlider.addEventListener('input', (e) => {
            confidenceValue.textContent = `${e.target.value}%`;
        });

        // Export functions
        document.getElementById('export-chart').addEventListener('click', () => {
            this.exportChart();
        });

        document.getElementById('export-results').addEventListener('click', () => {
            this.exportResults();
        });

        // Role change handler
        window.addEventListener('roleChanged', (e) => {
            this.handleRoleChange(e.detail.role);
        });
    }

    exportChart() {
        if (this.charts.main) {
            const url = this.charts.main.toBase64Image();
            const link = document.createElement('a');
            link.download = `pamtalk_analysis_${new Date().toISOString().split('T')[0]}.png`;
            link.href = url;
            link.click();
        }
    }

    exportResults() {
        if (!this.analysisResults || this.analysisResults.length === 0) {
            this.utils.showAlert('내보낼 분석 결과가 없습니다.', 'warning');
            return;
        }

        const csv = this.convertToCSV(this.analysisResults);
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = `pamtalk_analysis_results_${new Date().toISOString().split('T')[0]}.csv`;
        link.href = url;
        link.click();
        window.URL.revokeObjectURL(url);
    }

    convertToCSV(data) {
        if (!data || data.length === 0) return '';

        const headers = Object.keys(data[0]);
        const csvHeaders = headers.join(',');

        const csvRows = data.map(row => {
            return headers.map(header => {
                const value = row[header];
                return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
            }).join(',');
        });

        return [csvHeaders, ...csvRows].join('\n');
    }

    handleRoleChange(role) {
        console.log('AI 분석 페이지 역할 변경:', role);

        // Show/hide role-specific elements
        const roleElements = document.querySelectorAll('[data-role]');
        roleElements.forEach(element => {
            const allowedRoles = element.dataset.role.split(',');
            element.style.display = allowedRoles.includes(role) ? 'block' : 'none';
        });

        // Refresh analysis if needed based on role
        if (this.analysisResults.length > 0) {
            this.runAnalysis();
        }
    }
}

// Initialize analytics manager when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.analyticsManager = new AnalyticsManager();
});