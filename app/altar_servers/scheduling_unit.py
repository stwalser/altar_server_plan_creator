"""A module that contains the scheduling unit class, which is used in queues."""

import datetime


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

    def avoid(self: "SchedulingUnit") -> set:
        """Get the masses on which this scheduling unit can't be scheduled.

        :return: The list of masses on which this scheduling unit can't be scheduled.
        """
        avoid_set = set()
        for server in self.servers:
            avoid_set.update(server.avoid)
        return avoid_set

    def vacations(self: "SchedulingUnit") -> set:
        vacations = set()
        for server in self.servers:
            for vacation in server.vacations:
                day_difference = vacation.end - vacation.start
                vacations.update(
                    [
                        vacation.start + datetime.timedelta(days=x)
                        for x in range(max(1, day_difference.days))
                    ]
                )
        return vacations

    @property
    def locations(self: "SchedulingUnit") -> list:
        """The locations the servers of this scheduling unit can be assigned to.

        :return:
        """
        return self.servers[0].locations

    def __str__(self: "SchedulingUnit") -> str:
        """Return string representation of the object."""
        return str([str(server) for server in self.servers])

    def __repr__(self: "SchedulingUnit") -> str:
        """Return string representation of the object."""
        return str([str(server) for server in self.servers])
