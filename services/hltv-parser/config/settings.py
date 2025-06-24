"""
Configuration settings for HLTV Parser
"""

import os
from typing import Dict, Any

# Base URLs
HLTV_BASE_URL = "https://www.hltv.org"

# Request settings
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # Задержка между запросами в секундах
MAX_RETRIES = 3

# Headers для запросов
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Настройки парсинга
PARSING_CONFIG = {
    'max_recent_matches': 5,
    'max_roster_size': 10,
    'enable_caching': True,
    'cache_duration': 3600,  # 1 час в секундах
}

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Тестовые команды для проверки
TEST_TEAMS = [
    'vitality',
    'navi',
    'faze', 
    'g2',
    'liquid'
] 