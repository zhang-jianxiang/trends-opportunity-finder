#!/usr/bin/env python3
"""
Google Trends 每日自动采集与分析
这是 GitHub Actions 定时任务的入口程序

执行流程:
  1. 数据采集 - 从 Google Trends 获取关键词趋势数据
  2. 趋势分析 - 计算趋势指标和机会评分
  3. 机会检测 - 识别和记录市场机会
"""

import sys
import os
import time
from datetime import datetime

# 将 backend 目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.database import Database
from src.collector import TrendsCollector
from src.analyzer import TrendAnalyzer
from src.opportunity import OpportunityDetector

from loguru import logger

# 确保 logs 目录存在
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs"), exist_ok=True)

# 配置日志
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


def main():
    """主执行函数"""
    start_time = time.time()
    today = datetime.now().strftime("%Y-%m-%d")

    logger.info("=" * 60)
    logger.info(f"Google Trends 每日任务启动 - {today}")
    logger.info("=" * 60)

    # 验证配置
    if not Config.validate():
        logger.error("配置验证失败！请检查环境变量 SUPABASE_URL 和 SUPABASE_KEY")
        logger.info(f"\n当前配置:\n{Config.summary()}")
        sys.exit(1)

    logger.info(f"配置摘要:\n{Config.summary()}")
    logger.info("-" * 60)

    db = Database()
    total_records = 0
    has_errors = False

    # 步骤 1: 数据采集
    logger.info(">>> 步骤 1/3: 数据采集")
    collect_start = time.time()

    try:
        collector = TrendsCollector()
        collect_result = collector.collect_all()
        total_records = collect_result["records_collected"]
        collect_duration = int(time.time() - collect_start)

        logger.info(f"采集完成: {total_records} 条记录, 耗时 {collect_duration}s, 错误 {collect_result['errors']} 批")

        db.insert_log(
            task_name="data_collection",
            status="success" if collect_result["errors"] == 0 else "partial",
            records=total_records,
            duration=collect_duration,
        )

        if collect_result["errors"] > 0:
            has_errors = True

    except Exception as e:
        collect_duration = int(time.time() - collect_start)
        logger.error(f"数据采集失败: {e}")
        db.insert_log(
            task_name="data_collection",
            status="failed",
            duration=collect_duration,
            error=str(e)
        )
        has_errors = True

    logger.info("-" * 60)

    # 步骤 2: 趋势分析
    logger.info(">>> 步骤 2/3: 趋势分析")
    analyze_start = time.time()

    try:
        analyzer = TrendAnalyzer()
        analysis_results = analyzer.analyze_all()
        analyze_duration = int(time.time() - analyze_start)

        logger.info(f"分析完成: {len(analysis_results)} 条结果, 耗时 {analyze_duration}s")

        db.insert_log(
            task_name="trend_analysis",
            status="success",
            records=len(analysis_results),
            duration=analyze_duration,
        )

    except Exception as e:
        analyze_duration = int(time.time() - analyze_start)
        logger.error(f"趋势分析失败: {e}")
        db.insert_log(
            task_name="trend_analysis",
            status="failed",
            duration=analyze_duration,
            error=str(e)
        )
        has_errors = True

    logger.info("-" * 60)

    # 步骤 3: 机会检测
    logger.info(">>> 步骤 3/3: 机会检测")
    opp_start = time.time()

    try:
        detector = OpportunityDetector()
        opportunities = detector.detect_all()
        opp_duration = int(time.time() - opp_start)

        logger.info(f"机会检测完成: 发现 {len(opportunities)} 个新机会, 耗时 {opp_duration}s")

        if opportunities:
            logger.info("机会列表:")
            for i, opp in enumerate(opportunities, 1):
                logger.info(f"  {i}. [{opp['opportunity_type']}] {opp['title']} (评分: {opp['score']})")

        db.insert_log(
            task_name="opportunity_detection",
            status="success",
            records=len(opportunities),
            duration=opp_duration,
        )

    except Exception as e:
        opp_duration = int(time.time() - opp_start)
        logger.error(f"机会检测失败: {e}")
        db.insert_log(
            task_name="opportunity_detection",
            status="failed",
            duration=opp_duration,
            error=str(e)
        )
        has_errors = True

    # 汇总
    total_duration = int(time.time() - start_time)
    status = "success" if not has_errors else "partial"

    logger.info("=" * 60)
    logger.info(f"每日任务完成 - 状态: {status.upper()}")
    logger.info(f"总耗时: {total_duration}s | 数据记录: {total_records} 条")
    logger.info("=" * 60)

    sys.exit(0 if not has_errors else 1)


if __name__ == "__main__":
    main()
