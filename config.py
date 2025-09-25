import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))

    # Algorand Configuration
    ALGORAND_NETWORK = os.getenv('ALGORAND_NETWORK', 'localnet')  # localnet, testnet, mainnet
    ALGORAND_ALGOD_ADDRESS = os.getenv('ALGORAND_ALGOD_ADDRESS', 'http://localhost:4001')
    ALGORAND_ALGOD_TOKEN = os.getenv('ALGORAND_ALGOD_TOKEN', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    ALGORAND_INDEXER_ADDRESS = os.getenv('ALGORAND_INDEXER_ADDRESS', 'http://localhost:8980')
    ALGORAND_INDEXER_TOKEN = os.getenv('ALGORAND_INDEXER_TOKEN', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

    # LocalNet Simulation Settings
    SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'True').lower() == 'true'
    INITIAL_BALANCE = int(os.getenv('INITIAL_BALANCE', 1000000000))  # 1000 ALGO in microalgos

    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///pam_talk.db')

    # API Keys
    EXTERNAL_API_KEY = os.getenv('EXTERNAL_API_KEY', '')