// Farms page specific JavaScript
class FarmsManager {
    constructor() {
        this.api = window.pamtalkAPI;
        this.utils = window.pamtalkUtils;
        this.farms = [];
        this.filteredFarms = [];
        this.currentPage = 1;
        this.farmsPerPage = 10;

        this.init();
    }

    async init() {
        await this.loadFarms();
        this.setupEventListeners();
        this.updateStatistics();
    }

    async loadFarms() {
        try {
            this.utils.showLoading('farms-table');

            const farmsData = await this.api.getFarms();

            if (farmsData.success) {
                this.farms = farmsData.data.farms || [];
                this.filteredFarms = [...this.farms];
                this.renderFarmsTable();
                this.updatePagination();
            } else {
                throw new Error('농장 데이터 로딩 실패');
            }
        } catch (error) {
            console.error('농장 데이터 로딩 오류:', error);
            this.utils.showError('farms-table', '농장 데이터를 불러올 수 없습니다.');
        }
    }

    updateStatistics() {
        const activeFarms = this.farms.filter(farm => farm.status === 'active').length;
        const totalArea = this.farms.reduce((sum, farm) => sum + (farm.size_hectares || 0), 0);
        const productTypes = new Set();
        let totalEsgScore = 0;
        let esgCount = 0;

        this.farms.forEach(farm => {
            if (farm.products) {
                farm.products.forEach(product => productTypes.add(product));
            }
            if (farm.esg_data && farm.esg_data.overall_score) {
                totalEsgScore += farm.esg_data.overall_score;
                esgCount++;
            }
        });

        document.getElementById('active-farms').textContent = activeFarms;
        document.getElementById('total-area').textContent = totalArea.toFixed(1);
        document.getElementById('product-types').textContent = productTypes.size;
        document.getElementById('avg-esg').textContent =
            esgCount > 0 ? (totalEsgScore / esgCount).toFixed(1) : '-';
    }

