#!/usr/bin/env python3
"""Runner for parsing upcoming CS:GO matches from HLTV.

This script is intended to be executed from the project root or from the
`services/hltv-parser` directory.  It adds the sibling `src` directory to
`sys.path` so that local modules (`match_parser`, etc.) can be imported
without installing the package.
"""

import sys
import os
import logging
from contextlib import suppress

# Ensure we can import from ../src regardless of the current working directory
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_PATH = os.path.join(_CURRENT_DIR, "..", "src")
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

# pylint: disable=wrong-import-position
from match_parser import MatchParser  # type: ignore
from selenium import webdriver  # type: ignore
from selenium.webdriver.firefox.options import Options as FirefoxOptions  # type: ignore
from selenium.webdriver.firefox.service import Service as FirefoxService  # type: ignore
import geckodriver_autoinstaller  # type: ignore


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("runner.match_parser")


def _init_driver() -> webdriver.Firefox:
    """Initialise a head-less Firefox driver ready for parsing."""
    logger.info("Initialising head-less Firefox WebDriver …")

    # Ensure the correct geckodriver binary is available
    geckodriver_path = geckodriver_autoinstaller.install()

    options = FirefoxOptions()
    options.add_argument("--headless")

    service = FirefoxService(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


def main() -> None:
    """Entry-point: parse upcoming matches and optionally persist them."""
    driver = None

    try:
        driver = _init_driver()

        # Instantiate the parser.  Set `dry_run=False` to write into DB.
        with MatchParser(driver, dry_run=True) as parser:
            parser.parse_and_save_upcoming_matches()

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Fatal error whilst running match parser: %s", exc)

    finally:
        with suppress(Exception):
            if driver is not None:
                driver.quit()
                logger.info("WebDriver has been closed.")


if __name__ == "__main__":
    main() 