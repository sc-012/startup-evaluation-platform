"""
AI-Powered Startup Evaluation Metrics Framework
Implements the 5-category evaluation system based on the CSV framework
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class EvaluationMetrics:
    """Comprehensive evaluation metrics for startup assessment"""
    financial_health_score: float
    team_quality_score: float
    market_opportunity_score: float
    product_traction_score: float
    risk_score: float
    overall_investment_score: float
    investment_recommendation: str
    confidence_level: str
    evaluation_timestamp: str

class StartupEvaluator:
    """AI-powered startup evaluation engine using 5-category metrics framework"""
    
    def __init__(self):
        self.metrics_weights = {
            'financial_health': 0.25,
            'team_quality': 0.20,
            'market_opportunity': 0.20,
            'product_traction': 0.20,
            'risk_assessment': 0.15
        }
        
        # Sector-specific benchmarks
        self.sector_benchmarks = {
            'AI/ML': {
                'avg_arr_growth': 150,
                'avg_team_efficiency': 85,
                'avg_market_size': 1000000000,
                'avg_competition_level': 0.7
            },
            'FinTech': {
                'avg_arr_growth': 120,
                'avg_team_efficiency': 80,
                'avg_market_size': 5000000000,
                'avg_competition_level': 0.8
            },
            'HealthTech': {
                'avg_arr_growth': 100,
                'avg_team_efficiency': 75,
                'avg_market_size': 2000000000,
                'avg_competition_level': 0.6
            },
            'SaaS': {
                'avg_arr_growth': 130,
                'avg_team_efficiency': 90,
                'avg_market_size': 3000000000,
                'avg_competition_level': 0.9
            }
        }
    
    def evaluate_financial_health(self, extracted_data: Dict[str, Any]) -> float:
        """Evaluate financial health based on revenue, growth, and sustainability"""
        score = 0.0
        factors = []
        
        # ARR Analysis (0-30 points)
        arr_crore = extracted_data.get('arr_crore', 0)
        if arr_crore > 0:
            if arr_crore >= 10:  # 10+ crores ARR
                score += 30
                factors.append("Strong ARR: ₹{:.1f} crores".format(arr_crore))
            elif arr_crore >= 5:  # 5-10 crores ARR
                score += 25
                factors.append("Good ARR: ₹{:.1f} crores".format(arr_crore))
            elif arr_crore >= 1:  # 1-5 crores ARR
                score += 20
                factors.append("Moderate ARR: ₹{:.1f} crores".format(arr_crore))
            else:
                score += 10
                factors.append("Early stage ARR: ₹{:.1f} crores".format(arr_crore))
        
        # Revenue Model Analysis (0-25 points)
        revenue_model = extracted_data.get('revenue_model', '').lower()
        if 'saas' in revenue_model or 'subscription' in revenue_model:
            score += 25
            factors.append("Recurring revenue model")
        elif 'marketplace' in revenue_model or 'commission' in revenue_model:
            score += 20
            factors.append("Marketplace/commission model")
        elif 'one-time' in revenue_model or 'license' in revenue_model:
            score += 15
            factors.append("One-time/license model")
        else:
            score += 10
            factors.append("Other revenue model")
        
        # Valuation Analysis (0-25 points)
        valuation = extracted_data.get('valuation_pre_money_crore', 0)
        if valuation > 0:
            if valuation >= 100:  # 100+ crores valuation
                score += 25
                factors.append("High valuation: ₹{:.1f} crores".format(valuation))
            elif valuation >= 50:  # 50-100 crores valuation
                score += 20
                factors.append("Good valuation: ₹{:.1f} crores".format(valuation))
            elif valuation >= 20:  # 20-50 crores valuation
                score += 15
                factors.append("Moderate valuation: ₹{:.1f} crores".format(valuation))
            else:
                score += 10
                factors.append("Early stage valuation: ₹{:.1f} crores".format(valuation))
        
        # Key Metrics Analysis (0-20 points)
        key_metrics = extracted_data.get('key_metrics', {})
        mrr_lakh = key_metrics.get('mrr_lakh', 0)
        churn_rate = key_metrics.get('churn_rate', 0)
        customer_count = key_metrics.get('customer_count', 0)
        
        if mrr_lakh > 0:
            if mrr_lakh >= 50:  # 50+ lakhs MRR
                score += 10
                factors.append("Strong MRR: ₹{:.1f} lakhs".format(mrr_lakh))
            elif mrr_lakh >= 20:  # 20-50 lakhs MRR
                score += 8
                factors.append("Good MRR: ₹{:.1f} lakhs".format(mrr_lakh))
            else:
                score += 5
                factors.append("Early MRR: ₹{:.1f} lakhs".format(mrr_lakh))
        
        if churn_rate > 0:
            if churn_rate <= 5:  # Low churn
                score += 5
                factors.append("Low churn: {:.1f}%".format(churn_rate))
            elif churn_rate <= 10:  # Moderate churn
                score += 3
                factors.append("Moderate churn: {:.1f}%".format(churn_rate))
            else:
                score += 1
                factors.append("High churn: {:.1f}%".format(churn_rate))
        
        if customer_count > 0:
            if customer_count >= 1000:
                score += 5
                factors.append("Large customer base: {:,}".format(customer_count))
            elif customer_count >= 100:
                score += 3
                factors.append("Good customer base: {:,}".format(customer_count))
            else:
                score += 1
                factors.append("Small customer base: {:,}".format(customer_count))
        
        return min(score, 100.0), factors
    
    def evaluate_team_quality(self, extracted_data: Dict[str, Any]) -> float:
        """Evaluate team quality based on founders, team size, and experience"""
        score = 0.0
        factors = []
        
        # Team Size Analysis (0-30 points)
        team_size = extracted_data.get('team_size', 0)
        if team_size > 0:
            if team_size >= 20:  # 20+ team members
                score += 30
                factors.append("Large team: {} members".format(team_size))
            elif team_size >= 10:  # 10-20 team members
                score += 25
                factors.append("Good team size: {} members".format(team_size))
            elif team_size >= 5:  # 5-10 team members
                score += 20
                factors.append("Moderate team: {} members".format(team_size))
            else:
                score += 15
                factors.append("Small team: {} members".format(team_size))
        
        # Founders Analysis (0-40 points)
        founders = extracted_data.get('founders', [])
        if founders:
            founder_count = len(founders)
            if founder_count >= 3:  # 3+ founders
                score += 40
                factors.append("Multiple founders: {} people".format(founder_count))
            elif founder_count == 2:  # 2 founders
                score += 35
                factors.append("Co-founder team: {} people".format(founder_count))
            else:  # 1 founder
                score += 25
                factors.append("Solo founder: {} person".format(founder_count))
        else:
            score += 10
            factors.append("Founder information not available")
        
        # Stage Analysis (0-30 points)
        stage = extracted_data.get('stage', '').lower()
        if 'series a' in stage or 'series b' in stage:
            score += 30
            factors.append("Advanced stage: {}".format(stage))
        elif 'seed' in stage or 'pre-seed' in stage:
            score += 25
            factors.append("Early stage: {}".format(stage))
        elif 'pre-revenue' in stage or 'idea' in stage:
            score += 15
            factors.append("Very early stage: {}".format(stage))
        else:
            score += 20
            factors.append("Stage: {}".format(stage))
        
        return min(score, 100.0), factors
    
    def evaluate_market_opportunity(self, extracted_data: Dict[str, Any]) -> float:
        """Evaluate market opportunity based on sector, market size, and competition"""
        score = 0.0
        factors = []
        
        # Sector Analysis (0-40 points)
        sector = extracted_data.get('sector', '').lower()
        if sector in self.sector_benchmarks:
            benchmark = self.sector_benchmarks[sector]
            score += 40
            factors.append("High-growth sector: {}".format(sector))
        elif any(keyword in sector for keyword in ['tech', 'ai', 'ml', 'saas', 'fintech']):
            score += 35
            factors.append("Tech sector: {}".format(sector))
        elif any(keyword in sector for keyword in ['health', 'education', 'ecommerce']):
            score += 30
            factors.append("Stable sector: {}".format(sector))
        else:
            score += 20
            factors.append("Other sector: {}".format(sector))
        
        # Market Size Analysis (0-30 points)
        # This would typically come from external data sources
        # For now, we'll use sector-based assumptions
        if sector in self.sector_benchmarks:
            market_size = self.sector_benchmarks[sector]['avg_market_size']
            if market_size >= 5000000000:  # 5B+ market
                score += 30
                factors.append("Large market opportunity")
            elif market_size >= 1000000000:  # 1B+ market
                score += 25
                factors.append("Good market opportunity")
            else:
                score += 20
                factors.append("Moderate market opportunity")
        else:
            score += 15
            factors.append("Market size unknown")
        
        # Competition Analysis (0-30 points)
        if sector in self.sector_benchmarks:
            competition_level = self.sector_benchmarks[sector]['avg_competition_level']
            if competition_level <= 0.5:  # Low competition
                score += 30
                factors.append("Low competition market")
            elif competition_level <= 0.7:  # Moderate competition
                score += 25
                factors.append("Moderate competition")
            else:  # High competition
                score += 20
                factors.append("High competition market")
        else:
            score += 20
            factors.append("Competition level unknown")
        
        return min(score, 100.0), factors
    
    def evaluate_product_traction(self, extracted_data: Dict[str, Any]) -> float:
        """Evaluate product traction based on user metrics and growth"""
        score = 0.0
        factors = []
        
        # Customer Growth Analysis (0-40 points)
        key_metrics = extracted_data.get('key_metrics', {})
        customer_count = key_metrics.get('customer_count', 0)
        
        if customer_count > 0:
            if customer_count >= 10000:  # 10K+ customers
                score += 40
                factors.append("High customer traction: {:,}".format(customer_count))
            elif customer_count >= 1000:  # 1K-10K customers
                score += 35
                factors.append("Good customer traction: {:,}".format(customer_count))
            elif customer_count >= 100:  # 100-1K customers
                score += 30
                factors.append("Moderate customer traction: {:,}".format(customer_count))
            else:
                score += 20
                factors.append("Early customer traction: {:,}".format(customer_count))
        else:
            score += 10
            factors.append("Customer data not available")
        
        # Revenue Growth Analysis (0-35 points)
        arr_crore = extracted_data.get('arr_crore', 0)
        if arr_crore > 0:
            if arr_crore >= 5:  # 5+ crores ARR
                score += 35
                factors.append("Strong revenue traction")
            elif arr_crore >= 1:  # 1-5 crores ARR
                score += 30
                factors.append("Good revenue traction")
            else:
                score += 25
                factors.append("Early revenue traction")
        else:
            score += 15
            factors.append("Revenue data not available")
        
        # Product-Market Fit Indicators (0-25 points)
        churn_rate = key_metrics.get('churn_rate', 0)
        if churn_rate > 0:
            if churn_rate <= 5:  # Low churn indicates PMF
                score += 25
                factors.append("Strong product-market fit")
            elif churn_rate <= 10:  # Moderate churn
                score += 20
                factors.append("Good product-market fit")
            else:
                score += 15
                factors.append("Developing product-market fit")
        else:
            score += 15
            factors.append("PMF data not available")
        
        return min(score, 100.0), factors
    
    def evaluate_risk_assessment(self, extracted_data: Dict[str, Any]) -> float:
        """Evaluate risk factors and return risk score (lower is better)"""
        risk_score = 0.0
        risk_factors = []
        
        # Financial Risk (0-30 points)
        arr_crore = extracted_data.get('arr_crore', 0)
        if arr_crore == 0:
            risk_score += 30
            risk_factors.append("No revenue yet")
        elif arr_crore < 1:  # Less than 1 crore ARR
            risk_score += 20
            risk_factors.append("Very low revenue")
        elif arr_crore < 5:  # Less than 5 crores ARR
            risk_score += 10
            risk_factors.append("Low revenue")
        
        # Team Risk (0-25 points)
        team_size = extracted_data.get('team_size', 0)
        if team_size < 3:
            risk_score += 25
            risk_factors.append("Very small team")
        elif team_size < 5:
            risk_score += 15
            risk_factors.append("Small team")
        elif team_size < 10:
            risk_score += 10
            risk_factors.append("Moderate team size")
        
        # Market Risk (0-20 points)
        sector = extracted_data.get('sector', '').lower()
        if not sector or sector == 'unknown':
            risk_score += 20
            risk_factors.append("Unclear market focus")
        elif any(keyword in sector for keyword in ['crypto', 'blockchain', 'nft']):
            risk_score += 15
            risk_factors.append("High-risk sector")
        
        # Stage Risk (0-25 points)
        stage = extracted_data.get('stage', '').lower()
        if 'pre-revenue' in stage or 'idea' in stage:
            risk_score += 25
            risk_factors.append("Very early stage")
        elif 'seed' in stage or 'pre-seed' in stage:
            risk_score += 15
            risk_factors.append("Early stage")
        elif 'series a' in stage or 'series b' in stage:
            risk_score += 5
            risk_factors.append("Proven stage")
        
        return min(risk_score, 100.0), risk_factors
    
    def generate_investment_recommendation(self, overall_score: float, risk_score: float) -> str:
        """Generate investment recommendation based on overall score and risk"""
        if overall_score >= 80 and risk_score <= 20:
            return "Strong Buy"
        elif overall_score >= 70 and risk_score <= 30:
            return "Buy"
        elif overall_score >= 60 and risk_score <= 40:
            return "Hold"
        elif overall_score >= 50:
            return "Weak Hold"
        else:
            return "Sell"
    
    def get_confidence_level(self, extracted_data: Dict[str, Any]) -> str:
        """Determine confidence level based on data completeness"""
        data_points = 0
        total_points = 8
        
        if extracted_data.get('company_name'): data_points += 1
        if extracted_data.get('sector'): data_points += 1
        if extracted_data.get('arr_crore', 0) > 0: data_points += 1
        if extracted_data.get('team_size', 0) > 0: data_points += 1
        if extracted_data.get('stage'): data_points += 1
        if extracted_data.get('valuation_pre_money_crore', 0) > 0: data_points += 1
        if extracted_data.get('revenue_model'): data_points += 1
        if extracted_data.get('founders'): data_points += 1
        
        confidence = data_points / total_points
        
        if confidence >= 0.8:
            return "High"
        elif confidence >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def evaluate_startup(self, extracted_data: Dict[str, Any]) -> EvaluationMetrics:
        """Main evaluation method that combines all metrics"""
        logger.info("Starting comprehensive startup evaluation")
        
        # Evaluate each category
        financial_score, financial_factors = self.evaluate_financial_health(extracted_data)
        team_score, team_factors = self.evaluate_team_quality(extracted_data)
        market_score, market_factors = self.evaluate_market_opportunity(extracted_data)
        traction_score, traction_factors = self.evaluate_product_traction(extracted_data)
        risk_score, risk_factors = self.evaluate_risk_assessment(extracted_data)
        
        # Calculate weighted overall score
        overall_score = (
            financial_score * self.metrics_weights['financial_health'] +
            team_score * self.metrics_weights['team_quality'] +
            market_score * self.metrics_weights['market_opportunity'] +
            traction_score * self.metrics_weights['product_traction'] +
            (100 - risk_score) * self.metrics_weights['risk_assessment']
        )
        
        # Generate recommendation
        recommendation = self.generate_investment_recommendation(overall_score, risk_score)
        confidence = self.get_confidence_level(extracted_data)
        
        logger.info(f"Evaluation complete - Overall Score: {overall_score:.1f}, Risk: {risk_score:.1f}, Recommendation: {recommendation}")
        
        return EvaluationMetrics(
            financial_health_score=financial_score,
            team_quality_score=team_score,
            market_opportunity_score=market_score,
            product_traction_score=traction_score,
            risk_score=risk_score,
            overall_investment_score=overall_score,
            investment_recommendation=recommendation,
            confidence_level=confidence,
            evaluation_timestamp=datetime.now().isoformat()
        )
