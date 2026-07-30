#!/usr/bin/env python3
"""
Google Trends 姣忔棩鑷姩閲囬泦涓庡垎鏋?
杩欐槸 GitHub Actions 瀹氭椂浠诲姟鐨勫叆鍙ｇ▼搴?

鎵ц娴佺▼:
  1. 鏁版嵁閲囬泦 - 浠?Google Trends 鑾峰彇鍏抽敭璇嶈秼鍔挎暟鎹?
  2. 瓒嬪娍鍒嗘瀽 - 璁＄畻瓒嬪娍鎸囨爣鍜屾満浼氳瘎鍒?
  3. 鏈轰細妫€娴?- 璇嗗埆鍜岃褰曞競鍦烘満浼?
"""

import sys
import os
import time
from datetime import datetime

# 灏?backend 鐩綍鍔犲叆 Python 璺緞
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.database import Database
from src.collector import TrendsCollector
from src.analyzer import TrendAnalyzer
from src.opportunity import OpportunityDetector

from loguru import logger

# 纭繚 logs 鐩綍瀛樺湪
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs"), exist_ok=True)

# 閰嶇疆鏃ュ織
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
    """涓绘墽琛屽嚱鏁?""
    start_time = time.time()
    today = datetime.now().strftime("%Y-%m-%d")

    logger.info("=" * 60)
    logger.info(f"Google Trends 姣忔棩浠诲姟鍚姩 - {today}")
    logger.info("=" * 60)

    # 楠岃瘉閰嶇疆
    if not Config.validate():
        logger.error("閰嶇疆楠岃瘉澶辫触锛佽妫€鏌ョ幆澧冨彉閲?SUPABASE_URL 鍜?SUPABASE_KEY")
        logger.info(f"\n褰撳墠閰嶇疆:\n{Config.summary()}")
        sys.exit(1)

    logger.info(f"閰嶇疆鎽樿:\n{Config.summary()}")
    logger.info("-" * 60)

    db = Database()
    total_records = 0
    has_errors = False

    # 姝ラ 1: 鏁版嵁閲囬泦
    logger.info(">>> 姝ラ 1/3: 鏁版嵁閲囬泦")
    collect_start = time.time()

    try:
        collector = TrendsCollector()
        collect_result = collector.collect_all()
        total_records = collect_result["records_collected"]
        collect_duration = int(time.time() - collect_start)

        logger.info(f"閲囬泦瀹屾垚: {total_records} 鏉¤褰? 鑰楁椂 {collect_duration}s, 閿欒 {collect_result['errors']} 鎵?)

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
        logger.error(f"鏁版嵁閲囬泦澶辫触: {e}")
        db.insert_log(
            task_name="data_collection",
            status="failed",
            duration=collect_duration,
            error=str(e)
        )
        has_errors = True

    logger.info("-" * 60)

    # 姝ラ 2: 瓒嬪娍鍒嗘瀽
    logger.info(">>> 姝ラ 2/3: 瓒嬪娍鍒嗘瀽")
    analyze_start = time.time()

    try:
        analyzer = TrendAnalyzer()
        analysis_results = analyzer.analyze_all()
        analyze_duration = int(time.time() - analyze_start)

        logger.info(f"鍒嗘瀽瀹屾垚: {len(analysis_results)} 鏉＄粨鏋? 鑰楁椂 {analyze_duration}s")

        db.insert_log(
            task_name="trend_analysis",
            status="success",
            records=len(analysis_results),
            duration=analyze_duration,
        )

    except Exception as e:
        analyze_duration = int(time.time() - analyze_start)
        logger.error(f"瓒嬪娍鍒嗘瀽澶辫触: {e}")
        db.insert_log(
            task_name="trend_analysis",
            status="failed",
            duration=analyze_duration,
            error=str(e)
        )
        has_errors = True

    logger.info("-" * 60)

    # 姝ラ 3: 鏈轰細妫€娴?
    logger.info(">>> 姝ラ 3/3: 鏈轰細妫€娴?)
    opp_start = time.time()

    try:
        detector = OpportunityDetector()
        opportunities = detector.detect_all()
        opp_duration = int(time.time() - opp_start)

        logger.info(f"鏈轰細妫€娴嬪畬鎴? 鍙戠幇 {len(opportunities)} 涓柊鏈轰細, 鑰楁椂 {opp_duration}s")

        if opportunities:
            logger.info("鏈轰細鍒楄〃:")
            for i, opp in enumerate(opportunities, 1):
                logger.info(f"  {i}. [{opp['opportunity_type']}] {opp['title']} (璇勫垎: {opp['score']})")

        db.insert_log(
            task_name="opportunity_detection",
            status="success",
            records=len(opportunities),
            duration=opp_duration,
        )

    except Exception as e:
        opp_duration = int(time.time() - opp_start)
        logger.error(f"鏈轰細妫€娴嬪け璐? {e}")
        db.insert_log(
            task_name="opportunity_detection",
            status="failed",
            duration=opp_duration,
            error=str(e)
        )
        has_errors = True

    # 姹囨€?
    total_duration = int(time.time() - start_time)
    status = "success" if not has_errors else "partial"

    logger.info("=" * 60)
    logger.info(f"姣忔棩浠诲姟瀹屾垚 - 鐘舵€? {status.upper()}")
    logger.info(f"鎬昏€楁椂: {total_duration}s | 鏁版嵁璁板綍: {total_records} 鏉?)
    logger.info("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    main()
