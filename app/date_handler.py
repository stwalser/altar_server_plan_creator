from datetime import datetime, timedelta

from event_calendar import EventCalendar, EventDay
from holy_mass import Day, HolyMass


def create_calendar(
    start_date: datetime.date, end_date: datetime.date, event_calendar: EventCalendar,
):
    calendar = []
    date = start_date
    while date <= end_date:
        event_day = event_calendar.get_event_day_by_date(date)
        if event_day is not None:
            calendar.append(create_calendar_day(date, event_day))

        date += timedelta(days=1)
    return calendar


def create_calendar_day(date: datetime.time, event_day: EventDay):
    calendar_day = Day(date, event_day)
    calendar_day.name = event_day.name

    for event in event_day.events:
        calendar_day.add_mass(HolyMass(event))

    return calendar_day
