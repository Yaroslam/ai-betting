#!/usr/bin/env python3
"""
Test script for HLTV Parser using Selenium - Testing with Vitality team
"""

import sys
import os
import logging

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hltv_parser_selenium import HLTVParserSelenium

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_vitality_selenium():
    """Тестирование парсера на команде Vitality с Selenium"""
    parser = None
    try:
        parser = HLTVParserSelenium()
        
        logger.info("=" * 60)
        logger.info("ТЕСТИРОВАНИЕ HLTV PARSER (SELENIUM) - КОМАНДА VITALITY")
        logger.info("=" * 60)
        
        # Тест 1: Поиск команды
        logger.info("\n1. Поиск команды Vitality...")
        team_id = parser.find_team_by_name("vitality")
        if team_id:
            logger.info(f"✅ Команда найдена! ID: {team_id}")
        else:
            logger.error("❌ Команда не найдена")
            return False
        
        # Тест 2: Получение информации о команде
        logger.info("\n2. Получение информации о команде...")
        team_info = parser.get_team_info("vitality")
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
                
                # Тест 3: Получение статистики первого игрока
                if len(roster) > 0:
                    logger.info("\n3. Получение статистики первого игрока...")
                    first_player = roster[0]
                    player_stats = parser.get_player_stats(
                        first_player.get('player_id'), 
                        first_player.get('nickname')
                    )
                    if player_stats:
                        logger.info(f"✅ Статистика игрока {first_player.get('nickname')} получена:")
                        logger.info(f"   Настоящее имя: {player_stats.get('real_name', 'N/A')}")
                        logger.info(f"   Страна: {player_stats.get('country', 'N/A')}")
                        logger.info(f"   Рейтинг 2.0: {player_stats.get('rating_2_0', 'N/A')}")
                        logger.info(f"   K/D: {player_stats.get('kd_ratio', 'N/A')}")
                        logger.info(f"   ADR: {player_stats.get('adr', 'N/A')}")
                        logger.info(f"   KAST: {player_stats.get('kast', 'N/A')}%")
                        logger.info(f"   Хедшоты: {player_stats.get('headshot_percentage', 'N/A')}%")
                    else:
                        logger.warning(f"⚠️ Не удалось получить статистику для {first_player.get('nickname')}")
            else:
                logger.warning("   ⚠️ Состав команды не найден")
        else:
            logger.error("❌ Не удалось получить информацию о команде")
            return False
        
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
            parser.close()


def main():
    """Основная функция"""
    try:
        success = test_vitality_selenium()
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
    main() 