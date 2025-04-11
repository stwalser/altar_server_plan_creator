"""A module that contains the altar server wrapper class."""

import copy
import itertools
import secrets
import statistics

from altar_servers.altar_server import AltarServer
from altar_servers.scheduling_unit import SchedulingUnit
from dates.day import Day
from dates.holy_mass import HolyMass
from events.event import Event
from pydantic import BaseModel


def get_distribution(altar_servers: list) -> list:
    """Get how often each server was assigned on the plan."""
    return [
        (server.name, len(server.service_dates))
        for server in sorted(altar_servers, key=lambda x: x.name)
    ]


def su_is_considered(su: SchedulingUnit, event_id: str) -> bool:
    """Check if a scheduling unit should be considered for an event.

    :param su: The scheduling unit to check.
    :param event_id: The id of the event to check.
    :return: True, if the scheduling unit should be considered. False, otherwise.
    """
    values = []
    for server in su.servers:
        if event_id in server.fine_tuner:
            values.append(server.fine_tuner[event_id])
        else:
            values.append(1)
    return (secrets.randbelow(100) / 100) <= statistics.mean(values)


class AltarServers(BaseModel):
    """The altar server class contains the queues that manage the servers.

    There is a queue for all servers and one for those that were chosen for a certain mass,
    but could not be assigned due to different reasons. This waiting queue has priority over the
    other queues. The high mass priority queue is for servers which should preferred at high
    masses.
    """

    altar_servers: list[AltarServer]

    def model_post_init(self: "AltarServers", *_: str) -> None:
        """Create the altar servers object, which holds the different queues.

        :param context: The pydantic context
        """
        self.__add_siblings_to_objects()
        self.__scheduling_units = []
        self.__create_scheduling_units()

        self.__already_chosen_this_round = []

    @property
    def scheduling_units(self: "AltarServers") -> list:
        """Get all scheduling units.

        :return: The scheduling units.
        """
        return self.__scheduling_units

    def empty_already_chosen_list(self: "AltarServers") -> None:
        """Delete all entries from the already chosen list."""
        self.__already_chosen_this_round = []

    def get_server_by_name(self, name: str) -> AltarServer:
        """Get the server object by its name."""
        for server in self.altar_servers:
            if server.name == name:
                return server
        raise KeyError(name)

    def clear_state(self: "AltarServers") -> None:
        """Reset all variables marking the state of the assignment process.

        Delete the list containing the servers already assigned this round and
        remove all the dates assigned to a server.

        :return:
        """
        self.empty_already_chosen_list()

        for server in self.altar_servers:
            server.service_dates = []

    def su_is_available_at(
        self: "AltarServers",
        su: SchedulingUnit,
        day: Day,
        mass: HolyMass,
        potential_weekday_id: int | None,
    ) -> bool:
        """Check if a scheduling unit is available at a certain mass.

        :param su: The scheduling unit to check.
        :param day: The day to check.
        :param mass: The mass to check.
        :param potential_weekday_id: The weekday id of an event if the time of the mass matches
        with a weekday mass.
        :return:
        """
        return (
            su not in self.__already_chosen_this_round
            and su.is_available_on(day.date)
            and (potential_weekday_id is None or potential_weekday_id not in su.avoid)
            and day.servers_of_su_not_assigned(su)
            and (mass.event.location is None or mass.event.location in su.locations)
        )

    def __create_scheduling_units(self: "AltarServers") -> None:
        """Create scheduling units which group siblings and servers that want to server together."""
        for altar_server in self.altar_servers:
            if not any(altar_server in unit.servers for unit in self.__scheduling_units):
                self.__scheduling_units.append(
                    SchedulingUnit([altar_server, *altar_server.sibling_names])
                )

    def __add_siblings_to_objects(self: "AltarServers") -> None:
        """Get the sibling objects from the list and add them to the individual sibling lists."""
        for altar_server in self.altar_servers:
            if altar_server.has_siblings():
                object_list = [
                    next(filter(lambda x: x.name == sibling_name, self.altar_servers))
                    for sibling_name in altar_server.sibling_names
                ]
                altar_server.sibling_names = object_list

    def get_available_scheduling_units(self: "AltarServers", event: Event) -> list:
        """Get the scheduling units available at a certain event.

        :param event: The event under consideration.
        :return: A list container all available scheduling units.
        """
        return list(filter(lambda x: all(x.avoid(event.id)), self.__scheduling_units))

    def assign_scheduling_unit(
        self: "AltarServers", scheduling_unit: SchedulingUnit, mass: HolyMass
    ) -> int:
        """Assign a server without siblings to a mass.

        :param scheduling_unit: The scheduling unit.
        :param mass: The mass to assign the server to.
        :return: 1 to increase the counter.
        """
        mass.add_scheduling_unit(scheduling_unit)
        self.__choose_for(scheduling_unit, mass)
        return len(scheduling_unit)

    def __choose_for(self: "AltarServers", su: SchedulingUnit, mass: HolyMass) -> None:
        """Add a server to the already chosen list.

        If the length of the list equals the number of the servers, the list is cleared.
        :param su: The scheduling unit to add extend the list for.
        """
        for server in su.servers:
            server.service_dates.append(mass.day.date)
        self.__already_chosen_this_round.append(su)
        if len(self.__already_chosen_this_round) == len(self.altar_servers):
            self.empty_already_chosen_list()

    def get_copy(self: "AltarServers") -> list[AltarServer]:
        """Get a copy of the altar server list.

        :return: The list.
        """
        return copy.deepcopy(self.altar_servers)

    def calculate_statistics(self: "AltarServers") -> tuple:
        """Get the variance of the number of services and of the distances between the services.

        :param altar_servers: The altar servers object.
        :return: The variance of the number of services and of the distances between the services.
        """
        distribution = []
        distances = []
        for server in self.altar_servers:
            distribution.append(len(server.service_dates))
            distances.extend(
                (date_pair[1] - date_pair[0]).days
                for date_pair in itertools.pairwise(server.service_dates)
            )

        return statistics.pvariance(distribution), statistics.pvariance(distances)
