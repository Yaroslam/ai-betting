"""
HLTV Parser - Версия с Selenium headless браузером
"""

import time
import re
import logging
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import geckodriver_autoinstaller
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HLTVParserSelenium:
    """Парсер для HLTV.org с использованием Selenium headless браузера"""
    
    BASE_URL = "https://www.hltv.org"
    
    def __init__(self):
        self.driver = None
        self._init_driver()
    
    def _init_driver(self):
        """Инициализация headless Firefox драйвера"""
        try:
            logger.info("Инициализируем headless Firefox драйвер...")
            
            # Автоматически устанавливаем geckodriver
            geckodriver_autoinstaller.install()
            
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--window-size=1920,1080")
            
            # Настраиваем профиль Firefox
            firefox_profile = webdriver.FirefoxProfile()
            
            # Реалистичный User-Agent
            firefox_profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")
            
            # Отключаем изображения для ускорения
            firefox_profile.set_preference("permissions.default.image", 2)
            
            # Включаем JavaScript для получения статистики (может потребоваться для динамического контента)
            firefox_profile.set_preference("javascript.enabled", True)
            
            # Настройки для обхода детекции
            firefox_profile.set_preference("dom.webdriver.enabled", False)
            firefox_profile.set_preference("useAutomationExtension", False)
            
            # В новых версиях Selenium профиль передается через опции
            firefox_options.profile = firefox_profile
            
            self.driver = webdriver.Firefox(
                options=firefox_options
            )
            
            logger.info("Headless Firefox драйвер инициализирован успешно")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Firefox драйвера: {e}")
            raise
    
    def _fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Получить страницу через Selenium и распарсить её"""
        for attempt in range(retries):
            try:
                logger.info(f"Загружаем страницу через Selenium (попытка {attempt + 1}): {url}")
                
                # Задержка между попытками
                if attempt > 0:
                    time.sleep(5 + attempt * 2)
                
                # Загружаем страницу
                self.driver.get(url)
                
                # Ждем загрузки страницы и динамического контента
                time.sleep(5 + attempt * 2)
                
                # Проверяем, что страница загрузилась
                if "Access Denied" in self.driver.title or "403" in self.driver.title:
                    logger.warning(f"Страница заблокирована (попытка {attempt + 1}): {self.driver.title}")
                    if attempt < retries - 1:
                        logger.info("Пытаемся обойти блокировку...")
                        time.sleep(10 + attempt * 5)
                        continue
                    else:
                        logger.error("Сайт блокирует запросы даже через браузер")
                        return None
                
                # Получаем HTML
                html = self.driver.page_source
                logger.info(f"Страница загружена успешно, размер: {len(html)} символов")
                
                # Проверяем, что это не страница ошибки
                if len(html) < 1000:
                    logger.warning("Получена подозрительно короткая страница")
                    if attempt < retries - 1:
                        continue
                
                return BeautifulSoup(html, 'html.parser')
                
            except Exception as e:
                logger.error(f"Ошибка при загрузке {url} (попытка {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(5 + attempt * 2)
                    continue
                return None
        
        return None
    
    def find_team_by_name(self, team_name: str) -> Optional[int]:
        """Найти ID команды по названию"""
        # Используем известные ID команд
        known_teams = {
            'vitality': 9565,  # Правильный ID для Team Vitality
            'navi': 4608,
            'faze': 6667,
            'g2': 5995,
            'liquid': 5973,
            'astralis': 6665,
            'fnatic': 4991,
            'mouz': 4494,
            'big': 7532,
            'heroic': 7175,
        }
        
        if team_name.lower() in known_teams:
            logger.info(f"Используем известный ID для команды {team_name}: {known_teams[team_name.lower()]}")
            return known_teams[team_name.lower()]
        
        logger.error(f"Команда {team_name} не найдена в базе известных команд")
        return None
    
    def get_team_info(self, team_identifier) -> Optional[Dict[str, Any]]:
        """Получить полную информацию о команде по ID или названию"""
        try:
            # Определяем, передан ID или название команды
            if isinstance(team_identifier, int):
                team_id = team_identifier
                team_name = "team"  # Используем общее название для URL
            else:
                # Найдем ID команды по названию
                team_id = self.find_team_by_name(team_identifier)
                if not team_id:
                    logger.error(f"Команда {team_identifier} не найдена")
                    return None
                team_name = team_identifier
            
            logger.info(f"Получаем информацию о команде с ID: {team_id}")
            
            # Получаем страницу команды
            team_url = f"{self.BASE_URL}/team/{team_id}/"
            soup = self._fetch_page(team_url)
            
            if not soup:
                return None
            
            # Парсим основную информацию
            roster = self._parse_team_roster(soup, team_id)
            team_info = {
                'team_id': team_id,
                'name': self._parse_team_name(soup),
                'country': self._parse_team_country(soup),
                'ranking': self._parse_team_ranking_from_page(soup),
                'roster': roster,
                'player_count': len(roster),
            }
            
            return team_info
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о команде: {e}")
            return None
    
    def get_team_roster(self, team_id: int) -> List[Dict[str, Any]]:
        """Получить состав команды"""
        try:
            logger.info(f"Получаем состав команды с ID: {team_id}")
            
            # Получаем страницу команды
            team_url = f"{self.BASE_URL}/team/{team_id}/"
            soup = self._fetch_page(team_url)
            
            if not soup:
                return []
            
            return self._parse_team_roster(soup, team_id)
            
        except Exception as e:
            logger.error(f"Ошибка при получении состава команды {team_id}: {e}")
            return []
    
    def _parse_team_name(self, soup: BeautifulSoup) -> str:
        """Парсинг названия команды"""
        try:
            # Пробуем несколько вариантов селекторов
            selectors = [
                'h1.profile-team-name',
                '.profile-team-name',
                'h1',
                '.team-name',
                '[class*="team-name"]',
                '[class*="profile-team"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    name = element.get_text().strip()
                    if name and name != "HLTV.org" and len(name) < 50:
                        logger.info(f"Найдено название команды: {name}")
                        return name
            
            # Пробуем из title
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                match = re.search(r'(.+?) - HLTV', title_text)
                if match:
                    name = match.group(1).strip()
                    logger.info(f"Название команды из title: {name}")
                    return name
            
            logger.warning("Не удалось найти название команды")
            return "Unknown Team"
        except Exception as e:
            logger.error(f"Ошибка при парсинге названия команды: {e}")
            return "Unknown Team"
    
    def _parse_team_country(self, soup: BeautifulSoup) -> str:
        """Парсинг страны команды"""
        try:
            # Ищем флаг
            flag_selectors = [
                'img.flag',
                'img[class*="flag"]',
                'img[alt*="flag"]'
            ]
            
            for selector in flag_selectors:
                flag_elements = soup.select(selector)
                for flag_element in flag_elements:
                    alt_text = flag_element.get('alt', '')
                    if alt_text and alt_text != "flag":
                        logger.info(f"Найдена страна команды: {alt_text}")
                        return alt_text
            
            logger.warning("Не удалось найти страну команды")
            return "Unknown"
        except Exception as e:
            logger.error(f"Ошибка при парсинге страны команды: {e}")
            return "Unknown"
    
    def _parse_team_ranking_from_page(self, soup: BeautifulSoup) -> Optional[int]:
        """Парсинг рейтинга команды со страницы команды"""
        try:
            # Ищем элементы с рейтингом
            ranking_selectors = [
                '.profile-team-stat .right',
                '.team-ranking',
                '.ranking-header .right',
                '[class*="ranking"]',
                '[class*="rank"]'
            ]
            
            for selector in ranking_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    # Ищем паттерн #число
                    match = re.search(r'#(\d+)', text)
                    if match:
                        ranking = int(match.group(1))
                        logger.info(f"Найден рейтинг команды: #{ranking}")
                        return ranking
            
            logger.warning("Не удалось найти рейтинг команды")
            return None
        except Exception as e:
            logger.error(f"Ошибка при парсинге рейтинга команды: {e}")
            return None
    
    def _parse_team_roster(self, soup: BeautifulSoup, team_id: int) -> List[Dict[str, Any]]:
        """Парсинг состава команды"""
        try:
            roster = []
            
            # Ищем различные селекторы для состава
            roster_selectors = [
                '.bodyshot-team a[href*="/player/"]',
                '.lineup-con a[href*="/player/"]',
                '.player-nick a[href*="/player/"]',
                'a[href*="/player/"]'
            ]
            
            found_players = set()  # Для избежания дубликатов
            
            for selector in roster_selectors:
                player_links = soup.select(selector)
                
                for link in player_links:
                    href = link.get('href')
                    if href and '/player/' in href:
                        player_id_match = re.search(r'/player/(\d+)/', href)
                        
                        if player_id_match:
                            player_id = int(player_id_match.group(1))
                            
                            # Избегаем дубликатов
                            if player_id in found_players:
                                continue
                            found_players.add(player_id)
                            
                            # Получаем никнейм игрока
                            nickname = link.get_text().strip()
                            if not nickname:
                                # Пробуем найти в дочерних элементах
                                for child in link.find_all(['span', 'div']):
                                    child_text = child.get_text().strip()
                                    if child_text and len(child_text) < 20:
                                        nickname = child_text
                                        break
                            
                            if nickname and nickname != "Unknown" and len(nickname) < 20:
                                roster.append({
                                    'player_id': player_id,
                                    'nickname': nickname,
                                    'team_id': team_id
                                })
                                logger.info(f"Найден игрок: {nickname} (ID: {player_id})")
                
                if len(roster) >= 5:  # Обычно в команде 5 игроков
                    break
            
            logger.info(f"Найдено игроков в составе: {len(roster)}")
            return roster
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге состава команды: {e}")
            return []
    
    def get_player_stats(self, player_id: int, player_nickname: str = None) -> Optional[Dict[str, Any]]:
        """Получить статистику игрока"""
        try:
            # Используем URL для статистики игрока
            if player_nickname:
                player_url = f"{self.BASE_URL}/stats/players/{player_id}/{player_nickname}"
            else:
                player_url = f"{self.BASE_URL}/stats/players/{player_id}/"
            soup = self._fetch_page(player_url)
            
            if not soup:
                return None
            
            # Парсим основную информацию игрока
            player_info = self._parse_player_basic_info(soup, player_id)
            
            # Парсим статистику
            stats = self._parse_player_statistics(soup)
            
            return {
                **player_info,
                **stats
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики игрока {player_id}: {e}")
            return None
    
    def _parse_player_basic_info(self, soup: BeautifulSoup, player_id: int) -> Dict[str, Any]:
        """Парсинг основной информации игрока"""
        try:
            info = {'player_id': player_id}
            
            # Никнейм - на странице статистики может быть в разных местах
            nickname_selectors = [
                'h1.summaryNickname',
                '.summaryNickname', 
                '.playerNickname',
                '.player-name h1',
                'h1',
                '.stats-top-player h1'
            ]
            
            for selector in nickname_selectors:
                element = soup.select_one(selector)
                if element:
                    nickname = element.get_text().strip()
                    if nickname and len(nickname) < 30 and nickname != "HLTV.org":
                        info['nickname'] = nickname
                        logger.info(f"Найден никнейм игрока: {nickname}")
                        break
            
            # Настоящее имя
            realname_selectors = [
                '.summaryRealname',
                '.playerRealname',
                '.player-realname',
                '.real-name',
                '[class*="realname"]'
            ]
            
            for selector in realname_selectors:
                element = soup.select_one(selector)
                if element:
                    realname = element.get_text().strip()
                    if realname and len(realname) < 50:
                        info['real_name'] = realname
                        logger.info(f"Найдено настоящее имя: {realname}")
                        break
            
            # Страна
            flag_selectors = [
                'img.flag',
                'img[class*="flag"]',
                '.player-country img'
            ]
            
            for selector in flag_selectors:
                flag_element = soup.select_one(selector)
                if flag_element:
                    country = flag_element.get('alt', '').strip()
                    if country and country != 'flag':
                        info['country'] = country
                        logger.info(f"Найдена страна игрока: {info['country']}")
                        break
            
            # Возраст
            age_selectors = [
                '.summaryPlayerAge',
                '.player-age',
                '.age'
            ]
            
            for selector in age_selectors:
                element = soup.select_one(selector)
                if element:
                    age_text = element.get_text().strip()
                    import re
                    age_match = re.search(r'(\d+)', age_text)
                    if age_match:
                        info['age'] = int(age_match.group(1))
                        logger.info(f"Найден возраст игрока: {info['age']}")
                        break
            
            return info
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге основной информации игрока: {e}")
            return {'player_id': player_id}
    
    def _parse_player_statistics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Парсинг статистики игрока со страницы /stats/players/"""
        try:
            stats = {}
            import re
            
            logger.info("Начинаем поиск статистики игрока на странице статистики...")
            
            # Специфичные селекторы для страницы статистики HLTV
            stat_selectors = [
                '.summaryStatBreakdownRow',
                '.summaryStatBreakdown', 
                '.stats-row',
                '.statistic',
                '.standard-box',
                '.large-strong',
                '.playerSummaryStatBox',
                '.summary-stat',
                '.stats-table tr',
                '.player-stat'
            ]
            
            # Ищем основные статистические блоки
            for selector in stat_selectors:
                elements = soup.select(selector)
                logger.info(f"Найдено элементов для селектора '{selector}': {len(elements)}")
                
                for element in elements:
                    element_text = element.get_text().strip()
                    if len(element_text) > 3:  # Игнорируем слишком короткие элементы
                        logger.info(f"Анализируем элемент: {element_text[:150]}...")
                        
                        # Ищем числовые значения в тексте
                        numbers = re.findall(r'\d+\.?\d*', element_text)
                        
                        # Рейтинг 2.0
                        if 'rating' in element_text.lower() and '2.0' in element_text:
                            for num in numbers:
                                try:
                                    val = float(num)
                                    if 0.5 <= val <= 2.5:  # Разумные границы для рейтинга
                                        stats['rating_2_0'] = val
                                        logger.info(f"✅ Найден рейтинг 2.0: {val}")
                                        break
                                except ValueError:
                                    continue
                        
                        # K/D соотношение
                        elif ('k/d' in element_text.lower() or 'kd' in element_text.lower()) and 'rating' not in element_text.lower():
                            for num in numbers:
                                try:
                                    val = float(num)
                                    if 0.1 <= val <= 5.0:  # Разумные границы для K/D
                                        stats['kd_ratio'] = val
                                        logger.info(f"✅ Найден K/D: {val}")
                                        break
                                except ValueError:
                                    continue
                        
                        # ADR
                        elif 'adr' in element_text.lower():
                            for num in numbers:
                                try:
                                    val = float(num)
                                    if 30 <= val <= 150:  # Разумные границы для ADR
                                        stats['adr'] = val
                                        logger.info(f"✅ Найден ADR: {val}")
                                        break
                                except ValueError:
                                    continue
                        
                        # KAST
                        elif 'kast' in element_text.lower():
                            for num in numbers:
                                try:
                                    val = float(num)
                                    if 40 <= val <= 100:  # KAST в процентах
                                        stats['kast'] = val
                                        logger.info(f"✅ Найден KAST: {val}%")
                                        break
                                except ValueError:
                                    continue
                        
                        # Процент хедшотов
                        elif 'hs%' in element_text.lower() or ('headshot' in element_text.lower() and '%' in element_text):
                            for num in numbers:
                                try:
                                    val = float(num)
                                    if 10 <= val <= 80:  # Разумные границы для HS%
                                        stats['headshot_percentage'] = val
                                        logger.info(f"✅ Найден процент хедшотов: {val}%")
                                        break
                                except ValueError:
                                    continue
                        
                        # Карты сыграно
                        elif 'maps' in element_text.lower() and 'played' in element_text.lower():
                            for num in numbers:
                                try:
                                    val = int(float(num))
                                    if val > 0:
                                        stats['maps_played'] = val
                                        logger.info(f"✅ Найдено карт сыграно: {val}")
                                        break
                                except ValueError:
                                    continue
            
            # Дополнительный поиск в таблицах со статистикой
            tables = soup.find_all('table')
            logger.info(f"Найдено таблиц для анализа: {len(tables)}")
            
            for i, table in enumerate(tables):
                table_text = table.get_text().lower()
                
                # Проверяем, содержит ли таблица статистику
                if any(keyword in table_text for keyword in ['rating', 'k/d', 'adr', 'kast', 'hs%']):
                    logger.info(f"Анализируем таблицу {i+1} со статистикой...")
                    
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        row_text = ' '.join([cell.get_text().strip() for cell in cells])
                        
                        if len(cells) >= 2:
                            # Ищем паттерны в строке таблицы
                            numbers = re.findall(r'\d+\.?\d*', row_text)
                            row_lower = row_text.lower()
                            
                            if 'rating' in row_lower and '2.0' in row_lower and numbers:
                                try:
                                    val = float(numbers[0])
                                    if 0.5 <= val <= 2.5:
                                        stats['rating_2_0'] = val
                                        logger.info(f"✅ Из таблицы найден рейтинг 2.0: {val}")
                                except (ValueError, IndexError):
                                    pass
                            
                            elif 'k/d' in row_lower and 'rating' not in row_lower and numbers:
                                try:
                                    val = float(numbers[0])
                                    if 0.1 <= val <= 5.0:
                                        stats['kd_ratio'] = val
                                        logger.info(f"✅ Из таблицы найден K/D: {val}")
                                except (ValueError, IndexError):
                                    pass
                            
                            elif 'adr' in row_lower and numbers:
                                try:
                                    val = float(numbers[0])
                                    if 30 <= val <= 150:
                                        stats['adr'] = val
                                        logger.info(f"✅ Из таблицы найден ADR: {val}")
                                except (ValueError, IndexError):
                                    pass
            
            logger.info(f"🎯 Итого найдено статистических показателей: {len(stats)}")
            for key, value in stats.items():
                logger.info(f"   {key}: {value}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге статистики игрока: {e}")
            return {}
    
    def close(self):
        """Закрыть браузер"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Браузер закрыт")
            except Exception as e:
                logger.error(f"Ошибка при закрытии браузера: {e}")
    
    def __del__(self):
        """Деструктор - автоматически закрываем браузер"""
        self.close() 