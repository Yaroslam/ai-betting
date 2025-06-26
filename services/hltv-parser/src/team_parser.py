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
        """Инициализация headless Firefox драйвера с обходом защиты от ботов"""
        try:
            logger.info("Инициализируем stealth Firefox для парсера команд...")
            
            # Автоматически устанавливаем geckodriver
            geckodriver_autoinstaller.install()
            
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--window-size=1920,1080")
            
            # Настраиваем профиль Firefox для обхода детекции ботов
            firefox_profile = webdriver.FirefoxProfile()
            
            # Стандартный User-Agent
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
            firefox_profile.set_preference("general.useragent.override", user_agent)
            logger.info(f"Используем User-Agent: {user_agent}")
            
            # Загружаем изображения для более реалистичного поведения
            firefox_profile.set_preference("permissions.default.image", 1)
            
            # Настройки для обхода детекции веб-драйвера
            firefox_profile.set_preference("dom.webdriver.enabled", False)
            firefox_profile.set_preference("useAutomationExtension", False)
            firefox_profile.set_preference("marionette.enabled", False)
            
            # Отключаем автоматизацию в navigator
            firefox_profile.set_preference("dom.disable_beforeunload", True)
            firefox_profile.set_preference("dom.successive_dialog_time_limit", 0)
            
            # Настройки для имитации реального браузера
            firefox_profile.set_preference("network.http.connection-retry-timeout", 0)
            firefox_profile.set_preference("network.http.connection-timeout", 90)
            firefox_profile.set_preference("network.http.response.timeout", 90)
            
            # Включаем JavaScript (нужен для HLTV)
            firefox_profile.set_preference("javascript.enabled", True)
            
            # Настройки приватности
            firefox_profile.set_preference("privacy.trackingprotection.enabled", False)
            firefox_profile.set_preference("network.cookie.cookieBehavior", 0)
            
            # Языковые настройки
            firefox_profile.set_preference("intl.accept_languages", "en-US,en;q=0.9")
            
            # Дополнительные настройки для обхода детекции
            firefox_profile.set_preference("media.peerconnection.enabled", False)
            firefox_profile.set_preference("media.navigator.enabled", False)
            firefox_profile.set_preference("webgl.disabled", True)
            firefox_profile.set_preference("media.autoplay.default", 0)
            
            # Настройки времени загрузки
            firefox_profile.set_preference("network.http.connection-timeout", 120)
            firefox_profile.set_preference("network.http.response.timeout", 120)
            
            firefox_options.profile = firefox_profile
            
            self.driver = webdriver.Firefox(options=firefox_options)
            self.driver.set_page_load_timeout(60)  # Увеличиваем таймаут
            self.driver.implicitly_wait(15)
            
            # Устанавливаем размер окна для имитации реального браузера
            self.driver.set_window_size(1920, 1080)
            
            # Выполняем JavaScript для дополнительного сокрытия автоматизации
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Stealth Firefox для парсера команд инициализирован успешно")
            
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
        """Загрузить страницу рейтинга команд с имитацией человеческого поведения"""
        year, month, day = self._get_last_monday_date()
        url = f"{self.BASE_URL}/ranking/teams/{year}/{month}/{day}"
        
        for attempt in range(retries):
            try:
                logger.info(f"Загружаем рейтинг команд (попытка {attempt + 1}): {url}")
                
                if attempt > 0:
                    delay = 15 + attempt * 10
                    logger.info(f"Ждем {delay} секунд перед повторной попыткой...")
                    time.sleep(delay)
                
                # Загружаем страницу рейтинга
                logger.info(f"Загружаем страницу рейтинга: {url}")
                self.driver.get(url)
                
                # Ждем загрузки
                loading_delay = 8 + attempt * 3
                logger.info(f"Ждем загрузки {loading_delay} секунд...")
                time.sleep(loading_delay)
                
                # Проверяем заголовок страницы
                page_title = self.driver.title
                logger.info(f"Заголовок страницы: {page_title}")
                
                # Обрабатываем Cloudflare защиту
                if "just a moment" in page_title.lower() or "checking your browser" in page_title.lower():
                    logger.info("Обнаружена защита Cloudflare, ждем прохождения проверки...")
                    
                    # Ждем до 60 секунд пока Cloudflare не пропустит
                    cloudflare_wait = 0
                    max_cloudflare_wait = 60
                    
                    while cloudflare_wait < max_cloudflare_wait:
                        time.sleep(5)
                        cloudflare_wait += 5
                        
                        current_title = self.driver.title
                        
                        # Проверяем, прошли ли мы Cloudflare
                        if "just a moment" not in current_title.lower() and "checking" not in current_title.lower():
                            logger.info(f"Cloudflare пройден! Новый заголовок: {current_title}")
                            page_title = current_title
                            break
                            
                        if cloudflare_wait % 15 == 0:
                            logger.info(f"Ждем Cloudflare... ({cloudflare_wait}/{max_cloudflare_wait}s)")
                    
                    if cloudflare_wait >= max_cloudflare_wait:
                        logger.warning("Cloudflare не пропустил за отведенное время")
                        if attempt < retries - 1:
                            time.sleep(60)
                            continue
                        else:
                            return None
                
                # Проверяем на блокировку или ошибки
                if any(keyword in page_title.lower() for keyword in ["access denied", "403", "forbidden", "blocked"]):
                    logger.warning(f"Страница заблокирована (попытка {attempt + 1}): {page_title}")
                    if attempt < retries - 1:
                        block_delay = 45 + attempt * 20
                        logger.info(f"Ждем {block_delay} секунд из-за блокировки...")
                        time.sleep(block_delay)
                        continue
                    else:
                        return None
                
                # Получаем HTML
                html = self.driver.page_source
                logger.info(f"Страница рейтинга загружена успешно, размер: {len(html)} символов")
                
                # Проверяем качество полученных данных
                if len(html) < 1000:
                    logger.warning("Получена подозрительно короткая страница")
                    if attempt < retries - 1:
                        continue
                
                # Проверяем наличие ключевых элементов HLTV
                if "hltv" not in html.lower() or "ranking" not in html.lower():
                    logger.warning("Страница не содержит ожидаемый контент рейтинга HLTV")
                    if attempt < retries - 1:
                        continue
                
                return BeautifulSoup(html, 'html.parser')
                
            except Exception as e:
                logger.error(f"Ошибка при загрузке рейтинга команд {url} (попытка {attempt + 1}): {e}")
                if attempt < retries - 1:
                    error_delay = 20 + attempt * 10
                    logger.info(f"Ждем {error_delay} секунд после ошибки...")
                    time.sleep(error_delay)
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
            
            # Получаем весь текст элемента для анализа
            row_text = team_row.get_text()
            
            # Ищем ссылку на команду (самый надежный способ)
            team_link = team_row.find('a', href=re.compile(r'/team/\d+/'))
            if not team_link:
                logger.warning(f"Не найдена ссылка на команду в элементе: {row_text[:100]}...")
                return None
            
            # Название команды и ссылка
            team_info['name'] = team_link.text.strip()
            href = team_link.get('href', '')
            team_info['hltv_url'] = self.BASE_URL + href
            
            # Извлекаем ID команды из URL
            id_match = re.search(r'/team/(\d+)/', href)
            if id_match:
                team_info['hltv_id'] = int(id_match.group(1))
            
            # Ищем рейтинг (ищем числа с # или просто числа в начале)
            rank_patterns = [
                r'#(\d+)',  # #1, #2, etc.
                r'^(\d+)\.',  # 1., 2., etc. в начале строки
                r'\b(\d+)\b'  # любое число
            ]
            
            for pattern in rank_patterns:
                rank_match = re.search(pattern, row_text)
                if rank_match:
                    try:
                        potential_rank = int(rank_match.group(1))
                        if 1 <= potential_rank <= 100:  # Разумный диапазон для рейтинга
                            team_info['rank'] = potential_rank
                            break
                    except:
                        continue
            
            # Ищем очки (числа с 'points', 'pts' или просто большие числа)
            points_patterns = [
                r'(\d+)\s*(?:points?|pts?)',
                r'\((\d+)\)',  # Числа в скобках
                r'(\d{3,})'  # Числа от 100 и больше (вероятно очки)
            ]
            
            for pattern in points_patterns:
                points_match = re.search(pattern, row_text, re.IGNORECASE)
                if points_match:
                    try:
                        potential_points = int(points_match.group(1))
                        if potential_points >= 100:  # Минимальные очки для топ команд
                            team_info['points'] = potential_points
                            break
                    except:
                        continue
            
            # Ищем ссылки на игроков
            player_links = team_row.find_all('a', href=re.compile(r'/player/\d+/'))
            for player_link in player_links:
                player_url = self.BASE_URL + player_link.get('href', '')
                team_info['player_urls'].append(player_url)
            
            # Если не нашли рейтинг, попробуем извлечь из контекста
            if team_info['rank'] is None:
                # Ищем числа в соседних элементах
                parent = team_row.parent
                if parent:
                    siblings = parent.find_all(['td', 'div', 'span'])
                    for sibling in siblings:
                        sibling_text = sibling.get_text().strip()
                        rank_match = re.search(r'^#?(\d+)$', sibling_text)
                        if rank_match:
                            try:
                                rank = int(rank_match.group(1))
                                if 1 <= rank <= 100:
                                    team_info['rank'] = rank
                                    break
                            except:
                                continue
            
            logger.info(f"Извлечена информация о команде: {team_info['name']} (#{team_info['rank']}, {team_info['points']} очков)")
            return team_info
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении информации о команде: {e}")
            import traceback
            traceback.print_exc()
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
        
        # Ищем строки с командами - используем более широкий поиск
        team_rows = []
        
        # Сначала пробуем найти любые ссылки на команды
        team_links = soup.find_all('a', href=re.compile(r'/team/\d+/'))
        logger.info(f"Найдено ссылок на команды: {len(team_links)}")
        
        if team_links:
            # Группируем ссылки по родительским элементам
            seen_teams = set()
            for link in team_links:
                team_name = link.text.strip()
                if team_name and team_name not in seen_teams:
                    # Ищем родительский элемент, который содержит всю информацию о команде
                    parent = link.parent
                    while parent and parent.name != 'body':
                        # Проверяем, содержит ли родитель рейтинг или очки
                        parent_text = parent.get_text()
                        if any(keyword in parent_text.lower() for keyword in ['#', 'points', 'pts', 'rank']):
                            team_rows.append(parent)
                            seen_teams.add(team_name)
                            break
                        parent = parent.parent
        
        # Если не нашли через ссылки, пробуем стандартные селекторы
        if not team_rows:
            team_rows = soup.find_all('div', class_='ranked-team')
        
        if not team_rows:
            team_rows = soup.find_all('tr', class_=re.compile(r'team-row|ranking-row'))
        
        if not team_rows:
            # Ищем все строки таблицы, которые могут содержать команды
            all_rows = soup.find_all('tr')
            team_rows = [row for row in all_rows if row.find('a', href=re.compile(r'/team/\d+/'))]
        
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
                        player_delay = 5
                        logger.info(f"Пауза {player_delay} секунд перед следующим игроком...")
                        time.sleep(player_delay)
                
                teams.append(team_info)
                logger.info(f"Команда {team_info['name']} обработана успешно")
                
                # Пауза между обработкой команд
                team_delay = 3
                logger.info(f"Пауза {team_delay} секунд перед следующей командой...")
                time.sleep(team_delay)
                
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