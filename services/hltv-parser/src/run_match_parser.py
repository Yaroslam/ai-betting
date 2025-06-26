import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import geckodriver_autoinstaller

from match_parser import MatchParser

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Основная функция для инициализации драйвера и запуска парсера матчей.
    """
    logger.info("Инициализация драйвера Firefox для парсера матчей...")
    options = FirefoxOptions()
    options.add_argument("--headless")
    
    driver = None
    try:
        # Автоматически устанавливаем/обновляем geckodriver той же версии, что и установленный Firefox
        geckodriver_autoinstaller.install()
        service = FirefoxService()
        driver = webdriver.Firefox(service=service, options=options)
        
        logger.info("Переход на страницу матчей и ожидание загрузки контента...")
        driver.get("https://www.hltv.org/matches")
        
        # Пытаемся дождаться появления хотя бы одной ссылки матча, но не падаем при ошибке
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.match"))
            )
            logger.info("Контент матчей загружен. Запуск MatchParser...")
        except Exception as wait_err:
            logger.warning(f"Не удалось дождаться селектора a.match: {wait_err}. Продолжаем...")
        
        # Сохраняем HTML страницы для оффлайн-анализа структуры
        try:
            html_path = "matches_page.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info(f"HTML страницы матчей сохранён в {html_path}")
        except Exception as save_err:
            logger.warning(f"Не удалось сохранить HTML страницы матчей: {save_err}")
        
        parser = MatchParser(driver, dry_run=True)
        parser.parse_and_save_upcoming_matches()
        
    except Exception as e:
        logger.error(f"Произошла глобальная ошибка: {e}")
    finally:
        if driver:
            driver.quit()
            logger.info("Драйвер Firefox был успешно закрыт.")


if __name__ == "__main__":
    main() 