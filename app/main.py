"""A module that contains the high level function calls of the altar server plan creator."""

import copy
import logging
import sys
from datetime import datetime

from altar_servers.altar_servers import AltarServers, get_distribution
from dates.date_handler import clear_calendar, create_calendar
from events.event_calendar import EventCalendar
from latex_handler import generate_pdf
from server_handler import assign_servers
from tqdm import tqdm

from utils.utils import load_yaml_file

TOTAL_OPTIMIZE_ROUNDS = 10
PROGRAM_NAME = "Mini-Plan Ersteller"
logger = logging.getLogger(PROGRAM_NAME)


def main() -> None:
    """Load the config files and call the individual steps."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s - %(message)s")
    logger.info("Willkommen beim %s", PROGRAM_NAME)

    logger.info("Konfiguration wird geladen...")
    raw_altar_servers = load_yaml_file("config/altar_servers.yaml")
    raw_event_calendar = load_yaml_file("config/holy_masses.yaml")
    raw_custom_masses = load_yaml_file("config/custom_masses.yaml")
    event_calendar = EventCalendar(raw_event_calendar, raw_custom_masses)
    plan_info = load_yaml_file("config/plan_info.yaml")

    start_date = datetime.strptime(plan_info["start_date"], "%d.%m.%Y").astimezone().date()
    end_date = datetime.strptime(plan_info["end_date"], "%d.%m.%Y").astimezone().date()

    logger.info("Kalender wird erstellet...")
    calendar = create_calendar(start_date, end_date, event_calendar)
    print(calendar)
    logger.info("Abgeschlossen")
    logger.info("Ministranten werden erstellet...")
    altar_servers = AltarServers(raw_altar_servers, event_calendar)
    logger.info("Abgeschlossen")

    logger.info("Ministranten werden eingeteilt...")

    final_altar_servers, final_calendar = optimize_assignments(calendar, altar_servers)

    logger.info("Statistik")
    for server in get_distribution(final_altar_servers):
        logger.info(server)
    logger.info("PDF wird erstellt")
    generate_pdf(final_calendar, start_date, end_date, plan_info["welcome_text"])
    logger.info("Abgeschlossen")


def optimize_assignments(calendar: list, altar_servers: AltarServers) -> tuple:
    """Create multiple plans until keep the one with the lowest score in number of services.

    :param calendar: The calendar.
    :param altar_servers: The raw altar server dictionary.
    :return: The resulting altar servers object and the calendar object with all altar servers
    assigned.
    """
    final_calendar = None
    final_altar_servers = None
    final_variance1 = 1000
    final_variance2 = 1000
    iterations = tqdm(total=TOTAL_OPTIMIZE_ROUNDS)
    for _ in range(TOTAL_OPTIMIZE_ROUNDS):
        assign_servers(calendar, altar_servers)
        variance1, variance2 = altar_servers.calculate_statistics()
        if variance1 < final_variance1 and variance2 < final_variance2:
            final_altar_servers = altar_servers.get_copy()
            final_calendar = copy.deepcopy(calendar)
            final_variance1 = variance1
            final_variance2 = variance2

        iterations.update(1)
        logger.info(iterations)
        sys.stdout.flush()

        clear_calendar(calendar)
        altar_servers.clear_state()
    return final_altar_servers, final_calendar


if __name__ == "__main__":
    main()
