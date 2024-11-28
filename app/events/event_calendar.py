"""A module that contains the Event Calendar class."""
import copy
from datetime import datetime

from events.event_day import EventDay


class EventCalendar:
    """The Event calendar class that contains all events and their information."""

    def __init__(self: "EventCalendar", raw_event_calendar: list, raw_custom_masses: list) -> None:
        """Create an Event calendar object.

        :param raw_event_calendar: The dictionary containing all regular masses from the .yaml file.
        :param raw_custom_masses: The dictionary containing all custom masses from the .yaml file.
        """
        self.weekday_events = {}
        self.irregular_events = {}
        self.custom_masses = {}
        for raw_event_day in raw_event_calendar:
            event_day = EventDay(raw_event_day)
            if event_day.weekday is not None:
                self.weekday_events[event_day.weekday] = event_day
            else:
                self.irregular_events[event_day.date] = event_day

        for raw_custom_day in raw_custom_masses:
            event_day = EventDay(raw_custom_day)
            self.custom_masses[event_day.date] = event_day
        print(self.custom_masses)

    def get_event_day_by_date(self: "EventCalendar", date: datetime.date) -> EventDay | None:
        """Get the event day object if there are any events on a specific date.

        :param date: The date to get the event day object for.
        :return: The event day object if there are any events, else None.
        """
        event_day = None
        if date.weekday() in self.weekday_events:
            event_day = copy.deepcopy(self.weekday_events[date.weekday()])

        if date in self.irregular_events:
            event_day = self.irregular_events[date]

        if date in self.custom_masses:
            if event_day is None:
                return self.custom_masses[date]
            else:
                event_day.events.extend(self.custom_masses[date].events)

        return event_day
