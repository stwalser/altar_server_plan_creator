"""A module that contains the scheduling unit class, which is used in queues."""
import datetime
import itertools


class SchedulingUnit:
    """The scheduling unit class.

    Siblings, which always want to be together, are in one scheduling object.
    """

    minis = None

    def __init__(self: "SchedulingUnit", minis: list) -> None:
        """Create a scheduling unit object. It contains one or multiple minis.

        Multiple siblings are grouped in a scheduling unit.

        :param minis: The list of minis.
        """
        self.minis: list = minis

    def __len__(self: "SchedulingUnit") -> int:
        """Get the number of minis in this scheduling unit.

        :return: The number of minis in this scheduling unit.
        """
        return len(self.minis)

    @property
    def avoid(self: "SchedulingUnit") -> list:
        """Get the masses on which this scheduling unit can't be scheduled.

        :return: The list of masses on which this scheduling unit can't be scheduled.
        """
        return list(itertools.chain(self.minis))

    @property
    def locations(self: "SchedulingUnit") -> list:
        """The locations the minis of this scheduling unit can be assigned to.

        :return:
        """
        return self.minis[0].locations

    def is_available(self: "SchedulingUnit", date: datetime.date) -> bool:
        """Check if all minis of the scheduling unit are available.

        :param date: The date to check.
        :return: True, if the server is available at a certain date. Otherwise, False.
        """
        return all(mini.is_available(date) for mini in self.minis)
