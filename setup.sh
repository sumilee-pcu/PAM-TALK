#!/bin/bash

# PAM-TALK 시스템 환경 설정 자동화 스크립트
# Ubuntu/Debian 및 macOS 지원

set -e  # 오류 발생시 스크립트 종료

# 색상 코드 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수들
log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${BLUE}🔧 $1${NC}"
}

# 배너 출력
print_banner() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 PAM-TALK 설치 스크립트                  ║"
    echo "║          블록체인 기반 AI 농업 예측 플랫폼 환경 설정            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# 운영체제 감지
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="ubuntu"
        elif [ -f /etc/redhat-release ]; then
            OS="centos"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi

    log_info "감지된 운영체제: $OS"
}

# 필수 도구 설치
install_system_dependencies() {
    log_step "시스템 의존성 설치 중..."

    case $OS in
        ubuntu)
            sudo apt-get update
            sudo apt-get install -y curl wget git build-essential software-properties-common
            log_info "Ubuntu 시스템 패키지 설치 완료"
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                log_step "Homebrew 설치 중..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install curl wget git
            log_info "macOS 시스템 패키지 설치 완료"
            ;;
        *)
            log_warning "알 수 없는 운영체제. 수동으로 curl, wget, git를 설치해주세요."
            ;;
    esac
}

# Python 설치 확인 및 설치
install_python() {
    log_step "Python 설치 확인 중..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python $PYTHON_VERSION 이미 설치됨"

        # Python 3.8 이상 확인
        if python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
            log_info "Python 버전 요구사항 만족"
        else
            log_warning "Python 3.8 이상이 필요합니다. 업그레이드해주세요."
            return 1
        fi
    else
        log_step "Python 3 설치 중..."
        case $OS in
            ubuntu)
                sudo apt-get install -y python3 python3-pip python3-venv python3-dev
                ;;
            macos)
                brew install python3
                ;;
            *)
                log_error "Python 설치를 수동으로 진행해주세요: https://python.org"
                return 1
                ;;
        esac
        log_info "Python 설치 완료"
    fi

    # pip 업그레이드
    python3 -m pip install --upgrade pip
    log_info "pip 업그레이드 완료"
}

# Node.js 설치 (선택사항 - 프론트엔드 개발용)
install_nodejs() {
    log_step "Node.js 설치 확인 중..."

    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_info "Node.js $NODE_VERSION 이미 설치됨"
    else
        log_step "Node.js 설치 중..."
        case $OS in
            ubuntu)
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            macos)
                brew install node
                ;;
            *)
                log_warning "Node.js를 수동으로 설치해주세요: https://nodejs.org"
                return 1
                ;;
        esac
        log_info "Node.js 설치 완료"
    fi
}

# 가상환경 생성 및 활성화
setup_virtual_environment() {
    log_step "Python 가상환경 설정 중..."

    # 기존 가상환경 제거 (선택사항)
    if [ -d "venv" ]; then
        log_warning "기존 가상환경 발견. 제거하고 새로 생성합니다."
        rm -rf venv
    fi

    # 가상환경 생성
    python3 -m venv venv
    log_info "가상환경 생성 완료"

    # 가상환경 활성화 스크립트 생성
    cat > activate_env.sh << 'EOF'
#!/bin/bash
# PAM-TALK 가상환경 활성화 스크립트

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ PAM-TALK 가상환경 활성화 완료"
    echo "💡 비활성화하려면: deactivate"
else
    echo "❌ 가상환경을 찾을 수 없습니다. setup.sh를 다시 실행해주세요."
fi
EOF
    chmod +x activate_env.sh

    # Windows용 배치 파일도 생성
    cat > activate_env.bat << 'EOF'
@echo off
REM PAM-TALK 가상환경 활성화 스크립트 (Windows)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ PAM-TALK 가상환경 활성화 완료
    echo 💡 비활성화하려면: deactivate
) else (
    echo ❌ 가상환경을 찾을 수 없습니다. setup.sh를 다시 실행해주세요.
)
EOF

    log_info "가상환경 활성화 스크립트 생성: activate_env.sh (Linux/macOS), activate_env.bat (Windows)"
}

