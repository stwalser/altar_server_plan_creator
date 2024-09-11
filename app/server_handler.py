"""A module that contains the functionality of assigning servers to masses."""

import queue

from altar_server import AltarServer, AltarServers
from event_calendar import Event, EventDay
from holy_mass import Day, HolyMass


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
                n_servers_assigned = assign_high_mass_priority_servers(
                    mass, n_servers_assigned, servers
                )

            while n_servers_assigned < mass.event.n_servers:
                chosen_server = get_server_from_queues(servers, day, mass)
                if server_not_assigned_this_day(chosen_server, day) and (
                        mass.event.location is None or mass.event.location in
                        chosen_server.locations):
                    if chosen_server.has_siblings():
                        if all(
                                is_available(servers, sibling, day, mass)
                                for sibling in chosen_server.siblings
                        ):
                            if (
                                    n_servers_assigned + len(chosen_server.siblings) + 1
                                    <= mass.event.n_servers
                            ):
                                n_servers_assigned += assign_single_server(chosen_server, mass,
                                                                           servers)
                                for sibling in chosen_server.siblings:
                                    n_servers_assigned += assign_single_server(sibling, mass,
                                                                               servers)
                            else:
                                raise BadSituationError
                    else:
                        n_servers_assigned += assign_single_server(chosen_server, mass, servers)


def server_not_assigned_this_day(chosen_server, day):
    """Check if a server has been assigned on this day already.

    That can be due to high-priority assignments or custom masses that take place on the same day as
    normal masses.
    :param chosen_server: The chosen server.
    :param day: The day to check.
    :return: True, if the server has not been assigned on this day yet. False otherwise.
    """
    for mass in day.masses:
        if chosen_server in mass.servers:
            return False
    return True


def is_available(
        servers: AltarServers, chosen_server: AltarServer, day: Day, mass: HolyMass
) -> bool:
    """Check if a server is available at a certain mass.

    This is required, because not all siblings may available at a certain mass.
    :param servers: The servers object.
    :param chosen_server: The server to check the availability for.
    :param day: The day of the mass.
    :param mass: The holy mass.
    :return: True if the server is available, else False.
    """
    day_queue = get_queue_for_event(servers, day.event_day, mass.event)
    return chosen_server in list(day_queue.queue)


def assign_high_mass_priority_servers(mass: HolyMass, n_servers_assigned: int,
                                      servers: AltarServers) -> int:
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
        servers.high_mass_priority.put(chosen_server)
        n_servers_assigned += 1
        chosen_server.number_of_services += 1
        servers.choose(chosen_server)
    return n_servers_assigned


def assign_single_server(chosen_server: AltarServer, mass: HolyMass, servers: AltarServers) -> int:
    """Assign a server without siblings to a mass.

    :param chosen_server: The server.
    :param mass: The mass to assign the server to.
    :param servers: Wrapper object of all servers.
    :return: 1 to increase the counter.
    """
    mass.add_server(chosen_server)
    servers.choose(chosen_server)
    chosen_server.number_of_services += 1
    return 1


def get_server_from_queues(servers: AltarServers, day: Day, mass: HolyMass) -> AltarServer:
    """Get a server from the correct queue.

    If the queue for an event is empty, it is refilled. The server is only chosen, if it has not
    been chosen this round. This mechanism is required, because of the sibling mechanism. It is
    possible that a server was already assigned because of its sibling. The counter ensures that if
    all servers in the queue have been assigned already, the already assigned list is cleared.
    :param servers: Wrapper object of all servers.
    :param day: Holds the information about the day.
    :param mass: Holds the information about the mass.
    :return: The chosen server.
    """
    count = 0
    while True:
        day_queue = get_queue_for_event(servers, day.event_day, mass.event)
        if day_queue.empty():
            servers.fill_queue_for(day.event_day, mass.event)
        next_server = day_queue.get_nowait()

        if next_server not in servers.already_chosen_this_round and day.available(next_server):
            break

        day_queue.put(next_server)

        count += 1
        if count > len(day_queue.queue):
            servers.empty_already_chosen_list()

    return next_server


def get_queue_for_event(servers: AltarServers, event_day: EventDay, event: Event) -> queue.Queue:
    """Get the queue from which the servers must be taken for a given event.

    :param servers: The servers object.
    :param event_day: The event day.
    :param event: The event object.
    :return: The queue from which the servers must be taken.
    """
    if (
            event_day.id in servers.regular_queues
            and event.time in servers.regular_queues[event_day.id]
    ):
        return servers.regular_queues[event_day.id][event.time]
    elif event.time in servers.regular_queues["SUNDAY"]:
        return servers.regular_queues["SUNDAY"][event.time]

    return servers.other_queue
