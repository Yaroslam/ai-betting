"""
HLTV Team Ranking Parser
Парсер рейтинга команд с HLTV.org
"""

import re
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
import calendar
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import geckodriver_autoinstaller
from bs4 import BeautifulSoup

from database import SessionLocal, Team, Player, TeamRoster
from player_parser import PlayerParser

logger = logging.getLogger(__name__)


class TeamParser:
    """Парсер рейтинга команд с HLTV.org"""
    
    BASE_URL = "https://www.hltv.org"
    
    def __init__(self):
        self.driver = None
        self.db = SessionLocal()
        self.player_parser = None
        self._init_driver()
    
    def _init_driver(self):
        """Инициализация headless Firefox драйвера"""
        try:
            logger.info("Инициализируем headless Firefox для парсера команд...")
            
            # Автоматически устанавливаем geckodriver
            geckodriver_autoinstaller.install()
            
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--window-size=1920,1080")
            firefox_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Настраиваем профиль Firefox для максимальной производительности
            firefox_profile = webdriver.FirefoxProfile()
            
            # Реалистичный User-Agent
            firefox_profile.set_preference("general.useragent.override", 
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")
            
            # Отключаем изображения для ускорения
            firefox_profile.set_preference("permissions.default.image", 2)
            
            # Настройки для обхода детекции
            firefox_profile.set_preference("dom.webdriver.enabled", False)
            firefox_profile.set_preference("useAutomationExtension", False)
            
            # Настройки для ускорения
            firefox_profile.set_preference("network.http.pipelining", True)
            firefox_profile.set_preference("browser.cache.disk.enable", False)
            firefox_profile.set_preference("browser.cache.memory.enable", False)
            firefox_profile.set_preference("network.http.use-cache", False)
            
            firefox_options.profile = firefox_profile
            
            self.driver = webdriver.Firefox(options=firefox_options)
            self.driver.set_page_load_timeout(45)
            self.driver.implicitly_wait(10)
            
            logger.info("Headless Firefox для парсера команд инициализирован успешно")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Firefox драйвера: {e}")
            raise
    
    def _get_last_monday_date(self) -> Tuple[int, str, int]:
        """Получить дату последнего понедельника для URL рейтинга"""
        today = date.today()
        
        # Находим последний понедельник
        days_since_monday = today.weekday()  # 0 = понедельник
        if days_since_monday == 0:
            # Сегодня понедельник
            last_monday = today
        else:
            # Вычисляем предыдущий понедельник
            last_monday = today - timedelta(days=days_since_monday)
        
        year = last_monday.year
        month = calendar.month_name[last_monday.month].lower()
        day = last_monday.day
        
        logger.info(f"Последний понедельник: {year}/{month}/{day}")
        return year, month, day
    
    def _fetch_ranking_page(self, retries: int = 3) -> Optional[BeautifulSoup]:
        """Загрузить страницу рейтинга команд"""
        year, month, day = self._get_last_monday_date()
        url = f"{self.BASE_URL}/ranking/teams/{year}/{month}/{day}"
        
        for attempt in range(retries):
            try:
                logger.info(f"Загружаем рейтинг команд (попытка {attempt + 1}): {url}")
                
                if attempt > 0:
                    time.sleep(5 + attempt * 2)
                
                # Сначала загружаем главную страницу HLTV для получения cookies
                if attempt == 0:
                    try:
                        self.driver.get(self.BASE_URL)
                        time.sleep(2)
                    except:
                        pass
                
                # Загружаем страницу рейтинга
                self.driver.get(url)
                
                # Ждем загрузки контента
                time.sleep(4 + attempt)
                
                # Проверяем на блокировку или ошибки
                if "Access Denied" in self.driver.title or "403" in self.driver.title or "Not Found" in self.driver.title:
                    logger.warning(f"Страница заблокирована или не найдена (попытка {attempt + 1}): {self.driver.title}")
                    if attempt < retries - 1:
                        time.sleep(15 + attempt * 5)
                        continue
                    else:
                        return None
                
                # Получаем HTML
                html = self.driver.page_source
                logger.info(f"Страница рейтинга загружена успешно, размер: {len(html)} символов")
                
                if len(html) < 1000:
                    logger.warning("Получена подозрительно короткая страница")
                    if attempt < retries - 1:
                        continue
                
                return BeautifulSoup(html, 'html.parser')
                
            except Exception as e:
                logger.error(f"Ошибка при загрузке рейтинга команд {url} (попытка {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(10 + attempt * 3)
                    continue
                return None
        
        return None
    
    def _extract_team_info(self, team_row) -> Optional[Dict[str, Any]]:
        """Извлечь информацию о команде из строки таблицы"""
        try:
            team_info = {
                'rank': None,
                'name': '',
                'points': None,
                'hltv_url': '',
                'hltv_id': None,
                'player_urls': []
            }
            
            # Место в рейтинге
            rank_elem = team_row.find('span', class_='position')
            if rank_elem:
                try:
                    team_info['rank'] = int(rank_elem.text.strip().replace('#', ''))
                except:
                    pass
            
            # Название команды и ссылка
            team_link = team_row.find('a', class_='teamName')
            if team_link:
                team_info['name'] = team_link.text.strip()
                team_info['hltv_url'] = self.BASE_URL + team_link.get('href', '')
                
                # Извлекаем ID команды из URL
                href = team_link.get('href', '')
                id_match = re.search(r'/team/(\d+)/', href)
                if id_match:
                    team_info['hltv_id'] = int(id_match.group(1))
            
            # Очки команды
            points_elem = team_row.find('span', class_='points')
            if points_elem:
                try:
                    points_text = points_elem.text.strip().replace('(', '').replace(')', '').replace(' points', '')
                    team_info['points'] = int(points_text)
                except:
                    pass
            
            # Ссылки на игроков
            player_links = team_row.find_all('a', href=re.compile(r'/player/'))
            for player_link in player_links:
                player_url = self.BASE_URL + player_link.get('href', '')
                team_info['player_urls'].append(player_url)
            
            logger.info(f"Извлечена информация о команде: {team_info['name']} (#{team_info['rank']})")
            return team_info
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении информации о команде: {e}")
            return None
    
    def _extract_player_id_and_nickname(self, player_url: str) -> Optional[Tuple[int, str]]:
        """Извлечь ID и никнейм игрока из URL"""
        try:
            # URL формата: https://www.hltv.org/player/20425/r1nkle
            match = re.search(r'/player/(\d+)/([^/]+)', player_url)
            if match:
                player_id = int(match.group(1))
                nickname = match.group(2)
                return player_id, nickname
            return None
        except Exception as e:
            logger.error(f"Ошибка при извлечении ID игрока из URL {player_url}: {e}")
            return None
    
    def parse_team_ranking(self, max_teams: int = 30) -> List[Dict[str, Any]]:
        """Парсить рейтинг команд"""
        logger.info(f"Начинаем парсинг рейтинга команд (топ {max_teams})")
        
        # Загружаем страницу рейтинга
        soup = self._fetch_ranking_page()
        if not soup:
            logger.error("Не удалось загрузить страницу рейтинга команд")
            return []
        
        teams = []
        
        # Ищем строки с командами
        team_rows = soup.find_all('div', class_='ranked-team')
        if not team_rows:
            # Альтернативный поиск
            team_rows = soup.find_all('tr', class_=re.compile(r'team-row|ranking-row'))
        
        if not team_rows:
            logger.warning("Не найдены строки с командами, попробуем другой селектор")
            # Еще один альтернативный поиск
            ranking_table = soup.find('table', class_='ranking-table')
            if ranking_table:
                team_rows = ranking_table.find_all('tr')[1:]  # Пропускаем заголовок
        
        logger.info(f"Найдено строк с командами: {len(team_rows)}")
        
        for i, team_row in enumerate(team_rows[:max_teams]):
            try:
                logger.info(f"Обрабатываем команду {i + 1} из {min(len(team_rows), max_teams)}")
                
                team_info = self._extract_team_info(team_row)
                if not team_info or not team_info['name']:
                    continue
                
                # Парсим игроков команды
                team_info['players'] = []
                for player_url in team_info['player_urls']:
                    player_data = self._extract_player_id_and_nickname(player_url)
                    if player_data:
                        player_id, nickname = player_data
                        
                        # Создаем парсер игроков, если еще не создан
                        if not self.player_parser:
                            self.player_parser = PlayerParser()
                        
                        # Парсим информацию об игроке
                        logger.info(f"Парсим игрока: {nickname} (ID: {player_id})")
                        player_info = self.player_parser.parse_player(player_id, nickname)
                        
                        if player_info:
                            team_info['players'].append(player_info)
                            # Сохраняем игрока в базу данных
                            self.player_parser.save_player_to_database(player_info)
                        
                        # Пауза между парсингом игроков
                        time.sleep(2)
                
                teams.append(team_info)
                logger.info(f"Команда {team_info['name']} обработана успешно")
                
                # Пауза между обработкой команд
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка при обработке команды {i + 1}: {e}")
                continue
        
        logger.info(f"Парсинг рейтинга команд завершен. Обработано команд: {len(teams)}")
        return teams
    
    def save_team_to_database(self, team_data: Dict[str, Any]) -> bool:
        """Сохранить данные команды в базу данных"""
        try:
            # Проверяем существующую команду
            existing_team = self.db.query(Team).filter(
                Team.hltv_id == team_data['hltv_id']
            ).first()
            
            if existing_team:
                # Обновляем существующую команду
                existing_team.name = team_data['name']
                existing_team.current_rank = team_data['rank']
                existing_team.points = team_data['points']
                existing_team.hltv_url = team_data['hltv_url']
                existing_team.last_updated = datetime.now()
                
                team = existing_team
                logger.info(f"Обновлена команда: {team_data['name']}")
                
            else:
                # Создаем новую команду
                team = Team(
                    hltv_id=team_data['hltv_id'],
                    name=team_data['name'],
                    current_rank=team_data['rank'],
                    points=team_data['points'],
                    hltv_url=team_data['hltv_url'],
                    country_code='',  # Заполнится из информации игроков
                    country_name='',
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    is_active=True
                )
                
                self.db.add(team)
                logger.info(f"Создана новая команда: {team_data['name']}")
            
            self.db.commit()
            self.db.refresh(team)
            
            # Сохраняем состав команды
            if team_data.get('players'):
                self._save_team_roster(team.id, team_data['players'])
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении команды {team_data.get('name', 'Unknown')}: {e}")
            self.db.rollback()
            return False
    
    def _save_team_roster(self, team_id: int, players: List[Dict[str, Any]]) -> bool:
        """Сохранить состав команды"""
        try:
            # Удаляем старый состав
            self.db.query(TeamRoster).filter(TeamRoster.team_id == team_id).delete()
            
            # Добавляем новый состав
            for player_data in players:
                player = self.db.query(Player).filter(
                    Player.hltv_id == player_data['hltv_id']
                ).first()
                
                if player:
                    roster_entry = TeamRoster(
                        team_id=team_id,
                        player_id=player.id,
                        role='Player',  # Базовая роль
                        joined_at=datetime.now(),
                        is_active=True
                    )
                    
                    self.db.add(roster_entry)
            
            self.db.commit()
            logger.info(f"Сохранен состав команды ID {team_id}: {len(players)} игроков")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении состава команды ID {team_id}: {e}")
            self.db.rollback()
            return False
    
    def save_all_teams_to_database(self, teams: List[Dict[str, Any]]) -> int:
        """Сохранить все команды в базу данных"""
        saved_count = 0
        
        for team_data in teams:
            if self.save_team_to_database(team_data):
                saved_count += 1
        
        logger.info(f"Сохранено команд в базу данных: {saved_count} из {len(teams)}")
        return saved_count
    
    def close(self):
        """Закрыть соединения"""
        if self.driver:
            self.driver.quit()
        if self.player_parser:
            self.player_parser.close()
        if self.db:
            self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 