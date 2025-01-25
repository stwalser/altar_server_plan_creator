"""A module that contains the Event Calendar class."""

import copy
import datetime

from dateutil import easter
from events.event_day import EventDay
from pydantic import BaseModel

EASTER_SUNDAY = easter.easter(
    datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=2))).year
)


class EventCalendar(BaseModel):
    """The Event calendar class that contains all events and their information."""

    weekday: dict[int, EventDay]
    easter: dict[int, EventDay]
    date: dict[datetime.date, EventDay]
    custom: dict[datetime.date, EventDay]

    def get_event_day_by_date(self: "EventCalendar", date: datetime.date) -> EventDay | None:
        """Get the event day object if there are any events on a specific date.

        :param date: The date to get the event day object for.
        :return: The event day object if there are any events, else None.
        """
        event_day = None
        if date.weekday() in self.weekday:
            event_day = copy.deepcopy(self.weekday[date.weekday()])

        if date in self.date:
            event_day = self.date[date]

        days_to_easter: int = (date - EASTER_SUNDAY).days
        if days_to_easter in self.easter:
            event_day = self.easter[days_to_easter]

        if date in self.custom:
            if event_day is None:
                return self.custom[date]

            event_day.events.extend(self.custom[date].events)

        return event_day

    def custom_event_is_weekday_in_special(
        self: "EventCalendar", date: datetime.date, time: datetime.time
    ) -> int | None:
        """Return the id of a weekday event if the specified date and time match.

        If a custom event is on the same weekday and at the same time as an existing weekday
        event, this method returns the id of that weekday event. This is necessary to avoid
        assigning servers on special masses that take place at the exact same time as weekday
        events they need to avoid.

        :param date: The date of the event.
        :param time: The time of the event.
        :return: The id of the weekday event if it exists, else None.
        """
        for date_key, event_day in self.weekday.items():
            if date_key == date:
                for event in event_day.events:
                    if event.time == time:
                        return event.id
        return None
