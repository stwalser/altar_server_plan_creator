"""A module that contains the Event Day class."""

from events.event import Event
from pydantic import BaseModel


class EventDay(BaseModel):
    """Class that represents a day containing one or multiple events."""

    id: str
    name: str | None = None
    events: list[Event]

    def __str__(self: "EventDay") -> str:
        """Return string representation of the object."""
        return f"{self.id} - {self.name}"

    def __repr__(self: "EventDay") -> str:
        """Return a string representation of the object."""
        return self.__str__()
