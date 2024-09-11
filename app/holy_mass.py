"""A module that contains the representation of the holy mass and a calendar day."""

from datetime import datetime

from altar_server import AltarServer
from event_calendar import Event, EventDay


class HolyMass:
    """The representation of a holy mass."""

    def __init__(self: "HolyMass", event: Event) -> None:
        """Create a holy mass object.

        :param event: The event object associated with this holy mass.
        """
        self.servers = []
        self.event = event

    def add_server(self: "HolyMass", server: AltarServer) -> None:
        """Add a server to the holy mass.

        :param server: The server to add.
        """
        self.servers.append(server)

    def __str__(self: "HolyMass") -> str:
        """Return a string representation of the holy mass."""
        return f"{self.event} - {self.servers}"

    def __repr__(self: "HolyMass") -> str:
        """Return a string representation of the holy mass."""
        return self.__str__()


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
        self.masses.append(mass)

    def available(self: "Day", server: AltarServer) -> bool:
        """Check if a server is available on a given day. Could be unavailable due to vacation.

        :param server: The server to check.
        :return: True if the server is available, False otherwise.
        """
        for element in server.avoid:
            if isinstance(element, dict) and "long" in element:
                vacation = element["long"]
                start = datetime.strptime(vacation["start"], "%d.%m.%Y").astimezone().date()
                end = datetime.strptime(vacation["end"], "%d.%m.%Y").astimezone().date()

                if start <= self.date <= end:
                    return False

        return True


    def __str__(self: "Day") -> str:
        """Return a string representation of the day."""
        return f"{self.date} - {self.event_day} - {self.masses}"

    def __repr__(self: "Day") -> str:
        """Return a string representation of the day."""
        return self.__str__()