# Python 패키지 설치
install_python_packages() {
    log_step "Python 패키지 설치 중..."

    # 가상환경 활성화
    source venv/bin/activate 2>/dev/null || {
        log_error "가상환경 활성화 실패"
        return 1
    }

    # requirements.txt가 있는지 확인
    if [ ! -f "requirements.txt" ]; then
        log_warning "requirements.txt가 없습니다. 기본 패키지를 설치합니다."

        # 기본 requirements.txt 생성
        cat > requirements.txt << 'EOF'
# PAM-TALK 시스템 기본 요구사항
flask==2.3.3
flask-cors==4.0.0
requests==2.31.0
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
prophet==1.1.4
pytest==7.4.0
python-dotenv==1.0.0

# 블록체인 관련
web3==6.9.0
eth-account==0.9.0

# 데이터베이스
sqlalchemy==2.0.20
sqlite3

# AI/ML 추가
matplotlib==3.7.2
seaborn==0.12.2
joblib==1.3.2

# API 문서화
flask-swagger-ui==4.11.1

# 로깅
structlog==23.1.0

# 환경 변수
python-decouple==3.8
EOF
        log_info "기본 requirements.txt 생성 완료"
    fi

    # 패키지 설치
    pip install -r requirements.txt

    # 추가 개발 도구 설치
    pip install black flake8 pytest-cov

    log_info "Python 패키지 설치 완료"

    # 설치된 패키지 목록 저장
    pip freeze > requirements-frozen.txt
    log_info "설치된 패키지 목록 저장: requirements-frozen.txt"
}

# 환경 변수 파일 생성
setup_environment_file() {
    log_step "환경 변수 파일 설정 중..."

    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info ".env.example에서 .env 파일 생성"
        else
            cat > .env << 'EOF'
# PAM-TALK 시스템 환경 변수

# Flask 설정
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production

# 데이터베이스
DATABASE_URL=sqlite:///pamtalk.db

# AI 모델 설정
AI_MODEL_PATH=./ai_models
PREDICTION_CACHE_TTL=3600

# 블록체인 설정
BLOCKCHAIN_NETWORK=localhost
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=your-private-key-here

# API 설정
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=True

# 로깅
LOG_LEVEL=INFO
LOG_FILE=pamtalk.log

# 외부 서비스
WEATHER_API_KEY=your-weather-api-key
MARKET_DATA_API_KEY=your-market-api-key
EOF
            log_info "기본 .env 파일 생성"
        fi
    else
        log_warning ".env 파일이 이미 존재합니다."
    fi

    log_warning "⚠️  .env 파일의 설정을 확인하고 필요한 값들을 업데이트해주세요!"
}

# 디렉토리 구조 생성
create_directory_structure() {
    log_step "디렉토리 구조 생성 중..."

    directories=(
        "data"
        "logs"
        "ai_models/saved"
        "static/css"
        "static/js"
        "static/images"
        "templates"
        "tests/unit"
        "tests/integration"
        "contracts/compiled"
        "api/routes"
        "scripts"
    )

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "디렉토리 생성: $dir"
        fi
    done

    # .gitkeep 파일 생성 (빈 디렉토리 추적용)
    touch data/.gitkeep logs/.gitkeep ai_models/saved/.gitkeep

    log_info "디렉토리 구조 생성 완료"
}

