"""A module that contains the Event Day class."""

from datetime import datetime, timedelta, timezone

from dateutil import easter

from app.events.event import Event

EASTER_SUNDAY = easter.easter(datetime.now(tz=timezone(timedelta(hours=2))).year)


class EventDay:
    """Class that represents a day containing one or multiple events."""

    def __init__(self: "EventDay", raw_event: dict) -> None:
        """Create a new EventDay object.

        :param raw_event: The dictionary containing information about the event day.
        """
        self.id = next(iter(raw_event))
        inner = raw_event[self.id]

        self.weekday = None
        self.date = None
        self.name = ""
        self.events = []

        if "name" in inner:
            self.name = inner["name"]

        if "weekday" in inner["date"]:
            self.weekday = inner["date"]["weekday"]
        elif "easter" in inner["date"]:
            self.date = EASTER_SUNDAY + timedelta(days=int(inner["date"]["easter"]))
        else:
            self.date = datetime.strptime(inner["date"], "%d.%m.").astimezone().date()
            self.date = self.date.replace(year=datetime.now().astimezone().year)

        for raw_mass in inner["masses"]:
            self.events.append(Event(raw_mass))

    def __str__(self: "EventDay") -> str:
        """Return string representation of the object."""
        return f"{self.date} - {self.weekday} - {self.id}"

    def __repr__(self: "EventDay") -> str:
        """Return a string representation of the object."""
        return self.__str__()
