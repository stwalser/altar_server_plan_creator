from queue import Empty

from altar_server import AltarServer, AltarServers
from holy_mass import Day, HolyMass


def assign_altar_servers(calendar: list, servers: AltarServers) -> None:
    for day in calendar:
        for mass in day.masses:
            n_servers_assigned = 0
            while n_servers_assigned < mass.event.n_servers:
                chosen_server = get_server_from_queues(servers, day, mass)

                if chosen_server.has_siblings():
                    if n_servers_assigned + len(chosen_server.siblings) + 1 <= mass.event.n_servers:
                        mass.add_server(chosen_server)
                        servers.queue.put(chosen_server)
                        n_servers_assigned += 1

                        for sibling in chosen_server.siblings:
                            if sibling.is_available(day.event_day, mass.event):
                                mass.add_server(sibling)
                                sibling.already_chosen_this_round = True
                                n_servers_assigned += 1
                else:
                    mass.add_server(chosen_server)
                    servers.queue.put(chosen_server)
                    n_servers_assigned += 1


def get_server_from_queues(servers: AltarServers, day: Day, mass: HolyMass) -> AltarServer:
    class SameElementTwice(Exception):
        pass

    old_unsuitable = None
    while True:
        while True:
            try:
                chosen_server = servers.waiting.get_nowait()
                if chosen_server == old_unsuitable:
                    raise SameElementTwice
            except (Empty, SameElementTwice):
                chosen_server = servers.queue.get_nowait()

            if chosen_server.already_chosen_this_round:
                chosen_server.already_chosen_this_round = False
                servers.queue.put(chosen_server)
            else:
                break

        if not chosen_server.is_available(day.event_day, mass.event):
            old_unsuitable = chosen_server
            servers.waiting.put(chosen_server)
        else:
            return chosen_server
