#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-TALK ESG Score Calculator

This module implements comprehensive ESG (Environmental, Social, Governance) scoring
for agricultural farms and producers, with integration to ESG-GOLD token issuance.
"""

import math
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np

@dataclass
class ESGScore:
    """ESG Score data structure"""
    farm_id: str
    environmental_score: float
    social_score: float
    governance_score: float
    overall_score: float
    score_breakdown: Dict
    esg_gold_tokens: int
    calculated_at: str
    valid_until: str
    certification_level: str

@dataclass
class FarmData:
    """Farm data structure for ESG calculation"""
    farm_id: str
    farm_name: str
    location: str
    size_hectares: float

    # Environmental data
    organic_certified: bool
    water_usage_per_hectare: float  # liters per hectare per year
    carbon_emissions: float  # tons CO2 per hectare per year
    renewable_energy_percentage: float  # 0-100
    biodiversity_score: int  # 0-10
    soil_health_score: int  # 0-10
    waste_management_score: int  # 0-10

    # Social data
    fair_wage_certification: bool
    community_investment_percentage: float  # 0-100 (% of revenue)
    worker_safety_score: int  # 0-10
    local_employment_percentage: float  # 0-100
    training_programs: bool
    healthcare_provided: bool

    # Governance data
    transparency_score: int  # 0-10
    certifications: List[str]
    record_keeping_score: int  # 0-10
    stakeholder_engagement_score: int  # 0-10
    ethical_practices_score: int  # 0-10
    supply_chain_traceability: bool

class ESGCalculator:
    """
    Comprehensive ESG Score Calculator for Agricultural Farms
    """

    def __init__(self):
        self.scoring_weights = {
            'environmental': 0.40,  # 40% weight
            'social': 0.35,         # 35% weight
            'governance': 0.25      # 25% weight
        }

        self.environmental_weights = {
            'organic_certification': 0.20,
            'water_efficiency': 0.20,
            'carbon_footprint': 0.25,
            'renewable_energy': 0.15,
            'biodiversity': 0.10,
            'soil_health': 0.10
        }

        self.social_weights = {
            'fair_wage': 0.25,
            'community_investment': 0.20,
            'worker_safety': 0.25,
            'local_employment': 0.15,
            'training_healthcare': 0.15
        }

        self.governance_weights = {
            'transparency': 0.25,
            'certifications': 0.25,
            'record_keeping': 0.20,
            'stakeholder_engagement': 0.15,
            'ethical_practices': 0.15
        }

        self.certification_mapping = {
            'organic': 25,
            'fair_trade': 20,
            'carbon_neutral': 20,
            'rainforest_alliance': 15,
            'global_gap': 10,
            'iso_14001': 15,
            'social_accountability': 15
        }

        self.token_multiplier_base = 1000  # Base tokens per ESG point
        self.size_factor_threshold = 10    # hectares

    def calculate_environmental_score(self, farm_data: FarmData) -> Tuple[float, Dict]:
        """Calculate Environmental (E) score"""
        scores = {}
        breakdown = {}

        # Organic Certification (0-100)
        organic_score = 100 if farm_data.organic_certified else 0
        scores['organic_certification'] = organic_score
        breakdown['organic_certification'] = {
            'score': organic_score,
            'criteria': 'Organic certified' if farm_data.organic_certified else 'Not organic certified',
            'impact': 'High positive impact on soil and ecosystem health' if farm_data.organic_certified else 'Opportunity for improvement'
        }

        # Water Efficiency (0-100, lower usage = higher score)
        # Benchmark: <5000L/ha = excellent, >20000L/ha = poor
        if farm_data.water_usage_per_hectare <= 5000:
            water_score = 100
        elif farm_data.water_usage_per_hectare >= 20000:
            water_score = 0
        else:
            water_score = max(0, 100 - ((farm_data.water_usage_per_hectare - 5000) / 150))

        scores['water_efficiency'] = water_score
        breakdown['water_efficiency'] = {
            'score': round(water_score, 1),
            'usage': f"{farm_data.water_usage_per_hectare:,.0f} L/ha/year",
            'benchmark': 'Excellent (<5000), Good (5000-12000), Poor (>20000)',
            'recommendation': 'Implement drip irrigation' if water_score < 70 else 'Water usage is efficient'
        }

        # Carbon Footprint (0-100, lower emissions = higher score)
        # Benchmark: <2 tons/ha = excellent, >8 tons/ha = poor
        if farm_data.carbon_emissions <= 2:
            carbon_score = 100
        elif farm_data.carbon_emissions >= 8:
            carbon_score = 0
        else:
            carbon_score = max(0, 100 - ((farm_data.carbon_emissions - 2) * 16.67))

        scores['carbon_footprint'] = carbon_score
        breakdown['carbon_footprint'] = {
            'score': round(carbon_score, 1),
            'emissions': f"{farm_data.carbon_emissions:.1f} tons CO2/ha/year",
            'benchmark': 'Excellent (<2), Good (2-5), Poor (>8)',
            'recommendation': 'Reduce machinery use and implement carbon sequestration' if carbon_score < 70 else 'Carbon footprint is well managed'
        }

        # Renewable Energy (0-100, direct mapping)
        renewable_score = farm_data.renewable_energy_percentage
        scores['renewable_energy'] = renewable_score
        breakdown['renewable_energy'] = {
            'score': renewable_score,
            'percentage': f"{renewable_score}% renewable energy",
            'recommendation': 'Install solar panels or wind turbines' if renewable_score < 50 else 'Good renewable energy adoption'
        }

        # Biodiversity (0-100, scale from 0-10 to 0-100)
        biodiversity_score = farm_data.biodiversity_score * 10
        scores['biodiversity'] = biodiversity_score
        breakdown['biodiversity'] = {
            'score': biodiversity_score,
            'raw_score': f"{farm_data.biodiversity_score}/10",
            'recommendation': 'Plant native species and create wildlife corridors' if biodiversity_score < 70 else 'Biodiversity is well supported'
        }

        # Soil Health (0-100, scale from 0-10 to 0-100)
        soil_score = farm_data.soil_health_score * 10
        scores['soil_health'] = soil_score
        breakdown['soil_health'] = {
            'score': soil_score,
            'raw_score': f"{farm_data.soil_health_score}/10",
            'recommendation': 'Implement cover cropping and reduce tillage' if soil_score < 70 else 'Soil health is well maintained'
        }

        # Calculate weighted environmental score
        environmental_score = sum(
            scores[key] * self.environmental_weights[key]
            for key in scores.keys()
        )

        return environmental_score, breakdown

    def calculate_social_score(self, farm_data: FarmData) -> Tuple[float, Dict]:
        """Calculate Social (S) score"""
        scores = {}
        breakdown = {}

        # Fair Wage Certification (0-100)
        fair_wage_score = 100 if farm_data.fair_wage_certification else 0
        scores['fair_wage'] = fair_wage_score
        breakdown['fair_wage'] = {
            'score': fair_wage_score,
            'certified': farm_data.fair_wage_certification,
            'recommendation': 'Obtain fair wage certification' if not farm_data.fair_wage_certification else 'Fair wage practices certified'
        }

        # Community Investment (0-100, direct mapping)
        community_score = min(100, farm_data.community_investment_percentage * 10)  # Cap at 100
        scores['community_investment'] = community_score
        breakdown['community_investment'] = {
            'score': community_score,
            'percentage': f"{farm_data.community_investment_percentage}% of revenue",
            'recommendation': 'Increase community investment' if community_score < 50 else 'Strong community engagement'
        }

        # Worker Safety (0-100, scale from 0-10 to 0-100)
        safety_score = farm_data.worker_safety_score * 10
        scores['worker_safety'] = safety_score
        breakdown['worker_safety'] = {
            'score': safety_score,
            'raw_score': f"{farm_data.worker_safety_score}/10",
            'recommendation': 'Improve safety training and equipment' if safety_score < 70 else 'Worker safety is well managed'
        }

        # Local Employment (0-100, direct mapping)
        local_employment_score = farm_data.local_employment_percentage
        scores['local_employment'] = local_employment_score
        breakdown['local_employment'] = {
            'score': local_employment_score,
            'percentage': f"{local_employment_score}% local workers",
            'recommendation': 'Hire more locally' if local_employment_score < 70 else 'Strong local employment'
        }

        # Training and Healthcare (0-100, bonus for both)
        training_healthcare_score = 0
        if farm_data.training_programs:
            training_healthcare_score += 50
        if farm_data.healthcare_provided:
            training_healthcare_score += 50

        scores['training_healthcare'] = training_healthcare_score
        breakdown['training_healthcare'] = {
            'score': training_healthcare_score,
            'training': farm_data.training_programs,
            'healthcare': farm_data.healthcare_provided,
            'recommendation': 'Provide both training and healthcare benefits' if training_healthcare_score < 100 else 'Comprehensive worker benefits'
        }

        # Calculate weighted social score
        social_score = sum(
            scores[key] * self.social_weights[key]
            for key in scores.keys()
        )

        return social_score, breakdown

    def calculate_governance_score(self, farm_data: FarmData) -> Tuple[float, Dict]:
        """Calculate Governance (G) score"""
        scores = {}
        breakdown = {}

        # Transparency (0-100, scale from 0-10 to 0-100)
        transparency_score = farm_data.transparency_score * 10
        scores['transparency'] = transparency_score
        breakdown['transparency'] = {
            'score': transparency_score,
            'raw_score': f"{farm_data.transparency_score}/10",
            'recommendation': 'Improve data sharing and reporting' if transparency_score < 70 else 'Excellent transparency practices'
        }

        # Certifications (0-100, weighted by certification importance)
        cert_score = 0
        cert_details = []
        for cert in farm_data.certifications:
            cert_lower = cert.lower().replace(' ', '_')
            if cert_lower in self.certification_mapping:
                cert_value = self.certification_mapping[cert_lower]
                cert_score += cert_value
                cert_details.append(f"{cert}: {cert_value} points")

        cert_score = min(100, cert_score)  # Cap at 100
        scores['certifications'] = cert_score
        breakdown['certifications'] = {
            'score': cert_score,
            'count': len(farm_data.certifications),
            'details': cert_details,
            'recommendation': 'Obtain additional certifications (Organic, Fair Trade, etc.)' if cert_score < 70 else 'Strong certification portfolio'
        }

        # Record Keeping (0-100, scale from 0-10 to 0-100)
        record_score = farm_data.record_keeping_score * 10
        scores['record_keeping'] = record_score
        breakdown['record_keeping'] = {
            'score': record_score,
            'raw_score': f"{farm_data.record_keeping_score}/10",
            'recommendation': 'Implement digital record keeping systems' if record_score < 70 else 'Excellent record management'
        }

        # Stakeholder Engagement (0-100, scale from 0-10 to 0-100)
        engagement_score = farm_data.stakeholder_engagement_score * 10
        scores['stakeholder_engagement'] = engagement_score
        breakdown['stakeholder_engagement'] = {
            'score': engagement_score,
            'raw_score': f"{farm_data.stakeholder_engagement_score}/10",
            'recommendation': 'Increase community and investor engagement' if engagement_score < 70 else 'Strong stakeholder relationships'
        }

        # Ethical Practices (0-100, scale from 0-10 to 0-100)
        ethical_score = farm_data.ethical_practices_score * 10
        scores['ethical_practices'] = ethical_score
        breakdown['ethical_practices'] = {
            'score': ethical_score,
            'raw_score': f"{farm_data.ethical_practices_score}/10",
            'traceability': farm_data.supply_chain_traceability,
            'recommendation': 'Strengthen ethical guidelines and supply chain transparency' if ethical_score < 70 else 'Strong ethical practices'
        }

        # Calculate weighted governance score
        governance_score = sum(
            scores[key] * self.governance_weights[key]
            for key in scores.keys()
        )

        return governance_score, breakdown

    def calculate_esg_gold_tokens(self, overall_score: float, farm_size: float,
                                 trade_volume: Optional[float] = None) -> int:
        """Calculate ESG-GOLD token issuance based on ESG score and farm characteristics"""

        # Base tokens calculation
        base_tokens = overall_score * self.token_multiplier_base

        # Size factor (larger farms get diminishing returns)
        if farm_size <= self.size_factor_threshold:
            size_factor = 1.0
        else:
            size_factor = 1.0 + math.log10(farm_size / self.size_factor_threshold) * 0.5

        # ESG tier multiplier
        if overall_score >= 90:
            tier_multiplier = 2.0  # Platinum tier
        elif overall_score >= 80:
            tier_multiplier = 1.5  # Gold tier
        elif overall_score >= 70:
            tier_multiplier = 1.2  # Silver tier
        elif overall_score >= 60:
            tier_multiplier = 1.0  # Bronze tier
        else:
            tier_multiplier = 0.5  # Improvement needed

        # Trade volume bonus (if provided)
        volume_bonus = 1.0
        if trade_volume:
            volume_bonus = min(2.0, 1.0 + (trade_volume / 1000000))  # Up to 2x bonus for high volume

        # Calculate final tokens
        final_tokens = int(base_tokens * size_factor * tier_multiplier * volume_bonus)

        return final_tokens

    def determine_certification_level(self, overall_score: float) -> str:
        """Determine ESG certification level based on score"""
        if overall_score >= 90:
            return "ESG Platinum"
        elif overall_score >= 80:
            return "ESG Gold"
        elif overall_score >= 70:
            return "ESG Silver"
        elif overall_score >= 60:
            return "ESG Bronze"
        else:
            return "ESG Candidate"

    def calculate_score(self, farm_data: FarmData, trade_volume: Optional[float] = None) -> ESGScore:
        """
        Main method to calculate comprehensive ESG score

        Args:
            farm_data: Farm data for ESG calculation
            trade_volume: Optional trade volume for token bonus calculation

        Returns:
            ESGScore object with detailed breakdown
        """

        # Calculate individual component scores
        env_score, env_breakdown = self.calculate_environmental_score(farm_data)
        social_score, social_breakdown = self.calculate_social_score(farm_data)
        gov_score, gov_breakdown = self.calculate_governance_score(farm_data)

        # Calculate overall weighted score
        overall_score = (
            env_score * self.scoring_weights['environmental'] +
            social_score * self.scoring_weights['social'] +
            gov_score * self.scoring_weights['governance']
        )

        # Calculate ESG-GOLD token issuance
        esg_gold_tokens = self.calculate_esg_gold_tokens(overall_score, farm_data.size_hectares, trade_volume)

        # Determine certification level
        certification_level = self.determine_certification_level(overall_score)

        # Create detailed score breakdown
        score_breakdown = {
            'environmental': {
                'score': round(env_score, 2),
                'weight': self.scoring_weights['environmental'],
                'weighted_contribution': round(env_score * self.scoring_weights['environmental'], 2),
                'breakdown': env_breakdown
            },
            'social': {
                'score': round(social_score, 2),
                'weight': self.scoring_weights['social'],
                'weighted_contribution': round(social_score * self.scoring_weights['social'], 2),
                'breakdown': social_breakdown
            },
            'governance': {
                'score': round(gov_score, 2),
                'weight': self.scoring_weights['governance'],
                'weighted_contribution': round(gov_score * self.scoring_weights['governance'], 2),
                'breakdown': gov_breakdown
            },
            'calculation_details': {
                'base_tokens': overall_score * self.token_multiplier_base,
                'farm_size_factor': farm_data.size_hectares,
                'trade_volume_bonus': trade_volume if trade_volume else 0,
                'final_token_calculation': f"{overall_score:.2f} × {self.token_multiplier_base} × multipliers = {esg_gold_tokens}"
            }
        }

        # Create ESG Score object
        now = datetime.now()
        valid_until = now + timedelta(days=365)  # Valid for 1 year

        esg_score = ESGScore(
            farm_id=farm_data.farm_id,
            environmental_score=round(env_score, 2),
            social_score=round(social_score, 2),
            governance_score=round(gov_score, 2),
            overall_score=round(overall_score, 2),
            score_breakdown=score_breakdown,
            esg_gold_tokens=esg_gold_tokens,
            calculated_at=now.isoformat(),
            valid_until=valid_until.isoformat(),
            certification_level=certification_level
        )

        return esg_score

    def generate_improvement_recommendations(self, esg_score: ESGScore) -> Dict[str, List[str]]:
        """Generate specific improvement recommendations based on ESG score"""
        recommendations = {
            'environmental': [],
            'social': [],
            'governance': [],
            'priority_actions': []
        }

        # Environmental recommendations
        env_breakdown = esg_score.score_breakdown['environmental']['breakdown']
        if env_breakdown['organic_certification']['score'] < 100:
            recommendations['environmental'].append('Obtain organic certification to improve environmental score by up to 20 points')

        if env_breakdown['water_efficiency']['score'] < 70:
            recommendations['environmental'].append('Implement water-efficient irrigation systems (drip irrigation, moisture sensors)')
            recommendations['priority_actions'].append('Water efficiency improvement - High impact')

        if env_breakdown['carbon_footprint']['score'] < 70:
            recommendations['environmental'].append('Reduce carbon emissions through renewable energy and efficient machinery')
            recommendations['priority_actions'].append('Carbon footprint reduction - High impact')

        # Social recommendations
        social_breakdown = esg_score.score_breakdown['social']['breakdown']
        if social_breakdown['fair_wage']['score'] < 100:
            recommendations['social'].append('Obtain fair wage certification')
            recommendations['priority_actions'].append('Fair wage certification - Medium impact')

        if social_breakdown['worker_safety']['score'] < 70:
            recommendations['social'].append('Improve worker safety training and provide better protective equipment')

        # Governance recommendations
        gov_breakdown = esg_score.score_breakdown['governance']['breakdown']
        if gov_breakdown['certifications']['score'] < 70:
            recommendations['governance'].append('Obtain additional certifications (ISO 14001, Rainforest Alliance, etc.)')

        if gov_breakdown['transparency']['score'] < 70:
            recommendations['governance'].append('Implement transparent reporting systems and regular stakeholder updates')

        return recommendations

    def compare_farms(self, farm_scores: List[ESGScore]) -> Dict:
        """Compare multiple farms' ESG scores"""
        if not farm_scores:
            return {}

        comparison = {
            'farm_count': len(farm_scores),
            'average_scores': {
                'environmental': np.mean([score.environmental_score for score in farm_scores]),
                'social': np.mean([score.social_score for score in farm_scores]),
                'governance': np.mean([score.governance_score for score in farm_scores]),
                'overall': np.mean([score.overall_score for score in farm_scores])
            },
            'top_performers': {
                'environmental': max(farm_scores, key=lambda x: x.environmental_score),
                'social': max(farm_scores, key=lambda x: x.social_score),
                'governance': max(farm_scores, key=lambda x: x.governance_score),
                'overall': max(farm_scores, key=lambda x: x.overall_score)
            },
            'certification_distribution': {},
            'total_esg_tokens': sum(score.esg_gold_tokens for score in farm_scores)
        }

        # Count certification levels
        cert_levels = [score.certification_level for score in farm_scores]
        for level in set(cert_levels):
            comparison['certification_distribution'][level] = cert_levels.count(level)

        return comparison

    def save_esg_assessment(self, esg_score: ESGScore, filename: Optional[str] = None) -> str:
        """Save ESG assessment to file"""
        if not filename:
            filename = f"data/esg_assessments/{esg_score.farm_id}_esg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Create directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Convert to dictionary for JSON serialization
        assessment_data = asdict(esg_score)

        with open(filename, 'w') as f:
            json.dump(assessment_data, f, indent=2, default=str)

        return filename