"""A module that contains the representations of events and event days and their associated data."""

from datetime import datetime, timedelta, timezone

from dateutil import easter

EASTER_SUNDAY = easter.easter(datetime.now(tz=timezone(timedelta(hours=2))).year)


class Event:
    """Class that represents a single event in the event calendar. Typically, a mass."""

    def __init__(self: "Event", raw_mass: dict) -> None:
        """Create a new Event object.

        :param raw_mass: The dictionary containing info about the mass.
        """
        time_string = next(iter(raw_mass))

        self.time = datetime.strptime(time_string, "%H:%M").astimezone().time()
        self.comment = ""
        self.high_mass = False
        self.location = ""

        inner = raw_mass[time_string]

        self.n_servers = inner["n_servers"]

        if "comment" in inner:
            self.comment = inner["comment"]
        if "high_mass" in inner:
            self.high_mass = True
        if "location" in inner:
            self.location = inner["location"]

    def __str__(self: "Event") -> str:
        """Return string representation of the object."""
        return f"{self.time}: {self.comment}"

    def __repr__(self: "Event") -> str:
        """Return a string representation of the object."""
        return self.__str__()


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
            self.date = datetime.strptime(inner["date"], "%d.%m.%Y").astimezone().date()

        for raw_mass in inner["masses"]:
            self.events.append(Event(raw_mass))

    def __str__(self: "EventDay") -> str:
        """Return string representation of the object."""
        return f"{self.date} - {self.weekday} - {self.id}"

    def __repr__(self: "EventDay") -> str:
        """Return a string representation of the object."""
        return self.__str__()


class EventCalendar:
    """The Event calendar class that contains all events and their information."""

    def __init__(self: "EventCalendar", raw_event_calendar: list, raw_custom_masses: list) -> None:
        """Create an Event calendar object.

        :param raw_event_calendar: The dictionary containing all regular masses from the .yaml file.
        :param raw_custom_masses: The dictionary containing all custom masses from the .yaml file.
        """
        self.weekday_events = {}
        self.irregular_events = {}
        self.additional_events = {}
        for raw_event_day in raw_event_calendar:
            event_day = EventDay(raw_event_day)
            if event_day.weekday is not None:
                self.weekday_events[event_day.weekday] = event_day
            else:
                self.irregular_events[event_day.date] = event_day

        for raw_custom_mass in raw_custom_masses:
            event_day = EventDay(raw_custom_mass)
            if event_day.date in self.irregular_events:
                self.irregular_events[event_day.date].events += event_day.events
            else:
                self.irregular_events[event_day.date] = event_day
                if event_day.date.weekday() in self.weekday_events:
                    self.irregular_events[event_day.date].events += self.weekday_events[
                        event_day.date.weekday()
                    ].events

    def get_event_day_by_date(self: "EventCalendar", date: datetime.date) -> EventDay | None:
        """Get the event day object if there are any events on a specific date.

        :param date: The date to get the event day object for.
        :return: The event day object if there are any events, else None.
        """
        if date in self.irregular_events:
            return self.irregular_events[date]

        if date.weekday() in self.weekday_events:
            return self.weekday_events[date.weekday()]

        return None
