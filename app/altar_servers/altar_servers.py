"""A module that contains the altar server wrapper class."""

import random
from collections import deque

from altar_servers.altar_server import AltarServer
from altar_servers.scheduling_unit import SchedulingUnit
from dates.day import Day
from dates.holy_mass import HolyMass
from events.event import Event
from events.event_calendar import EventCalendar


def list_to_queue(collection1: list, collection: deque) -> None:
    """Add all elements from the list to a queue."""
    for item in collection1:
        collection.append(item)


def get_distribution(altar_servers: list) -> list:
    """Get how often each server was assigned on the plan."""
    return [
        (server.name, len(server.service_dates))
        for server in sorted(altar_servers, key=lambda x: x.name)
    ]


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
        self.scheduling_units = []
        self.__create_scheduling_units()

        self.__regular_queues = {}
        self.__regular_queues_cache = {}

        for event_day in event_calendar.weekday_events.values():
            for event in event_day.events:
                self.__regular_queues[event] = deque()
                self.__regular_queues_cache[event] = []

        self.__shuffle_and_rebuild_cache()

        self.__other_queue = deque()  # All servers get refilled
        self.__fill_all_refillable_queues()

        self.high_mass_priority = deque()  # Doesn't get empty -> No refill
        list_to_queue(
            list(filter(lambda x: x.always_high_mass, self.scheduling_units)),
            self.high_mass_priority,
        )

        self.already_chosen_this_round = []

    def __shuffle_and_rebuild_cache(self: "AltarServers") -> None:
        """Shuffle the altar server list and rebuild the cache.

        This is done to maintain an order over the different queues. The alternative
        would be to shuffle before assigning the servers to the individual queues, but then some
        could be assigned in rapid succession. This way we are keeping rounds of assignments.
        """
        for event in self.__regular_queues:
            random.shuffle(self.scheduling_units)
            self.__regular_queues[event].clear()
            self.__regular_queues_cache[event] = self.__get_available_scheduling_units(event)

    def __create_scheduling_units(self: "AltarServers") -> None:
        for altar_server in self.altar_servers:
            if not any(altar_server in unit.minis for unit in self.scheduling_units):
                self.scheduling_units.append(SchedulingUnit([altar_server, *altar_server.siblings]))

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
        self.__other_queue.clear()
        list_to_queue(self.scheduling_units, self.__other_queue)

        for event in self.__regular_queues:
            self.__regular_queues[event].clear()
            list_to_queue(self.__regular_queues_cache[event], self.__regular_queues[event])

    def __get_available_scheduling_units(self: "AltarServers", event: Event) -> list:
        return list(filter(lambda x: event.id not in x.avoid, self.scheduling_units))

    def clear_state(self: "AltarServers") -> None:
        """Remove all information in the object that is added during one round."""
        self.already_chosen_this_round = []

        for server in self.altar_servers:
            server.service_dates = []

        self.__shuffle_and_rebuild_cache()
        self.__fill_all_refillable_queues()

    def __refill_queue_for(self: "AltarServers", event: Event) -> None:
        """Add all the servers which are available at the given event to the queue of the mass.

        :param event: The event.
        """
        if event in self.__regular_queues:
            list_to_queue(self.__regular_queues_cache[event], self.__regular_queues[event])
            return

        for key in self.__regular_queues:
            if key.time == event.time:
                list_to_queue(self.__regular_queues_cache[key], self.__regular_queues[key])
                return

        list_to_queue(self.scheduling_units, self.__other_queue)

    def __get_queue_for_event(self: "AltarServers", event: Event) -> deque:
        """Get the queue from which the servers must be taken for a given event.

        :param event: The event object.
        :return: The queue from which the servers must be taken.
        """
        if event in self.__regular_queues:
            return self.__regular_queues[event]

        for key in self.__regular_queues:
            if key.time == event.time:
                return self.__regular_queues[key]

        return self.__other_queue

    def get_su_from_queues(self: "AltarServers", day: Day, mass: HolyMass) -> AltarServer:
        """Get a server from the correct queue.

        If the queue for an event is empty, it is refilled. The server is only chosen, if it has not
        been chosen this round. This mechanism is required, because of the sibling mechanism. It is
        possible that a server was already assigned because of its sibling. The counter ensures that
        if all servers in the queue have been assigned already, the already assigned list is
        cleared.
        :param day: Holds the information about the day.
        :param mass: Holds the information about the mass.
        :return: The chosen server.
        """
        count = 0
        while True:
            day_queue = self.__get_queue_for_event(mass.event)
            try:
                next_su = day_queue.popleft()
            except IndexError:
                self.__refill_queue_for(mass.event)
                continue

            if (next_su not in self.already_chosen_this_round
                    and next_su.is_available(day.date)
                    and day.server_not_assigned(next_su)
                    and (mass.event.location is None or mass.event.location in next_su.locations)
            ):
                break

            count += 1
            if count > len(day_queue):
                self.__empty_already_chosen_list()

        return next_su

    def is_available(self: "AltarServers", chosen_server: AltarServer, mass: HolyMass) -> bool:
        """Check if a server is available at a certain mass.

        This is required, because not all siblings may available at a certain mass.
        :param chosen_server: The server to check the availability for.
        :param day: The day of the mass.
        :param mass: The holy mass.
        :return: True if the server is available, else False.
        """
        day_queue = self.__get_queue_for_event(mass.event)
        try:
            day_queue.index(chosen_server)
        except ValueError:
            return False
        else:
            return True

    def assign_scheduling_unit(self: "AltarServers", scheduling_unit: SchedulingUnit,
                               mass: HolyMass) -> int:
        """Assign a server without siblings to a mass.

        :param scheduling_unit: The scheduling unit.
        :param mass: The mass to assign the server to.
        :return: 1 to increase the counter.
        """
        mass.add_scheduling_unit(scheduling_unit)
        self.__choose_for(scheduling_unit, mass)
        return len(scheduling_unit)

    def assign_high_mass_priority_servers(
            self: "AltarServers", mass: HolyMass, n_servers_assigned: int
    ) -> int:
        """Assign servers to a mass that are prioritized for high masses.

        :param mass: The holy mass.
        :param n_servers_assigned: The number of servers assigned to the mass before the
        prioritization.
        :return: The number of servers assigned to the mass after the prioritization.
        """
        already_considered = []
        while n_servers_assigned < mass.event.n_servers:
            chosen_su = self.high_mass_priority.popleft()
            if chosen_su in already_considered:
                self.high_mass_priority.append(chosen_su)
                return n_servers_assigned

            already_considered.append(chosen_su)
            mass.add_scheduling_unit(chosen_su)
            self.high_mass_priority.append(chosen_su)
            n_servers_assigned += 1
            self.__choose_for(chosen_su, mass)
        return n_servers_assigned

    def __choose_for(self: "AltarServers", su: SchedulingUnit, mass: HolyMass) -> None:
        """Add a server to the already chosen list.

        If the length of the list equals the number of the servers, the list is cleared.
        :param su: The scheduling unit to add extend the list for.
        """
        for server in su.minis:
            server.service_dates.append(mass.day.date)
        self.already_chosen_this_round.append(su)
        if len(self.already_chosen_this_round) == len(self.altar_servers):
            self.__empty_already_chosen_list()

    def __empty_already_chosen_list(self: "AltarServers") -> None:
        """Delete all entries from the already chosen list."""
        self.already_chosen_this_round = []