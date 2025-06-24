#!/usr/bin/env python3
"""
HLTV Parser - Main entry point
Парсер для получения информации о командах и игроках с HLTV.org
"""

import asyncio
import logging
from hltv_parser import HLTVParser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Основная функция для тестирования парсера"""
    try:
        parser = HLTVParser()
        
        # Тестируем на команде Vitality
        team_name = "vitality"
        logger.info(f"Начинаем парсинг команды: {team_name}")
        
        # Получаем информацию о команде
        team_info = await parser.get_team_info(team_name)
        if team_info:
            logger.info("Информация о команде получена успешно")
            logger.info(f"Команда: {team_info.get('name')}")
            logger.info(f"Рейтинг: {team_info.get('ranking')}")
            logger.info(f"Состав: {[player['nickname'] for player in team_info.get('roster', [])]}")
            
            # Получаем последние матчи
            recent_matches = await parser.get_recent_matches(team_info.get('team_id'))
            if recent_matches:
                logger.info(f"Получено последних матчей: {len(recent_matches)}")
            
            # Получаем статистику игроков
            for player in team_info.get('roster', [])[:2]:  # Тестируем на первых двух игроках
                player_stats = await parser.get_player_stats(player['player_id'])
                if player_stats:
                    logger.info(f"Статистика игрока {player['nickname']} получена")
        
        logger.info("Парсинг завершен успешно")
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 