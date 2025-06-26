import logging
import re
import time
from datetime import datetime
from typing import Optional, Dict, Any

from bs4 import BeautifulSoup
from selenium.common import WebDriverException
from selenium.webdriver.firefox.webdriver import WebDriver
from sqlalchemy.orm import Session
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Попытка опционального импорта модуля database. В режиме dry-run он не обязателен
try:
    from database import SessionLocal, Team, Match, get_team_by_name
except ModuleNotFoundError:
    SessionLocal = None  # type: ignore
    Team = Match = None  # type: ignore

    def get_team_by_name(*_args, **_kwargs):  # type: ignore
        return None

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MatchParser:
    """
    Парсер для предстоящих матчей с сайта HLTV.org.
    Собирает информацию о матчах, в которых участвуют команды,
    присутствующие в локальной базе данных.
    """
    BASE_URL = "https://www.hltv.org"
    PAGE_LOAD_TIMEOUT = 15  # секунд ожидания полной загрузки
    RETRY_DELAY_BASE = 5    # базовая задержка перед повтором

    MATCHES_PAGE = f"{BASE_URL}/matches"

    def __init__(self, driver: WebDriver, dry_run: bool = False):
        """Создать парсер.

        :param driver: Selenium WebDriver
        :param dry_run: Если True — ничего не пишет в БД, только логирует результаты.
        """
        self.driver = driver
        self.dry_run = dry_run
        # Сессию создаём только если не в режиме dry-run (чтобы не требовать запущенную БД)
        self.db_session: Optional[Session] = None if dry_run else SessionLocal()

    # ---- Контекстный менеджер ------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db_session is not None:
            self.db_session.close()

    def _get_page_soup(self, url: str, wait_css_selector: Optional[str] = None, retries: int = 3) -> Optional[BeautifulSoup]:
        """Загрузить страницу и вернуть BeautifulSoup с поддержкой ретраев.

        :param wait_css_selector: CSS-селектор, который должен появиться на странице, прежде
            чем мы сочтём загрузку успешной. Если None — ждём только readyState.
        :param retries: количество повторных попыток при ошибках Selenium.
        """
        for attempt in range(retries):
            try:
                logger.info(f"Загрузка страницы: {url} (попытка {attempt + 1}/{retries})")
                self.driver.get(url)

                # Ожидаем полной загрузки документа
                WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )

                # Доп. ожидание специфического контента (если задан)
                if wait_css_selector:
                    WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_css_selector))
                    )

                return BeautifulSoup(self.driver.page_source, 'html.parser')

            except WebDriverException as e:
                logger.warning(f"Ошибка Selenium при загрузке {url}: {e}")
                if attempt < retries - 1:
                    delay = self.RETRY_DELAY_BASE * (attempt + 1)
                    logger.info(f"Повтор через {delay} c...")
                    time.sleep(delay)
                else:
                    logger.error("Достигнут лимит попыток загрузки страницы.")
        return None

    def _parse_match_datetime(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Извлечь дату и время матча со страницы матча."""
        try:
            time_element = soup.find('div', class_='time')
            if not time_element:
                return None
            
            # Вся информация о времени находится в unix-timestamp в атрибуте data-unix
            unix_timestamp_ms = time_element.get('data-unix')
            if unix_timestamp_ms:
                # Конвертируем миллисекунды в секунды и создаем объект datetime
                return datetime.fromtimestamp(int(unix_timestamp_ms) / 1000)
        except (AttributeError, ValueError, TypeError) as e:
            logger.error(f"Не удалось извлечь или конвертировать дату матча: {e}")
        return None

    def save_match_to_database(self, match_data: Dict[str, Any]):
        """Сохранить или обновить матч в базе данных."""
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Матч к сохранению: {match_data}")
            return

        existing_match = self.db_session.query(Match).filter(Match.hltv_id == match_data['hltv_id']).first()
        
        if existing_match:
            logger.info(f"Матч {match_data['hltv_id']} уже существует. Обновляем...")
            existing_match.team1_id = match_data['team1_id']
            existing_match.team2_id = match_data['team2_id']
            existing_match.scheduled_at = match_data['scheduled_at']
            existing_match.hltv_url = match_data['hltv_url']
            existing_match.match_format = match_data.get('match_format', existing_match.match_format)
            existing_match.updated_at = datetime.now()
        else:
            logger.info(f"Создаем новый матч {match_data['hltv_id']} в базе.")
            new_match = Match(**match_data)
            self.db_session.add(new_match)
            
        try:
            self.db_session.commit()
        except Exception as e:
            logger.error(f"Ошибка при сохранении матча {match_data['hltv_id']} в БД: {e}")
            self.db_session.rollback()

    def parse_and_save_upcoming_matches(self):
        """
        Основной метод. Парсит страницу с матчами и сохраняет релевантные в БД.
        """
        # Переходим на страницу всех матчей и ждём, пока появится секция Upcoming
        soup = self._get_page_soup(self.MATCHES_PAGE, 'div.matches-list-wrapper')
        if not soup:
            logger.error("Не удалось создать BeautifulSoup из исходного кода страницы.")
            return

        matches_wrappers = soup.find_all('div', class_='matches-list-wrapper')
        if not matches_wrappers:
            logger.warning("Не найдено 'div.matches-list-wrapper' — проверьте верстку HLTV.")
            return

        match_elements = []
        match_urls = []  # Для вывода пользователю
        seen_urls = set()
        for wrapper in matches_wrappers:
            # Находим все ссылки на матчи, но исключаем те, что расположены внутри
            # блоков <div class="matches-chronologically-hide"> (скрытые в UI).
            elems = wrapper.find_all('a', href=re.compile(r'^/matches/\d+/'))
            for e in elems:
                if e.find_parent('div', class_='matches-chronologically-hide') is not None:
                    # Пропускаем скрытые хронологически матчи
                    continue
                abs_url = self.BASE_URL + e['href']
                if abs_url in seen_urls:
                    continue  # Уже видели такой матч

                seen_urls.add(abs_url)
                match_elements.append(e)
                match_urls.append(abs_url)

        logger.info(f"Найдено {len(match_elements)} ссылок на предстоящие матчи для анализа.")

        # Выводим полный список URL (удобно для ручной проверки)
        for url in match_urls:
            logger.info(f"MATCH_URL: {url}")

        for match_elem in match_elements:
            try:
                # Извлекаем названия команд
                team_names_divs = match_elem.find_all('div', class_='matchTeamName')
                if len(team_names_divs) != 2:
                    continue  # Интересуют только матчи 1 на 1

                team1_name = team_names_divs[0].text.strip()
                team2_name = team_names_divs[1].text.strip()

                # Определяем, есть ли полноценные блоки команд в карточке. Если нет — считаем команду неизвестной.
                team1_div_present = match_elem.find('div', class_='match-team team1') is not None
                team2_div_present = match_elem.find('div', class_='match-team team2') is not None

                is_team1_unknown = not team1_div_present
                is_team2_unknown = not team2_div_present

                # Для логов: если команда неизвестна, маркируем как TBD
                if is_team1_unknown:
                    team1_name = 'TBD'
                if is_team2_unknown:
                    team2_name = 'TBD'

                # Проверяем наличие обеих команд в нашей БД
                if not self.dry_run:
                    team1_db = get_team_by_name(self.db_session, team1_name)
                    team2_db = get_team_by_name(self.db_session, team2_name)
                    
                    if not (team1_db and team2_db):
                        logger.info(f"Пропуск матча '{team1_name}' vs '{team2_name}', одной или обеих команд нет в БД.")
                        continue

                    logger.info(f"Найден релевантный матч: '{team1_name}' (ID: {team1_db.id}) vs '{team2_name}' (ID: {team2_db.id})")
                else:
                    # В режиме dry-run считаем матч релевантным без проверки БД
                    team1_db = team2_db = None

                # Получаем ссылку на детальную страницу матча
                match_url = self.BASE_URL + match_elem['href']
                match_id_match = re.search(r'/matches/(\d+)/', match_url)
                if not match_id_match:
                    continue
                
                hltv_match_id = int(match_id_match.group(1))

                # Переходим на страницу матча для получения даты
                detail_soup = self._get_page_soup(match_url)
                if not detail_soup:
                    logger.warning(f"Не удалось загрузить детальную страницу для матча {hltv_match_id}")
                    continue

                scheduled_time = self._parse_match_datetime(detail_soup)
                if not scheduled_time:
                    logger.warning(f"Не удалось получить дату для матча {hltv_match_id}")
                    continue
                
                match_format = self._parse_match_format(detail_soup) or 'TBD'

                # Определяем идентификаторы команд с учётом неизвестных.
                if self.dry_run:
                    team1_id_val = 0 if is_team1_unknown else None
                    team2_id_val = 0 if is_team2_unknown else None
                else:
                    team1_id_val = 0 if is_team1_unknown else (team1_db.id if team1_db else 0)
                    team2_id_val = 0 if is_team2_unknown else (team2_db.id if team2_db else 0)

                match_data = {
                    'hltv_id': hltv_match_id,
                    'team1_id': team1_id_val,
                    'team2_id': team2_id_val,
                    'scheduled_at': scheduled_time,
                    'hltv_url': match_url,
                    'status': 'scheduled',
                    'match_format': match_format,
                }

                self.save_match_to_database(match_data)
                
                # Бережём HLTV: небольшая пауза между запросами
                time.sleep(3) 

            except Exception as e:
                logger.error(f"Произошла непредвиденная ошибка при обработке матча: {e}")
                continue
        
        logger.info("Парсинг предстоящих матчей завершен.")

    @staticmethod
    def _parse_match_format(soup: BeautifulSoup) -> Optional[str]:
        """Попытаться определить формат матча (bo1/bo3/bo5)."""
        bestof_div = soup.find('div', class_='bestof')
        if bestof_div and bestof_div.text:
            match = re.search(r'Best of (\d)', bestof_div.text)
            if match:
                return f"bo{match.group(1)}"
        return None 