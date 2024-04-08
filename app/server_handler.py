import copy
import random


def add_servers_to_masses(masses: list, servers: list) -> None:
    not_assigned_servers = copy.deepcopy(servers)
    assigned_servers = []

    for day in masses:
        for mass in day.masses:
            n_servers_assigned = 0
            while n_servers_assigned < mass.n_servers:
                try:
                    chosen_server = random.choice(not_assigned_servers)
                except IndexError:
                    not_assigned_servers = assigned_servers
                    assigned_servers = []
                    chosen_server = random.choice(not_assigned_servers)

                if type(chosen_server) is str:
                    mass.add_server(chosen_server)
                    move(chosen_server, not_assigned_servers, assigned_servers)
                    n_servers_assigned += 1
                else:
                    inner_data = chosen_server[list(chosen_server)[0]]
                    if n_servers_assigned + len(inner_data["siblings"]) + 1 <= mass.n_servers:
                        mass.add_server(list(chosen_server)[0])
                        move(chosen_server, not_assigned_servers, assigned_servers)
                        for server in inner_data["siblings"]:
                            mass.add_server(server)
                            sibling = find_dict_in_list(server, servers)
                            move(sibling, not_assigned_servers, assigned_servers)

                        n_servers_assigned += len(inner_data["siblings"]) + 1


def move(element, a: list, b: list) -> None:
    a.remove(element)
    b.append(element)


def find_dict_in_list(key: str, list: list) -> dict:
    for ele in list:
        if type(ele) is dict and key in ele:
            return ele
