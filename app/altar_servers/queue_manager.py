"""The queue manager module."""

import random
from collections import deque

from altar_servers.altar_servers import AltarServers
from altar_servers.scheduling_unit import SchedulingUnit
from dates.day import Day
from dates.holy_mass import HolyMass
from events.event import Event
from events.event_calendar import EventCalendar


def list_to_queue(collection1: list, collection: deque) -> None:
    """Add all elements from the list to a queue."""
    for item in collection1:
        collection.append(item)


class QueueManager:
    """The queue manager."""

    def __init__(
        self: "QueueManager", event_calendar: EventCalendar, altar_servers: AltarServers
    ) -> None:
        """Create a QueueManager.

        :param event_calendar: The event calendar.
        :param altar_servers: The altar servers.
        """
        self.event_calendar = event_calendar
        self.__altar_servers = altar_servers

        self.__regular_queues = {}
        self.__regular_queues_cache = {}

        for event_day in event_calendar.weekday.values():
            for event in event_day.events:
                self.__regular_queues[event] = deque()
                self.__regular_queues_cache[event] = []

        self.__shuffle_and_rebuild_cache()
        self.__other_queue = deque()  # All servers get refilled
        self.__fill_all_refillable_queues()

    def __shuffle_and_rebuild_cache(self: "QueueManager") -> None:
        """Shuffle the altar server list and rebuild the cache.

        This is done to maintain an order over the different queues. The alternative
        would be to shuffle before assigning the servers to the individual queues, but then some
        could be assigned in rapid succession. This way we are keeping rounds of assignments.
        """
        random.shuffle(self.__altar_servers.scheduling_units)

        for event in self.__regular_queues:
            self.__regular_queues[event].clear()
            self.__regular_queues_cache[event] = (
                self.__altar_servers.get_available_scheduling_units(event)
            )

    def __fill_all_refillable_queues(self: "QueueManager") -> None:
        """Take the servers from the cache and assign them to the individual queues."""
        self.__other_queue.clear()
        list_to_queue(self.__altar_servers.scheduling_units, self.__other_queue)

        for event in self.__regular_queues:
            self.__regular_queues[event].clear()
            list_to_queue(self.__regular_queues_cache[event], self.__regular_queues[event])

    def __refill_queue_for(self: "QueueManager", event: Event) -> None:
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

        list_to_queue(self.__scheduling_units, self.__other_queue)

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

    def get_su_from_queues(self: "QueueManager", day: Day, mass: HolyMass) -> SchedulingUnit:
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
        day_queue = self.__get_queue_for_event(mass.event)

        while True:
            try:
                next_su: SchedulingUnit = day_queue.popleft()
            except IndexError:
                self.__refill_queue_for(mass.event)
                continue

            potential_weekday_id = self.event_calendar.custom_event_is_weekday_in_special(
                day.date, mass.event.time
            )
            if self.__altar_servers.su_is_available_at(
                next_su, day, mass, potential_weekday_id
            ) and self.__altar_servers.su_is_considered(next_su, mass.event.id):
                break

            count += 1
            if count > len(day_queue):
                self.__altar_servers.empty_already_chosen_list()

        return next_su

    def clear_state(self: "QueueManager") -> None:
        """Remove all information in the object that is added during one round."""
        self.__altar_servers.clear_state()

        self.__shuffle_and_rebuild_cache()
        self.__fill_all_refillable_queues()