    renderFarmsTable() {
        const tbody = document.getElementById('farms-table');

        if (this.filteredFarms.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">등록된 농장이 없습니다</td>
                </tr>
            `;
            return;
        }

        const startIndex = (this.currentPage - 1) * this.farmsPerPage;
        const endIndex = startIndex + this.farmsPerPage;
        const currentPageFarms = this.filteredFarms.slice(startIndex, endIndex);

        const rows = currentPageFarms.map(farm => {
            const esgScore = farm.esg_data?.overall_score || 0;
            const products = farm.products ? farm.products.slice(0, 3).join(', ') : 'N/A';

            return `
                <tr>
                    <td>
                        <strong>${farm.farm_name}</strong>
                        <br>
                        <small class="text-muted">${farm.farm_id}</small>
                    </td>
                    <td>${farm.owner_name}</td>
                    <td>${farm.location}</td>
                    <td>${farm.size_hectares} ha</td>
                    <td>${products}</td>
                    <td>
                        <div class="esg-score-circle ${this.utils.getESGColor(esgScore)}"
                             style="width: 40px; height: 40px; font-size: 0.8rem;">
                            ${esgScore.toFixed(1)}
                        </div>
                    </td>
                    <td>
                        <span class="badge ${this.utils.getStatusBadge(farm.status)}">
                            ${farm.status === 'active' ? '활성' : '비활성'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1"
                                onclick="window.farmsManager.viewFarmDetails('${farm.farm_id}')"
                                title="상세 보기">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info"
                                onclick="window.farmsManager.viewFarmPrediction('${farm.farm_id}')"
                                title="수요 예측">
                            <i class="fas fa-chart-line"></i>
                        </button>
                    </td>
                </tr>
            `;
        });

        tbody.innerHTML = rows.join('');
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredFarms.length / this.farmsPerPage);
        const pagination = document.getElementById('farms-pagination');

        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let paginationHTML = '';

        // Previous button
        paginationHTML += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="window.farmsManager.changePage(${this.currentPage - 1})" tabindex="-1">이전</a>
            </li>
        `;

        // Page numbers
        const maxVisiblePages = 5;
        const startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="window.farmsManager.changePage(${i})">${i}</a>
                </li>
            `;
        }

        // Next button
        paginationHTML += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="window.farmsManager.changePage(${this.currentPage + 1})">다음</a>
            </li>
        `;

        pagination.innerHTML = paginationHTML;
    }

    changePage(page) {
        const totalPages = Math.ceil(this.filteredFarms.length / this.farmsPerPage);

        if (page < 1 || page > totalPages) return;

        this.currentPage = page;
        this.renderFarmsTable();
        this.updatePagination();
    }

    applyFilters() {
        const statusFilter = document.getElementById('status-filter').value;
        const productFilter = document.getElementById('product-filter').value;
        const searchTerm = document.getElementById('search-input').value.toLowerCase();

        this.filteredFarms = this.farms.filter(farm => {
            // Status filter
            if (statusFilter && farm.status !== statusFilter) {
                return false;
            }

            // Product filter
            if (productFilter && (!farm.products || !farm.products.includes(productFilter))) {
                return false;
            }

            // Search filter
            if (searchTerm) {
                const searchableText = `${farm.farm_name} ${farm.owner_name} ${farm.location}`.toLowerCase();
                if (!searchableText.includes(searchTerm)) {
                    return false;
                }
            }

            return true;
        });

        this.currentPage = 1;
        this.renderFarmsTable();
        this.updatePagination();
    }

    async viewFarmDetails(farmId) {
        try {
            const farmData = await this.api.getFarm(farmId);

            if (farmData.success) {
                this.renderFarmDetailsModal(farmData.data);
                const modal = new bootstrap.Modal(document.getElementById('farmDetailsModal'));
                modal.show();
            } else {
                throw new Error('농장 상세 정보를 불러올 수 없습니다');
            }
        } catch (error) {
            console.error('농장 상세 정보 오류:', error);
            this.utils.showAlert('농장 상세 정보를 불러올 수 없습니다.', 'danger');
        }
    }

    renderFarmDetailsModal(farm) {
        const content = document.getElementById('farm-details-content');

        const esgScore = farm.esg_data?.overall_score || 0;
        const certifications = farm.certifications || [];
        const products = farm.products || [];

        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>기본 정보</h6>
                    <table class="table table-sm">
                        <tbody>
                            <tr><th>농장 ID:</th><td>${farm.farm_id}</td></tr>
                            <tr><th>농장명:</th><td>${farm.farm_name}</td></tr>
                            <tr><th>소유자:</th><td>${farm.owner_name}</td></tr>
                            <tr><th>위치:</th><td>${farm.location}</td></tr>
                            <tr><th>면적:</th><td>${farm.size_hectares} ha</td></tr>
                            <tr><th>설립일:</th><td>${this.utils.formatDate(farm.established_date || '')}</td></tr>
                            <tr><th>상태:</th><td>
                                <span class="badge ${this.utils.getStatusBadge(farm.status)}">
                                    ${farm.status === 'active' ? '활성' : '비활성'}
                                </span>
                            </td></tr>
                        </tbody>
                    </table>

                    <h6>연락처 정보</h6>
                    <table class="table table-sm">
                        <tbody>
                            <tr><th>전화:</th><td>${farm.contact_info?.phone || 'N/A'}</td></tr>
                            <tr><th>이메일:</th><td>${farm.contact_info?.email || 'N/A'}</td></tr>
                        </tbody>
                    </table>
                </div>

                <div class="col-md-6">
                    <h6>ESG 정보</h6>
                    <div class="text-center mb-3">
                        <div class="esg-score-circle ${this.utils.getESGColor(esgScore)}" style="width: 80px; height: 80px;">
                            ${esgScore.toFixed(1)}
                        </div>
                        <p class="mt-2">${this.utils.getESGLabel(esgScore)} ESG 성과</p>
                    </div>

                    <table class="table table-sm">
                        <tbody>
                            <tr><th>유기농 인증:</th><td>
                                ${farm.esg_data?.organic_certified ?
                                    '<span class="badge bg-success">인증</span>' :
                                    '<span class="badge bg-secondary">미인증</span>'}
                            </td></tr>
                            <tr><th>물 사용량:</th><td>${farm.esg_data?.water_usage_per_hectare || 'N/A'} L/ha</td></tr>
                            <tr><th>탄소 배출량:</th><td>${farm.esg_data?.carbon_emissions || 'N/A'} t/ha</td></tr>
                            <tr><th>재생에너지:</th><td>${farm.esg_data?.renewable_energy_percentage || 'N/A'}%</td></tr>
                        </tbody>
                    </table>

                    <h6>재배 품목</h6>
                    <div class="mb-3">
                        ${products.map(product =>
                            `<span class="badge bg-primary me-1">${product}</span>`
                        ).join('')}
                    </div>

                    <h6>인증</h6>
                    <div>
                        ${certifications.map(cert =>
                            `<span class="badge bg-success me-1">${cert}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    async viewFarmPrediction(farmId) {
        try {
            const predictionData = await this.api.getFarmPrediction(farmId, 14);

            if (predictionData.success) {
                // Redirect to analytics page with farm filter
                window.location.href = `analytics.html?farm=${farmId}`;
            } else {
                throw new Error('수요 예측 데이터를 불러올 수 없습니다');
            }
        } catch (error) {
            console.error('수요 예측 오류:', error);
            this.utils.showAlert('수요 예측 데이터를 불러올 수 없습니다.', 'danger');
        }
    }

    async registerFarm() {
        try {
            const form = document.getElementById('farm-form');
            const formData = new FormData(form);

            // Collect products
            const products = [];
            document.querySelectorAll('input[type="checkbox"][id^="product-"]:checked').forEach(cb => {
                products.push(cb.value);
            });

            // Collect certifications
            const certifications = [];
            document.querySelectorAll('input[type="checkbox"][id^="cert-"]:checked').forEach(cb => {
                certifications.push(cb.value);
            });

            const farmData = {
                farm_id: document.getElementById('farm-id').value,
                farm_name: document.getElementById('farm-name').value,
                owner_name: document.getElementById('owner-name').value,
                location: document.getElementById('location').value,
                size_hectares: parseFloat(document.getElementById('size-hectares').value),
                established_date: document.getElementById('established-date').value,
                contact_info: {
                    phone: document.getElementById('phone').value,
                    email: document.getElementById('email').value
                },
                products: products,
                certifications: certifications,
                esg_data: {
                    organic_certified: certifications.includes('organic'),
                    water_usage_per_hectare: parseInt(document.getElementById('water-usage').value) || 5000,
                    carbon_emissions: parseFloat(document.getElementById('carbon-emissions').value) || 2.5,
                    renewable_energy_percentage: parseFloat(document.getElementById('renewable-energy').value) || 60
                },
                status: 'active'
            };

            const result = await this.api.registerFarm(farmData);

            if (result.success) {
                this.utils.showAlert('농장이 성공적으로 등록되었습니다.', 'success');

                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('farmModal'));
                modal.hide();

                // Reset form
                form.reset();

                // Reload farms
                await this.loadFarms();
                this.updateStatistics();
            } else {
                throw new Error(result.error?.message || '농장 등록에 실패했습니다');
            }
        } catch (error) {
            console.error('농장 등록 오류:', error);
            this.utils.showAlert('농장 등록 중 오류가 발생했습니다: ' + error.message, 'danger');
        }
    }

    setupEventListeners() {
        // Filter controls
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.applyFilters();
        });

        // Enter key in search input
        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            }
        });

        // Farm registration
        document.getElementById('save-farm').addEventListener('click', () => {
            this.registerFarm();
        });

        // Role change handler
        window.addEventListener('roleChanged', (e) => {
            this.handleRoleChange(e.detail.role);
        });
    }

    handleRoleChange(role) {
        console.log('농장 관리 페이지 역할 변경:', role);

        // Show/hide role-specific elements
        const roleElements = document.querySelectorAll('[data-role]');
        roleElements.forEach(element => {
            const allowedRoles = element.dataset.role.split(',');
            element.style.display = allowedRoles.includes(role) ? 'block' : 'none';
        });

        // Reload data if needed based on role
        this.loadFarms();
    }
}

// Initialize farms manager when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.farmsManager = new FarmsManager();
});