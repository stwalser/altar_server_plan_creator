"""A module that contains the scheduling unit class, which is used in queues."""

import datetime
import secrets
import statistics


class SchedulingUnit:
    """The scheduling unit class.

    Siblings, which always want to be together, are in one scheduling object.
    """

    servers = None

    def __init__(self: "SchedulingUnit", minis: list) -> None:
        """Create a scheduling unit object. It contains one or multiple minis.

        Multiple siblings are grouped in a scheduling unit.

        :param minis: The list of minis.
        """
        self.servers: list = minis

    def __len__(self: "SchedulingUnit") -> int:
        """Get the number of minis in this scheduling unit.

        :return: The number of minis in this scheduling unit.
        """
        return len(self.servers)

    def avoid(self: "SchedulingUnit", event_id: str) -> set:
        """Get the masses on which this scheduling unit can't be scheduled.

        :return: The list of masses on which this scheduling unit can't be scheduled.
        """
        avoid = set()
        for server in self.servers:
            for identifier, value in server.fine_tuner.items():
                if event_id == identifier:
                    avoid.add(value)
        return avoid

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

    def is_considered(self: "SchedulingUnit", event_id: str) -> bool:
        """Check if a scheduling unit should be considered for an event.

        :param su: The scheduling unit to check.
        :param event_id: The id of the event to check.
        :return: True, if the scheduling unit should be considered. False, otherwise.
        """
        values = []
        for server in self.servers:
            if event_id in server.fine_tuner:
                values.append(server.fine_tuner[event_id])
            else:
                values.append(1)
        return (secrets.randbelow(100) / 100) <= statistics.mean(values)

    def __str__(self: "SchedulingUnit") -> str:
        """Return string representation of the object."""
        return str([str(server) for server in self.servers])

    def __repr__(self: "SchedulingUnit") -> str:
        """Return string representation of the object."""
        return str([str(server) for server in self.servers])
