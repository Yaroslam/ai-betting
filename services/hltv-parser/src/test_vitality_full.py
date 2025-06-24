#!/usr/bin/env python3
"""
Полный тест парсера HLTV для команды Vitality и всех её игроков
"""

import sys
import os
import logging
import time
from typing import Dict, Any, List

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hltv_parser_selenium import HLTVParserSelenium

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Данные команды Vitality
VITALITY_TEAM_ID = 9565
VITALITY_PLAYERS = [
    {"id": 7322, "nickname": "apEX"},
    {"id": 11816, "nickname": "ropz"},
    {"id": 11893, "nickname": "ZywOo"},
    {"id": 16693, "nickname": "flameZ"},
    {"id": 18462, "nickname": "mezii"}
]

def test_team_info(parser: HLTVParserSelenium) -> bool:
    """Тестирование получения информации о команде"""
    try:
        logger.info("🏆 ТЕСТИРОВАНИЕ ИНФОРМАЦИИ О КОМАНДЕ VITALITY")
        logger.info("=" * 60)
        
        team_info = parser.get_team_info(VITALITY_TEAM_ID)
        
        if not team_info:
            logger.error("❌ Не удалось получить информацию о команде")
            return False
        
        logger.info("✅ Информация о команде получена:")
        logger.info(f"  Название: {team_info.get('name', 'N/A')}")
        logger.info(f"  Страна: {team_info.get('country', 'N/A')}")
        logger.info(f"  Рейтинг: #{team_info.get('ranking', 'N/A')}")
        logger.info(f"  Количество игроков: {team_info.get('player_count', 'N/A')}")
        
        # Проверяем обязательные поля
        required_fields = ['name', 'country']
        missing_fields = [field for field in required_fields if not team_info.get(field)]
        
        if missing_fields:
            logger.warning(f"⚠️ Отсутствуют обязательные поля: {missing_fields}")
            return False
        
        logger.info("✅ Тест информации о команде пройден успешно!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании команды: {e}")
        return False

def test_team_roster(parser: HLTVParserSelenium) -> bool:
    """Тестирование получения состава команды"""
    try:
        logger.info("\n👥 ТЕСТИРОВАНИЕ СОСТАВА КОМАНДЫ VITALITY")
        logger.info("=" * 60)
        
        roster = parser.get_team_roster(VITALITY_TEAM_ID)
        
        if not roster:
            logger.error("❌ Не удалось получить состав команды")
            return False
        
        logger.info(f"✅ Найдено игроков в составе: {len(roster)}")
        
        for i, player in enumerate(roster, 1):
            logger.info(f"  {i}. {player.get('nickname', 'N/A')} (ID: {player.get('player_id', 'N/A')})")
        
        # Проверяем, что нашли хотя бы 4 игроков (обычно в команде 5)
        if len(roster) < 4:
            logger.warning(f"⚠️ Найдено мало игроков: {len(roster)} (ожидается 5)")
            return False
        
        logger.info("✅ Тест состава команды пройден успешно!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании состава: {e}")
        return False

