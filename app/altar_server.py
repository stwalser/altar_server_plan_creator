"""A module that contains the class that represents a server and also contains the wrapper class."""

import logging
import queue
import random
from datetime import datetime

from event_calendar import Event, EventDay, EventCalendar


class AltarServer:
    """The altar server class, containing the information of one server and convenience methods."""

    def __init__(self: "AltarServer", raw_altar_server: dict) -> None:
        """Create an altar server object from a dictionary that contains all the info.

        :param raw_altar_server: The dictionary with the info on the server.
        """
        self.name = ""
        self.siblings = []
        self.avoid = []
        self.locations = []
        self.always_high_mass = False
        self.number_of_services = 0

        if isinstance(raw_altar_server, str):
            self.name = raw_altar_server
        elif isinstance(raw_altar_server, dict):
            self.name = next(iter(raw_altar_server))
            inner = raw_altar_server[self.name]
            if "siblings" in inner:
                self.siblings = inner["siblings"]
            if "avoid" in inner:
                for element in inner["avoid"]:
                    try:
                        time = datetime.strptime(element, "%H:%M").astimezone().time()
                        self.avoid.append(time)
                    except ValueError:
                        self.avoid.append(element)
            if "always_high_mass" in inner:
                self.always_high_mass = True
            if "locations" in inner:
                self.locations = inner["locations"]

    def has_siblings(self: "AltarServer") -> bool:
        """Check if a server has siblings.

        :return: True if the server has siblings, else False.
        """
        return len(self.siblings) > 0

    def __str__(self: "AltarServer") -> str:
        """Return string representation of the object."""
        return str(self.name)

    def __repr__(self: "AltarServer") -> str:
        """Return string representation of the object."""
        return str(self.name)


class AltarServers:
    """The altar server class contains the queues that manage the servers.

    There is a queue for all servers and one for those that were chosen for a certain mass,
    but could not be assigned due to different reasons. This waiting queue has priority over the
    other queues. The high mass priority queue is for servers which should preferred at high
    masses.
    """

    def __init__(
        self: "AltarServers", raw_altar_servers: dict, event_calendar: EventCalendar
    ) -> None:
        """Create the altar servers object, which holds the different queues.

        :param raw_altar_servers: The dictionary containing all the altar servers and their info.
        """
        self.altar_servers = [
            AltarServer(raw_altar_server) for raw_altar_server in raw_altar_servers
        ]
        random.shuffle(self.altar_servers)

        for altar_server in self.altar_servers:
            if altar_server.has_siblings():
                object_list = [
                    next(filter(lambda x: x.name == sibling_name, self.altar_servers))
                    for sibling_name in altar_server.siblings
                ]
                altar_server.siblings = object_list

        self.regular_queues = {}
        self.other_queue = queue.Queue()
        self.high_mass_priority = queue.Queue()

        self.already_chosen_this_round = []

        for event_day in event_calendar.weekday_events.values():
            self.regular_queues[event_day.id] = {}
            for event in event_day.events:
                self.regular_queues[event_day.id][event.time] = queue.Queue()
                self.fill_queue_for(event_day, event)
                print(event, self.regular_queues[event_day.id][event.time].queue)

        for altar_server in self.altar_servers:
            self.other_queue.put(altar_server)

        for altar_server in list(filter(lambda x: x.always_high_mass, self.altar_servers)):
            self.high_mass_priority.put(altar_server)

    def print_distribution(self):
        for server in sorted(self.altar_servers, key=lambda x: x.name):
            print(server.name, server.number_of_services)

    def fill_queue_for(self: "AltarServers", event_day: EventDay, event: Event) -> None:
        if event_day.id not in self.regular_queues:
            for altar_server in self.altar_servers:
                self.other_queue.put(altar_server)
        else:
            print(type(event.time))
            for server in self.altar_servers:
                print(server.avoid)
            for altar_server in list(
                filter(
                    lambda x: event_day.id not in x.avoid and event.time not in x.avoid,
                    self.altar_servers,
                )
            ):
                self.regular_queues[event_day.id][event.time].put(altar_server)

    def choose(self: "AltarServers", server: AltarServer) -> None:
        self.already_chosen_this_round.append(server)
        if len(self.already_chosen_this_round) == len(self.altar_servers):
            self.empty_already_chosen_list()

    def empty_already_chosen_list(self):
        self.already_chosen_this_round = []
