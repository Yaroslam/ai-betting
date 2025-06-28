#!/usr/bin/env python3
"""Runner for parsing HLTV top teams ranking.

Adds the sibling `src` directory to import local parser modules.
"""

import sys
import os
import logging

# Ensure we can import from ../src regardless of the current working directory
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_PATH = os.path.join(_CURRENT_DIR, "..", "src")
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

from team_parser import TeamParser  # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("runner.team_parser")


def main() -> None:
    """Entry-point for parsing the current HLTV top-team ranking."""
    with TeamParser() as parser:
        teams = parser.parse_team_ranking(max_teams=30)
        logger.info("Parsed and saved %s teams from ranking", len(teams))


if __name__ == "__main__":
    main() 