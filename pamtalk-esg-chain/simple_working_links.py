"""
Simple Working Algorand Links Generator
No special characters, just working links
"""
from algosdk import account, mnemonic
import random

def create_account():
    private_key, address = account.generate_account()
    account_mnemonic = mnemonic.from_private_key(private_key)
    return {
        'address': address,
        'private_key': private_key,
        'mnemonic': account_mnemonic
    }

def main():
    print("PAM-TALK ESG Chain - Working Algorand Explorer Links")
    print("=" * 60)

    # Create real accounts
    admin = create_account()
    user1 = create_account()

    print("\nGENERATED ACCOUNTS:")
    print("-" * 30)
    print(f"Admin Address: {admin['address']}")
    print(f"User1 Address: {user1['address']}")

    # Working explorer URLs (as of 2025)
    explorers = [
        ("AlgoExplorer MainNet", "https://algoexplorer.io"),
        ("AlgoExplorer TestNet", "https://testnet.algoexplorer.io"),
        ("Pera Explorer", "https://explorer.perawallet.app"),
        ("Allo Explorer", "https://allo.info"),
        ("AlgoDEV TestNet", "https://testnet-api.algonode.cloud")
    ]

    print("\nTRY THESE EXPLORER LINKS:")
    print("-" * 40)

    for name, base_url in explorers:
        print(f"\n{name}:")
        print(f"  Admin Wallet: {base_url}/address/{admin['address']}")
        print(f"  User1 Wallet: {base_url}/address/{user1['address']}")

    # Faucet URLs
    print(f"\nFREE ALGO FAUCETS:")
    print("-" * 20)
    faucets = [
        "https://testnet.algoexplorer.io/dispenser",
        "https://dispenser.testnet.aws.algodev.network/",
        "https://bank.testnet.algorand.network/"
    ]

    for i, faucet in enumerate(faucets, 1):
        print(f"{i}. {faucet}")

    # Sample ASA and TX formats
    sample_asa = random.randint(100000000, 999999999)
    sample_tx = "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for _ in range(52)])

    print(f"\nSAMPLE TOKEN (ASA) LINKS:")
    print(f"https://algoexplorer.io/asset/{sample_asa}")
    print(f"https://testnet.algoexplorer.io/asset/{sample_asa}")

    print(f"\nSAMPLE TRANSACTION LINKS:")
    print(f"https://algoexplorer.io/tx/{sample_tx}")
    print(f"https://testnet.algoexplorer.io/tx/{sample_tx}")

    # Save to file
    with open('working_algorand_links.txt', 'w') as f:
        f.write("PAM-TALK ESG Chain - Working Algorand Links\n")
        f.write("=" * 50 + "\n\n")

        f.write("ACCOUNT INFORMATION:\n")
        f.write(f"Admin Address: {admin['address']}\n")
        f.write(f"Admin Mnemonic: {admin['mnemonic']}\n\n")
        f.write(f"User1 Address: {user1['address']}\n")
        f.write(f"User1 Mnemonic: {user1['mnemonic']}\n\n")

        f.write("EXPLORER LINKS TO TRY:\n")
        for name, base_url in explorers:
            f.write(f"\n{name}:\n")
            f.write(f"Admin: {base_url}/address/{admin['address']}\n")
            f.write(f"User1: {base_url}/address/{user1['address']}\n")

        f.write(f"\nFAUCET LINKS:\n")
        for faucet in faucets:
            f.write(f"{faucet}\n")

    print(f"\nSUCCESS! Information saved to 'working_algorand_links.txt'")
    print(f"\nNEXT STEPS:")
    print(f"1. Try the explorer links above in your browser")
    print(f"2. Use faucet links to get free test ALGO")
    print(f"3. Once you have ALGO, create real tokens and transactions")
    print(f"4. All real transactions will have working explorer links!")

if __name__ == "__main__":
    main()

    