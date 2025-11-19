from dotenv import load_dotenv
import os

load_dotenv()

ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "")
ALGOD_HEADERS = {"X-Algo-API-Token": ALGOD_TOKEN} if ALGOD_TOKEN else {}
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

HCF_ADDRESS = os.getenv("HCF_ADDRESS")
HCF_MNEMONIC = os.getenv("HCF_MNEMONIC")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
ASA_ID = os.getenv("ASA_ID")
