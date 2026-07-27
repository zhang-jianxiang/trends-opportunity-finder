"""
Supabase 数据库操作模块
"""

from datetime import date, datetime
from typing import Optional, List, Dict
from loguru import logger
from supabase import create_client, Client

from .config import Config


class Database:
    """Supabase 数据库操作封装"""

    def __init__(self):
        if not Config.validate():
            raise ValueError("Supabase 配置不完整，请检查环境变量")
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )

    # ================== 关键词操作 ==================

    def get_or_create_keyword(self, keyword: str, category: str = "general") -> int:
        """获取或创建关键词，返回 ID"""
        result = self.client.table("keywords").select("id").eq("keyword", keyword).execute()
        if result.data:
            return result.data[0]["id"]

        insert_result = self.client.table("keywords").insert({
            "keyword": keyword,
            "category": category
        }).execute()
        return insert_result.data[0]["id"]

    def get_keyword_id(self, keyword: str) -> Optional[int]:
        """根据关键词文本获取 ID"""
        result = self.client.table("keywords").select("id").eq("keyword", keyword).execute()
        return result.data[0]["id"] if result.data else None

    def get_all_keywords(self) -> List[Dict]:
        """获取所有活跃关键词"""
        result = self.client.table("keywords").select("*").eq("is_active", True).execute()
        return result.data

    # ================== 地区操作 ==================

    def get_region_id(self, region_code: str) -> Optional[int]:
        """根据地区代码获取 ID"""
        result = self.client.table("regions").select("id").eq("region_code", region_code).execute()
        return result.data[0]["id"] if result.data else None

    def get_all_regions(self) -> List[Dict]:
        """获取所有活跃地区"""
        result = self.client.table("regions").select("*").eq("is_active", True).execute()
        return result.data

    # ================== 趋势数据操作 ==================

    def insert_trends_data(self, keyword_id: int, region_id: int,
                           data_date: str, score: int):
        """插入趋势数据（存在则更新）"""
        self.client.table("trends_data").upsert({
            "keyword_id": keyword_id,
            "region_id": region_id,
            "date": data_date,
            "score": score,
            "collected_at": datetime.utcnow().isoformat()
        }, on_conflict="keyword_id,region_id,date").execute()

    def insert_related_queries(self, keyword_id: int, region_id: int,
                               data_date: str, query_type: str,
                               query_text: str, value: str):
        """插入相关查询数据"""
        self.client.table("related_queries").insert({
            "keyword_id": keyword_id,
            "region_id": region_id,
            "date": data_date,
            "query_type": query_type,
            "query_text": query_text,
            "value": value,
            "collected_at": datetime.utcnow().isoformat()
        }).execute()

    def get_trends_history(self, keyword_id: int, region_id: int,
                           days: int = 90) -> List[Dict]:
        """获取趋势历史数据"""
        from datetime import timedelta
        start_date = (date.today() - timedelta(days=days)).isoformat()
        result = (
            self.client.table("trends_data")
            .select("date, score")
            .eq("keyword_id", keyword_id)
            .eq("region_id", region_id)
            .gte("date", start_date)
            .order("date", desc=False)
            .execute()
        )
        return result.data

    # ================== 分析结果操作 ==================

    def insert_analysis(self, data: Dict):
        """插入分析结果（存在则更新）"""
        self.client.table("trend_analysis").upsert(data,
            on_conflict="keyword_id,region_id,analysis_date").execute()

    def get_recent_analysis(self, days: int = 7) -> List[Dict]:
        """获取最近的分析结果"""
        from datetime import timedelta
        start_date = (date.today() - timedelta(days=days)).isoformat()
        result = (
            self.client.table("trend_analysis")
            .select("*, keywords(keyword), regions(region_code, region_name)")
            .gte("analysis_date", start_date)
            .order("opportunity_score", desc=True)
            .execute()
        )
        return result.data

    # ================== 机会操作 ==================

    def insert_opportunity(self, data: Dict):
        """插入市场机会"""
        self.client.table("opportunities").insert(data).execute()

    def get_active_opportunities(self, limit: int = 50) -> List[Dict]:
        """获取活跃机会列表"""
        result = (
            self.client.table("opportunities")
            .select("*, keywords(keyword, category), regions(region_code, region_name)")
            .eq("status", "active")
            .order("score", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data

    def update_opportunity_status(self, opp_id: int, status: str):
        """更新机会状态"""
        self.client.table("opportunities").update({"status": status}).eq("id", opp_id).execute()

    # ================== 日志操作 ==================

    def insert_log(self, task_name: str, status: str,
                   records: int = 0, duration: int = 0, error: str = None):
        """插入采集日志"""
        self.client.table("collection_logs").insert({
            "task_name": task_name,
            "status": status,
            "records_collected": records,
            "duration_seconds": duration,
            "error_message": error,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
