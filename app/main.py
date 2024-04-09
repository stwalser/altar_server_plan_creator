from datetime import datetime

import yaml
from date_handler import create_mass_list
from event_calendar import EventCalendar
from latex_handler import generate_pdf
from server_handler import add_servers_to_masses

PROGRAM_NAME = "Mini-Plan Ersteller"


def load_yaml_file(name):
    with open(name, encoding="utf-8") as file:
        return yaml.safe_load(file)


def main():
    print(f"Willkommen beim {PROGRAM_NAME}")

    print("Konfiguration wird geladen...")
    servers = load_yaml_file("config/minis.yaml")
    raw_event_calendar = load_yaml_file("config/holy_masses.yaml")
    event_calendar = EventCalendar(raw_event_calendar)
    custom_masses = load_yaml_file("config/custom_masses.yaml")
    plan_info = load_yaml_file("config/plan_info.yaml")

    start_date = datetime.strptime(plan_info["start_date"], "%d.%m.%Y").date()
    end_date = datetime.strptime(plan_info["end_date"], "%d.%m.%Y").date()
    print("Abgeschlossen")

    print("Messkalender wird erstellt...")
    days = create_mass_list(start_date, end_date, event_calendar, custom_masses)
    print("Abgeschlossen")
    print("Ministranten werden eingeteilt...")
    add_servers_to_masses(days, servers)
    print("Abgeschlossen")
    print("PDF wird erstellt")
    generate_pdf(days, start_date, end_date, plan_info["welcome_text"])
    print("Abgeschlossen")


if __name__ == "__main__":
    main()
