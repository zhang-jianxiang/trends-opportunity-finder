#!/usr/bin/env python3
"""
Google Trends Daily Collection and Analysis
Entry point for GitHub Actions scheduled workflow

Flow:
  1. Data Collection - Fetch keyword trends from Google Trends
  2. Trend Analysis - Calculate trend metrics and opportunity scores
  3. Opportunity Detection - Identify and record market opportunities
"""

import sys
import os
import time
from datetime import datetime

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.database import Database
from src.collector import TrendsCollector
from src.analyzer import TrendAnalyzer
from src.opportunity import OpportunityDetector

from loguru import logger

# Ensure logs directory exists
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs"), exist_ok=True)

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
    level="INFO"
)
logger.add(
    "logs/daily_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="DEBUG",
    rotation="1 day",
    retention="30 days"
)


def safe_log(db, **kwargs):
    """Safely insert a log entry, ignoring database errors"""
    try:
        db.insert_log(**kwargs)
    except Exception as e:
        logger.warning(f"Failed to insert log entry: {e}")


def main():
    """Main execution function"""
    start_time = time.time()
    today = datetime.now().strftime("%Y-%m-%d")

    logger.info("=" * 60)
    logger.info(f"Google Trends Daily Task Started - {today}")
    logger.info("=" * 60)

    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed! Check DATABASE_URL environment variable.")
        logger.info(f"Current config:\n{Config.summary()}")
        sys.exit(0)

    logger.info(f"Config summary:\n{Config.summary()}")
    logger.info("-" * 60)

    db = Database()
    total_records = 0

    # Step 1: Data Collection
    logger.info(">>> Step 1/3: Data Collection")
    collect_start = time.time()

    try:
        collector = TrendsCollector()
        collect_result = collector.collect_all()
        total_records = collect_result["records_collected"]
        collect_duration = int(time.time() - collect_start)

        logger.info(f"Collection done: {total_records} records, {collect_duration}s, {collect_result['errors']} errors")

        safe_log(db,
            task_name="data_collection",
            status="success" if collect_result["errors"] == 0 else "partial",
            records=total_records,
            duration=collect_duration,
        )

    except Exception as e:
        collect_duration = int(time.time() - collect_start)
        logger.error(f"Data collection failed: {e}")
        safe_log(db,
            task_name="data_collection",
            status="failed",
            duration=collect_duration,
            error=str(e)
        )

    logger.info("-" * 60)

    # Step 2: Trend Analysis
    logger.info(">>> Step 2/3: Trend Analysis")
    analyze_start = time.time()

    try:
        analyzer = TrendAnalyzer()
        analysis_results = analyzer.analyze_all()
        analyze_duration = int(time.time() - analyze_start)

        logger.info(f"Analysis done: {len(analysis_results)} results, {analyze_duration}s")

        safe_log(db,
            task_name="trend_analysis",
            status="success",
            records=len(analysis_results),
            duration=analyze_duration,
        )

    except Exception as e:
        analyze_duration = int(time.time() - analyze_start)
        logger.error(f"Trend analysis failed: {e}")
        safe_log(db,
            task_name="trend_analysis",
            status="failed",
            duration=analyze_duration,
            error=str(e)
        )

    logger.info("-" * 60)

    # Step 3: Opportunity Detection
    logger.info(">>> Step 3/3: Opportunity Detection")
    opp_start = time.time()

    try:
        detector = OpportunityDetector()
        opportunities = detector.detect_all()
        opp_duration = int(time.time() - opp_start)

        logger.info(f"Opportunity detection done: {len(opportunities)} new opportunities, {opp_duration}s")

        if opportunities:
            logger.info("Opportunities:")
            for i, opp in enumerate(opportunities, 1):
                logger.info(f"  {i}. [{opp['opportunity_type']}] {opp['title']} (score: {opp['score']})")

        safe_log(db,
            task_name="opportunity_detection",
            status="success",
            records=len(opportunities),
            duration=opp_duration,
        )

    except Exception as e:
        opp_duration = int(time.time() - opp_start)
        logger.error(f"Opportunity detection failed: {e}")
        safe_log(db,
            task_name="opportunity_detection",
            status="failed",
            duration=opp_duration,
            error=str(e)
        )

    # Summary
    total_duration = int(time.time() - start_time)

    logger.info("=" * 60)
    logger.info(f"Daily task complete - Total time: {total_duration}s | Records: {total_records}")
    logger.info("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    main()
