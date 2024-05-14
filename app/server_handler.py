"""A module that contains the functionality of assigning servers to masses."""
import random
from queue import Empty

from altar_server import AltarServer, AltarServers
from holy_mass import Day, HolyMass


class SameServerTwiceError(Exception):
    """Simple Exception that is thrown when a server has already been considered for a mass."""


def assign_altar_servers(calendar: list, servers: AltarServers) -> None:
    """Assign altar servers to a calendar consisting of multiple masses.

    :param calendar: The list of all days, where a mass takes place.
    :param servers: Wrapper object of all servers.
    """
    total_servers_assigned = 0
    for day in calendar:
        for mass in day.masses:
            n_servers_assigned = 0
            if total_servers_assigned >= len(servers.queue.queue) + len(servers.waiting.queue):
                print("shuffled")
                servers.shuffle_servers(list(servers.queue.queue))
                total_servers_assigned = 0

            if mass.event.high_mass:
                n_servers_assigned = assign_high_mass_priority_servers(
                    mass, n_servers_assigned, servers
                )

            while n_servers_assigned < mass.event.n_servers:
                chosen_server = get_server_from_queues(servers, day, mass)

                if chosen_server.has_siblings():
                    if n_servers_assigned + len(chosen_server.siblings) + 1 <= mass.event.n_servers:
                        n_servers_assigned += assign_single_server(chosen_server, mass, servers)

                        for sibling in chosen_server.siblings:
                            if sibling.is_available(day.event_day, mass.event):
                                n_servers_assigned += assign_sibling_server(sibling, mass)
                    else:
                        servers.queue.put(chosen_server)
                else:
                    n_servers_assigned += assign_single_server(chosen_server, mass, servers)

            total_servers_assigned += n_servers_assigned


def assign_high_mass_priority_servers(
    mass: HolyMass, n_servers_assigned: int, servers: AltarServers
) -> int:
    """Assign servers to a mass that are prioritized for high masses.

    :param mass: The holy mass.
    :param n_servers_assigned: The number of servers assigned to the mass before the prioritization.
    :param servers: Wrapper object of all servers.
    :return: The number of servers assigned to the mass after the prioritization.
    """
    already_considered = []
    while n_servers_assigned < mass.event.n_servers:
        chosen_server = servers.high_mass_priority.get_nowait()
        if chosen_server in already_considered:
            servers.high_mass_priority.put(chosen_server)
            return n_servers_assigned

        already_considered.append(chosen_server)
        mass.add_server(chosen_server)
        chosen_server.already_chosen_this_round = True
        servers.high_mass_priority.put(chosen_server)
        n_servers_assigned += 1
        chosen_server.number_of_services += 1  # do manually, because is_available() is not  called
    return n_servers_assigned


def assign_single_server(chosen_server: AltarServer, mass: HolyMass, servers: AltarServers) -> int:
    """Assign a server without siblings to a mass.

    :param chosen_server: The server.
    :param mass: The mass to assign the server to.
    :param servers: Wrapper object of all servers.
    :return: 1 to increase the counter.
    """
    mass.add_server(chosen_server)
    servers.queue.put(chosen_server)
    chosen_server.number_of_services += 1
    return 1


def assign_sibling_server(sibling: AltarServer, mass: HolyMass) -> int:
    """Assign sibling server to a mass.

    It sets the already_chosen_this_round flag to true to skip the sibling, when it is dequeued
    the next time.
    :param sibling: The sibling server.
    :param mass: The mass to assign the sibling server to.
    :return: 1 to increase the counter.
    """
    mass.add_server(sibling)
    sibling.already_chosen_this_round = True
    sibling.number_of_services += 1
    return 1


def get_server_from_queues(servers: AltarServers, day: Day, mass: HolyMass) -> AltarServer:
    """Get an available server from one of the queues.

    If there is a server in the waiting queue, it is preferred. Otherwise, the next one from the
    standard queue is chosen. If the server is not available, it is added to the waiting queue.
    :param servers: Wrapper object of all servers.
    :param day: Holds the information about the day.
    :param mass: Holds the information about the mass.
    :return: The chosen server.
    """
    already_considered = []
    while True:
        while True:
            try:
                chosen_server = servers.waiting.get_nowait()
                check_if_already_considered(already_considered, chosen_server, servers)
            except (Empty, SameServerTwiceError):
                chosen_server = servers.queue.get_nowait()

            if chosen_server.already_chosen_this_round:
                chosen_server.already_chosen_this_round = False
                servers.queue.put(chosen_server)
            else:
                break

        if not chosen_server.is_available(day.event_day, mass.event):
            already_considered.append(chosen_server)
            servers.waiting.put(chosen_server)
        else:
            return chosen_server


def check_if_already_considered(
    already_considered: list, chosen_server: AltarServer, servers: AltarServers
) -> None:
    """Check if a server was already considered and if it is, raise and error.

    :param servers:
    :param already_considered: list of already considered servers.
    :param chosen_server: server to check.
    """
    if chosen_server in already_considered:
        servers.waiting.put(chosen_server)
        raise SameServerTwiceError
