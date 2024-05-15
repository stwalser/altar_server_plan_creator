"""A module that contains the functionality of assigning servers to masses."""

import queue

from altar_server import AltarServer, AltarServers
from event_calendar import EventDay, Event
from holy_mass import Day, HolyMass


class SameServerTwiceError(Exception):
    """Simple Exception that is thrown when a server has already been considered for a mass."""


def assign_altar_servers(calendar: list, servers: AltarServers) -> None:
    """Assign altar servers to a calendar consisting of multiple masses.

    :param calendar: The list of all days, where a mass takes place.
    :param servers: Wrapper object of all servers.
    """
    for day in calendar:
        print(day)
        for mass in day.masses:
            print(mass)
            n_servers_assigned = 0

            if mass.event.high_mass:
                n_servers_assigned = assign_high_mass_priority_servers(
                    mass, n_servers_assigned, servers
                )

            while n_servers_assigned < mass.event.n_servers:
                chosen_server = get_server_from_queues(servers, day, mass)
                print(chosen_server)
                if chosen_server.has_siblings():
                    if all(
                            [
                                is_available(servers, sibling, day.event_day, mass.event)
                                for sibling in chosen_server.siblings
                            ]
                    ):
                        if (
                                n_servers_assigned + len(chosen_server.siblings) + 1
                                <= mass.event.n_servers
                        ):
                            n_servers_assigned += assign_single_server(chosen_server, mass, servers)
                            for sibling in chosen_server.siblings:
                                n_servers_assigned += assign_single_server(sibling, mass, servers)
                        else:
                            reinsert_server_into_queue(servers, chosen_server, day, mass)
                            prevent_endless_loop(servers, chosen_server, day.event_day, mass.event)
                else:
                    n_servers_assigned += assign_single_server(chosen_server, mass, servers)


def is_available(
        servers: AltarServers, chosen_server: AltarServer, event_day: EventDay, event: Event
) -> bool:
    day_queue = get_queue_for_event(servers, event_day, event)
    return chosen_server in list(day_queue.queue)


def prevent_endless_loop(
        servers: AltarServers, chosen_server: AltarServer, event_day: EventDay, event: Event
) -> None:
    day_queue = get_queue_for_event(servers, event_day, event)
    if all([server.has_siblings() for server in day_queue.queue]):
        servers.fill_queue_for(event_day, event)


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


def reinsert_server_into_queue(
        servers: AltarServers, server: AltarServer, day: Day, mass: HolyMass
) -> None:
    if (
            day.event_day.id in servers.regular_queues
            and mass.event.time in servers.regular_queues[day.event_day.id]
    ):
        servers.regular_queues[day.event_day.id][mass.event.time].put(server)
    else:
        servers.other_queue.put(server)


def get_server_from_queues(servers: AltarServers, day: Day, mass: HolyMass) -> AltarServer:
    """
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
            print("Refilled", mass, day_queue.queue)
        next_server = day_queue.get_nowait()

        if next_server not in servers.already_chosen_this_round:
            break
        else:
            day_queue.put(next_server)

        count += 1
        if count > len(day_queue.queue):
            servers.empty_already_chosen_list()

    return next_server


def get_queue_for_event(servers: AltarServers, event_day: EventDay, event: Event) -> queue.Queue:
    if (
            event_day.id in servers.regular_queues
            and event.time in servers.regular_queues[event_day.id]
    ):
        return servers.regular_queues[event_day.id][event.time]
    else:
        return servers.other_queue
