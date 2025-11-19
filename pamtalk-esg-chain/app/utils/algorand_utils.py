# app/utils/algorand_utils.py

from algosdk.v2client import algod
from app.config import ALGOD_ADDRESS, ALGOD_TOKEN

def get_algod_client():
    headers = {
        "X-API-Key": ALGOD_TOKEN
    }
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, headers)