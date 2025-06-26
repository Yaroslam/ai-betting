"""
HLTV Player Profile Parser
Парсер профилей игроков с HLTV.org
"""

import re
import time
import logging
from typing import Dict, Optional, Any
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import geckodriver_autoinstaller
from bs4 import BeautifulSoup
from datetime import datetime, date

from database import SessionLocal, Player, PlayerStatistics

logger = logging.getLogger(__name__)


class PlayerParser:
    """Парсер профилей игроков с HLTV.org"""
    
    BASE_URL = "https://www.hltv.org"
    
    def __init__(self):
        self.driver = None
        self.db = SessionLocal()
        self._init_driver()
    
    def _init_driver(self):
        """Инициализация headless Firefox драйвера с обходом защиты от ботов"""
        try:
            logger.info("Инициализируем stealth Firefox для парсера игроков...")
            
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
            
            logger.info("Stealth Firefox для парсера игроков инициализирован успешно")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Firefox драйвера: {e}")
            raise
    
    def _fetch_player_page(self, player_id: int, nickname: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Загрузить страницу профиля игрока с имитацией человеческого поведения"""
        url = f"{self.BASE_URL}/stats/players/{player_id}/{nickname}"
        
        for attempt in range(retries):
            try:
                logger.info(f"Загружаем профиль игрока (попытка {attempt + 1}): {url}")
                
                if attempt > 0:
                    delay = 10 + attempt * 5
                    logger.info(f"Ждем {delay} секунд перед повторной попыткой...")
                    time.sleep(delay)
                
                # Загружаем страницу игрока
                logger.info(f"Загружаем страницу игрока: {url}")
                self.driver.get(url)
                
                # Ждем загрузки
                time.sleep(5 + attempt * 2)
                
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
                        block_delay = 30 + attempt * 15
                        logger.info(f"Ждем {block_delay} секунд из-за блокировки...")
                        time.sleep(block_delay)
                        continue
                    else:
                        return None
                
                # Получаем HTML
                html = self.driver.page_source
                logger.info(f"Страница игрока загружена успешно, размер: {len(html)} символов")
                
                # Проверяем качество полученных данных
                if len(html) < 1000:
                    logger.warning("Получена подозрительно короткая страница")
                    if attempt < retries - 1:
                        continue
                
                # Проверяем наличие ключевых элементов HLTV
                if "hltv" not in html.lower() or "player" not in html.lower():
                    logger.warning("Страница не содержит ожидаемый контент HLTV")
                    if attempt < retries - 1:
                        continue
                
                return BeautifulSoup(html, 'html.parser')
                
            except Exception as e:
                logger.error(f"Ошибка при загрузке профиля игрока {url} (попытка {attempt + 1}): {e}")
                if attempt < retries - 1:
                    error_delay = 15 + attempt * 5
                    logger.info(f"Ждем {error_delay} секунд после ошибки...")
                    time.sleep(error_delay)
                    continue
                return None
        
        return None
    
    def _extract_basic_info(self, soup: BeautifulSoup, player_id: int) -> Dict[str, Any]:
        """Извлечь базовую информацию об игроке"""
        player_info = {
            'hltv_id': player_id,
            'nickname': '',
            'real_name': '',
            'country_code': '',
            'country_name': '',
            'age': None,
            'hltv_url': f"{self.BASE_URL}/stats/players/{player_id}"
        }
        
        try:
            # Никнейм игрока
            nickname_elem = soup.find('h1', class_='summaryNickname')
            if nickname_elem:
                player_info['nickname'] = nickname_elem.text.strip()
            
            # Настоящее имя
            real_name_elem = soup.find('div', class_='summaryRealname')
            if real_name_elem:
                player_info['real_name'] = real_name_elem.text.strip()
            
            # Извлечение страны и возраста оказалось ненадежным из-за динамической загрузки,
            # поэтому эти поля могут оставаться пустыми.

            logger.info(f"Базовая информация извлечена: {player_info['nickname']} ({player_info['real_name']})")
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении базовой информации: {e}")
        
        return player_info
    
    def _extract_statistics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Извлечь игровую статистику игрока"""
        stats = {
            'rating_2_0': None,
            'impact': None,
            'adr': None,
            'kd_ratio': None,
            'kast': None,
            'dpr': None,
            'kpr': None,
            'maps_played': 0
        }
        
        try:
            # Новый подход: ищем все ряды статистики по классу 'stats-row'
            stat_rows = soup.find_all('div', class_='stats-row')
            for row in stat_rows:
                children = row.find_all('span')
                if len(children) == 2:
                    stat_name = children[0].text.strip().lower()
                    stat_value = children[1].text.strip()

                    try:
                        if 'rating' in stat_name:
                            stats['rating_2_0'] = float(stat_value)
                        elif 'k/d ratio' in stat_name:
                            stats['kd_ratio'] = float(stat_value)
                        elif 'damage / round' in stat_name:
                            stats['adr'] = float(stat_value)
                        elif 'deaths / round' in stat_name:
                            stats['dpr'] = float(stat_value)
                        elif 'kills / round' in stat_name:
                            stats['kpr'] = float(stat_value)
                        elif 'maps played' in stat_name:
                            stats['maps_played'] = int(stat_value)
                    except (ValueError, IndexError):
                        logger.warning(f"Не удалось обработать значение '{stat_value}' для '{stat_name}'")
                        continue

            # Старый подход для KAST и Impact, которые могут быть в другом блоке
            stat_breakdown = soup.find_all('div', class_='summaryStatBreakdownRow')
            for row in stat_breakdown:
                data_name_div = row.find('div', class_='summaryStatBreakdownDataPoint')
                data_value_div = row.find('div', class_='summaryStatBreakdownDataValue')

                if data_name_div and data_value_div:
                    stat_name = data_name_div.text.strip().lower()
                    stat_value = data_value_div.text.strip()
                    
                    try:
                        if 'impact' in stat_name:
                            stats['impact'] = float(stat_value)
                        elif 'kast' in stat_name:
                            stats['kast'] = float(stat_value.replace('%', ''))
                    except (ValueError, IndexError):
                        logger.warning(f"Не удалось обработать значение (breakdown) '{stat_value}' для '{stat_name}'")
                        continue

            # Логируем найденную статистику
            found_stats = {k: v for k, v in stats.items() if v is not None and v != 0}
            logger.info(f"Извлеченная статистика: {found_stats}")
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении статистики: {e}")
        
        return stats
    
    def parse_player(self, player_id: int, nickname: str) -> Optional[Dict[str, Any]]:
        """Парсить профиль игрока по ID и никнейму"""
        logger.info(f"Начинаем парсинг игрока: {nickname} (ID: {player_id})")
        
        # Загружаем страницу
        soup = self._fetch_player_page(player_id, nickname)
        if not soup:
            logger.error(f"Не удалось загрузить страницу игрока {nickname}")
            return None
        
        # Извлекаем базовую информацию
        player_info = self._extract_basic_info(soup, player_id)
        
        # Извлекаем статистику
        stats = self._extract_statistics(soup)
        
        # Объединяем данные
        result = {
            **player_info,
            'statistics': stats
        }
        
        logger.info(f"Парсинг игрока {nickname} завершен успешно")
        return result
    
    def save_player_to_database(self, player_data: Dict[str, Any]) -> bool:
        """Сохранить данные игрока в базу данных"""
        try:
            # Проверяем существующего игрока
            existing_player = self.db.query(Player).filter(
                Player.hltv_id == player_data['hltv_id']
            ).first()
            
            if existing_player:
                # Обновляем существующего игрока
                existing_player.nickname = player_data['nickname']
                existing_player.real_name = player_data['real_name']
                existing_player.country_code = player_data['country_code']
                existing_player.country_name = player_data['country_name']
                existing_player.age = player_data['age']
                existing_player.hltv_url = player_data['hltv_url']
                existing_player.is_active = True
                
                player = existing_player
                logger.info(f"Обновлен игрок: {player_data['nickname']}")
                
            else:
                # Создаем нового игрока
                player = Player(
                    hltv_id=player_data['hltv_id'],
                    nickname=player_data['nickname'],
                    real_name=player_data['real_name'],
                    country_code=player_data['country_code'],
                    country_name=player_data['country_name'],
                    age=player_data['age'],
                    hltv_url=player_data['hltv_url'],
                    is_active=True
                )
                
                self.db.add(player)
                logger.info(f"Создан новый игрок: {player_data['nickname']}")
            
            self.db.commit()
            self.db.refresh(player)
            
            # Сохраняем статистику
            if player_data.get('statistics'):
                self._save_player_statistics(player.id, player_data['statistics'])
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении игрока {player_data.get('nickname', 'Unknown')}: {e}")
            self.db.rollback()
            return False
    
    def _save_player_statistics(self, player_id: int, stats: Dict[str, Any]) -> bool:
        """Сохранить статистику игрока"""
        try:
            # Текущий период (последний месяц)
            today = date.today()
            period_start = today.replace(day=1)
            
            # Ищем существующую статистику за текущий период
            existing_stats = self.db.query(PlayerStatistics).filter(
                PlayerStatistics.player_id == player_id,
                PlayerStatistics.period_start == period_start
            ).first()
            
            if existing_stats:
                # Обновляем существующую статистику
                existing_stats.rating_2_0 = stats.get('rating_2_0')
                existing_stats.kd_ratio = stats.get('kd_ratio')
                existing_stats.adr = stats.get('adr')
                existing_stats.kast = stats.get('kast')
                existing_stats.kills_per_round = stats.get('kpr')
                existing_stats.deaths_per_round = stats.get('dpr')
                existing_stats.maps_played = stats.get('maps_played', 0)
                existing_stats.last_updated = datetime.now()
                
                logger.info(f"Обновлена статистика игрока ID {player_id}")
                
            else:
                # Создаем новую статистику
                new_stats = PlayerStatistics(
                    player_id=player_id,
                    rating_2_0=stats.get('rating_2_0'),
                    kd_ratio=stats.get('kd_ratio'),
                    adr=stats.get('adr'),
                    kast=stats.get('kast'),
                    kills_per_round=stats.get('kpr'),
                    deaths_per_round=stats.get('dpr'),
                    maps_played=stats.get('maps_played', 0),
                    period_start=period_start,
                    period_end=today,
                    last_updated=datetime.now()
                )
                
                self.db.add(new_stats)
                logger.info(f"Создана новая статистика игрока ID {player_id}")
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении статистики игрока ID {player_id}: {e}")
            self.db.rollback()
            return False
    
    def close(self):
        """Закрыть соединения"""
        if self.driver:
            self.driver.quit()
        if self.db:
            self.db.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 