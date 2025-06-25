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
    
    # Примеры игроков для тестирования
    test_players = [
        (20425, 'r1nkle'),
        (11893, 's1mple'),
        (8183, 'ZywOo')
    ]
    
    with PlayerParser() as parser:
        for player_id, nickname in test_players:
            try:
                logger.info(f"Тестируем парсинг игрока: {nickname} (ID: {player_id})")
                
                # Парсим игрока
                player_data = parser.parse_player(player_id, nickname)
                
                if player_data:
                    logger.info(f"Успешно спарсен игрок: {player_data['nickname']}")
                    logger.info(f"Статистика: {player_data.get('statistics', {})}")
                    
                    # Сохраняем в базу данных
                    if parser.save_player_to_database(player_data):
                        logger.info(f"Игрок {nickname} сохранен в базу данных")
                    else:
                        logger.error(f"Не удалось сохранить игрока {nickname} в базу данных")
                else:
                    logger.error(f"Не удалось спарсить игрока {nickname}")
                
            except Exception as e:
                logger.error(f"Ошибка при тестировании игрока {nickname}: {e}")


def test_team_parser():
    """Тестирование парсера команд"""
    logger.info("Начинаем тестирование парсера команд...")
    
    with TeamParser() as parser:
        try:
            # Парсим топ-5 команд для тестирования
            teams = parser.parse_team_ranking(max_teams=5)
            
            if teams:
                logger.info(f"Успешно спарсено команд: {len(teams)}")
                
                # Сохраняем в базу данных
                saved_count = parser.save_all_teams_to_database(teams)
                logger.info(f"Сохранено команд в базу данных: {saved_count}")
                
                # Показываем информацию о командах
                for team in teams:
                    logger.info(f"Команда #{team['rank']}: {team['name']} ({team['points']} очков)")
                    logger.info(f"  Игроков в команде: {len(team.get('players', []))}")
                    
            else:
                logger.error("Не удалось спарсить команды")
                
        except Exception as e:
            logger.error(f"Ошибка при тестировании парсера команд: {e}")


def main():
    """Главная функция"""
    logger.info("=" * 50)
    logger.info("Запуск HLTV парсеров")
    logger.info(f"Время запуска: {datetime.now()}")
    logger.info("=" * 50)
    
    try:
        # Тестируем парсер игроков
        logger.info("1. Тестирование парсера игроков...")
        test_player_parser()
        
        logger.info("\n" + "=" * 50)
        
        # Тестируем парсер команд
        logger.info("2. Тестирование парсера команд...")
        test_team_parser()
        
        logger.info("=" * 50)
        logger.info("Тестирование завершено успешно!")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 