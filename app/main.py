"""A module that contains the high level function calls of the altar server plan creator."""

import logging
import statistics
import sys
from datetime import datetime
from pathlib import Path

import yaml
from altar_server import AltarServers
from date_handler import create_calendar
from event_calendar import EventCalendar
from latex_handler import generate_pdf
from server_handler import BadSituationError, assign_altar_servers
from tqdm import tqdm

TOTAL_OPTIMIZE_ROUNDS = 1000

PROGRAM_NAME = "Mini-Plan Ersteller"
logger = logging.getLogger(PROGRAM_NAME)


def load_yaml_file(path: str) -> list | dict:
    """Load a yaml file at the given path.

    :param path: The path to the yaml file.
    :return: The dictionary containing the content of the yaml file.
    """
    with Path(path).open("r") as file:
        return yaml.safe_load(file)


def main() -> None:
    """Load the config files and call the individual steps."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s - %(message)s")
    logger.info("Willkommen beim %s", PROGRAM_NAME)

    logger.info("Konfiguration wird geladen...")
    raw_altar_servers = load_yaml_file("config/minis.yaml")
    raw_event_calendar = load_yaml_file("config/holy_masses.yaml")
    raw_custom_masses = load_yaml_file("config/custom_masses.yaml")
    event_calendar = EventCalendar(raw_event_calendar, raw_custom_masses)
    plan_info = load_yaml_file("config/plan_info.yaml")

    start_date = datetime.strptime(plan_info["start_date"], "%d.%m.%Y").astimezone().date()
    end_date = datetime.strptime(plan_info["end_date"], "%d.%m.%Y").astimezone().date()
    logger.info("Abgeschlossen")

    logger.info("Ministranten werden eingeteilt...")

    final_altar_servers, final_calendar = optimize_assignments(end_date, event_calendar,
                                                               raw_altar_servers, start_date)

    logger.info("Statistik")
    for server in final_altar_servers.get_distribution():
        logger.info(server)
    logger.info("PDF wird erstellt")
    generate_pdf(final_calendar, start_date, end_date, plan_info["welcome_text"])
    logger.info("Abgeschlossen")


def optimize_assignments(end_date, event_calendar, raw_altar_servers, start_date) -> tuple:
    final_calendar = None
    final_altar_servers = None
    final_variance = 10
    iterations = tqdm(total=TOTAL_OPTIMIZE_ROUNDS)
    for _ in range(TOTAL_OPTIMIZE_ROUNDS):
        altar_servers, calendar = assign_servers(end_date, event_calendar, raw_altar_servers,
                                                 start_date)
        distribution = [item[1] for item in altar_servers.get_distribution()]
        variance = statistics.pvariance(distribution)
        if variance < final_variance:
            final_altar_servers = altar_servers
            final_calendar = calendar
            final_variance = variance

        iterations.update(1)
        logger.info(iterations)
        sys.stdout.flush()
    return final_altar_servers, final_calendar


def assign_servers(end_date, event_calendar, raw_altar_servers, start_date) -> tuple:
    count = 1
    while True:
        altar_servers = AltarServers(raw_altar_servers, event_calendar)
        calendar = create_calendar(start_date, end_date, event_calendar)
        try:
            assign_altar_servers(calendar, altar_servers)
        except BadSituationError:
            count += 1
            continue
        break

    return altar_servers, calendar


if __name__ == "__main__":
    main()
