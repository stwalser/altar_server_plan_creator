"""A module that contains the scheduling unit class, which is used in queues."""

import datetime


class SchedulingUnit:
    """The scheduling unit class.

    Siblings, which always want to be together, are in one scheduling object.
    """

    servers = None
    avoid = set()

    def __init__(self: "SchedulingUnit", minis: list) -> None:
        """Create a scheduling unit object. It contains one or multiple minis.

        Multiple siblings are grouped in a scheduling unit.

        :param minis: The list of minis.
        """
        self.servers: list = minis
        for server in self.servers:
            self.avoid = self.avoid.union(set(server.avoid))

    def __len__(self: "SchedulingUnit") -> int:
        """Get the number of minis in this scheduling unit.

        :return: The number of minis in this scheduling unit.
        """
        return len(self.servers)

    @property
    def locations(self: "SchedulingUnit") -> list:
        """The locations the servers of this scheduling unit can be assigned to.

        :return:
        """
        return self.servers[0].locations

    def is_available_on(self: "SchedulingUnit", date: datetime.date) -> bool:
        """Check if all servers of the scheduling unit are available.

        :param date: The date to check.
        :return: True, if the server is available at a certain date. Otherwise, False.
        """
        return all(server.is_available(date) for server in self.servers)

    def __str__(self: "SchedulingUnit") -> str:
        """Return string representation of the object."""
        return str([str(server) for server in self.servers])

    def __repr__(self: "SchedulingUnit") -> str:
        """Return string representation of the object."""
        return str([str(server) for server in self.servers])
