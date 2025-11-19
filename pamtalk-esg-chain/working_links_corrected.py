# -*- coding: utf-8 -*-
"""
실제 작동하는 Algorand 탐색기 링크 생성
2025년 현재 활성화된 탐색기들 사용
"""
import os
from algosdk import account, mnemonic
import random

class WorkingLinksGenerator:
    def __init__(self):
        # 2025년 현재 작동하는 Algorand 탐색기들
        self.explorers = {
            'algoexplorer': 'https://algoexplorer.io',
            'algoexplorer_testnet': 'https://testnet.algoexplorer.io',
            'pera': 'https://explorer.perawallet.app',
            'bitquery': 'https://explorer.bitquery.io/algorand_testnet',
            'allo': 'https://allo.info'
        }

    def create_account(self):
        private_key, address = account.generate_account()
        account_mnemonic = mnemonic.from_private_key(private_key)
        return {
            'address': address,
            'private_key': private_key,
            'mnemonic': account_mnemonic
        }

    def generate_working_links(self):
        print("=== PAM-TALK ESG Chain - 실제 작동하는 링크 생성 ===")
        print()

        # 실제 계정 생성
        admin = self.create_account()
        user1 = self.create_account()
        user2 = self.create_account()

        print("🔗 실제 작동하는 Algorand 탐색기 링크들:")
        print("-" * 60)

        # 각 탐색기별로 링크 생성
        explorers_to_test = [
            ("AlgoExplorer 메인넷", "https://algoexplorer.io"),
            ("AlgoExplorer 테스트넷", "https://testnet.algoexplorer.io"),
            ("Pera Wallet Explorer", "https://explorer.perawallet.app"),
            ("Allo.info Explorer", "https://allo.info"),
            ("Bitquery TestNet", "https://explorer.bitquery.io/algorand_testnet")
        ]

        print("\n📱 관리자 지갑 주소:")
        print(f"주소: {admin['address']}")
        for name, base_url in explorers_to_test:
            if 'bitquery' in base_url:
                print(f"{name}: {base_url}/address/{admin['address']}")
            elif 'allo' in base_url:
                print(f"{name}: {base_url}/address/{admin['address']}")
            else:
                print(f"{name}: {base_url}/address/{admin['address']}")

        print(f"\n👤 사용자1 지갑 주소:")
        print(f"주소: {user1['address']}")
        for name, base_url in explorers_to_test:
            if 'bitquery' in base_url:
                print(f"{name}: {base_url}/address/{user1['address']}")
            elif 'allo' in base_url:
                print(f"{name}: {base_url}/address/{user1['address']}")
            else:
                print(f"{name}: {base_url}/address/{user1['address']}")

        # 대체 무료 ALGO 받는 방법들
        print(f"\n💰 무료 ALGO 받는 방법들:")
        faucets = [
            "https://testnet.algoexplorer.io/dispenser",
            "https://dispenser.testnet.aws.algodev.network/",
            "https://faucet.testnet.algorand.network/",
            "https://bank.testnet.algorand.network/"
        ]

        for i, faucet in enumerate(faucets, 1):
            print(f"{i}. {faucet}")

        # 샘플 ASA 및 트랜잭션 형식
        sample_asa = random.randint(100000000, 999999999)
        sample_tx = "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for _ in range(52)])

        print(f"\n🪙 토큰(ASA) 링크 형식:")
        for name, base_url in explorers_to_test:
            if 'bitquery' not in base_url:
                print(f"{name}: {base_url}/asset/{sample_asa}")

        print(f"\n📝 거래(TX) 링크 형식:")
        for name, base_url in explorers_to_test:
            if 'bitquery' not in base_url:
                print(f"{name}: {base_url}/tx/{sample_tx}")

        # 대체 방법들
        print(f"\n🔧 대체 접근 방법들:")
        print("1. Algorand Wallet 앱 사용 (모바일)")
        print("2. MyAlgo Wallet (https://wallet.myalgo.com)")
        print("3. Pera Wallet (https://perawallet.app)")
        print("4. AlgoSigner 브라우저 확장")

        # 파일로 저장
        with open('corrected_working_links.txt', 'w', encoding='utf-8') as f:
            f.write("PAM-TALK ESG Chain - 실제 작동하는 링크들\n")
            f.write("=" * 50 + "\n\n")

            f.write("관리자 지갑:\n")
            f.write(f"주소: {admin['address']}\n")
            f.write(f"니모닉: {admin['mnemonic']}\n\n")

            f.write("사용자1 지갑:\n")
            f.write(f"주소: {user1['address']}\n")
            f.write(f"니모닉: {user1['mnemonic']}\n\n")

            f.write("탐색기 링크들:\n")
            for name, base_url in explorers_to_test:
                f.write(f"{name}:\n")
                f.write(f"  관리자: {base_url}/address/{admin['address']}\n")
                f.write(f"  사용자1: {base_url}/address/{user1['address']}\n")
                f.write(f"  샘플 ASA: {base_url}/asset/{sample_asa}\n")
                f.write(f"  샘플 TX: {base_url}/tx/{sample_tx}\n\n")

        print(f"\n💾 모든 정보가 'corrected_working_links.txt'에 저장되었습니다")

        # 실제 연결 테스트 안내
        print(f"\n✅ 실제 테스트 방법:")
        print("1. 위 링크들 중 하나를 직접 브라우저에서 테스트")
        print("2. 지갑 주소가 탐색기에서 조회되는지 확인")
        print("3. 무료 ALGO Faucet에서 테스트 ALGO 받기")
        print("4. 실제 토큰 생성 및 전송 테스트")

        return {
            'admin': admin,
            'user1': user1,
            'user2': user2,
            'sample_asa': sample_asa,
            'sample_tx': sample_tx
        }

def main():
    generator = WorkingLinksGenerator()
    results = generator.generate_working_links()

    print(f"\n🎯 다음 단계:")
    print("1. 위 링크들을 직접 브라우저에서 테스트해보세요")
    print("2. 작동하는 탐색기를 찾으면 실제 토큰 생성을 진행할 수 있습니다")
    print("3. 모든 정보는 corrected_working_links.txt 파일에 저장되었습니다")

if __name__ == "__main__":
    main()