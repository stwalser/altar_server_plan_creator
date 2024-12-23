"""A module that contains the representations of events and event days and their associated data."""

from datetime import datetime


class Event:
    """Class that represents a single event in the event calendar. Typically, a mass."""

    def __init__(self: "Event", raw_mass: dict) -> None:
        """Create a new Event object.

        :param raw_mass: The dictionary containing info about the mass.
        """
        self.id = next(iter(raw_mass))
        self.time = None
        self.comment = ""
        self.location = None
        self.pre_assigned_servers = []

        inner = raw_mass[self.id]

        self.n_servers = inner["n_servers"]

        if "comment" in inner:
            self.comment = inner["comment"]
        if "location" in inner:
            self.location = inner["location"]
        if "time" in inner:
            self.time = datetime.strptime(inner["time"], "%H:%M").astimezone().time()
        if "servers" in inner:
            self.pre_assigned_servers = inner["servers"]

    def __str__(self: "Event") -> str:
        """Return string representation of the object."""
        return f"{self.time}: {self.comment}"

    def __repr__(self: "Event") -> str:
        """Return a string representation of the object."""
        return self.__str__()