# 개발 도구 설정
setup_development_tools() {
    log_step "개발 도구 설정 중..."

    # .gitignore 파일 생성/업데이트
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
.venv/

# Environment Variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# AI Models
ai_models/saved/*.pkl
ai_models/saved/*.joblib
ai_models/saved/*.h5

# Blockchain
contracts/compiled/*.json
keystore/

# Temporary files
tmp/
temp/
*.tmp

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
EOF
        log_info ".gitignore 파일 생성"
    fi

    # pytest 설정 파일
    if [ ! -f "pytest.ini" ]; then
        cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --ignore=venv
EOF
        log_info "pytest.ini 파일 생성"
    fi

    # 코드 품질 설정
    cat > .flake8 << 'EOF'
[flake8]
max-line-length = 88
exclude = venv,__pycache__,.git
ignore = E203,W503
EOF

    log_info "개발 도구 설정 완료"
}

# 실행 스크립트 생성
create_run_scripts() {
    log_step "실행 스크립트 생성 중..."

    # 개발 서버 실행 스크립트
    cat > run_dev.sh << 'EOF'
#!/bin/bash
# PAM-TALK 개발 서버 실행 스크립트

echo "🚀 PAM-TALK 개발 서버 시작..."

# 가상환경 활성화
source venv/bin/activate

# 환경 변수 로드
export FLASK_ENV=development
export FLASK_DEBUG=True

# API 서버 시작
cd api && python app.py

echo "✅ 개발 서버 시작 완료!"
echo "🌐 접속 주소: http://localhost:5000"
EOF
    chmod +x run_dev.sh

    # 테스트 실행 스크립트
    cat > run_all_tests.sh << 'EOF'
#!/bin/bash
# PAM-TALK 전체 테스트 실행 스크립트

echo "🧪 PAM-TALK 테스트 시작..."

# 가상환경 활성화
source venv/bin/activate

# 코드 품질 검사
echo "📋 코드 품질 검사 중..."
flake8 .

# 유닛 테스트 실행
echo "🔬 유닛 테스트 실행 중..."
pytest tests/unit/ -v

# 통합 테스트 실행
echo "🔗 통합 테스트 실행 중..."
pytest tests/integration/ -v

echo "✅ 모든 테스트 완료!"
EOF
    chmod +x run_all_tests.sh

    # 배포 스크립트
    cat > deploy.sh << 'EOF'
#!/bin/bash
# PAM-TALK 배포 스크립트

echo "🚢 PAM-TALK 배포 준비..."

# 가상환경 활성화
source venv/bin/activate

# 코드 품질 검사
flake8 . || exit 1

# 테스트 실행
pytest || exit 1

# 의존성 정리
pip freeze > requirements.txt

# 배포 파일 생성
echo "📦 배포 파키지 생성 중..."
# 여기에 실제 배포 로직 추가

echo "✅ 배포 준비 완료!"
EOF
    chmod +x deploy.sh

    log_info "실행 스크립트 생성 완료"
}

# 데이터베이스 초기화
initialize_database() {
    log_step "데이터베이스 초기화 중..."

    # 가상환경 활성화
    source venv/bin/activate 2>/dev/null || true

    # 기본 설정이 있다면 데이터베이스 초기화 실행
    if [ -f "basic_setup.py" ]; then
        python basic_setup.py
        log_info "데이터베이스 초기화 완료"
    else
        log_warning "basic_setup.py를 찾을 수 없습니다. 수동으로 데이터베이스를 초기화해주세요."
    fi
}

# 헬스 체크
run_health_check() {
    log_step "시스템 헬스 체크 실행 중..."

    # Python 버전 확인
    python3 --version

    # 가상환경 확인
    if [ -d "venv" ]; then
        log_info "가상환경 존재 확인"
    else
        log_error "가상환경이 없습니다"
        return 1
    fi

    # 필수 파일 확인
    required_files=("requirements.txt" ".env" "run_demo.py")
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_info "$file 존재 확인"
        else
            log_warning "$file이 없습니다"
        fi
    done

    # 패키지 설치 확인
    source venv/bin/activate 2>/dev/null || true
    python -c "import flask, pandas, numpy" 2>/dev/null && log_info "핵심 패키지 설치 확인" || log_warning "일부 패키지가 설치되지 않았습니다"

    log_info "헬스 체크 완료"
}

# 사용법 출력
print_usage() {
    cat << EOF

📖 PAM-TALK 시스템 사용법
═══════════════════════════

🔧 환경 설정 (최초 1회):
   ./setup.sh

🚀 시스템 시작:
   ./run_demo.py                # 전체 데모 시스템 실행
   ./run_dev.sh                # 개발 서버만 실행
   source activate_env.sh       # 가상환경 활성화

🧪 테스트 실행:
   ./run_all_tests.sh          # 전체 테스트 실행
   python -m pytest           # pytest 직접 실행

📁 주요 디렉토리:
   api/                        # REST API 서버
   data/                       # 데이터 파일
   tests/                      # 테스트 코드
   ai_models/                  # AI 모델 파일
   contracts/                  # 스마트 계약

🌐 접속 주소:
   http://localhost:5000       # 메인 대시보드
   http://localhost:5000/api   # API 엔드포인트

💡 도움말:
   python run_demo.py --help   # 데모 실행 옵션
   pytest --help              # 테스트 옵션

EOF
}

# 메인 실행 함수
main() {
    print_banner

    # 명령줄 옵션 처리
    case "${1:-}" in
        --help|-h)
            print_usage
            exit 0
            ;;
        --health-check)
            run_health_check
            exit 0
            ;;
        --skip-install)
            log_info "패키지 설치를 스킵합니다."
            SKIP_INSTALL=true
            ;;
    esac

    log_step "PAM-TALK 시스템 환경 설정을 시작합니다..."

    # 단계별 설치 실행
    detect_os
    install_system_dependencies
    install_python
    install_nodejs
    setup_virtual_environment

    if [ "${SKIP_INSTALL:-false}" != "true" ]; then
        install_python_packages
    fi

    setup_environment_file
    create_directory_structure
    setup_development_tools
    create_run_scripts
    initialize_database

    # 최종 헬스 체크
    run_health_check

    # 완료 메시지
    echo ""
    log_info "🎉 PAM-TALK 시스템 환경 설정이 완료되었습니다!"
    echo ""
    print_usage

    log_step "다음 명령으로 시스템을 시작할 수 있습니다:"
    echo "   source activate_env.sh   # 가상환경 활성화"
    echo "   python run_demo.py       # 데모 시스템 실행"
    echo ""
}

# 스크립트 실행
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi