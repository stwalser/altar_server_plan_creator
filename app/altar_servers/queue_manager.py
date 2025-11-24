"""The queue manager module."""

import random
from collections import deque

from altar_servers.altar_servers import AltarServers
from altar_servers.scheduling_unit import SchedulingUnit
from dates.day import Day
from dates.holy_mass import HolyMass
from events.event_calendar import EventCalendar
from utils.exceptions import BadSituationError


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

        self.__regular_queues: dict[str, deque] = {}
        self.__other_queue = deque()  # All servers get refilled

        for event_day in event_calendar.weekday.values():
            for event in event_day.events:
                self.__regular_queues[event.id] = deque()

        self.__shuffle_clear_and_fill_queues()

    def __shuffle_clear_and_fill_queues(self: "QueueManager") -> None:
        """Shuffle the altar server list and rebuild the cache.

        This is done to maintain an order over the different queues. The alternative
        would be to shuffle before assigning the servers to the individual queues, but then some
        could be assigned in rapid succession. This way we are keeping rounds of assignments.
        """
        random.shuffle(self.__altar_servers.scheduling_units)

        for event_id in self.__regular_queues:
            self.__regular_queues[event_id].clear()
            list_to_queue(
                self.__altar_servers.get_available_scheduling_units(event_id),
                self.__regular_queues[event_id],
            )

        self.__other_queue.clear()
        list_to_queue(
            list(filter(lambda x: not x.no_special, self.__altar_servers.scheduling_units)),
            self.__other_queue,
        )

    def __get_queue_for_event(self: "AltarServers", identifier: str) -> deque:
        """Get the queue from which the servers must be taken for a given event.

        :param treated_as_id: The event object.
        :return: The queue from which the servers must be taken.
        """
        if identifier in self.__regular_queues:
            return self.__regular_queues[identifier]

        return self.__other_queue

    def get_su_from_queues(
        self: "QueueManager", day: Day, mass: HolyMass, did_not_fit: list
    ) -> SchedulingUnit:
        """Get a server from the correct queue.

        If the queue for an event is empty, it is refilled. The server is only chosen, if it has not
        been chosen this round. This mechanism is required, because of the sibling mechanism. It is
        possible that a server was already assigned because of its sibling. The counter ensures that
        if all servers in the queue have been assigned already, the already assigned list is
        cleared.
        :param did_not_fit:
        :param day: Holds the information about the day.
        :param mass: Holds the information about the mass.
        :return: The chosen server.
        """
        count = 0
        emptied = False
        day_queue = self.__get_queue_for_event(
            mass.event.treated_as if mass.event.treated_as is not None else mass.event.id
        )

        while True:
            next_su: SchedulingUnit = day_queue.popleft()
            day_queue.append(next_su)  # Re-insert

            if next_su in did_not_fit:
                raise BadSituationError

            if self.__altar_servers.su_is_available_at(next_su, day, mass):
                break

            count += 1
            if count > len(day_queue):
                if emptied:
                    raise BadSituationError
                self.__altar_servers.empty_already_chosen_list()
                emptied = True

        return next_su

    def clear_state(self: "QueueManager") -> None:
        """Remove all information in the object that is added during one round."""
        self.__altar_servers.clear_state()

        self.__shuffle_clear_and_fill_queues()
