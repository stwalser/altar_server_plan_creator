from queue import Empty

from altar_server import AltarServer, AltarServers
from holy_mass import Day, HolyMass


class SameElementTwice(Exception):
    pass


def assign_altar_servers(calendar: list, servers: AltarServers) -> None:
    for day in calendar:
        for mass in day.masses:
            n_servers_assigned = 0
            if mass.event.high_mass:
                n_servers_assigned = assign_priority_servers(mass, n_servers_assigned, servers)

            while n_servers_assigned < mass.event.n_servers:
                chosen_server = get_server_from_queues(servers, day, mass)

                if chosen_server.has_siblings():
                    if n_servers_assigned + len(chosen_server.siblings) + 1 <= mass.event.n_servers:
                        n_servers_assigned += assign_server(chosen_server, mass, servers)

                        for sibling in chosen_server.siblings:
                            if sibling.is_available(day.event_day, mass.event):
                                n_servers_assigned += assign_server(sibling, mass, servers, True)
                else:
                    n_servers_assigned += assign_server(chosen_server, mass, servers)


def assign_priority_servers(mass, n_servers_assigned, servers):
    already_considered = []
    while n_servers_assigned < mass.event.n_servers:
        chosen_server = servers.high_mass_priority.get_nowait()
        if chosen_server in already_considered:
            return n_servers_assigned

        already_considered.append(chosen_server)
        mass.add_server(chosen_server)
        chosen_server.already_chosen_this_round = True
        servers.high_mass_priority.put(chosen_server)
        n_servers_assigned += 1
    return n_servers_assigned


def assign_server(chosen_server, mass, servers, out_of_order=False):
    mass.add_server(chosen_server)
    if out_of_order:
        chosen_server.already_chosen_this_round = True
    else:
        servers.queue.put(chosen_server)
    return 1


def get_server_from_queues(servers: AltarServers, day: Day, mass: HolyMass) -> AltarServer:
    already_considered = []
    while True:
        while True:
            try:
                chosen_server = servers.waiting.get_nowait()
                if chosen_server in already_considered:
                    raise SameElementTwice
            except (Empty, SameElementTwice):
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
