"""A module that contains the functionality of assigning servers to masses."""

from altar_servers.altar_servers import AltarServers
from altar_servers.queue_manager import QueueManager
from altar_servers.scheduling_unit import SchedulingUnit
from dates.date_handler import clear_calendar
from dates.day import Day
from dates.holy_mass import HolyMass


class BadSituationError(Exception):
    """Raised when two siblings should be assigned to an event where only one spot is left."""


def assign_servers(
    calendar: list, queue_manager: QueueManager, altar_servers: AltarServers
) -> None:
    """Create a single plan by assigning servers until all masses are covered.

    :param calendar: The event calendar.
    :param altar_servers: The altar servers object.
    """
    while True:
        try:
            _assign_altar_servers(calendar, queue_manager, altar_servers)
        except BadSituationError:
            clear_calendar(calendar)
            queue_manager.clear_state()
            continue
        break


def _pre_assign(mass: HolyMass, day: Day, altar_servers: AltarServers) -> int:
    assigned = 0
    if mass.event.servers is not None:
        if isinstance(mass.event.servers, dict):
            for date, item_list in mass.event.servers.items():
                if date == day.date:
                    for name in item_list:
                        try:
                            server = altar_servers.get_server_by_name(name)
                            altar_servers.assign_scheduling_unit(SchedulingUnit([server]), mass)
                            assigned += 1
                        except KeyError:
                            continue
        else:
            for item in mass.event.servers:
                try:
                    server = altar_servers.get_server_by_name(item)
                    altar_servers.assign_scheduling_unit(SchedulingUnit([server]), mass)
                    assigned += 1
                except KeyError:
                    continue
    return assigned


def _assign_altar_servers(
    calendar: list, queue_manager: QueueManager, altar_servers: AltarServers
) -> None:
    """Assign altar servers to a calendar consisting of multiple masses.

    :param calendar: The list of all days, where a mass takes place.
    :param servers: Wrapper object of all servers.
    """
    for day in calendar:
        for mass in sorted(day.masses, key=lambda x: x.event.time):
            n_servers_assigned = _pre_assign(mass, day, altar_servers)
            while n_servers_assigned < mass.event.n_servers:
                chosen_su = queue_manager.get_su_from_queues(day, mass)
                if n_servers_assigned + len(chosen_su) <= mass.event.n_servers:
                    n_servers_assigned += altar_servers.assign_scheduling_unit(chosen_su, mass)
                else:
                    raise BadSituationError
