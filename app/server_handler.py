import copy
import random

from altar_server import AltarServer, AltarServers


def assign_altar_servers(calendar: list, servers: AltarServers) -> None:
    not_assigned_servers = copy.deepcopy(servers.all)
    assigned_servers = []

    for day in calendar:
        for mass in day.masses:
            n_servers_assigned = 0
            while n_servers_assigned < mass.event.n_servers:
                try:
                    chosen_server: AltarServer = random.choice(not_assigned_servers)
                except IndexError:
                    not_assigned_servers = assigned_servers
                    assigned_servers = []
                    chosen_server = random.choice(not_assigned_servers)

                if chosen_server.has_siblings():
                    if n_servers_assigned + len(chosen_server.siblings) + 1 <= mass.event.n_servers:
                        mass.add_server(chosen_server)
                        move(chosen_server, not_assigned_servers, assigned_servers)
                        for sibling in chosen_server.siblings:
                            mass.add_server(sibling)
                            move(sibling, not_assigned_servers, assigned_servers)

                        n_servers_assigned += len(chosen_server.siblings) + 1
                else:
                    mass.add_server(chosen_server)
                    move(chosen_server, not_assigned_servers, assigned_servers)
                    n_servers_assigned += 1


def move(element, a: list, b: list) -> None:
    a.remove(element)
    b.append(element)


def find_dict_in_list(key: str, list: list) -> dict:
    for ele in list:
        if type(ele) is dict and key in ele:
            return ele
