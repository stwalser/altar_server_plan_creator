"""A module that contains the Day class."""

from datetime import datetime

from dates.holy_mass import HolyMass
from events.event_day import EventDay


class Day:
    """The representation of a day of the calendar."""

    def __init__(self: "Day", date: datetime.date, event_day: EventDay, masses=None) -> None:
        """Create a calendar day object.

        :param date: The date of the day.
        :param event_day: The associated event day.
        """
        if masses is None:
            masses = list()
        self.masses = masses
        self.date = date
        self.event_day = event_day

    def add_mass(self: "Day", mass: HolyMass) -> None:
        """Add a mass to the day.

        :param mass: The mass to add.
        """
        mass.day = self
        self.masses.append(mass)

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
