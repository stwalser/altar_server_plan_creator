"""A module that contains the representation of the holy mass and a calendar day."""

from altar_servers.scheduling_unit import SchedulingUnit
from events.event import Event


class HolyMass:
    """The representation of a holy mass."""

    def __init__(self: "HolyMass", event: Event, servers=None) -> None:
        """Create a holy mass object.

        :param event: The event object associated with this holy mass.
        """
        if servers is None:
            servers = []
        self.servers = servers
        self.event = event
        self.day = None

    def add_scheduling_unit(self: "HolyMass", scheduling_unit: SchedulingUnit) -> None:
        """Add a server to the holy mass.

        :param scheduling_unit: The scheduling unit to add the minis from.
        """
        self.servers.extend(scheduling_unit.servers)
        for server in scheduling_unit.servers:
            server.service_dates.append(self.day.date)

    def __str__(self: "HolyMass") -> str:
        """Return a string representation of the holy mass."""
        return f"{self.event} - {self.servers}"

    def __repr__(self: "HolyMass") -> str:
        """Return a string representation of the holy mass."""
        return self.__str__()
