"""
Simple Flask admin dashboard for monitoring account balance and token info.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from flask import Flask, jsonify, render_template_string

ADMIN_ADDRESS = "HXEHBWEDLO272XOIFFME26D5EAWULT4PGE75V3NKGGBIMQL2JM7S4ZU5PM"
ACCOUNT_API_URL = (
    f"https://testnet-api.algonode.cloud/v2/accounts/{ADMIN_ADDRESS}"
)
TOKEN_INFO_PATH = Path(__file__).resolve().parent.parent / "pam_token_created.txt"

app = Flask(__name__)


def fetch_balance() -> Dict[str, Any]:
    """Fetch latest balance information from Algonode API."""
    try:
        response = requests.get(ACCOUNT_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        micro_algo = data.get("amount", 0)
        algo_balance = micro_algo / 1_000_000
        return {
            "address": ADMIN_ADDRESS,
            "balance_micro": micro_algo,
            "balance_algo": algo_balance,
        }
    except requests.RequestException as exc:
        return {
            "address": ADMIN_ADDRESS,
            "error": str(exc),
        }


def load_token_info() -> Optional[Dict[str, str]]:
    """Read token creation summary if it exists."""
    if not TOKEN_INFO_PATH.exists():
        return None

    raw_text = TOKEN_INFO_PATH.read_text(encoding="utf-8")

    # Older scripts saved literal \n sequences instead of actual newlines.
    if "\n" in raw_text and "
" not in raw_text:
        lines = raw_text.split("\n")
    else:
        lines = raw_text.splitlines()

    info: Dict[str, str] = {}
    for line in lines:
        line = line.strip()
        if line.startswith("REAL ASA ID:"):
            info["asset_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("REAL Creation TX:"):
            info["tx_id"] = line.split(":", 1)[1].strip()
        elif line.startswith("API Asset Info:"):
            info["asset_url"] = line.split(":", 1)[1].strip()
        elif line.startswith("API Transaction:"):
            info["tx_url"] = line.split(":", 1)[1].strip()
    return info or None


@app.route("/api/balance")
def api_balance():
    return jsonify(fetch_balance())


@app.route("/api/token")
def api_token():
    info = load_token_info()
    if info is None:
        return jsonify({"message": "Token has not been created yet."}), 404
    return jsonify(info)


@app.route("/")
def index():
    balance = fetch_balance()
    token_info = load_token_info()

    template = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>PAM Admin Dashboard</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 2rem; }
          h1 { color: #0a516d; }
          .card { border: 1px solid #dee2e6; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
          code { background: #f8f9fa; padding: 0.2rem 0.4rem; border-radius: 4px; }
          a { color: #0a516d; }
        </style>
      </head>
      <body>
        <h1>PAM Admin Dashboard</h1>
        <div class="card">
          <h2>Account Balance</h2>
          <p><strong>Address:</strong> <code>{{ balance.address }}</code></p>
          {% if balance.error %}
            <p style="color: #c0392b;">API Error: {{ balance.error }}</p>
          {% else %}
            <p><strong>Balance:</strong> {{ "{:.6f}".format(balance.balance_algo) }} ALGO</p>
            <p><small>{{ balance.balance_micro | int }} microAlgos</small></p>
          {% endif %}
        </div>

        <div class="card">
          <h2>Latest Token</h2>
          {% if token_info %}
            <p><strong>ASA ID:</strong> <code>{{ token_info.asset_id }}</code></p>
            <p><strong>Transaction:</strong> <code>{{ token_info.tx_id }}</code></p>
            <p>
              <a href="{{ token_info.asset_url }}" target="_blank">View Asset API</a> |
              <a href="{{ token_info.tx_url }}" target="_blank">View Transaction API</a>
            </p>
          {% else %}
            <p>No token record found. Run <code>python step2_create_token.py</code> first.</p>
          {% endif %}
        </div>
      </body>
    </html>
    """
    return render_template_string(template, balance=balance, token_info=token_info)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
