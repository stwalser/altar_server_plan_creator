"""A module that contains the functionality of assigning servers to masses."""
from altar_servers.altar_servers import AltarServers
from altar_servers.scheduling_unit import SchedulingUnit
from dates.date_handler import clear_calendar
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


def _assign_altar_servers(calendar: list, servers: AltarServers) -> None:
    """Assign altar servers to a calendar consisting of multiple masses.

    :param calendar: The list of all days, where a mass takes place.
    :param servers: Wrapper object of all servers.
    """
    for day in calendar:
        for mass in sorted(day.masses, key=lambda x: not x.event.high_mass):
            n_servers_assigned = 0

            if mass.event.high_mass:
                n_servers_assigned = _assign_high_mass_priority_servers(servers, mass,
                                                                        n_servers_assigned)
            while n_servers_assigned < mass.event.n_servers:
                chosen_su = servers.get_su_from_queues(day, mass)
                if n_servers_assigned + len(chosen_su) <= mass.event.n_servers:
                    n_servers_assigned += _assign_scheduling_unit(chosen_su, mass)
                else:
                    raise BadSituationError


def _assign_scheduling_unit(scheduling_unit: SchedulingUnit, mass: HolyMass) -> int:
    """Assign a server without siblings to a mass.

    :param scheduling_unit: The scheduling unit.
    :param mass: The mass to assign the server to.
    :return: 1 to increase the counter.
    """
    mass.add_scheduling_unit(scheduling_unit)
    _choose_for(scheduling_unit, mass)
    return 1


def _choose_for(su: SchedulingUnit, mass: HolyMass) -> None:
    """Add a server to the already chosen list.

    If the length of the list equals the number of the servers, the list is cleared.
    :param su: The scheduling unit to add extend the list for.
    """
    for server in su.minis:
        server.service_dates.append(mass.day.date)


def _assign_high_mass_priority_servers(
        servers: AltarServers, mass: HolyMass, n_servers_assigned: int
) -> int:
    """Assign servers to a mass that are prioritized for high masses.

    :param mass: The holy mass.
    :param n_servers_assigned: The number of servers assigned to the mass before the
    prioritization.
    :return: The number of servers assigned to the mass after the prioritization.
    """
    already_considered = []
    while n_servers_assigned < mass.event.n_servers:
        chosen_su = servers.high_mass_priority.popleft()
        if chosen_su in already_considered:
            servers.high_mass_priority.append(chosen_su)
            return n_servers_assigned

        already_considered.append(chosen_su)
        mass.add_scheduling_unit(chosen_su)
        servers.high_mass_priority.append(chosen_su)
        n_servers_assigned += 1
        _choose_for(chosen_su, mass)
    return n_servers_assigned
