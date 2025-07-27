"""A module that contains the Day class."""

from datetime import datetime

from altar_servers.scheduling_unit import SchedulingUnit
from dates.holy_mass import HolyMass
from events.event_day import EventDay


class Day:
    """The representation of a day of the calendar."""

    def __init__(self: "Day", date: datetime.date, event_day: EventDay) -> None:
        """Create a calendar day object.

        :param date: The date of the day.
        :param event_day: The associated event day.
        """
        self.date = None
        self.date = date
        self.event_day = event_day
        self.masses = []

    def add_mass(self: "Day", mass: HolyMass) -> None:
        """Add a mass to the day.

        :param mass: The mass to add.
        """
        mass.day = self
        self.masses.append(mass)

    def servers_of_su_not_assigned(self: "Day", su: SchedulingUnit) -> bool:
        """Check if a server has been assigned on this day already.

        That can be due to pre-assignments or custom masses that take place on the same
        day as normal masses or if a round ends during a day that demands a lot of servers.
        :param su: The scheduling unit to check.
        :return: True, if the server has not been assigned on this day yet. False otherwise.
        """
        return all(all(server not in mass.servers for mass in self.masses) for server in su.servers)

    def get_mass_at(self: "Day", time: datetime.time) -> HolyMass | None:
        for mass in self.masses:
            if mass.event.time == datetime.strptime(time, "%H:%M:%S").time():
                return mass
        return None

    def __str__(self: "Day") -> str:
        """Return a string representation of the day."""
        return f"{self.date} - {self.event_day} - {self.masses}"

    def __repr__(self: "Day") -> str:
        """Return a string representation of the day."""
        return self.__str__()
