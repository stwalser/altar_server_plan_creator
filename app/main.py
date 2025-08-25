"""A module that contains the high level function calls of the altar server plan creator."""

import copy
import logging
import subprocess
import sys
from pathlib import Path

from altar_servers.altar_servers import AltarServers, get_distribution
from altar_servers.queue_manager import QueueManager
from altar_servers.server_handler import assign_servers
from dates.date_handler import clear_calendar, create_calendar
from events.event_calendar import EventCalendar
from plan_info.plan_info import PlanInfo
from tqdm import tqdm
from utils.latex_handler import generate_pdf

TOTAL_OPTIMIZE_ROUNDS = 5000
PROGRAM_NAME = "Mini-Plan Ersteller"
logger = logging.getLogger(PROGRAM_NAME)


def main() -> None:
    """Load the config files and call the individual steps."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s - %(message)s")
    logger.info("Willkommen beim %s", PROGRAM_NAME)

    if Path.exists(Path("output/plan.tex")):
        logger.info("Plan existiert bereits. Kompilere erneut ...")
        try:
            # ruff: noqa: S603
            subprocess.run(
                [
                    "/usr/bin/pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory=output",
                    "output/plan.tex",
                ],
                check=True,
            )
            logger.info("Abgeschlossen")
        except subprocess.CalledProcessError as e:
            logger.info("Fehler: %s", e)
    else:
        logger.info("Konfiguration wird geladen...")
        raw_event_calendar = Path("config/holy_masses.json").read_text()
        event_calendar = EventCalendar.model_validate_json(raw_event_calendar)

        raw_plan_info = Path("config/plan_info.json").read_text()
        plan_info = PlanInfo.model_validate_json(raw_plan_info)

        logger.info("Kalender wird erstellet...")
        calendar = create_calendar(plan_info.start_date, plan_info.end_date, event_calendar)
        logger.info("Abgeschlossen")
        logger.info("Ministranten werden erstellt...")
        raw_altar_servers = Path("config/altar_servers.json").read_text()
        altar_servers = AltarServers.model_validate_json(raw_altar_servers)
        logger.info("Abgeschlossen")
        logger.info("Warteschlangen werden erstellt...")
        queue_manager = QueueManager(event_calendar, altar_servers)
        logger.info("Abgeschlossen")

        logger.info("Ministranten werden eingeteilt...")

        final_altar_servers, final_calendar = optimize_assignments(
            calendar, queue_manager, altar_servers, event_calendar
        )

        logger.info("Statistik")
        for server in get_distribution(final_altar_servers):
            logger.info(server)

        logger.info("PDF wird erstellt")
        generate_pdf(
            final_calendar, plan_info.start_date, plan_info.end_date, plan_info.welcome_text
        )
        logger.info("Abgeschlossen")


def optimize_assignments(
    calendar: list,
    queue_manager: QueueManager,
    altar_servers: AltarServers,
    event_calendar: EventCalendar,
) -> tuple:
    """Create multiple plans until keep the one with the lowest score in number of services.

    :param event_calendar:
    :param queue_manager:
    :param calendar: The calendar.
    :param altar_servers: The raw altar server dictionary.
    :return: The resulting altar servers object and the calendar object with all altar servers
    assigned.
    """
    final_calendar = None
    final_altar_servers = None
    sum_of_variances_final = sys.maxsize
    iterations = tqdm(total=TOTAL_OPTIMIZE_ROUNDS)
    for i in range(TOTAL_OPTIMIZE_ROUNDS):
        assign_servers(calendar, queue_manager, altar_servers)
        sum_of_variances = sum(altar_servers.calculate_statistics(event_calendar))
        if sum_of_variances < sum_of_variances_final:
            logger.info(f"{i} WAS BETTER {sum_of_variances}")
            final_altar_servers = altar_servers.get_copy()
            final_calendar = copy.deepcopy(calendar)
            sum_of_variances_final = sum_of_variances

        iterations.update(1)
        sys.stdout.flush()

        clear_calendar(calendar)
        queue_manager.clear_state()
    return final_altar_servers, final_calendar


if __name__ == "__main__":
    main()
