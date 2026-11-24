"""Команда подбора заголовка для черновика статьи."""

import argparse
import logging
from importlib.metadata import version

import httpx

from lab8.liftwing import LiftWingError, suggest_title

logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Прочитать тему, вывести заголовок и вернуть код завершения."""
    parser = argparse.ArgumentParser(
        prog="mtp-title",
        description="Подобрать заголовок для черновика статьи в Википедии.",
    )
    parser.add_argument("topic", metavar="ТЕМА", help="Тема черновика")
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {version('mtp-lab8-variant5')}",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    try:
        with httpx.Client() as client:
            title = suggest_title(args.topic, client)
    except ValueError as error:
        parser.error(str(error))
    except LiftWingError as error:
        logger.error("%s", error)
        return 1

    print(title)
    return 0
