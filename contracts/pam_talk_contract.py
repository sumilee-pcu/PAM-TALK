#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK Smart Contract

This smart contract manages PAM-TALK tokens, ESG-GOLD tokens,
agricultural transactions, and demand predictions in a simulated blockchain environment.
"""

import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Token:
    """Token data structure"""
    token_id: int
    name: str
    symbol: str
    total_supply: int
    decimals: int
    creator: str
    created_at: int
    metadata: Dict

@dataclass
class Transaction:
    """Transaction record structure"""
    tx_id: str
    from_address: str
    to_address: str
    token_id: int
    amount: int
    transaction_type: str  # 'transfer', 'mint', 'burn', 'trade'
    metadata: Dict
    timestamp: int
    block_height: int

@dataclass
class AgricultureRecord:
    """Agricultural transaction record"""
    record_id: str
    producer: str
    consumer: str
    product_type: str
    quantity: int
    price_per_unit: int
    total_value: int
    quality_score: int
    esg_score: int
    timestamp: int
    location: str
    metadata: Dict

@dataclass
class DemandPrediction:
    """Demand prediction data"""
    prediction_id: str
    product_type: str
    predicted_demand: int
    confidence_score: float
    prediction_period: str  # 'daily', 'weekly', 'monthly'
    created_by: str
    timestamp: int
    features_used: List[str]
    metadata: Dict

class PAMTalkContract:
    """PAM-TALK Smart Contract Simulator"""

    def __init__(self):
        # Contract state
        self.tokens: Dict[int, Token] = {}
        self.balances: Dict[Tuple[str, int], int] = {}  # (address, token_id) -> balance
        self.transactions: List[Transaction] = []
        self.agriculture_records: List[AgricultureRecord] = []
        self.demand_predictions: List[DemandPrediction] = []

        # Contract metadata
        self.contract_id = self._generate_id("CONTRACT")
        self.creator = ""
        self.created_at = int(time.time())
        self.block_height = 0

        # Token counters
        self.next_token_id = 1

        # Initialize default tokens
        self._initialize_default_tokens()

    def _generate_id(self, prefix: str = "") -> str:
        """Generate unique ID"""
        timestamp = str(int(time.time() * 1000000))
        random_part = hashlib.sha256(f"{prefix}{timestamp}".encode()).hexdigest()[:8]
        return f"{prefix}_{timestamp}_{random_part}" if prefix else f"{timestamp}_{random_part}"

    def _initialize_default_tokens(self):
        """Initialize PAM-TALK and ESG-GOLD tokens"""
        # PAM-TALK Token
        self.create_token(
            name="PAM-TALK Token",
            symbol="PAMT",
            total_supply=1000000000,  # 1 billion tokens
            decimals=6,
            creator="SYSTEM",
            metadata={
                "description": "PAM-TALK platform utility token",
                "use_cases": ["trading", "staking", "governance"],
                "website": "https://pam-talk.io"
            }
        )

        # ESG-GOLD Token
        self.create_token(
            name="ESG-GOLD Token",
            symbol="ESGD",
            total_supply=100000000,  # 100 million tokens
            decimals=6,
            creator="SYSTEM",
            metadata={
                "description": "ESG performance-based reward token",
                "esg_weighted": True,
                "backing": "ESG scores and environmental impact"
            }
        )

    def create_token(self, name: str, symbol: str, total_supply: int,
                    decimals: int, creator: str, metadata: Dict = None) -> int:
        """Create a new token"""
        token_id = self.next_token_id
        self.next_token_id += 1

        token = Token(
            token_id=token_id,
            name=name,
            symbol=symbol,
            total_supply=total_supply,
            decimals=decimals,
            creator=creator,
            created_at=int(time.time()),
            metadata=metadata or {}
        )

        self.tokens[token_id] = token

        # Mint initial supply to creator
        if creator != "SYSTEM":
            self.balances[(creator, token_id)] = total_supply

            # Record mint transaction
            self._record_transaction(
                from_address="",
                to_address=creator,
                token_id=token_id,
                amount=total_supply,
                transaction_type="mint",
                metadata={"reason": "initial_supply"}
            )

        return token_id

    def transfer_tokens(self, from_address: str, to_address: str,
                       token_id: int, amount: int, metadata: Dict = None) -> Dict:
        """Transfer tokens between addresses"""
        # Validation
        if token_id not in self.tokens:
            return {"success": False, "error": "Token does not exist"}

        if amount <= 0:
            return {"success": False, "error": "Amount must be positive"}

        current_balance = self.balances.get((from_address, token_id), 0)
        if current_balance < amount:
            return {"success": False, "error": "Insufficient balance"}

        # Execute transfer
        self.balances[(from_address, token_id)] = current_balance - amount
        self.balances[(to_address, token_id)] = self.balances.get((to_address, token_id), 0) + amount

        # Record transaction
        tx_id = self._record_transaction(
            from_address=from_address,
            to_address=to_address,
            token_id=token_id,
            amount=amount,
            transaction_type="transfer",
            metadata=metadata or {}
        )

        return {
            "success": True,
            "tx_id": tx_id,
            "from_balance": self.balances[(from_address, token_id)],
            "to_balance": self.balances[(to_address, token_id)]
        }

    def mint_tokens(self, to_address: str, token_id: int, amount: int,
                   creator: str, metadata: Dict = None) -> Dict:
        """Mint new tokens (only for authorized creators)"""
        if token_id not in self.tokens:
            return {"success": False, "error": "Token does not exist"}

        token = self.tokens[token_id]
        if token.creator != creator and creator != "SYSTEM":
            return {"success": False, "error": "Not authorized to mint"}

        # Update supply and balance
        token.total_supply += amount
        self.balances[(to_address, token_id)] = self.balances.get((to_address, token_id), 0) + amount

        # Record transaction
        tx_id = self._record_transaction(
            from_address="",
            to_address=to_address,
            token_id=token_id,
            amount=amount,
            transaction_type="mint",
            metadata=metadata or {}
        )

        return {
            "success": True,
            "tx_id": tx_id,
            "new_balance": self.balances[(to_address, token_id)],
            "total_supply": token.total_supply
        }

    def record_agriculture_transaction(self, producer: str, consumer: str,
                                     product_type: str, quantity: int,
                                     price_per_unit: int, quality_score: int,
                                     esg_score: int, location: str,
                                     metadata: Dict = None) -> str:
        """Record an agricultural transaction"""
        record_id = self._generate_id("AGR")
        total_value = quantity * price_per_unit

        record = AgricultureRecord(
            record_id=record_id,
            producer=producer,
            consumer=consumer,
            product_type=product_type,
            quantity=quantity,
            price_per_unit=price_per_unit,
            total_value=total_value,
            quality_score=quality_score,
            esg_score=esg_score,
            timestamp=int(time.time()),
            location=location,
            metadata=metadata or {}
        )

        self.agriculture_records.append(record)

        # Calculate ESG-GOLD rewards
        self._calculate_esg_rewards(producer, esg_score, total_value)

        return record_id

    def store_demand_prediction(self, product_type: str, predicted_demand: int,
                               confidence_score: float, prediction_period: str,
                               created_by: str, features_used: List[str],
                               metadata: Dict = None) -> str:
        """Store demand prediction result"""
        prediction_id = self._generate_id("PRED")

        prediction = DemandPrediction(
            prediction_id=prediction_id,
            product_type=product_type,
            predicted_demand=predicted_demand,
            confidence_score=confidence_score,
            prediction_period=prediction_period,
            created_by=created_by,
            timestamp=int(time.time()),
            features_used=features_used,
            metadata=metadata or {}
        )

        self.demand_predictions.append(prediction)
        return prediction_id

    def get_esg_score(self, address: str, period_days: int = 30) -> Dict:
        """Calculate ESG score for an address based on recent transactions"""
        cutoff_time = int(time.time()) - (period_days * 24 * 3600)

        relevant_records = [
            record for record in self.agriculture_records
            if (record.producer == address or record.consumer == address)
            and record.timestamp >= cutoff_time
        ]

        if not relevant_records:
            return {
                "address": address,
                "esg_score": 0,
                "transactions_count": 0,
                "period_days": period_days,
                "breakdown": {}
            }

        # Calculate weighted ESG score
        total_value = sum(record.total_value for record in relevant_records)
        weighted_score = sum(
            record.esg_score * record.total_value
            for record in relevant_records
        ) / total_value if total_value > 0 else 0

        # ESG breakdown
        environmental_scores = [r.esg_score for r in relevant_records if 'environmental' in r.metadata.get('categories', [])]
        social_scores = [r.esg_score for r in relevant_records if 'social' in r.metadata.get('categories', [])]
        governance_scores = [r.esg_score for r in relevant_records if 'governance' in r.metadata.get('categories', [])]

        breakdown = {
            "environmental": sum(environmental_scores) / len(environmental_scores) if environmental_scores else 0,
            "social": sum(social_scores) / len(social_scores) if social_scores else 0,
            "governance": sum(governance_scores) / len(governance_scores) if governance_scores else 0
        }

        return {
            "address": address,
            "esg_score": round(weighted_score, 2),
            "transactions_count": len(relevant_records),
            "period_days": period_days,
            "total_trade_value": total_value,
            "breakdown": breakdown
        }

    def get_balance(self, address: str, token_id: int) -> int:
        """Get token balance for address"""
        return self.balances.get((address, token_id), 0)

    def get_token_info(self, token_id: int) -> Optional[Dict]:
        """Get token information"""
        if token_id not in self.tokens:
            return None

        token = self.tokens[token_id]
        return {
            "token_id": token.token_id,
            "name": token.name,
            "symbol": token.symbol,
            "total_supply": token.total_supply,
            "decimals": token.decimals,
            "creator": token.creator,
            "created_at": token.created_at,
            "metadata": token.metadata
        }

    def get_transaction_history(self, address: str = None, token_id: int = None,
                               limit: int = 100) -> List[Dict]:
        """Get transaction history"""
        filtered_txs = self.transactions

        if address:
            filtered_txs = [
                tx for tx in filtered_txs
                if tx.from_address == address or tx.to_address == address
            ]

        if token_id:
            filtered_txs = [tx for tx in filtered_txs if tx.token_id == token_id]

        # Sort by timestamp (newest first) and limit
        filtered_txs.sort(key=lambda x: x.timestamp, reverse=True)
        return [asdict(tx) for tx in filtered_txs[:limit]]

    def get_agriculture_records(self, producer: str = None, consumer: str = None,
                               product_type: str = None, limit: int = 100) -> List[Dict]:
        """Get agriculture transaction records"""
        filtered_records = self.agriculture_records

        if producer:
            filtered_records = [r for r in filtered_records if r.producer == producer]
        if consumer:
            filtered_records = [r for r in filtered_records if r.consumer == consumer]
        if product_type:
            filtered_records = [r for r in filtered_records if r.product_type == product_type]

        filtered_records.sort(key=lambda x: x.timestamp, reverse=True)
        return [asdict(record) for record in filtered_records[:limit]]

    def get_demand_predictions(self, product_type: str = None, created_by: str = None,
                              limit: int = 50) -> List[Dict]:
        """Get demand predictions"""
        filtered_predictions = self.demand_predictions

        if product_type:
            filtered_predictions = [p for p in filtered_predictions if p.product_type == product_type]
        if created_by:
            filtered_predictions = [p for p in filtered_predictions if p.created_by == created_by]

        filtered_predictions.sort(key=lambda x: x.timestamp, reverse=True)
        return [asdict(pred) for pred in filtered_predictions[:limit]]

    def _record_transaction(self, from_address: str, to_address: str,
                           token_id: int, amount: int, transaction_type: str,
                           metadata: Dict) -> str:
        """Internal function to record a transaction"""
        tx_id = self._generate_id("TX")
        self.block_height += 1

        transaction = Transaction(
            tx_id=tx_id,
            from_address=from_address,
            to_address=to_address,
            token_id=token_id,
            amount=amount,
            transaction_type=transaction_type,
            metadata=metadata,
            timestamp=int(time.time()),
            block_height=self.block_height
        )

        self.transactions.append(transaction)
        return tx_id

    def _calculate_esg_rewards(self, producer: str, esg_score: int, trade_value: int):
        """Calculate and mint ESG-GOLD rewards based on ESG score"""
        # ESG-GOLD token (assuming token_id = 2)
        esg_token_id = 2

        # Reward formula: higher ESG score = more rewards
        # Base reward rate: 1 ESGD per 1000 trade value
        # ESG multiplier: 1.0 to 2.0 based on score (0-100)
        base_reward = trade_value // 1000
        esg_multiplier = 1.0 + (esg_score / 100.0)  # 1.0 to 2.0
        reward_amount = int(base_reward * esg_multiplier * 1000000)  # Convert to microunits

        if reward_amount > 0:
            self.mint_tokens(
                to_address=producer,
                token_id=esg_token_id,
                amount=reward_amount,
                creator="SYSTEM",
                metadata={
                    "reason": "esg_reward",
                    "esg_score": esg_score,
                    "trade_value": trade_value,
                    "multiplier": esg_multiplier
                }
            )

    def get_contract_stats(self) -> Dict:
        """Get overall contract statistics"""
        return {
            "contract_id": self.contract_id,
            "created_at": self.created_at,
            "block_height": self.block_height,
            "total_tokens": len(self.tokens),
            "total_transactions": len(self.transactions),
            "total_agriculture_records": len(self.agriculture_records),
            "total_demand_predictions": len(self.demand_predictions),
            "unique_addresses": len(set(
                [addr for (addr, _) in self.balances.keys()]
            ))
        }

# Global contract instance for simulation
pam_talk_contract = PAMTalkContract()

def create_application() -> Dict:
    """Create and deploy PAM-TALK application"""
    contract = pam_talk_contract

    return {
        "success": True,
        "contract_id": contract.contract_id,
        "created_at": contract.created_at,
        "tokens_created": len(contract.tokens),
        "message": "PAM-TALK contract deployed successfully"
    }

def transfer_tokens(from_address: str, to_address: str, token_id: int,
                   amount: int, metadata: Dict = None) -> Dict:
    """Transfer tokens wrapper function"""
    return pam_talk_contract.transfer_tokens(
        from_address, to_address, token_id, amount, metadata
    )

def record_transaction(producer: str, consumer: str, product_type: str,
                      quantity: int, price_per_unit: int, quality_score: int,
                      esg_score: int, location: str, metadata: Dict = None) -> Dict:
    """Record agricultural transaction wrapper function"""
    record_id = pam_talk_contract.record_agriculture_transaction(
        producer, consumer, product_type, quantity, price_per_unit,
        quality_score, esg_score, location, metadata
    )

    return {
        "success": True,
        "record_id": record_id,
        "message": "Agriculture transaction recorded successfully"
    }

def get_esg_score(address: str, period_days: int = 30) -> Dict:
    """Get ESG score wrapper function"""
    return pam_talk_contract.get_esg_score(address, period_days)