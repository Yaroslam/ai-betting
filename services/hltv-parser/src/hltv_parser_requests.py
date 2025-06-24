"""
HLTV Parser - Альтернативная версия с requests
"""

import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class HLTVParserRequests:
    """Парсер для HLTV.org с использованием requests"""
    
    BASE_URL = "https://www.hltv.org"
    
    def __init__(self):
        self.session = requests.Session()
        
        # Настраиваем сессию как настоящий браузер
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
        
        # Получаем cookies с главной страницы
        self._init_session()
    
    def _init_session(self):
        """Инициализация сессии получением cookies"""
        try:
            logger.info("Инициализируем сессию...")
            response = self.session.get(self.BASE_URL, timeout=10)
            logger.info(f"Инициализация сессии: {response.status_code}")
            if response.status_code == 200:
                logger.info("Сессия инициализирована успешно")
            else:
                logger.warning(f"Предупреждение при инициализации: {response.status_code}")
        except Exception as e:
            logger.warning(f"Ошибка инициализации сессии: {e}")
    
    def _fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Получить страницу и распарсить её"""
        for attempt in range(retries):
            try:
                logger.info(f"Загружаем страницу (попытка {attempt + 1}): {url}")
                
                # Задержка между попытками
                if attempt > 0:
                    time.sleep(5 + attempt * 2)
                
                # Добавляем рефер
                headers = {'Referer': self.BASE_URL + '/'}
                
                # Имитируем человеческое поведение
                time.sleep(1 + attempt * 0.5)
                
                response = self.session.get(url, headers=headers, timeout=15)
                logger.info(f"Получен ответ: {response.status_code} для {url}")
                
                if response.status_code == 200:
                    logger.info(f"Страница загружена успешно, размер: {len(response.text)} символов")
                    return BeautifulSoup(response.text, 'html.parser')
                elif response.status_code == 403:
                    logger.warning(f"HTTP 403 (Access Denied) для URL: {url}")
                    if attempt < retries - 1:
                        logger.info("Пытаемся обойти блокировку...")
                        time.sleep(10 + attempt * 5)
                        continue
                    else:
                        logger.error("Сайт блокирует запросы после всех попыток.")
                        return None
                elif response.status_code == 429:
                    logger.warning(f"HTTP 429 (Too Many Requests) для URL: {url}")
                    if attempt < retries - 1:
                        logger.info("Слишком много запросов, ждем...")
                        time.sleep(20 + attempt * 10)
                        continue
                    return None
                else:
                    logger.error(f"HTTP {response.status_code} для URL: {url}")
                    if attempt < retries - 1:
                        time.sleep(5)
                        continue
                    return None
                    
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
            'vitality': 9565,
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
    
    def get_team_info(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Получить полную информацию о команде"""
        try:
            # Найдем ID команды
            team_id = self.find_team_by_name(team_name)
            if not team_id:
                logger.error(f"Команда {team_name} не найдена")
                return None
            
            logger.info(f"Найдена команда {team_name} с ID: {team_id}")
            
            # Получаем страницу команды
            team_url = f"{self.BASE_URL}/team/{team_id}/"
            soup = self._fetch_page(team_url)
            
            if not soup:
                return None
            
            # Парсим основную информацию
            team_info = {
                'team_id': team_id,
                'name': self._parse_team_name(soup),
                'country': self._parse_team_country(soup),
                'ranking': self._parse_team_ranking_from_page(soup),
                'roster': self._parse_team_roster(soup, team_id),
            }
            
            return team_info
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о команде {team_name}: {e}")
            return None
    
    def _parse_team_name(self, soup: BeautifulSoup) -> str:
        """Парсинг названия команды"""
        try:
            # Пробуем несколько вариантов селекторов
            selectors = [
                'h1.profile-team-name',
                '.profile-team-name',
                'h1',
                '.team-name'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    name = element.get_text().strip()
                    if name and name != "HLTV.org":
                        return name
            
            # Пробуем из title
            title = soup.find('title')
            if title:
                match = re.search(r'(.+?) - HLTV', title.get_text())
                if match:
                    return match.group(1).strip()
            
            return "Unknown Team"
        except Exception as e:
            logger.error(f"Ошибка при парсинге названия команды: {e}")
            return "Unknown Team"
    
    def _parse_team_country(self, soup: BeautifulSoup) -> str:
        """Парсинг страны команды"""
        try:
            flag_element = soup.find('img', class_='flag')
            if flag_element:
                alt_text = flag_element.get('alt', '')
                return alt_text
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
                '.ranking-header .right'
            ]
            
            for selector in ranking_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if text.startswith('#') and text[1:].isdigit():
                        return int(text[1:])
            
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
                '.bodyshot-team a',
                '.lineup-con a',
                '.player-nick a'
            ]
            
            for selector in roster_selectors:
                player_links = soup.select(selector)
                
                for link in player_links:
                    href = link.get('href')
                    if href and '/player/' in href:
                        player_id_match = re.search(r'/player/(\d+)/', href)
                        
                        if player_id_match:
                            player_id = int(player_id_match.group(1))
                            
                            # Получаем никнейм игрока
                            nickname = link.get_text().strip()
                            if not nickname:
                                # Пробуем найти в дочерних элементах
                                nick_element = link.find(class_='text-ellipsis')
                                if nick_element:
                                    nickname = nick_element.get_text().strip()
                            
                            if nickname and nickname != "Unknown":
                                roster.append({
                                    'player_id': player_id,
                                    'nickname': nickname,
                                    'team_id': team_id
                                })
                
                if roster:  # Если нашли игроков, прекращаем поиск
                    break
            
            logger.info(f"Найдено игроков в составе: {len(roster)}")
            return roster
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге состава команды: {e}")
            return [] 