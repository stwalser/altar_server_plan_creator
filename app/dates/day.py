"""A module that contains the Day class."""

from datetime import datetime

from app.altar_server.altar_server import AltarServer
from app.dates.holy_mass import HolyMass
from app.events.event_day import EventDay


class Day:
    """The representation of a day of the calendar."""

    def __init__(self: "Day", date: datetime.date, event_day: EventDay) -> None:
        """Create a calendar day object.

        :param date: The date of the day.
        :param event_day: The associated event day.
        """
        self.date = date
        self.event_day = event_day
        self.masses = []

    def add_mass(self: "Day", mass: HolyMass) -> None:
        """Add a mass to the day.

        :param mass: The mass to add.
        """
        mass.day = self
        self.masses.append(mass)

    def server_not_assigned(self: "Day", chosen_server: AltarServer) -> bool:
        """Check if a server has been assigned on this day already.

        That can be due to high-priority assignments or custom masses that take place on the same
        day as normal masses or if a round ends during a day that demands a lot of servers.
        :param chosen_server: The server to check.
        :return: True, if the server has not been assigned on this day yet. False otherwise.
        """
        return not any(chosen_server in mass.servers for mass in self.masses)

    def __str__(self: "Day") -> str:
        """Return a string representation of the day."""
        return f"{self.date} - {self.event_day} - {self.masses}"

    def __repr__(self: "Day") -> str:
        """Return a string representation of the day."""
        return self.__str__()
