"""
Algorand 메인넷 연결 테스트 스크립트
"""
from algorand_utils import AlgorandSimulator
from algosdk import account, mnemonic
from config import Config

def test_mainnet_connection():
    """메인넷 연결 테스트"""
    print("=" * 50)
    print("🔍 Algorand 메인넷 연결 테스트")
    print("=" * 50)

    # AlgorandSimulator 초기화
    algo_sim = AlgorandSimulator()

    # 네트워크 상태 확인
    status = algo_sim.get_network_status()
    print(f"\n📊 네트워크 상태:")
    print(f"  - 모드: {status.get('mode')}")
    print(f"  - 연결 상태: {status.get('connected')}")
    print(f"  - 네트워크: {status.get('network')}")

    if status.get('connected'):
        print(f"  - 마지막 라운드: {status.get('last_round')}")
        print(f"  - 노드 주소: {status.get('node_address')}")
        print("\n✅ 메인넷 연결 성공!")
        return True
    else:
        print("\n❌ 메인넷 연결 실패!")
        print("⚠️  .env 파일 설정을 확인하세요")
        print("\n설정 확인:")
        config = Config()
        print(f"  - ALGORAND_NETWORK: {config.ALGORAND_NETWORK}")
        print(f"  - ALGORAND_ALGOD_ADDRESS: {config.ALGORAND_ALGOD_ADDRESS}")
        print(f"  - SIMULATION_MODE: {config.SIMULATION_MODE}")
        return False

def test_account_balance(address):
    """계정 잔액 확인"""
    algo_sim = AlgorandSimulator()

    print(f"\n💰 계정 잔액 조회: {address[:8]}...{address[-8:]}")

    try:
        balance = algo_sim.get_balance(address)
        balance_algo = balance / 1_000_000  # microAlgos to ALGOs

        print(f"  - 잔액: {balance_algo:.6f} ALGO")
        print(f"  - microAlgos: {balance:,}")

        if balance_algo < 0.1:
            print("  ⚠️  잔액이 부족합니다. 최소 0.1 ALGO 필요")
            print("     (계정 유지를 위한 최소 잔액)")
        elif balance_algo < 1.0:
            print("  ⚠️  잔액이 낮습니다. 1 ALGO 이상 권장")
        else:
            print("  ✅ 잔액 충분")

        return balance_algo
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return 0

def test_create_new_account():
    """새 계정 생성 테스트 (테스트용)"""
    print(f"\n🆕 새 Algorand 계정 생성 (테스트)")

    algo_sim = AlgorandSimulator()
    account_info = algo_sim.create_account('test')

    print(f"  - 주소: {account_info['address']}")
    print(f"  - 니모닉 (처음 5단어): {' '.join(account_info['mnemonic'].split()[:5])}...")
    print(f"\n  ⚠️  실제 메인넷 계정은 지갑 앱에서 생성하세요!")

    return account_info

def validate_environment():
    """환경 설정 검증"""
    print("\n🔧 환경 설정 검증")

    config = Config()
    issues = []

    # 1. 네트워크 설정 확인
    if config.ALGORAND_NETWORK != 'mainnet':
        issues.append(f"⚠️  ALGORAND_NETWORK가 'mainnet'이 아닙니다: {config.ALGORAND_NETWORK}")
    else:
        print("  ✅ ALGORAND_NETWORK: mainnet")

    # 2. 시뮬레이션 모드 확인
    if config.SIMULATION_MODE:
        issues.append("⚠️  SIMULATION_MODE가 True입니다. False로 설정하세요.")
    else:
        print("  ✅ SIMULATION_MODE: False")

    # 3. API 엔드포인트 확인
    if 'localhost' in config.ALGORAND_ALGOD_ADDRESS:
        issues.append(f"⚠️  로컬 주소가 설정되어 있습니다: {config.ALGORAND_ALGOD_ADDRESS}")
    else:
        print(f"  ✅ ALGOD_ADDRESS: {config.ALGORAND_ALGOD_ADDRESS}")

    # 4. Flask 환경 확인
    if config.FLASK_ENV != 'production':
        print(f"  ⚠️  FLASK_ENV: {config.FLASK_ENV} (production 권장)")
    else:
        print("  ✅ FLASK_ENV: production")

    if issues:
        print(f"\n❌ {len(issues)}개의 설정 문제 발견:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("\n✅ 모든 환경 설정이 올바릅니다!")
        return True

def interactive_menu():
    """대화형 메뉴"""
    print("\n" + "=" * 50)
    print("🎯 Algorand 메인넷 테스트 메뉴")
    print("=" * 50)
    print("\n옵션을 선택하세요:")
    print("1. 환경 설정 검증")
    print("2. 네트워크 연결 테스트")
    print("3. 계정 잔액 조회")
    print("4. 새 계정 생성 (테스트)")
    print("5. 전체 테스트 실행")
    print("0. 종료")

    while True:
        choice = input("\n선택 (0-5): ").strip()

        if choice == '0':
            print("\n👋 종료합니다.")
            break
        elif choice == '1':
            validate_environment()
        elif choice == '2':
            test_mainnet_connection()
        elif choice == '3':
            address = input("\n지갑 주소를 입력하세요: ").strip()
            if address:
                test_account_balance(address)
            else:
                print("❌ 주소를 입력하지 않았습니다.")
        elif choice == '4':
            test_create_new_account()
        elif choice == '5':
            run_full_test()
        else:
            print("❌ 올바른 옵션을 선택하세요.")

def run_full_test():
    """전체 테스트 실행"""
    print("\n" + "=" * 50)
    print("🚀 전체 테스트 시작")
    print("=" * 50)

    # 1. 환경 설정 검증
    if not validate_environment():
        print("\n⚠️  환경 설정을 먼저 수정하세요.")
        return

    # 2. 연결 테스트
    if not test_mainnet_connection():
        print("\n❌ 연결 테스트 실패. 설정을 확인하세요.")
        return

    # 3. 계정 잔액 테스트
    address = input("\n지갑 주소를 입력하세요 (선택사항, Enter로 건너뛰기): ").strip()
    if address:
        test_account_balance(address)

    print("\n" + "=" * 50)
    print("✅ 전체 테스트 완료!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        # 대화형 메뉴 실행
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
