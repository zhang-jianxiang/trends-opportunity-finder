"""
Google Trends 数据采集模块
使用 pytrends 从 Google Trends 获取数据并存入 Supabase
"""

import time
import random
from datetime import datetime, date
from typing import List, Dict, Optional
import pandas as pd
from pytrends.request import TrendReq
from loguru import logger

from .config import Config
from .database import Database


class TrendsCollector:
    """Google Trends 数据采集器"""

    def __init__(self):
        self.db = Database()
        self.timeframe = Config.TIMEFRAME

        # 初始化 pytrends 客户端
        self.pytrends = TrendReq(
            hl='en-US',
            tz=360,
            timeout=(10, 25),
            retries=3,
            backoff_factor=0.5
        )

    def collect_all(self, keywords: List[str] = None, regions: List[str] = None) -> Dict:
        """
        采集所有关键词和地区的趋势数据

        Args:
            keywords: 关键词列表，为空则使用配置中的默认值
            regions: 地区列表，为空则使用配置中的默认值

        Returns:
            采集结果统计
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

        logger.info(f"开始采集: {len(keywords)} 个关键词, {len(regions)} 个地区")

        for region in regions:
            region_name = region if region else "Global"
            logger.info(f"--- 采集地区: {region_name} ---")

            # 分批处理关键词（每批最多4个，Google Trends限制）
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
                    logger.info(f"批次完成: {batch} -> {collected} 条记录")

                except Exception as e:
                    stats["errors"] += 1
                    stats["details"].append({
                        "region": region_name,
                        "keywords": batch,
                        "error": str(e),
                        "status": "failed"
                    })
                    logger.error(f"批次失败: {batch} -> {e}")

                # 随机延迟，避免被 Google 封 IP
                delay = random.uniform(2.0, 5.0)
                time.sleep(delay)

        logger.info(f"采集完成: 成功 {stats['records_collected']} 条, 失败 {stats['errors']} 批次")
        return stats

    def _collect_batch(self, keywords: List[str], region: str) -> int:
        """采集一批关键词的数据"""
        # 构建 payload
        self.pytrends.build_payload(
            kw_list=keywords,
            cat=0,
            timeframe=self.timeframe,
            geo=region,
            gprop=''
        )

        records_count = 0

        # 1. 获取兴趣趋势数据
        try:
            interest_df = self.pytrends.interest_over_time()
            records_count += self._save_interest_data(interest_df, keywords, region)
        except Exception as e:
            logger.warning(f"获取兴趣趋势失败: {e}")

        # 2. 获取相关查询
        try:
            related = self.pytrends.related_queries()
            records_count += self._save_related_queries(related, keywords, region)
        except Exception as e:
            logger.warning(f"获取相关查询失败: {e}")

        return records_count

    def _save_interest_data(self, df: pd.DataFrame, keywords: List[str], region: str) -> int:
        """保存兴趣趋势数据到数据库"""
        if df.empty:
            return 0

        count = 0
        region_id = self.db.get_region_id(region)
        if not region_id:
            logger.warning(f"地区 {region} 不在数据库中，跳过")
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
        """保存相关查询数据到数据库"""
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
        采集单个关键词的数据（用于测试或手动添加）

        Args:
            keyword: 关键词
            region: 地区代码

        Returns:
            采集结果
        """
        logger.info(f"采集单个关键词: {keyword} ({region or 'Global'})")
        result = self._collect_batch([keyword], region)
        return {
            "keyword": keyword,
            "region": region or "Global",
            "records": result,
            "status": "success" if result > 0 else "no_data"
        }
