"""A module that contains the class that represents a server and also contains the wrapper class."""

import queue
import random
from datetime import datetime

from event_calendar import Event, EventCalendar, EventDay


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
                    except (ValueError, TypeError):
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


def list_to_queue(altar_servers: list, collection: queue.Queue) -> None:
    """Add all elements fromo the list to a queue."""
    for altar_server in altar_servers:
        collection.put(altar_server)


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
        self.__add_siblings_to_objects()

        self.regular_queues = {}
        self.regular_queues_cache = {}

        for event_day in event_calendar.weekday_events.values():
            self.regular_queues[event_day.id] = {}
            self.regular_queues_cache[event_day.id] = {}
            for event in event_day.events:
                self.regular_queues[event_day.id][event.time] = queue.Queue()
                self.regular_queues_cache[event_day.id][event.time] = []

        self.__shuffle_and_rebuild_cache()

        self.other_queue = queue.Queue()  # All servers get refilled
        self.__fill_all_refillable_queues()

        self.high_mass_priority = queue.Queue()  # Doesn't get empty -> No refill
        list_to_queue(list(filter(lambda x: x.always_high_mass, self.altar_servers)),
                      self.high_mass_priority)

        self.already_chosen_this_round = []

    def __shuffle_and_rebuild_cache(self: "AltarServers") -> None:
        """Shuffle the altar server list and rebuild the cache.

        This is done to maintain an order over the different queues. The alternative
        would be to shuffle before assigning the servers to the individual queues, but then some
        could be assigned in rapid succession. This way we are keeping rounds of assignments.
        """
        random.shuffle(self.altar_servers)

        for event_id in self.regular_queues:
            for time in self.regular_queues[event_id]:
                self.regular_queues[event_id][time] = queue.Queue()
                self.regular_queues_cache[event_id][time] = self.__get_available_servers(event_id,
                                                                                         time)

    def __add_siblings_to_objects(self: "AltarServers") -> None:
        """Get the sibling objects from the list and add them to the individual sibling lists."""
        for altar_server in self.altar_servers:
            if altar_server.has_siblings():
                object_list = [
                    next(filter(lambda x: x.name == sibling_name, self.altar_servers))
                    for sibling_name in altar_server.siblings
                ]
                altar_server.siblings = object_list

    def __fill_all_refillable_queues(self: "AltarServers") -> None:
        """Take the servers from the cache and assign them to the individual queues."""
        self.other_queue = queue.Queue()
        list_to_queue(self.altar_servers, self.other_queue)

        for event_id in self.regular_queues:
            for time in self.regular_queues[event_id]:
                self.regular_queues[event_id][time] = queue.Queue()
                list_to_queue(self.regular_queues_cache[event_id][time],
                              self.regular_queues[event_id][time])

    def __get_available_servers(self: "AltarServers", event_id: str, time: datetime.time) -> list:
        return list(
            filter(lambda x: event_id not in x.avoid and time not in x.avoid, self.altar_servers )
        )

    def clear_state(self: "AltarServers") -> None:
        """Remove all information in the object that is added during one round."""
        self.already_chosen_this_round = []

        for server in self.altar_servers:
            server.number_of_services = 0

        self.__shuffle_and_rebuild_cache()
        self.__fill_all_refillable_queues()


    def fill_queue_for(self: "AltarServers", event_day: EventDay, event: Event) -> None:
        """Add all the servers which are available at the given event to the queue of the mass.

        :param event_day: The event day.
        :param event: The event.
        """
        if (
                event_day.id in self.regular_queues
                and event.time in self.regular_queues[event_day.id]
        ):
            list_to_queue(self.regular_queues_cache[event_day.id][event.time],
                          self.regular_queues[event_day.id][event.time])
        elif event.time in self.regular_queues["SUNDAY"]:
            list_to_queue(self.regular_queues_cache["SUNDAY"][event.time],
                          self.regular_queues["SUNDAY"][event.time])
        else:
            list_to_queue(self.altar_servers, self.other_queue)

    def choose(self: "AltarServers", server: AltarServer) -> None:
        """Add a server to the already chosen list.

        If the length of the list equals the number of the servers, the list is cleared.
        :param server: The server to add to the list.
        """
        self.already_chosen_this_round.append(server)
        if len(self.already_chosen_this_round) == len(self.altar_servers):
            self.empty_already_chosen_list()

    def empty_already_chosen_list(self: "AltarServers") -> None:
        """Delete all entries from the already chosen list."""
        self.already_chosen_this_round = []


def get_distribution(altar_servers: list) -> list:
    """Get how often each server was assigned on the plan."""
    return [
        (server.name, server.number_of_services)
        for server in sorted(altar_servers, key=lambda x: x.name)
    ]
