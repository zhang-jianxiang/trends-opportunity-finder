"""
Neon PostgreSQL 数据库操作模块
使用 psycopg2 直连 Neon，不依赖任何特定平台 SDK
"""

import psycopg2
import psycopg2.extras
from datetime import date, datetime
from typing import Optional, List, Dict
from loguru import logger

from .config import Config


class Database:
    """Neon PostgreSQL 数据库操作封装"""

    def __init__(self):
        if not Config.validate():
            raise ValueError("DATABASE_URL 未配置，请检查环境变量")
        self.conn = psycopg2.connect(Config.DATABASE_URL)
        self.conn.autocommit = True

    def _execute(self, query: str, params: tuple = None, fetch: str = None):
        """执行 SQL 查询的通用方法"""
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch == "all":
                    return cur.fetchall()
                elif fetch == "one":
                    return cur.fetchone()
                return None
        except Exception as e:
            logger.error(f"SQL error: {e}")
            raise

    def close(self):
        """关闭连接"""
        if self.conn and not self.conn.closed:
            self.conn.close()

    # ================== 关键词操作 ==================

    def get_or_create_keyword(self, keyword: str, category: str = "general") -> int:
        """获取或创建关键词，返回 ID"""
        result = self._execute(
            "SELECT id FROM keywords WHERE keyword = %s", (keyword,), "one"
        )
        if result:
            return result["id"]
        result = self._execute(
            "INSERT INTO keywords (keyword, category) VALUES (%s, %s) RETURNING id",
            (keyword, category), "one"
        )
        return result["id"]

    def get_keyword_id(self, keyword: str) -> Optional[int]:
        """根据关键词文本获取 ID"""
        result = self._execute(
            "SELECT id FROM keywords WHERE keyword = %s", (keyword,), "one"
        )
        return result["id"] if result else None

    def get_all_keywords(self) -> List[Dict]:
        """获取所有活跃关键词"""
        return self._execute(
            "SELECT * FROM keywords WHERE is_active = true", fetch="all"
        )

    # ================== 地区操作 ==================

    def get_region_id(self, region_code: str) -> Optional[int]:
        """根据地区代码获取 ID"""
        result = self._execute(
            "SELECT id FROM regions WHERE region_code = %s", (region_code,), "one"
        )
        return result["id"] if result else None

    def get_all_regions(self) -> List[Dict]:
        """获取所有活跃地区"""
        return self._execute(
            "SELECT * FROM regions WHERE is_active = true", fetch="all"
        )

    # ================== 趋势数据操作 ==================

    def insert_trends_data(self, keyword_id: int, region_id: int,
                           data_date: str, score: int):
        """插入趋势数据（存在则更新）"""
        self._execute(
            """INSERT INTO trends_data (keyword_id, region_id, date, score, collected_at)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (keyword_id, region_id, date)
               DO UPDATE SET score = EXCLUDED.score, collected_at = EXCLUDED.collected_at""",
            (keyword_id, region_id, data_date, score, datetime.utcnow())
        )

    def insert_related_queries(self, keyword_id: int, region_id: int,
                               data_date: str, query_type: str,
                               query_text: str, value: str):
        """插入相关查询数据"""
        self._execute(
            """INSERT INTO related_queries (keyword_id, region_id, date, query_type, query_text, value, collected_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (keyword_id, region_id, data_date, query_type, query_text, value, datetime.utcnow())
        )

    def get_trends_history(self, keyword_id: int, region_id: int,
                           days: int = 90) -> List[Dict]:
        """获取趋势历史数据"""
        from datetime import timedelta
        start_date = (date.today() - timedelta(days=days)).isoformat()
        return self._execute(
            """SELECT date, score FROM trends_data
               WHERE keyword_id = %s AND region_id = %s AND date >= %s
               ORDER BY date ASC""",
            (keyword_id, region_id, start_date), "all"
        )

    # ================== 分析结果操作 ==================

    def insert_analysis(self, data: Dict):
        """插入分析结果（存在则更新）"""
        self._execute(
            """INSERT INTO trend_analysis
               (keyword_id, region_id, analysis_date, current_score, avg_score_7d,
                avg_score_30d, score_change_pct, trend_direction, trend_strength,
                volatility, opportunity_score, market_potential, is_anomaly,
                anomaly_score, recommendation)
               VALUES (%(keyword_id)s, %(region_id)s, %(analysis_date)s, %(current_score)s,
                %(avg_score_7d)s, %(avg_score_30d)s, %(score_change_pct)s, %(trend_direction)s,
                %(trend_strength)s, %(volatility)s, %(opportunity_score)s, %(market_potential)s,
                %(is_anomaly)s, %(anomaly_score)s, %(recommendation)s)
               ON CONFLICT (keyword_id, region_id, analysis_date)
               DO UPDATE SET current_score = EXCLUDED.current_score,
                avg_score_7d = EXCLUDED.avg_score_7d, avg_score_30d = EXCLUDED.avg_score_30d,
                score_change_pct = EXCLUDED.score_change_pct, trend_direction = EXCLUDED.trend_direction,
                trend_strength = EXCLUDED.trend_strength, volatility = EXCLUDED.volatility,
                opportunity_score = EXCLUDED.opportunity_score, market_potential = EXCLUDED.market_potential,
                is_anomaly = EXCLUDED.is_anomaly, anomaly_score = EXCLUDED.anomaly_score,
                recommendation = EXCLUDED.recommendation""",
            data
        )

    def get_recent_analysis(self, days: int = 7) -> List[Dict]:
        """获取最近的分析结果（含关键词和地区信息）"""
        from datetime import timedelta
        start_date = (date.today() - timedelta(days=days)).isoformat()
        return self._execute(
            """SELECT ta.*, k.keyword, k.category, r.region_code, r.region_name
               FROM trend_analysis ta
               JOIN keywords k ON ta.keyword_id = k.id
               JOIN regions r ON ta.region_id = r.id
               WHERE ta.analysis_date >= %s
               ORDER BY ta.opportunity_score DESC""",
            (start_date,), "all"
        )

    # ================== 机会操作 ==================

    def insert_opportunity(self, data: Dict):
        """插入市场机会"""
        self._execute(
            """INSERT INTO opportunities
               (keyword_id, region_id, opportunity_type, title, description, score,
                market_size, competition_level, trend_direction, detected_date, status)
               VALUES (%(keyword_id)s, %(region_id)s, %(opportunity_type)s, %(title)s,
                %(description)s, %(score)s, %(market_size)s, %(competition_level)s,
                %(trend_direction)s, %(detected_date)s, %(status)s)""",
            data
        )

    def get_active_opportunities(self, limit: int = 50) -> List[Dict]:
        """获取活跃机会列表"""
        return self._execute(
            """SELECT o.*, k.keyword, k.category, r.region_code, r.region_name
               FROM opportunities o
               JOIN keywords k ON o.keyword_id = k.id
               JOIN regions r ON o.region_id = r.id
               WHERE o.status = 'active'
               ORDER BY o.score DESC LIMIT %s""",
            (limit,), "all"
        )

    def update_opportunity_status(self, opp_id: int, status: str):
        """更新机会状态"""
        self._execute(
            "UPDATE opportunities SET status = %s WHERE id = %s",
            (status, opp_id)
        )

    # ================== 日志操作 ==================

    def insert_log(self, task_name: str, status: str,
                   records: int = 0, duration: int = 0, error: str = None):
        """插入采集日志"""
        self._execute(
            """INSERT INTO collection_logs
               (task_name, status, records_collected, duration_seconds, error_message, created_at)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (task_name, status, records, duration, error, datetime.utcnow())
        )

    # ================== 统计查询 ==================

    def get_keyword_count(self) -> int:
        return self._execute(
            "SELECT COUNT(*) as cnt FROM keywords WHERE is_active = true", fetch="one"
        )["cnt"]

    def get_data_count(self) -> int:
        return self._execute(
            "SELECT COUNT(*) as cnt FROM trends_data", fetch="one"
        )["cnt"]

    def get_anomaly_count(self) -> int:
        return self._execute(
            "SELECT COUNT(*) as cnt FROM trend_analysis WHERE is_anomaly = true", fetch="one"
        )["cnt"]

    def get_recent_logs(self, limit: int = 3) -> List[Dict]:
        return self._execute(
            "SELECT * FROM collection_logs ORDER BY created_at DESC LIMIT %s",
            (limit,), "all"
        )
