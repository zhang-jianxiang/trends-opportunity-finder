"""
市场机会检测模块
从趋势分析结果中识别和记录市场机会
"""

from datetime import date
from typing import List, Dict
from loguru import logger

from .config import Config
from .database import Database


class OpportunityDetector:
    """市场机会检测器"""

    def __init__(self):
        self.db = Database()

    def detect_all(self) -> List[Dict]:
        """
        从最近的分析结果中检测市场机会

        Returns:
            新发现的机会列表
        """
        # 获取最近7天的分析结果
        recent = self.db.get_recent_analysis(days=7)

        if not recent:
            logger.info("没有可分析的数据")
            return []

        opportunities = []

        for analysis in recent:
            opp = self._evaluate_opportunity(analysis)
            if opp:
                try:
                    self.db.insert_opportunity(opp)
                    opportunities.append(opp)
                    logger.info(f"发现机会: {opp['title']} (评分: {opp['score']})")
                except Exception as e:
                    # 可能是重复机会，忽略
                    logger.debug(f"机会已存在或插入失败: {e}")

        logger.info(f"机会检测完成: 新发现 {len(opportunities)} 个机会")
        return opportunities

    def _evaluate_opportunity(self, analysis: Dict) -> Dict:
        """评估单个分析结果，判断是否构成机会"""

        score = analysis.get("opportunity_score", 0)
        trend = analysis.get("trend_direction", "stable")
        is_anomaly = analysis.get("is_anomaly", False)
        change_pct = analysis.get("score_change_pct", 0)
        current_score = analysis.get("current_score", 0)
        volatility = analysis.get("volatility", 0)

        # 低于阈值不记录
        if score < Config.OPPORTUNITY_THRESHOLD:
            return None

        # 关键词和地区信息
        keyword_info = analysis.get("keywords", {})
        region_info = analysis.get("regions", {})
        keyword_text = keyword_info.get("keyword", "unknown") if isinstance(keyword_info, dict) else str(keyword_info)
        region_code = region_info.get("region_code", "") if isinstance(region_info, dict) else str(region_info)
        region_name = region_info.get("region_name", "Global") if isinstance(region_info, dict) else "Global"

        # 确定机会类型
        opp_type = None
        title = ""
        description = ""

        if trend == "up" and score >= 75 and analysis.get("trend_strength", 0) > 50:
            opp_type = "trending_up"
            title = f"[上升趋势] {keyword_text} - {region_name}"
            description = (
                f"关键词 '{keyword_text}' 在 {region_name} 呈现强劲上升趋势。"
                f"趋势强度: {analysis.get('trend_strength', 0):.1f}%, "
                f"变化率: {change_pct:+.1f}%, "
                f"机会评分: {score:.1f}"
            )

        elif is_anomaly and change_pct > 50:
            opp_type = "emerging"
            title = f"[新兴趋势] {keyword_text} - {region_name}"
            description = (
                f"关键词 '{keyword_text}' 在 {region_name} 检测到异常增长。"
                f"变化率: {change_pct:+.1f}%, "
                f"异常分数: {analysis.get('anomaly_score', 0):.2f}, "
                f"可能是新兴市场趋势"
            )

        elif volatility > 0.4 and score >= 65:
            opp_type = "seasonal"
            title = f"[季节性机会] {keyword_text} - {region_name}"
            description = (
                f"关键词 '{keyword_text}' 在 {region_name} 呈现季节性波动模式。"
                f"波动性: {volatility:.3f}, "
                f"机会评分: {score:.1f}, "
                f"适合把握时机进入"
            )

        elif score >= 80 and volatility < 0.2:
            opp_type = "market_gap"
            title = f"[市场空白] {keyword_text} - {region_name}"
            description = (
                f"关键词 '{keyword_text}' 在 {region_name} 潜力大但竞争度低。"
                f"机会评分: {score:.1f}, "
                f"波动性: {volatility:.3f}, "
                f"是进入的理想时机"
            )

        if not opp_type:
            return None

        # 市场规模估算
        if current_score >= 80:
            market_size = "massive"
        elif current_score >= 60:
            market_size = "large"
        elif current_score >= 40:
            market_size = "medium"
        else:
            market_size = "small"

        # 竞争程度评估
        if volatility >= 0.5:
            competition = "high"
        elif volatility >= 0.2:
            competition = "medium"
        else:
            competition = "low"

        return {
            "keyword_id": analysis["keyword_id"],
            "region_id": analysis["region_id"],
            "opportunity_type": opp_type,
            "title": title,
            "description": description,
            "score": round(score, 2),
            "market_size": market_size,
            "competition_level": competition,
            "trend_direction": trend,
            "detected_date": date.today().isoformat(),
            "status": "active"
        }
