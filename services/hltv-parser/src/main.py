"""
Main file для запуска HLTV парсеров
"""

import logging
import sys
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hltv_parser.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

from player_parser import PlayerParser
from team_parser import TeamParser


def test_player_parser():
    """Тестирование парсера игроков"""
    logger.info("Начинаем тестирование парсера игроков...")
    
    # Ограиченный список игроков для тестирования обхода защиты
    test_players = [
        (11893, 's1mple')   # Тестируем только одного игрока для скорости
    ]
    
    successful_parses = 0
    
    with PlayerParser() as parser:
        for i, (player_id, nickname) in enumerate(test_players, 1):
            try:
                logger.info(f"[{i}/{len(test_players)}] Тестируем парсинг игрока: {nickname} (ID: {player_id})")
                
                # Парсим игрока
                player_data = parser.parse_player(player_id, nickname)
                
                if player_data:
                    logger.info(f"[OK] Успешно спарсен игрок: {player_data['nickname']}")
                    
                    # Показываем основную статистику
                    stats = player_data.get('statistics', {})
                    if stats.get('rating_2_0'):
                        logger.info(f"   Rating 2.0: {stats['rating_2_0']}")
                    if stats.get('kd_ratio'):
                        logger.info(f"   K/D Ratio: {stats['kd_ratio']}")
                    if stats.get('adr'):
                        logger.info(f"   ADR: {stats['adr']}")
                    
                    # Сохраняем в базу данных
                    if parser.save_player_to_database(player_data):
                        logger.info(f"[OK] Игрок {nickname} сохранен в базу данных")
                        successful_parses += 1
                    else:
                        logger.error(f"[ERROR] Не удалось сохранить игрока {nickname} в базу данных")
                else:
                    logger.error(f"[ERROR] Не удалось спарсить игрока {nickname}")
                
                # Пауза между игроками
                if i < len(test_players):
                    delay = 8
                    logger.info(f"Пауза {delay} секунд перед следующим игроком...")
                    import time
                    time.sleep(delay)
                
            except Exception as e:
                logger.error(f"[ERROR] Ошибка при тестировании игрока {nickname}: {e}")
    
    logger.info(f"Результат тестирования игроков: {successful_parses}/{len(test_players)} успешно")


def test_team_parser():
    """Тестирование парсера команд"""
    logger.info("Начинаем тестирование парсера команд...")
    
    with TeamParser() as parser:
        try:
            # Парсим только топ-2 команды для тестирования (меньше нагрузки)
            max_teams = 2
            logger.info(f"Парсим топ-{max_teams} команд для тестирования обхода защиты...")
            
            teams = parser.parse_team_ranking(max_teams=max_teams)
            
            if teams:
                logger.info(f"[OK] Успешно спарсено команд: {len(teams)}")
                
                # Показываем информацию о командах
                for team in teams:
                    logger.info(f"Команда #{team['rank']}: {team['name']} ({team['points']} очков)")
                    logger.info(f"   Игроков в команде: {len(team.get('players', []))}")
                    
                    # Показываем игроков команды
                    for player in team.get('players', []):
                        logger.info(f"   - {player.get('nickname', 'Unknown')} ({player.get('country_code', 'N/A')})")
                
                # Сохраняем в базу данных
                logger.info("Сохраняем команды в базу данных...")
                saved_count = parser.save_all_teams_to_database(teams)
                logger.info(f"[OK] Сохранено команд в базу данных: {saved_count}")
                
            else:
                logger.error("[ERROR] Не удалось спарсить команды")
                
        except Exception as e:
            logger.error(f"[ERROR] Ошибка при тестировании парсера команд: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Главная функция"""
    logger.info("=" * 60)
    logger.info("ЗАПУСК HLTV ПАРСЕРОВ С ОБХОДОМ ЗАЩИТЫ ОТ БОТОВ")
    logger.info(f"Время запуска: {datetime.now()}")
    logger.info("=" * 60)
    
    try:
        # Тестируем парсер игроков
        logger.info("1. Тестирование парсера игроков с stealth режимом...")
        test_player_parser()
        
        logger.info("\n" + "=" * 60)
        
        # Пауза между тестами
        import time
        pause = 12
        logger.info(f"Пауза {pause} секунд между тестами...")
        time.sleep(pause)
        
        # Тестируем парсер команд
        logger.info("2. Тестирование парсера команд с stealth режимом...")
        test_team_parser()
        
        logger.info("=" * 60)
        logger.info("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        logger.info(f"Время завершения: {datetime.now()}")
        logger.info("Проверьте базу данных для просмотра сохраненных данных")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 