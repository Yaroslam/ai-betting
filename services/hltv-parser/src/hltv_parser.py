"""
HLTV Parser - Основной класс для парсинга данных с HLTV.org
"""

import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PlayerInfo:
    """Информация об игроке"""
    player_id: int
    nickname: str
    real_name: str
    country: str
    age: Optional[int] = None
    team_id: Optional[int] = None


@dataclass
class PlayerStats:
    """Статистика игрока"""
    player_id: int
    rating_2_0: float
    kd_ratio: float
    adr: float
    kast: float
    headshot_percentage: float
    maps_played: int
    kills_per_round: float
    assists_per_round: float
    deaths_per_round: float
    saved_by_teammate_per_round: float
    saved_teammates_per_round: float


@dataclass
class TeamInfo:
    """Информация о команде"""
    team_id: int
    name: str
    country: str
    ranking: Optional[int]
    roster: List[PlayerInfo]
    recent_results: List[Dict[str, Any]]


class HLTVParser:
    """Парсер для HLTV.org"""
    
    BASE_URL = "https://www.hltv.org"
    
    def __init__(self):
        self.session = None
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _get_session(self):
        """Получить сессию или создать новую"""
        if not self.session:
            # Создаем jar для cookies
            jar = aiohttp.CookieJar()
            
            self.session = aiohttp.ClientSession(
                headers=self.base_headers,
                timeout=aiohttp.ClientTimeout(total=30),
                cookie_jar=jar,
                connector=aiohttp.TCPConnector(ssl=False)  # Отключаем SSL проверку
            )
            
            # Сначала заходим на главную страницу для получения cookies
            try:
                logger.info("Получаем cookies с главной страницы...")
                async with self.session.get(self.BASE_URL) as response:
                    if response.status == 200:
                        logger.info("Cookies получены успешно")
                    else:
                        logger.warning(f"Не удалось получить cookies: {response.status}")
            except Exception as e:
                logger.warning(f"Ошибка при получении cookies: {e}")
                
        return self.session
    
    async def _fetch_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Получить страницу и распарсить её"""
        for attempt in range(retries):
            try:
                session = await self._get_session()
                logger.info(f"Загружаем страницу (попытка {attempt + 1}): {url}")
                
                # Добавляем задержку между попытками
                if attempt > 0:
                    await asyncio.sleep(3 + attempt * 2)
                
                # Создаем специфичные заголовки для каждого запроса
                headers = self.base_headers.copy()
                headers['Referer'] = self.BASE_URL + '/'
                
                # Имитируем человеческое поведение - случайная задержка
                await asyncio.sleep(1 + attempt * 0.5)
                
                async with session.get(url, headers=headers) as response:
                    logger.info(f"Получен ответ: {response.status} для {url}")
                    
                    if response.status == 200:
                        html = await response.text()
                        logger.info(f"Страница загружена успешно, размер: {len(html)} символов")
                        return BeautifulSoup(html, 'html.parser')
                    elif response.status == 403:
                        logger.warning(f"HTTP 403 (Access Denied) для URL: {url}")
                        if attempt < retries - 1:
                            logger.info("Пытаемся обойти блокировку...")
                            await asyncio.sleep(8 + attempt * 3)  # Увеличиваем задержку
                            continue
                        else:
                            logger.error("Сайт блокирует запросы после всех попыток.")
                            return None
                    elif response.status == 429:
                        logger.warning(f"HTTP 429 (Too Many Requests) для URL: {url}")
                        if attempt < retries - 1:
                            logger.info("Слишком много запросов, ждем...")
                            await asyncio.sleep(15 + attempt * 5)
                            continue
                        return None
                    else:
                        logger.error(f"HTTP {response.status} для URL: {url}")
                        if attempt < retries - 1:
                            await asyncio.sleep(5)
                            continue
                        return None
                        
            except Exception as e:
                logger.error(f"Ошибка при загрузке {url} (попытка {attempt + 1}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(5 + attempt * 2)
                    continue
                return None
        
        return None
    
    async def find_team_by_name(self, team_name: str) -> Optional[int]:
        """Найти ID команды по названию"""
        # Попробуем несколько способов найти команду
        
        # Способ 1: используем известные ID команд (обходим блокировку поиска)
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
        
        # Способ 2: через поиск (если не заблокирован)
        search_url = f"{self.BASE_URL}/search?term={team_name}"
        soup = await self._fetch_page(search_url)
        
        if soup:
            # Ищем ссылки на команды в результатах поиска
            team_links = soup.find_all('a', href=re.compile(r'/team/\d+/'))
            
            for link in team_links:
                team_text = link.get_text().lower()
                if team_name.lower() in team_text:
                    href = link.get('href')
                    team_id_match = re.search(r'/team/(\d+)/', href)
                    if team_id_match:
                        return int(team_id_match.group(1))
        
        # Способ 3: через рейтинг команд
        logger.info("Пытаемся найти команду через рейтинг...")
        ranking_url = f"{self.BASE_URL}/ranking/teams/"
        soup = await self._fetch_page(ranking_url)
        
        if soup:
            team_elements = soup.find_all('a', href=re.compile(r'/team/\d+/'))
            for element in team_elements:
                team_text = element.get_text().lower()
                if team_name.lower() in team_text:
                    href = element.get('href')
                    team_id_match = re.search(r'/team/(\d+)/', href)
                    if team_id_match:
                        return int(team_id_match.group(1))
        
        logger.error(f"Команда {team_name} не найдена ни одним способом")
        return None
    
    async def get_team_info(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Получить полную информацию о команде"""
        try:
            # Сначала найдем ID команды
            team_id = await self.find_team_by_name(team_name)
            if not team_id:
                logger.error(f"Команда {team_name} не найдена")
                return None
            
            logger.info(f"Найдена команда {team_name} с ID: {team_id}")
            
            # Получаем страницу команды
            team_url = f"{self.BASE_URL}/team/{team_id}/"
            soup = await self._fetch_page(team_url)
            
            if not soup:
                return None
            
            # Парсим основную информацию
            team_info = {
                'team_id': team_id,
                'name': self._parse_team_name(soup),
                'country': self._parse_team_country(soup),
                'ranking': await self._parse_team_ranking(team_id),
                'roster': await self._parse_team_roster(soup, team_id),
            }
            
            return team_info
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о команде {team_name}: {e}")
            return None
    
    def _parse_team_name(self, soup: BeautifulSoup) -> str:
        """Парсинг названия команды"""
        try:
            name_element = soup.find('h1', class_='profile-team-name')
            if name_element:
                return name_element.get_text().strip()
            
            # Альтернативный способ
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
    
    async def _parse_team_ranking(self, team_id: int) -> Optional[int]:
        """Получить текущий рейтинг команды"""
        try:
            ranking_url = f"{self.BASE_URL}/ranking/teams/"
            soup = await self._fetch_page(ranking_url)
            
            if not soup:
                return None
            
            # Ищем команду в рейтинге
            team_rows = soup.find_all('div', class_='ranked-team')
            
            for i, row in enumerate(team_rows, 1):
                team_link = row.find('a', href=re.compile(f'/team/{team_id}/'))
                if team_link:
                    return i
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении рейтинга команды: {e}")
            return None
    
    async def _parse_team_roster(self, soup: BeautifulSoup, team_id: int) -> List[Dict[str, Any]]:
        """Парсинг состава команды"""
        try:
            roster = []
            
            # Ищем секцию с составом
            roster_section = soup.find('div', class_='bodyshot-team')
            if not roster_section:
                # Альтернативный поиск
                roster_section = soup.find('div', {'id': 'roster'})
            
            if roster_section:
                player_links = roster_section.find_all('a', href=re.compile(r'/player/\d+/'))
                
                for link in player_links:
                    href = link.get('href')
                    player_id_match = re.search(r'/player/(\d+)/', href)
                    
                    if player_id_match:
                        player_id = int(player_id_match.group(1))
                        
                        # Получаем никнейм игрока
                        nickname_element = link.find('div', class_='text-ellipsis')
                        if not nickname_element:
                            nickname_element = link.find('span')
                        
                        nickname = nickname_element.get_text().strip() if nickname_element else "Unknown"
                        
                        roster.append({
                            'player_id': player_id,
                            'nickname': nickname,
                            'team_id': team_id
                        })
            
            logger.info(f"Найдено игроков в составе: {len(roster)}")
            return roster
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге состава команды: {e}")
            return []
    
    async def get_recent_matches(self, team_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Получить последние матчи команды"""
        try:
            matches_url = f"{self.BASE_URL}/team/{team_id}/#tab-matchesBox"
            soup = await self._fetch_page(matches_url)
            
            if not soup:
                return []
            
            matches = []
            
            # Ищем блок с матчами
            match_elements = soup.find_all('div', class_='result-con')[:limit]
            
            for match_element in match_elements:
                try:
                    match_info = self._parse_single_match(match_element, team_id)
                    if match_info:
                        matches.append(match_info)
                except Exception as e:
                    logger.warning(f"Ошибка при парсинге матча: {e}")
                    continue
            
            logger.info(f"Получено последних матчей: {len(matches)}")
            return matches
            
        except Exception as e:
            logger.error(f"Ошибка при получении последних матчей: {e}")
            return []
    
    def _parse_single_match(self, match_element, team_id: int) -> Optional[Dict[str, Any]]:
        """Парсинг одного матча"""
        try:
            # Получаем ссылку на матч
            match_link = match_element.find('a')
            if not match_link:
                return None
            
            match_href = match_link.get('href')
            match_id_search = re.search(r'/matches/(\d+)/', match_href)
            match_id = int(match_id_search.group(1)) if match_id_search else None
            
            # Получаем счет
            score_element = match_element.find('span', class_='score-lost') or match_element.find('span', class_='score-won')
            score = score_element.get_text().strip() if score_element else "0-0"
            
            # Определяем результат (победа/поражение)
            is_win = 'score-won' in str(match_element)
            
            # Получаем информацию о противнике
            teams = match_element.find_all('div', class_='team')
            opponent = "Unknown"
            for team in teams:
                team_link = team.find('a')
                if team_link:
                    team_href = team_link.get('href')
                    if team_href and f'/team/{team_id}/' not in team_href:
                        opponent = team.get_text().strip()
                        break
            
            return {
                'match_id': match_id,
                'opponent': opponent,
                'score': score,
                'result': 'win' if is_win else 'loss',
                'match_url': urljoin(self.BASE_URL, match_href) if match_href else None
            }
            
        except Exception as e:
            logger.warning(f"Ошибка при парсинге матча: {e}")
            return None
    
    async def get_player_stats(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Получить статистику игрока"""
        try:
            player_url = f"{self.BASE_URL}/player/{player_id}/"
            soup = await self._fetch_page(player_url)
            
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
            
            # Никнейм
            nickname_element = soup.find('h1', class_='summaryNickname')
            if nickname_element:
                info['nickname'] = nickname_element.get_text().strip()
            
            # Настоящее имя
            realname_element = soup.find('div', class_='summaryRealname')
            if realname_element:
                info['real_name'] = realname_element.get_text().strip()
            
            # Страна
            flag_element = soup.find('img', class_='flag')
            if flag_element:
                info['country'] = flag_element.get('alt', 'Unknown')
            
            # Возраст
            age_element = soup.find('span', class_='summaryPlayerAge')
            if age_element:
                age_text = age_element.get_text()
                age_match = re.search(r'(\d+)', age_text)
                if age_match:
                    info['age'] = int(age_match.group(1))
            
            return info
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге основной информации игрока: {e}")
            return {'player_id': player_id}
    
    def _parse_player_statistics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Парсинг статистики игрока"""
        try:
            stats = {}
            
            # Ищем блок со статистикой
            stats_section = soup.find('div', class_='statistics')
            if not stats_section:
                return stats
            
            # Рейтинг 2.0
            rating_element = soup.find('span', class_='bold', string=re.compile(r'\d+\.\d+'))
            if rating_element:
                try:
                    stats['rating_2_0'] = float(rating_element.get_text().strip())
                except ValueError:
                    pass
            
            # Парсим все статистические показатели
            stat_elements = soup.find_all('div', class_='summaryStatBreakdownRow')
            
            for stat_element in stat_elements:
                try:
                    label_element = stat_element.find('span', class_='summaryStatBreakdownDataName')
                    value_element = stat_element.find('span', class_='summaryStatBreakdownDataValue')
                    
                    if label_element and value_element:
                        label = label_element.get_text().strip().lower()
                        value_text = value_element.get_text().strip()
                        
                        # Парсим различные типы статистики
                        if 'k/d ratio' in label:
                            stats['kd_ratio'] = float(value_text)
                        elif 'adr' in label:
                            stats['adr'] = float(value_text)
                        elif 'kast' in label:
                            stats['kast'] = float(value_text.replace('%', ''))
                        elif 'headshot' in label:
                            stats['headshot_percentage'] = float(value_text.replace('%', ''))
                        elif 'maps played' in label:
                            stats['maps_played'] = int(value_text)
                        elif 'kills per round' in label:
                            stats['kills_per_round'] = float(value_text)
                        elif 'assists per round' in label:
                            stats['assists_per_round'] = float(value_text)
                        elif 'deaths per round' in label:
                            stats['deaths_per_round'] = float(value_text)
                
                except (ValueError, AttributeError) as e:
                    logger.debug(f"Не удалось распарсить статистику: {e}")
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге статистики игрока: {e}")
            return {}
    
    async def close(self):
        """Закрыть сессию"""
        if self.session:
            await self.session.close() 