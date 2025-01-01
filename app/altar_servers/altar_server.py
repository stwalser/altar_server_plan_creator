"""A module that contains the class that represents a server."""

import datetime
from pydantic import BaseModel, Field

class Vacation(BaseModel):
    start: datetime.date
    end: datetime.date


class AltarServer(BaseModel):
    """The altar server class, containing the information of one server and convenience methods."""

    name: str
    sibling_names: list[str] | None = Field(alias="siblings", default=[])
    avoid: list[int] = []
    vacations: list[Vacation] = []
    locations: list[str] = []
    service_dates: list[datetime.date] = []

    def is_available(self: "AltarServer", date: datetime.date) -> bool:
        """See if a server is available at a certain date due to vacations.

        :param date: The date to check.
        :return: True, if the server is available at a certain date. Otherwise, False.
        """
        return not any(vacations.start <= date <= vacations.end for vacations in self.vacations)

    def has_siblings(self: "AltarServer") -> bool:
        """Check if a server has siblings.

        :return: True if the server has siblings, else False.
        """
        return len(self.sibling_names) > 0

    def __str__(self: "AltarServer") -> str:
        """Return string representation of the object."""
        return str(self.name)

    def __repr__(self: "AltarServer") -> str:
        """Return string representation of the object."""
        return str(self.name)
