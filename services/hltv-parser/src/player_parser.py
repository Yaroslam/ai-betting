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
        """Инициализация headless Firefox драйвера"""
        try:
            logger.info("Инициализируем headless Firefox для парсера игроков...")
            
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
            
            logger.info("Headless Firefox для парсера игроков инициализирован успешно")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Firefox драйвера: {e}")
            raise
    
    def _fetch_player_page(self, player_id: int, nickname: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Загрузить страницу профиля игрока"""
        url = f"{self.BASE_URL}/stats/players/{player_id}/{nickname}"
        
        for attempt in range(retries):
            try:
                logger.info(f"Загружаем профиль игрока (попытка {attempt + 1}): {url}")
                
                if attempt > 0:
                    time.sleep(5 + attempt * 2)
                
                # Сначала загружаем главную страницу HLTV для получения cookies
                if attempt == 0:
                    try:
                        self.driver.get(self.BASE_URL)
                        time.sleep(2)
                    except:
                        pass
                
                # Загружаем страницу игрока
                self.driver.get(url)
                
                # Ждем загрузки контента
                time.sleep(3 + attempt)
                
                # Проверяем на блокировку или ошибки
                if "Access Denied" in self.driver.title or "403" in self.driver.title or "Not Found" in self.driver.title:
                    logger.warning(f"Страница заблокирована или не найдена (попытка {attempt + 1}): {self.driver.title}")
                    if attempt < retries - 1:
                        time.sleep(10 + attempt * 5)
                        continue
                    else:
                        return None
                
                # Получаем HTML
                html = self.driver.page_source
                logger.info(f"Страница игрока загружена успешно, размер: {len(html)} символов")
                
                if len(html) < 1000:
                    logger.warning("Получена подозрительно короткая страница")
                    if attempt < retries - 1:
                        continue
                
                return BeautifulSoup(html, 'html.parser')
                
            except Exception as e:
                logger.error(f"Ошибка при загрузке профиля игрока {url} (попытка {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(8 + attempt * 3)
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
            
            # Страна
            country_elem = soup.find('img', class_='summaryCountryFlag')
            if country_elem:
                player_info['country_code'] = country_elem.get('alt', '').upper()[:3]
                player_info['country_name'] = country_elem.get('title', '')
            
            # Возраст
            age_elem = soup.find('span', class_='summaryPlayerAge')
            if age_elem:
                age_text = age_elem.text.strip()
                age_match = re.search(r'(\d+)', age_text)
                if age_match:
                    player_info['age'] = int(age_match.group(1))
            
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
            'dpr': None,  # Deaths per round
            'kpr': None,  # Kills per round
            'maps_played': 0
        }
        
        try:
            # Ищем статистику в блоке summaryStatBreakdown
            stat_blocks = soup.find_all('div', class_='summaryStatBreakdownRow')
            
            for block in stat_blocks:
                try:
                    # Ищем название статистики
                    data_name = block.find('div', class_='summaryStatBreakdownDataName')
                    data_value = block.find('div', class_='summaryStatBreakdownDataValue')
                    
                    if data_name and data_value:
                        stat_name = data_name.text.strip().lower()
                        stat_value = data_value.text.strip()
                        
                        # Rating 2.0
                        if 'rating' in stat_name:
                            try:
                                rating = float(stat_value)
                                if 0.5 <= rating <= 2.5:
                                    stats['rating_2_0'] = rating
                            except:
                                pass
                        
                        # K/D Ratio
                        elif 'k/d' in stat_name:
                            try:
                                stats['kd_ratio'] = float(stat_value)
                            except:
                                pass
                        
                        # ADR (Average Damage per Round)
                        elif 'adr' in stat_name:
                            try:
                                stats['adr'] = float(stat_value)
                            except:
                                pass
                        
                        # KAST
                        elif 'kast' in stat_name:
                            try:
                                kast_clean = stat_value.replace('%', '')
                                stats['kast'] = float(kast_clean)
                            except:
                                pass
                        
                        # Impact
                        elif 'impact' in stat_name:
                            try:
                                stats['impact'] = float(stat_value)
                            except:
                                pass
                        
                        # KPR (Kills per round)
                        elif 'kpr' in stat_name or ('kill' in stat_name and 'round' in stat_name):
                            try:
                                stats['kpr'] = float(stat_value)
                            except:
                                pass
                        
                        # DPR (Deaths per round)
                        elif 'dpr' in stat_name or ('death' in stat_name and 'round' in stat_name):
                            try:
                                stats['dpr'] = float(stat_value)
                            except:
                                pass
                        
                        # Maps played
                        elif 'maps' in stat_name:
                            try:
                                stats['maps_played'] = int(stat_value)
                            except:
                                pass
                        
                except Exception as e:
                    continue
            
            # Альтернативный поиск для статистики в других блоках
            if not stats['rating_2_0']:
                # Ищем Rating 2.0 в других местах
                rating_elems = soup.find_all(text=re.compile(r'\d+\.\d{2}'))
                for rating_elem in rating_elems:
                    try:
                        parent = rating_elem.parent
                        if parent and ('rating' in parent.get('class', []) or 'rating' in str(parent).lower()):
                            rating = float(rating_elem.strip())
                            if 0.5 <= rating <= 2.5:
                                stats['rating_2_0'] = rating
                                break
                    except:
                        continue
            
            # Поиск в таблицах статистики
            tables = soup.find_all('table')
            for table in tables:
                if 'stats' in str(table.get('class', [])).lower():
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            header = cells[0].text.strip().lower()
                            value = cells[1].text.strip()
                            
                            try:
                                if 'rating' in header and '2.0' in header:
                                    rating = float(value)
                                    if 0.5 <= rating <= 2.5:
                                        stats['rating_2_0'] = rating
                                elif 'k/d' in header:
                                    stats['kd_ratio'] = float(value)
                                elif 'adr' in header:
                                    stats['adr'] = float(value)
                                elif 'kast' in header:
                                    kast_clean = value.replace('%', '')
                                    stats['kast'] = float(kast_clean)
                                elif 'impact' in header:
                                    stats['impact'] = float(value)
                                elif 'kpr' in header:
                                    stats['kpr'] = float(value)
                                elif 'dpr' in header:
                                    stats['dpr'] = float(value)
                            except:
                                pass
            
            # Поиск статистики в основной области страницы
            stat_containers = soup.find_all('div', class_=re.compile(r'stats|statistic'))
            for container in stat_containers:
                text_content = container.get_text().lower()
                
                # Ищем rating 2.0
                if 'rating' in text_content and not stats['rating_2_0']:
                    rating_match = re.search(r'rating.*?(\d+\.\d{2})', text_content)
                    if rating_match:
                        try:
                            rating = float(rating_match.group(1))
                            if 0.5 <= rating <= 2.5:
                                stats['rating_2_0'] = rating
                        except:
                            pass
            
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