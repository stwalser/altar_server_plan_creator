"""A module that contains the representations of events and event days and their associated data."""
import datetime

from pydantic import BaseModel


class Event(BaseModel):
    """Class that represents a single event in the event calendar. Typically, a mass."""

    id: str
    n_servers: int
    time: datetime.time
    comment: str | None = None
    location: str | None = None
    servers: list[str] | dict[datetime.date, list[str]] | None = None

    def __str__(self: "Event") -> str:
        """Return string representation of the object."""
        return f"{self.time}: {self.comment}"

    def __repr__(self: "Event") -> str:
        """Return a string representation of the object."""
        return self.__str__()

    def __hash__(self) -> int:
        """Return the hash value of an event."""
        return self.id.__hash__()