def test_player_stats(parser: HLTVParserSelenium, player_data: Dict[str, Any]) -> bool:
    """Тестирование получения статистики игрока"""
    try:
        player_id = player_data["id"]
        nickname = player_data["nickname"]
        
        logger.info(f"\n📊 ТЕСТИРОВАНИЕ СТАТИСТИКИ ИГРОКА {nickname.upper()}")
        logger.info("=" * 60)
        
        player_stats = parser.get_player_stats(player_id, nickname)
        
        if not player_stats:
            logger.error(f"❌ Не удалось получить статистику игрока {nickname}")
            return False
        
        logger.info(f"✅ Статистика игрока {nickname} получена:")
        logger.info(f"  ID: {player_stats.get('player_id', 'N/A')}")
        logger.info(f"  Никнейм: {player_stats.get('nickname', 'N/A')}")
        logger.info(f"  Настоящее имя: {player_stats.get('real_name', 'N/A')}")
        logger.info(f"  Страна: {player_stats.get('country', 'N/A')}")
        logger.info(f"  Возраст: {player_stats.get('age', 'N/A')}")
        logger.info("  Статистика:")
        logger.info(f"    Rating 2.0: {player_stats.get('rating_2_0', 'N/A')}")
        logger.info(f"    K/D: {player_stats.get('kd_ratio', 'N/A')}")
        logger.info(f"    ADR: {player_stats.get('adr', 'N/A')}")
        logger.info(f"    KAST: {player_stats.get('kast', 'N/A')}{'%' if player_stats.get('kast') else ''}")
        logger.info(f"    HS%: {player_stats.get('headshot_percentage', 'N/A')}{'%' if player_stats.get('headshot_percentage') else ''}")
        
        # Подсчет успешно полученных статистик
        stats_fields = ['rating_2_0', 'kd_ratio', 'adr', 'kast', 'headshot_percentage']
        found_stats = sum(1 for field in stats_fields if player_stats.get(field) is not None)
        
        logger.info(f"  📈 Найдено статистик: {found_stats}/{len(stats_fields)}")
        
        # Проверяем минимальные требования
        if not player_stats.get('nickname'):
            logger.error(f"❌ Не найден никнейм игрока {nickname}")
            return False
        
        if found_stats == 0:
            logger.warning(f"⚠️ Не найдено статистик для игрока {nickname}")
            return False
        
        logger.info(f"✅ Тест игрока {nickname} пройден успешно!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании игрока {nickname}: {e}")
        return False

def run_full_test() -> bool:
    """Запуск полного теста"""
    parser = None
    try:
        logger.info("🚀 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ HLTV PARSER")
        logger.info("🎯 Команда: Team Vitality")
        logger.info("👥 Игроки: apEX, ropz, ZywOo, flameZ, mezii")
        logger.info("=" * 80)
        
        parser = HLTVParserSelenium()
        
        # Тест 1: Информация о команде
        if not test_team_info(parser):
            logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Тест информации о команде провален")
            return False
        
        # Тест 2: Состав команды
        if not test_team_roster(parser):
            logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Тест состава команды провален")
            return False
        
        # Тест 3: Статистика каждого игрока
        successful_players = 0
        total_players = len(VITALITY_PLAYERS)
        
        for player in VITALITY_PLAYERS:
            if test_player_stats(parser, player):
                successful_players += 1
            else:
                logger.warning(f"⚠️ Игрок {player['nickname']} не прошел тест")
            
            # Небольшая пауза между запросами
            time.sleep(2)
        
        # Оценка результатов
        logger.info("\n" + "=" * 80)
        logger.info("📋 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        logger.info("=" * 80)
        logger.info(f"✅ Информация о команде: УСПЕШНО")
        logger.info(f"✅ Состав команды: УСПЕШНО")
        logger.info(f"👥 Статистика игроков: {successful_players}/{total_players} успешно")
        
        success_rate = (successful_players / total_players) * 100
        logger.info(f"📊 Общий процент успеха: {success_rate:.1f}%")
        
        # Определяем успешность теста
        if successful_players >= total_players * 0.8:  # 80% игроков должны пройти тест
            logger.info("🎉 ПОЛНОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
            logger.info("✅ Парсер готов к использованию!")
            return True
        else:
            logger.error("❌ ТЕСТИРОВАНИЕ НЕ ПРОЙДЕНО!")
            logger.error(f"Требуется минимум {total_players * 0.8:.0f} успешных игроков из {total_players}")
            return False
        
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
        
    finally:
        if parser:
            parser.close()

def main():
    """Основная функция"""
    try:
        start_time = time.time()
        
        success = run_full_test()
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"\n⏱️ Время выполнения теста: {duration:.1f} секунд")
        
        if success:
            logger.info("=" * 80)
            logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            logger.info("🚀 ПАРСЕР ГОТОВ К РАБОТЕ!")
            logger.info("=" * 80)
            sys.exit(0)
        else:
            logger.error("=" * 80)
            logger.error("❌ ТЕСТИРОВАНИЕ ПРОВАЛЕНО!")
            logger.error("🔧 ТРЕБУЕТСЯ ДОРАБОТКА ПАРСЕРА!")
            logger.error("=" * 80)
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 