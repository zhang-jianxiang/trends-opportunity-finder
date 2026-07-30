"""
Google Trends Data Collection Module
Uses pytrends to fetch data from Google Trends and store in database
"""

import time
import random
from datetime import datetime, date
from typing import List, Dict, Optional
import pandas as pd
from loguru import logger

# Fix urllib3 compatibility (pytrends incompatible with urllib3 2.x)
from urllib3.util.retry import Retry
if not hasattr(Retry, 'DEFAULT_METHOD_WHITELIST'):
    Retry.DEFAULT_METHOD_WHITELIST = Retry.DEFAULT_ALLOWED_METHODS

from pytrends.request import TrendReq

from .config import Config
from .database import Database


class TrendsCollector:
    """Google Trends data collector"""

    def __init__(self):
        self.db = Database()
        self.timeframe = Config.TIMEFRAME

        # Initialize pytrends client
        self.pytrends = TrendReq(
            hl='en-US',
            tz=360,
            timeout=(10, 25),
            retries=3,
            backoff_factor=0.5
        )

    def collect_all(self, keywords: List[str] = None, regions: List[str] = None) -> Dict:
        """
        Collect trend data for all keywords and regions.

        Args:
            keywords: keyword list, uses config default if None
            regions: region list, uses config default if None

        Returns:
            Collection result statistics
        """
        if keywords is None:
            keywords = Config.KEYWORDS
        if regions is None:
            regions = Config.REGIONS

        stats = {
            "total_keywords": len(keywords),
            "total_regions": len(regions),
            "records_collected": 0,
            "errors": 0,
            "details": []
        }

        logger.info(f"Start collecting: {len(keywords)} keywords, {len(regions)} regions")

        for region in regions:
            region_name = region if region else "Global"
            logger.info(f"--- Collecting region: {region_name} ---")

            # Process keywords in batches (max 4 per batch, Google Trends limit)
            batch_size = 4
            for i in range(0, len(keywords), batch_size):
                batch = keywords[i:i + batch_size]

                try:
                    collected = self._collect_batch(batch, region)
                    stats["records_collected"] += collected
                    stats["details"].append({
                        "region": region_name,
                        "keywords": batch,
                        "collected": collected,
                        "status": "success"
                    })
                    logger.info(f"Batch done: {batch} -> {collected} records")

                except Exception as e:
                    stats["errors"] += 1
                    stats["details"].append({
                        "region": region_name,
                        "keywords": batch,
                        "error": str(e),
                        "status": "failed"
                    })
                    logger.error(f"Batch failed: {batch} -> {e}")

                # Random delay to avoid IP ban
                delay = random.uniform(2.0, 5.0)
                time.sleep(delay)

        logger.info(f"Collection complete: {stats['records_collected']} records, {stats['errors']} failed batches")
        return stats

    def _collect_batch(self, keywords: List[str], region: str) -> int:
        """Collect data for a batch of keywords"""
        # Build payload
        self.pytrends.build_payload(
            kw_list=keywords,
            cat=0,
            timeframe=self.timeframe,
            geo=region,
            gprop=''
        )

        records_count = 0

        # 1. Get interest over time data
        try:
            interest_df = self.pytrends.interest_over_time()
            records_count += self._save_interest_data(interest_df, keywords, region)
        except Exception as e:
            logger.warning(f"Failed to get interest over time: {e}")

        # 2. Get related queries
        try:
            related = self.pytrends.related_queries()
            records_count += self._save_related_queries(related, keywords, region)
        except Exception as e:
            logger.warning(f"Failed to get related queries: {e}")

        return records_count

    def _save_interest_data(self, df: pd.DataFrame, keywords: List[str], region: str) -> int:
        """Save interest over time data to database"""
        if df.empty:
            return 0

        count = 0
        region_id = self.db.get_region_id(region)
        if not region_id:
            logger.warning(f"Region {region} not found in database, skipping")
            return 0

        for keyword in keywords:
            if keyword not in df.columns:
                continue

            keyword_id = self.db.get_or_create_keyword(keyword)

            for idx, value in df[keyword].items():
                if pd.isna(value):
                    continue

                data_date = idx.date() if hasattr(idx, 'date') else str(idx)[:10]
                score = int(value)

                self.db.insert_trends_data(
                    keyword_id=keyword_id,
                    region_id=region_id,
                    data_date=str(data_date),
                    score=score
                )
                count += 1

        return count

    def _save_related_queries(self, related: Dict, keywords: List[str], region: str) -> int:
        """Save related queries data to database"""
        count = 0
        region_id = self.db.get_region_id(region)
        if not region_id:
            return 0

        today = date.today().isoformat()

        for keyword in keywords:
            if keyword not in related:
                continue

            keyword_id = self.db.get_keyword_id(keyword)
            if not keyword_id:
                continue

            for query_type in ['top', 'rising']:
                df = related[keyword].get(query_type)
                if df is None or df.empty:
                    continue

                for _, row in df.iterrows():
                    query_text = str(row.get('query', ''))
                    value = str(row.get('value', '0'))

                    if query_text:
                        self.db.insert_related_queries(
                            keyword_id=keyword_id,
                            region_id=region_id,
                            data_date=today,
                            query_type=query_type,
                            query_text=query_text,
                            value=value
                        )
                        count += 1

        return count

    def collect_single_keyword(self, keyword: str, region: str = "") -> Dict:
        """
        Collect data for a single keyword (for testing or manual addition).

        Args:
            keyword: keyword string
            region: region code

        Returns:
            Collection result
        """
        logger.info(f"Collecting single keyword: {keyword} ({region or 'Global'})")
        result = self._collect_batch([keyword], region)
        return {
            "keyword": keyword,
            "region": region or "Global",
            "records": result,
            "status": "success" if result > 0 else "no_data"
        }
