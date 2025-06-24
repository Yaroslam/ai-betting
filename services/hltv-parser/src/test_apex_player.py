#!/usr/bin/env python3
"""
Test script for HLTV Parser - Testing apEX player statistics
"""

import sys
import os
import logging
import time

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hltv_parser_selenium import HLTVParserSelenium

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_apex_player():
    """Тестирование парсера на игроке apEX"""
    parser = None
    try:
        parser = HLTVParserSelenium()
        
        logger.info("=" * 60)
        logger.info("ТЕСТИРОВАНИЕ HLTV PARSER - ИГРОК APEX")
        logger.info("=" * 60)
        
        # ID и никнейм apEX из предыдущего теста
        apex_id = 7322
        apex_nickname = "apEX"
        
        logger.info(f"\nПолучение детальной статистики игрока {apex_nickname} (ID: {apex_id})...")
        
        # Получаем статистику игрока
        player_stats = parser.get_player_stats(apex_id, apex_nickname)
        
        if player_stats:
            logger.info("✅ Статистика игрока получена успешно!")
            logger.info("\n" + "=" * 40)
            logger.info("ОСНОВНАЯ ИНФОРМАЦИЯ:")
            logger.info("=" * 40)
            logger.info(f"ID игрока: {player_stats.get('player_id', 'N/A')}")
            logger.info(f"Никнейм: {player_stats.get('nickname', 'N/A')}")
            logger.info(f"Настоящее имя: {player_stats.get('real_name', 'N/A')}")
            logger.info(f"Страна: {player_stats.get('country', 'N/A')}")
            logger.info(f"Возраст: {player_stats.get('age', 'N/A')}")
            
            logger.info("\n" + "=" * 40)
            logger.info("ИГРОВАЯ СТАТИСТИКА:")
            logger.info("=" * 40)
            logger.info(f"Рейтинг 2.0: {player_stats.get('rating_2_0', 'N/A')}")
            logger.info(f"K/D соотношение: {player_stats.get('kd_ratio', 'N/A')}")
            logger.info(f"ADR (урон за раунд): {player_stats.get('adr', 'N/A')}")
            logger.info(f"KAST: {player_stats.get('kast', 'N/A')}%")
            logger.info(f"Процент хедшотов: {player_stats.get('headshot_percentage', 'N/A')}%")
            logger.info(f"Карт сыграно: {player_stats.get('maps_played', 'N/A')}")
            logger.info(f"Убийств за раунд: {player_stats.get('kills_per_round', 'N/A')}")
            logger.info(f"Ассистов за раунд: {player_stats.get('assists_per_round', 'N/A')}")
            logger.info(f"Смертей за раунд: {player_stats.get('deaths_per_round', 'N/A')}")
            
            # Показываем все доступные ключи для отладки
            logger.info("\n" + "=" * 40)
            logger.info("ВСЕ ДОСТУПНЫЕ ДАННЫЕ:")
            logger.info("=" * 40)
            for key, value in player_stats.items():
                logger.info(f"{key}: {value}")
            
            return True
        else:
            logger.error("❌ Не удалось получить статистику игрока")
            return False
        
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
        success = test_apex_player()
        if success:
            logger.info("\n" + "=" * 60)
            logger.info("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            logger.info("=" * 60)
            sys.exit(0)
        else:
            logger.error("❌ Парсер не прошел тестирование!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 