"""A module that contains the altar server wrapper class."""

import copy
import itertools
import statistics

from altar_servers.altar_server import AltarServer
from altar_servers.scheduling_unit import SchedulingUnit
from pydantic import BaseModel


def get_distribution(altar_servers: list) -> list:
    """Get how often each server was assigned on the plan."""
    return [
        (server.name, len(server.service_dates))
        for server in sorted(altar_servers, key=lambda x: x.name)
    ]


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

    @property
    def scheduling_units(self: "AltarServers") -> list:
        """Get all scheduling units.

        :return: The scheduling units.
        """
        return self.__scheduling_units

    def get_su_from(self: "AltarServers", names: list) -> SchedulingUnit | None:
        for su in self.scheduling_units:
            if su.__repr__() == names:
                return su
        return None

    def get_n_servers_available_at(self: "AltarServers", event_id: int) -> int:
        count = 0
        for su in self.scheduling_units:
            if all([event_id not in server.avoid for server in su.servers]):
                count += len(su.servers)
        return count

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
