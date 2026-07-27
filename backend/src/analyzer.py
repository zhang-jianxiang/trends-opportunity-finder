"""
趋势分析模块
分析 Google Trends 数据，计算趋势指标和市场机会评分
"""

import numpy as np
from scipy import stats
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
from loguru import logger

from .config import Config
from .database import Database


class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self):
        self.db = Database()

    def analyze_all(self) -> List[Dict]:
        """
        分析所有关键词-地区组合的趋势

        Returns:
            分析结果列表
        """
        keywords = self.db.get_all_keywords()
        regions = self.db.get_all_regions()

        results = []
        today = date.today().isoformat()

        logger.info(f"开始分析: {len(keywords)} 关键词 x {len(regions)} 地区")

        for kw in keywords:
            for reg in regions:
                try:
                    # 获取历史数据
                    history = self.db.get_trends_history(
                        kw["id"], reg["id"], days=90
                    )

                    if len(history) < 7:
                        logger.debug(f"数据不足: {kw['keyword']} / {reg['region_code']} ({len(history)} 条)")
                        continue

                    # 执行分析
                    analysis = self._analyze_trend(
                        history, kw["id"], reg["id"], today
                    )

                    if analysis:
                        self.db.insert_analysis(analysis)
                        results.append(analysis)

                except Exception as e:
                    logger.error(f"分析失败 {kw['keyword']}/{reg['region_code']}: {e}")

        logger.info(f"分析完成: {len(results)} 条结果")
        return results

    def _analyze_trend(self, history: List[Dict], keyword_id: int,
                       region_id: int, analysis_date: str) -> Optional[Dict]:
        """分析单个关键词-地区组合"""

        scores = [h["score"] for h in history]

        if len(scores) < 2:
            return None

        # 基础指标
        current_score = scores[-1]
        avg_7d = np.mean(scores[-7:]) if len(scores) >= 7 else np.mean(scores)
        avg_30d = np.mean(scores[-30:]) if len(scores) >= 30 else np.mean(scores)

        # 变化率
        if scores[-2] > 0:
            change_pct = ((scores[-1] - scores[-2]) / scores[-2]) * 100
        else:
            change_pct = 0.0

        # 趋势方向和强度（线性回归）
        trend_dir, trend_str = self._calc_trend_direction(scores)

        # 波动性
        volatility = self._calc_volatility(scores[-30:])

        # 异常检测
        is_anomaly, anomaly_score = self._detect_anomaly(scores)

        # 机会评分
        opp_score = self._calc_opportunity_score(
            current_score, avg_7d, change_pct, trend_dir, trend_str, volatility
        )

        # 市场潜力分类
        market_potential = self._categorize_potential(opp_score)

        # 推荐建议
        recommendation = self._generate_recommendation(
            opp_score, trend_dir, is_anomaly, change_pct
        )

        return {
            "keyword_id": keyword_id,
            "region_id": region_id,
            "analysis_date": analysis_date,
            "current_score": int(current_score),
            "avg_score_7d": round(float(avg_7d), 2),
            "avg_score_30d": round(float(avg_30d), 2),
            "score_change_pct": round(float(change_pct), 2),
            "trend_direction": trend_dir,
            "trend_strength": round(float(trend_str), 2),
            "volatility": round(float(volatility), 4),
            "opportunity_score": round(float(opp_score), 2),
            "market_potential": market_potential,
            "is_anomaly": is_anomaly,
            "anomaly_score": round(float(anomaly_score), 4),
            "recommendation": recommendation,
        }

    def _calc_trend_direction(self, scores: List[float]) -> Tuple[str, float]:
        """使用线性回归计算趋势方向和强度"""
        x = np.arange(len(scores))
        y = np.array(scores)

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        if slope > Config.TREND_UP_THRESHOLD:
            direction = "up"
        elif slope < Config.TREND_DOWN_THRESHOLD:
            direction = "down"
        else:
            direction = "stable"

        # R² 作为趋势强度 (0-100)
        strength = abs(r_value ** 2) * 100
        strength = min(100, max(0, strength))

        return direction, strength

    def _calc_volatility(self, scores: List[float]) -> float:
        """计算波动性 (变异系数)"""
        if not scores or np.mean(scores) == 0:
            return 0.0
        return float(np.std(scores) / np.mean(scores))

    def _detect_anomaly(self, scores: List[float]) -> Tuple[bool, float]:
        """使用 Z-score 检测异常"""
        if len(scores) < 10:
            return False, 0.0

        mean = np.mean(scores[:-1])  # 不含最新值
        std = np.std(scores[:-1])

        if std == 0:
            return False, 0.0

        z_score = abs((scores[-1] - mean) / std)
        is_anomaly = z_score > Config.ANOMALY_THRESHOLD

        return is_anomaly, float(z_score)

    def _calc_opportunity_score(self, current: float, avg_7d: float,
                                change_pct: float, trend_dir: str,
                                trend_str: float, volatility: float) -> float:
        """
        计算机会评分 (0-100)

        权重分配:
        - 搜索量 (当前分数): 30%
        - 趋势方向和强度: 30%
        - 增长率: 25%
        - 稳定性 (低波动性): 15%
        """
        # 搜索量得分
        volume_score = min(100, current * 1.2)

        # 趋势得分
        if trend_dir == "up":
            trend_score = 60 + (trend_str * 0.4)
        elif trend_dir == "down":
            trend_score = 40 - (trend_str * 0.3)
        else:
            trend_score = 50
        trend_score = min(100, max(0, trend_score))

        # 增长率得分
        growth_score = 50 + (change_pct * 0.5)
        growth_score = min(100, max(0, growth_score))

        # 稳定性得分
        stability_score = max(0, 100 - (volatility * 200))

        # 加权总分
        total = (
            volume_score * 0.30 +
            trend_score * 0.30 +
            growth_score * 0.25 +
            stability_score * 0.15
        )

        return min(100, max(0, total))

    def _categorize_potential(self, score: float) -> str:
        """分类市场潜力"""
        if score >= 75:
            return "high"
        elif score >= 50:
            return "medium"
        else:
            return "low"

    def _generate_recommendation(self, score: float, trend: str,
                                 is_anomaly: bool, change_pct: float) -> str:
        """生成推荐建议"""
        if score >= 75 and trend == "up":
            return "强烈推荐：高潜力上升趋势关键词，值得重点关注和投入"
        elif score >= 75 and is_anomaly:
            return "重要机会：检测到异常高增长，建议立即研究市场动态"
        elif score >= 60 and trend == "up":
            return "值得考虑：中等潜力，呈现上升趋势，建议持续关注"
        elif score >= 60 and is_anomaly:
            return "注意监控：检测到异常波动，需要进一步分析原因"
        elif trend == "down" and score < 40:
            return "建议观望：当前处于下降趋势且潜力较低"
        elif is_anomaly:
            return "异常波动：建议调查变化原因，可能是短期事件影响"
        else:
            return "保持观察：当前表现稳定，继续日常监控"
