"""
配置管理模块
从环境变量读取所有配置
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件（从当前目录和上级目录查找）
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))


class Config:
    """全局配置"""

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # 关键词列表
    KEYWORDS: list = [
        k.strip() for k in os.getenv(
            "TRENDS_KEYWORDS",
            "artificial intelligence,machine learning,digital health,"
            "cryptocurrency,sustainable energy,remote work,"
            "electric vehicles,social media,online learning,fitness apps"
        ).split(",") if k.strip()
    ]

    # 地区列表（空字符串表示全球）
    _raw_regions = os.getenv("TRENDS_REGIONS", ",US,CN,GB,DE,JP").split(",")
    REGIONS: list = [r.strip() for r in _raw_regions]

    # 采集时间范围
    TIMEFRAME: str = os.getenv("TRENDS_TIMEFRAME", "today 3-m")

    # 分析参数
    TREND_UP_THRESHOLD: float = float(os.getenv("ANALYSIS_TREND_UP_THRESHOLD", "0.5"))
    TREND_DOWN_THRESHOLD: float = float(os.getenv("ANALYSIS_TREND_DOWN_THRESHOLD", "-0.3"))
    ANOMALY_THRESHOLD: float = float(os.getenv("ANALYSIS_ANOMALY_THRESHOLD", "2.0"))
    OPPORTUNITY_THRESHOLD: float = float(os.getenv("ANALYSIS_OPPORTUNITY_THRESHOLD", "60"))

    @classmethod
    def validate(cls) -> bool:
        """检查必要配置是否完整"""
        if not cls.SUPABASE_URL or not cls.SUPABASE_KEY:
            return False
        return True

    @classmethod
    def summary(cls) -> str:
        """返回配置摘要"""
        return (
            f"关键词数量: {len(cls.KEYWORDS)}\n"
            f"地区数量: {len(cls.REGIONS)}\n"
            f"时间范围: {cls.TIMEFRAME}\n"
            f"Supabase URL: {cls.SUPABASE_URL[:30]}..."
        )
