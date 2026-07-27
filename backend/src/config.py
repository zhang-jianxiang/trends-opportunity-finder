"""
Configuration module
"""

import os
from dotenv import load_dotenv

load_dotenv()
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
load_dotenv(os.path.join(_project_root, '.env'))


class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    KEYWORDS = [k.strip() for k in os.getenv('TRENDS_KEYWORDS', 'artificial intelligence,machine learning,digital health,cryptocurrency,sustainable energy,remote work,electric vehicles,social media,online learning,fitness apps').split(',') if k.strip()]
    _raw_regions = os.getenv('TRENDS_REGIONS', ',US,CN,GB,DE,JP').split(',')
    REGIONS = [r.strip() for r in _raw_regions]
    TIMEFRAME = os.getenv('TRENDS_TIMEFRAME', 'today 3-m')
    TREND_UP_THRESHOLD = float(os.getenv('ANALYSIS_TREND_UP_THRESHOLD', '0.5'))
    TREND_DOWN_THRESHOLD = float(os.getenv('ANALYSIS_TREND_DOWN_THRESHOLD', '-0.3'))
    ANOMALY_THRESHOLD = float(os.getenv('ANALYSIS_ANOMALY_THRESHOLD', '2.0'))
    OPPORTUNITY_THRESHOLD = float(os.getenv('ANALYSIS_OPPORTUNITY_THRESHOLD', '60'))

    @classmethod
    def validate(cls):
        return bool(cls.DATABASE_URL)

    @classmethod
    def summary(cls):
        url = cls.DATABASE_URL
        if '@' in url:
            prefix, suffix = url.split('@', 1)
            if ':' in prefix:
                scheme_user = prefix.split(':', 1)[0]
            url = scheme_user + ':****@)' + suffix
        return f'Keywords: {len(cls.KEYWORDS)}\nRegions: {len(cls.REGIONS)}\nTimeframe: {cls.TIMEFRAME}\nDatabase: {url[:50]}...'
