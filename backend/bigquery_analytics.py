"""
BigQuery Analytics Service for Peer Comparison
Provides sector benchmarking and startup analytics using BigQuery
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from google.cloud import bigquery
from google.cloud.exceptions import NotFound, GoogleCloudError
import logging

logger = logging.getLogger(__name__)

class BigQueryAnalyticsService:
    """Service for startup analytics and peer comparison using BigQuery"""
    
    def __init__(self, project_id: str, dataset_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.dataset_ref = self.client.dataset(dataset_id)
        
        # Initialize tables
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary BigQuery tables if they don't exist"""
        try:
            # Create dataset if it doesn't exist
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = "US"  # or your preferred location
            dataset.description = "Startup evaluation analytics dataset"
            
            try:
                self.client.create_dataset(dataset, timeout=30)
                logger.info(f"Created dataset {self.dataset_id}")
            except GoogleCloudError:
                logger.info(f"Dataset {self.dataset_id} already exists")
            
            # Create startups table
            self._create_startups_table()
            
            # Create evaluations table
            self._create_evaluations_table()
            
            # Create sector_benchmarks table
            self._create_sector_benchmarks_table()
            
        except Exception as e:
            logger.error(f"Error creating BigQuery tables: {e}")
    
    def _create_startups_table(self):
        """Create startups table schema"""
        table_id = f"{self.project_id}.{self.dataset_id}.startups"
        
        schema = [
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("company_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sector", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("stage", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("arr_crore", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("team_size", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("valuation_crore", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("revenue_model", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("founders", "STRING", mode="REPEATED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED")
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        table.description = "Startup company information"
        
        try:
            self.client.create_table(table)
            logger.info(f"Created table {table_id}")
        except GoogleCloudError:
            logger.info(f"Table {table_id} already exists")
    
    def _create_evaluations_table(self):
        """Create evaluations table schema"""
        table_id = f"{self.project_id}.{self.dataset_id}.evaluations"
        
        schema = [
            bigquery.SchemaField("evaluation_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("financial_health_score", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("team_quality_score", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("market_opportunity_score", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("product_traction_score", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("risk_score", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("overall_score", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("investment_recommendation", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("confidence_level", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("evaluated_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("evaluation_data", "JSON", mode="NULLABLE")
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        table.description = "Startup evaluation results"
        
        try:
            self.client.create_table(table)
            logger.info(f"Created table {table_id}")
        except GoogleCloudError:
            logger.info(f"Table {table_id} already exists")
    
    def _create_sector_benchmarks_table(self):
        """Create sector benchmarks table schema"""
        table_id = f"{self.project_id}.{self.dataset_id}.sector_benchmarks"
        
        schema = [
            bigquery.SchemaField("sector", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("metric_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("percentile_25", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("percentile_50", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("percentile_75", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("percentile_90", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("average", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED")
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        table.description = "Sector benchmarking data"
        
        try:
            self.client.create_table(table)
            logger.info(f"Created table {table_id}")
        except GoogleCloudError:
            logger.info(f"Table {table_id} already exists")
    
    def insert_startup_data(self, startup_data: Dict[str, Any]) -> bool:
        """Insert startup data into BigQuery"""
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.startups"
            table = self.client.get_table(table_id)
            
            # Prepare row data
            row = {
                "startup_id": startup_data.get("startup_id", ""),
                "company_name": startup_data.get("company_name", ""),
                "sector": startup_data.get("sector", ""),
                "stage": startup_data.get("stage", ""),
                "arr_crore": startup_data.get("arr_crore"),
                "team_size": startup_data.get("team_size"),
                "valuation_crore": startup_data.get("valuation_crore"),
                "revenue_model": startup_data.get("revenue_model"),
                "founders": startup_data.get("founders", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            errors = self.client.insert_rows_json(table, [row])
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                return False
            
            logger.info(f"Startup data inserted: {startup_data.get('startup_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting startup data: {e}")
            return False
    
    def insert_evaluation_data(self, evaluation_data: Dict[str, Any]) -> bool:
        """Insert evaluation data into BigQuery"""
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.evaluations"
            table = self.client.get_table(table_id)
            
            # Prepare row data
            row = {
                "evaluation_id": evaluation_data.get("evaluation_id", ""),
                "startup_id": evaluation_data.get("startup_id", ""),
                "financial_health_score": evaluation_data.get("financial_health_score", 0.0),
                "team_quality_score": evaluation_data.get("team_quality_score", 0.0),
                "market_opportunity_score": evaluation_data.get("market_opportunity_score", 0.0),
                "product_traction_score": evaluation_data.get("product_traction_score", 0.0),
                "risk_score": evaluation_data.get("risk_score", 0.0),
                "overall_score": evaluation_data.get("overall_score", 0.0),
                "investment_recommendation": evaluation_data.get("investment_recommendation", ""),
                "confidence_level": evaluation_data.get("confidence_level", ""),
                "evaluated_at": datetime.utcnow(),
                "evaluation_data": json.dumps(evaluation_data.get("evaluation_data", {}))
            }
            
            errors = self.client.insert_rows_json(table, [row])
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                return False
            
            logger.info(f"Evaluation data inserted: {evaluation_data.get('evaluation_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting evaluation data: {e}")
            return False
    
    def get_sector_benchmarks(self, sector: str) -> Dict[str, Any]:
        """Get sector benchmarking data"""
        try:
            query = f"""
            SELECT 
                metric_name,
                percentile_25,
                percentile_50,
                percentile_75,
                percentile_90,
                average
            FROM `{self.project_id}.{self.dataset_id}.sector_benchmarks`
            WHERE sector = @sector
            ORDER BY metric_name
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("sector", "STRING", sector)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            benchmarks = {}
            for row in results:
                benchmarks[row.metric_name] = {
                    "p25": row.percentile_25,
                    "p50": row.percentile_50,
                    "p75": row.percentile_75,
                    "p90": row.percentile_90,
                    "average": row.average
                }
            
            return benchmarks
            
        except Exception as e:
            logger.error(f"Error getting sector benchmarks: {e}")
            return {}
    
    def get_peer_comparison(self, startup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get peer comparison analysis"""
        try:
            sector = startup_data.get("sector", "")
            arr_crore = startup_data.get("arr_crore", 0)
            team_size = startup_data.get("team_size", 0)
            
            query = f"""
            WITH sector_data AS (
                SELECT 
                    arr_crore,
                    team_size,
                    financial_health_score,
                    team_quality_score,
                    market_opportunity_score,
                    product_traction_score,
                    overall_score
                FROM `{self.project_id}.{self.dataset_id}.evaluations` e
                JOIN `{self.project_id}.{self.dataset_id}.startups` s
                ON e.startup_id = s.startup_id
                WHERE s.sector = @sector
                AND e.evaluated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 12 MONTH)
            )
            SELECT 
                COUNT(*) as total_companies,
                AVG(arr_crore) as avg_arr,
                PERCENTILE_CONT(arr_crore, 0.5) OVER() as median_arr,
                PERCENTILE_CONT(arr_crore, 0.75) OVER() as p75_arr,
                PERCENTILE_CONT(arr_crore, 0.9) OVER() as p90_arr,
                AVG(team_size) as avg_team_size,
                AVG(financial_health_score) as avg_financial_score,
                AVG(team_quality_score) as avg_team_score,
                AVG(market_opportunity_score) as avg_market_score,
                AVG(product_traction_score) as avg_traction_score,
                AVG(overall_score) as avg_overall_score
            FROM sector_data
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("sector", "STRING", sector)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                return self._get_default_peer_comparison()
            
            row = results[0]
            
            # Calculate percentiles for current startup
            arr_percentile = self._calculate_percentile(arr_crore, row.avg_arr, row.p75_arr, row.p90_arr)
            team_efficiency = (arr_crore / team_size) if team_size > 0 else 0
            
            return {
                "sector": sector,
                "total_companies": row.total_companies,
                "arr_percentile": arr_percentile,
                "performance_tier": self._get_performance_tier(arr_percentile),
                "team_efficiency": team_efficiency,
                "sector_average_arr": row.avg_arr,
                "sector_median_arr": row.median_arr,
                "sector_p75_arr": row.p75_arr,
                "sector_p90_arr": row.p90_arr,
                "sector_average_team_size": row.avg_team_size,
                "sector_average_scores": {
                    "financial_health": row.avg_financial_score,
                    "team_quality": row.avg_team_score,
                    "market_opportunity": row.avg_market_score,
                    "product_traction": row.avg_traction_score,
                    "overall": row.avg_overall_score
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting peer comparison: {e}")
            return self._get_default_peer_comparison()
    
    def _calculate_percentile(self, value: float, avg: float, p75: float, p90: float) -> float:
        """Calculate percentile for a value based on sector data"""
        if value <= avg:
            return 50.0
        elif value <= p75:
            return 75.0
        elif value <= p90:
            return 90.0
        else:
            return 95.0
    
    def _get_performance_tier(self, percentile: float) -> str:
        """Get performance tier based on percentile"""
        if percentile >= 90:
            return "Top 10%"
        elif percentile >= 75:
            return "Top 25%"
        elif percentile >= 50:
            return "Above Average"
        else:
            return "Below Average"
    
    def _get_default_peer_comparison(self) -> Dict[str, Any]:
        """Get default peer comparison when no data available"""
        return {
            "sector": "Unknown",
            "total_companies": 0,
            "arr_percentile": 50,
            "performance_tier": "Average",
            "team_efficiency": 0,
            "sector_average_arr": 0,
            "sector_median_arr": 0,
            "sector_p75_arr": 0,
            "sector_p90_arr": 0,
            "sector_average_team_size": 0,
            "sector_average_scores": {
                "financial_health": 50,
                "team_quality": 50,
                "market_opportunity": 50,
                "product_traction": 50,
                "overall": 50
            }
        }
    
    def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """Get analytics data for dashboard"""
        try:
            query = f"""
            SELECT 
                s.sector,
                COUNT(*) as total_startups,
                AVG(e.overall_score) as avg_score,
                AVG(e.financial_health_score) as avg_financial,
                AVG(e.team_quality_score) as avg_team,
                AVG(e.market_opportunity_score) as avg_market,
                AVG(e.product_traction_score) as avg_traction,
                AVG(e.risk_score) as avg_risk,
                COUNT(CASE WHEN e.investment_recommendation = 'Strong Buy' THEN 1 END) as strong_buy_count,
                COUNT(CASE WHEN e.investment_recommendation = 'Buy' THEN 1 END) as buy_count,
                COUNT(CASE WHEN e.investment_recommendation = 'Hold' THEN 1 END) as hold_count,
                COUNT(CASE WHEN e.investment_recommendation = 'Sell' THEN 1 END) as sell_count
            FROM `{self.project_id}.{self.dataset_id}.evaluations` e
            JOIN `{self.project_id}.{self.dataset_id}.startups` s
            ON e.startup_id = s.startup_id
            WHERE e.evaluated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 6 MONTH)
            GROUP BY s.sector
            ORDER BY total_startups DESC
            """
            
            query_job = self.client.query(query)
            results = list(query_job.result())
            
            dashboard_data = {
                "sector_analysis": [],
                "total_evaluations": sum(row.total_startups for row in results),
                "average_scores": {
                    "overall": sum(row.avg_score for row in results) / len(results) if results else 0,
                    "financial": sum(row.avg_financial for row in results) / len(results) if results else 0,
                    "team": sum(row.avg_team for row in results) / len(results) if results else 0,
                    "market": sum(row.avg_market for row in results) / len(results) if results else 0,
                    "traction": sum(row.avg_traction for row in results) / len(results) if results else 0,
                    "risk": sum(row.avg_risk for row in results) / len(results) if results else 0
                },
                "recommendation_distribution": {
                    "strong_buy": sum(row.strong_buy_count for row in results),
                    "buy": sum(row.buy_count for row in results),
                    "hold": sum(row.hold_count for row in results),
                    "sell": sum(row.sell_count for row in results)
                }
            }
            
            for row in results:
                dashboard_data["sector_analysis"].append({
                    "sector": row.sector,
                    "total_startups": row.total_startups,
                    "avg_score": row.avg_score,
                    "avg_financial": row.avg_financial,
                    "avg_team": row.avg_team,
                    "avg_market": row.avg_market,
                    "avg_traction": row.avg_traction,
                    "avg_risk": row.avg_risk,
                    "strong_buy_count": row.strong_buy_count,
                    "buy_count": row.buy_count,
                    "hold_count": row.hold_count,
                    "sell_count": row.sell_count
                })
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting analytics dashboard data: {e}")
            return {}
    
    def seed_sample_data(self):
        """Seed sample data for testing"""
        try:
            # Sample sector benchmarks
            benchmarks_data = [
                {
                    "sector": "AI/ML",
                    "metric_name": "arr_crore",
                    "percentile_25": 0.5,
                    "percentile_50": 1.2,
                    "percentile_75": 2.8,
                    "percentile_90": 5.5,
                    "average": 2.1,
                    "updated_at": datetime.utcnow()
                },
                {
                    "sector": "AI/ML",
                    "metric_name": "team_size",
                    "percentile_25": 5,
                    "percentile_50": 12,
                    "percentile_75": 25,
                    "percentile_90": 45,
                    "average": 18,
                    "updated_at": datetime.utcnow()
                }
            ]
            
            table_id = f"{self.project_id}.{self.dataset_id}.sector_benchmarks"
            table = self.client.get_table(table_id)
            
            errors = self.client.insert_rows_json(table, benchmarks_data)
            if errors:
                logger.error(f"Error seeding sample data: {errors}")
            else:
                logger.info("Sample data seeded successfully")
                
        except Exception as e:
            logger.error(f"Error seeding sample data: {e}")

# Global instance
def get_analytics_service() -> BigQueryAnalyticsService:
    """Get BigQuery analytics service instance"""
    project_id = os.getenv("PROJECT_ID", "startup-ai-evaluator")
    dataset_id = os.getenv("DATASET_ID", "startup_evaluation")
    
    return BigQueryAnalyticsService(project_id, dataset_id)
