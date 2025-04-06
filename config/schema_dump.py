import json
from pathlib import Path

from altar_servers.altar_servers import AltarServers
from events.event_calendar import EventCalendar
from plan_info.plan_info import PlanInfo


def main():
    with Path("altar_servers.config.json").open("w") as file:
        json.dump(AltarServers.model_json_schema(), file, indent=4)

    with Path("holy_masses.config.json").open("w") as file:
        json.dump(EventCalendar.model_json_schema(), file, indent=4)

    with Path("plan_info.config.json").open("w") as file:
        json.dump(PlanInfo.model_json_schema(), file, indent=4)

if __name__ == "__main__":
    main()
