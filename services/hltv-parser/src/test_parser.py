#!/usr/bin/env python3
"""
Test script for HLTV Parser - Testing with Vitality team
"""

import asyncio
import sys
import os
import logging

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hltv_parser import HLTVParser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_vitality():
    """Тестирование парсера на команде Vitality"""
    parser = None
    try:
        parser = HLTVParser()
        
        logger.info("=" * 60)
        logger.info("ТЕСТИРОВАНИЕ HLTV PARSER - КОМАНДА VITALITY")
        logger.info("=" * 60)
        
        # Тест 1: Поиск команды
        logger.info("\n1. Поиск команды Vitality...")
        team_id = await parser.find_team_by_name("vitality")
        if team_id:
            logger.info(f"✅ Команда найдена! ID: {team_id}")
        else:
            logger.error("❌ Команда не найдена")
            return False
        
        # Тест 2: Получение информации о команде
        logger.info("\n2. Получение информации о команде...")
        team_info = await parser.get_team_info("vitality")
        if team_info:
            logger.info("✅ Информация о команде получена:")
            logger.info(f"   Название: {team_info.get('name', 'N/A')}")
            logger.info(f"   Страна: {team_info.get('country', 'N/A')}")
            logger.info(f"   Рейтинг: {team_info.get('ranking', 'N/A')}")
            logger.info(f"   Количество игроков: {len(team_info.get('roster', []))}")
            
            # Показываем состав
            roster = team_info.get('roster', [])
            if roster:
                logger.info("   Состав команды:")
                for i, player in enumerate(roster, 1):
                    logger.info(f"     {i}. {player.get('nickname', 'N/A')} (ID: {player.get('player_id', 'N/A')})")
        else:
            logger.error("❌ Не удалось получить информацию о команде")
            return False
        
        # Тест 3: Получение последних матчей
        logger.info("\n3. Получение последних матчей...")
        recent_matches = await parser.get_recent_matches(team_id, limit=5)
        if recent_matches:
            logger.info(f"✅ Получено матчей: {len(recent_matches)}")
            for i, match in enumerate(recent_matches, 1):
                result_emoji = "🟢" if match.get('result') == 'win' else "🔴"
                logger.info(f"   {i}. {result_emoji} vs {match.get('opponent', 'N/A')} - {match.get('score', 'N/A')}")
        else:
            logger.warning("⚠️ Не удалось получить последние матчи")
        
        # Тест 4: Получение статистики игроков (тестируем первых 2-х)
        logger.info("\n4. Получение статистики игроков...")
        if roster:
            for i, player in enumerate(roster[:2], 1):
                logger.info(f"\n   4.{i}. Статистика игрока {player.get('nickname', 'N/A')}...")
                
                await asyncio.sleep(2)  # Задержка между запросами
                
                player_stats = await parser.get_player_stats(player.get('player_id'))
                if player_stats:
                    logger.info(f"      ✅ Статистика получена:")
                    logger.info(f"         Настоящее имя: {player_stats.get('real_name', 'N/A')}")
                    logger.info(f"         Страна: {player_stats.get('country', 'N/A')}")
                    logger.info(f"         Возраст: {player_stats.get('age', 'N/A')}")
                    logger.info(f"         Рейтинг 2.0: {player_stats.get('rating_2_0', 'N/A')}")
                    logger.info(f"         K/D: {player_stats.get('kd_ratio', 'N/A')}")
                    logger.info(f"         ADR: {player_stats.get('adr', 'N/A')}")
                    logger.info(f"         KAST: {player_stats.get('kast', 'N/A')}%")
                    logger.info(f"         Хедшоты: {player_stats.get('headshot_percentage', 'N/A')}%")
                    logger.info(f"         Карт сыграно: {player_stats.get('maps_played', 'N/A')}")
                else:
                    logger.warning(f"      ⚠️ Не удалось получить статистику для {player.get('nickname', 'N/A')}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
        
    finally:
        if parser:
            await parser.close()


async def main():
    """Основная функция"""
    try:
        success = await test_vitality()
        if success:
            logger.info("Парсер работает корректно!")
            sys.exit(0)
        else:
            logger.error("Парсер не прошел тестирование!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 