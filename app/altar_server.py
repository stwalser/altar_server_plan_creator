"""A module that contains the class that represents a server and also contains the wrapper class."""

import logging
import queue
import random
from datetime import datetime

from event_calendar import Event, EventDay


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
        self.already_chosen_this_round = False
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

    def is_available(self: "AltarServer", event_day: EventDay, event: Event) -> bool:
        """Check if a server is available on a certain date or location.

        :param event_day: The event day object containing the info on the day.
        :param event: The event object containing info on the event itself.
        :return: True if the server is available, else False.
        """
        if event.location != "" and event.location not in self.locations:
            return False

        if event_day.id in self.avoid or event.time in self.avoid:
            return False

        return True

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

    def __init__(self: "AltarServers", raw_altar_servers: dict) -> None:
        """Create the altar servers object, which holds the different queues.

        :param raw_altar_servers: The dictionary containing all the altar servers and their info.
        """
        altar_servers = [AltarServer(raw_altar_server) for raw_altar_server in raw_altar_servers]

        for altar_server in altar_servers:
            if altar_server.has_siblings():
                object_list = [
                    next(filter(lambda x: x.name == sibling_name, altar_servers))
                    for sibling_name in altar_server.siblings
                ]
                altar_server.siblings = object_list

        self.queue = queue.Queue()
        self.waiting = queue.Queue()
        self.high_mass_priority = queue.Queue()

        self.shuffle_servers(altar_servers)

        for altar_server in list(filter(lambda x: x.always_high_mass, altar_servers)):
            self.high_mass_priority.put(altar_server)

    def shuffle_servers(self, altar_servers):
        """Shuffle the servers and assign them to the queue randomly.

        :param altar_servers: The servers
        """
        random.shuffle(altar_servers)
        self.queue = queue.Queue()
        for altar_server in altar_servers:
            self.queue.put(altar_server)

    def print_distribution(self):
        for server in sorted(list(self.queue.queue), key=lambda x: x.name):
            print(server.name, server.number_of_services)
        for server in sorted(list(self.waiting.queue), key=lambda x: x.name):
            print(server.name, server.number_of_services)
