"""A module that contains the high level function calls of the altar server plan creator."""

import logging
import subprocess
import sys
from pathlib import Path

from altar_servers.altar_servers import AltarServers, get_distribution
from dates.date_handler import create_calendar
from events.event_calendar import EventCalendar
from plan_info.plan_info import PlanInfo
from utils.latex_handler import generate_pdf
from z3Solver import z3solver

PROGRAM_NAME = "Mini-Plan Ersteller"
logger = logging.getLogger(PROGRAM_NAME)


def get_number_of_pauses(event_calendar: EventCalendar, total_servers: int) -> int:
    servers_required_on_week: int = 0
    n_events: int = 0
    for event_day in event_calendar.weekday.values():
        for event in event_day.events:
            servers_required_on_week += event.n_servers
            n_events += 1
    weeks_without_repetition: float = total_servers / servers_required_on_week
    return int(weeks_without_repetition * n_events)


def main() -> None:
    """Load the config files and call the individual steps."""
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s - %(message)s")
    logger.info("Willkommen beim %s", PROGRAM_NAME)

    # if Path.exists(Path("output/plan.tex")):
    #     recompile_existing_plan()
    # else:
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

    min_masses_between_services: int = get_number_of_pauses(
        event_calendar, len(altar_servers.altar_servers)
    )

    logger.info("Ministranten werden eingeteilt...")

    final_altar_servers, final_calendar = z3solver.solve(
        calendar, altar_servers, min_masses_between_services
    )

    logger.info("Statistik")
    for server in get_distribution(final_altar_servers):
        logger.info(server)

    logger.info("PDF wird erstellt")
    generate_pdf(final_calendar, plan_info.start_date, plan_info.end_date, plan_info.welcome_text)
    logger.info("Abgeschlossen")


def recompile_existing_plan():
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


if __name__ == "__main__":
    main()
