"""A module that contains the functionality of assigning servers to masses."""

from altar_servers import AltarServers


class SameServerTwiceError(Exception):
    """Simple Exception that is thrown when a server has already been considered for a mass."""


class BadSituationError(Exception):
    """Raised when two siblings should be assigned to an event where only one spot is left."""


def assign_altar_servers(calendar: list, servers: AltarServers) -> None:
    """Assign altar servers to a calendar consisting of multiple masses.

    :param calendar: The list of all days, where a mass takes place.
    :param servers: Wrapper object of all servers.
    """
    for day in calendar:
        for mass in sorted(day.masses, key=lambda x: not x.event.high_mass):
            n_servers_assigned = 0

            if mass.event.high_mass:
                n_servers_assigned = servers.assign_high_mass_priority_servers(
                    mass, n_servers_assigned
                )
            while n_servers_assigned < mass.event.n_servers:
                chosen_server = servers.get_server_from_queues(day, mass)
                if chosen_server.has_siblings():
                    if all(
                        servers.is_available(sibling, day, mass)
                        for sibling in chosen_server.siblings
                    ):
                        if (
                            n_servers_assigned + len(chosen_server.siblings) + 1
                            <= mass.event.n_servers
                        ):
                            n_servers_assigned += servers.assign_single_server(chosen_server, mass)
                            for sibling in chosen_server.siblings:
                                n_servers_assigned += servers.assign_single_server(sibling, mass)
                        else:
                            raise BadSituationError
                else:
                    n_servers_assigned += servers.assign_single_server(chosen_server, mass)
