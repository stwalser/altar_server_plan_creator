from datetime import datetime

import pytest

from altar_servers.altar_servers import AltarServers
from dates.date_handler import create_calendar
from events.event_calendar import EventCalendar
from server_handler import assign_servers
from utils.utils import load_yaml_file


@pytest.fixture(scope="module")
def plan():
    raw_altar_servers = load_yaml_file("../../config/altar_servers.yaml")
    raw_event_calendar = load_yaml_file("../../config/holy_masses.yaml")
    raw_custom_masses = load_yaml_file("../../config/custom_masses.yaml")
    event_calendar = EventCalendar(raw_event_calendar, raw_custom_masses)
    plan_info = load_yaml_file("../../config/plan_info.yaml")

    start_date = datetime.strptime(plan_info["start_date"], "%d.%m.%Y").astimezone().date()
    end_date = datetime.strptime(plan_info["end_date"], "%d.%m.%Y").astimezone().date()

    calendar = create_calendar(start_date, end_date, event_calendar)
    altar_servers = AltarServers(raw_altar_servers, event_calendar)
    assign_servers(calendar, altar_servers)
    yield calendar, event_calendar


class Test:
    def test_avoids_correct(self, plan):
        calendar = plan[0]
        for day in calendar:
            for mass in day.masses:
                for server in mass.servers:
                    assert mass.event.id not in server.avoid

    def test_vacations_correct(self, plan):
        calendar = plan[0]
        for day in calendar:
            for mass in day.masses:
                for server in mass.servers:
                    for vacation in server.vacations:
                        assert not vacation[0] <= day.date <= vacation[1]
