"""A module that contains the class that represents a server."""

from datetime import datetime


class AltarServer:
    """The altar server class, containing the information of one server and convenience methods."""

    def __init__(self: "AltarServer", raw_altar_server: dict) -> None:
        """Create an altar server object from a dictionary that contains all the info.

        :param raw_altar_server: The dictionary with the info on the server.
        """
        self.name = ""
        self.siblings = []
        self.avoid = []
        self.vacations = []
        self.locations = []
        self.always_high_mass = False
        self.service_dates = []

        if isinstance(raw_altar_server, str):
            self.name = raw_altar_server
        elif isinstance(raw_altar_server, dict):
            self.name = next(iter(raw_altar_server))
            inner = raw_altar_server[self.name]
            if "siblings" in inner:
                self.siblings = inner["siblings"]
            if "avoid" in inner:
                self.__parse_avoid(inner)
            if "always_high_mass" in inner:
                self.always_high_mass = True
            if "locations" in inner:
                self.locations = inner["locations"]

    def __parse_avoid(self: "AltarServer", inner: dict) -> None:
        for element in inner["avoid"]:
            if isinstance(element, int):
                self.avoid.append(element)
            else:
                self.vacations.append(
                    (
                        datetime.strptime(element["long"]["start"], "%d.%m.%Y").astimezone().date(),
                        datetime.strptime(element["long"]["end"], "%d.%m.%Y").astimezone().date(),
                    )
                )

    def is_available(self: "AltarServer", date: datetime.date) -> bool:
        """See if a server is available at a certain date due to vacations.

        :param date: The date to check.
        :return: True, if the server is available at a certain date. Otherwise, False.
        """
        return not any(vacations[0] <= date <= vacations[1] for vacations in self.vacations)

    def has_siblings(self: "AltarServer") -> bool:
        """Check if a server has siblings.

        :return: True if the server has siblings, else False.
        """
        return len(self.siblings) > 0

    def __str__(self: "AltarServer") -> str:
        """Return string representation of the object."""
        return str(self.name)

    def __repr__(self: "AltarServer") -> str:
        """Return string representation of the object."""
        return str(self.name)
