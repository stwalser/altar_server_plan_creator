"""A module that contains the functionality of assigning servers to masses."""
import datetime

from altar_servers.altar_servers import AltarServers
from altar_servers.scheduling_unit import SchedulingUnit
from dates.date_handler import clear_calendar
from dates.day import Day
from dates.holy_mass import HolyMass


class BadSituationError(Exception):
    """Raised when two siblings should be assigned to an event where only one spot is left."""


def assign_servers(calendar: list, altar_servers: AltarServers) -> None:
    """Create a single plan by assigning servers until all masses are covered.

    :param calendar: The event calendar.
    :param altar_servers: The altar servers object.
    """
    while True:
        try:
            _assign_altar_servers(calendar, altar_servers)
        except BadSituationError:
            clear_calendar(calendar)
            altar_servers.clear_state()
            continue
        break


def _pre_assign(mass: HolyMass, day: Day, servers: AltarServers) -> int:
    assigned = 0
    for item in mass.event.pre_assigned_servers:
        if isinstance(mass.event.pre_assigned_servers, dict):
            date = datetime.datetime.strptime(item, "%d.%m.")
            if date.month == day.date.month and date.day == day.date.day:
                for name in mass.event.pre_assigned_servers[item]:
                    try:
                        server = servers.get_server_by_name(name)
                        servers.assign_scheduling_unit(SchedulingUnit([server]), mass)
                        assigned += 1
                    except KeyError:
                        continue
        else:
            try:
                server = servers.get_server_by_name(item)
                servers.assign_scheduling_unit(SchedulingUnit([server]), mass)
                assigned += 1
            except KeyError:
                continue
    return assigned


def _assign_altar_servers(calendar: list, servers: AltarServers) -> None:
    """Assign altar servers to a calendar consisting of multiple masses.

    :param calendar: The list of all days, where a mass takes place.
    :param servers: Wrapper object of all servers.
    """
    for day in calendar:
        for mass in sorted(day.masses, key=lambda x: x.event.time):
            n_servers_assigned = _pre_assign(mass, day, servers)
            while n_servers_assigned < mass.event.n_servers:
                chosen_su = servers.get_su_from_queues(day, mass)
                if n_servers_assigned + len(chosen_su) <= mass.event.n_servers:
                    n_servers_assigned += servers.assign_scheduling_unit(chosen_su, mass)
                else:
                    raise BadSituationError
