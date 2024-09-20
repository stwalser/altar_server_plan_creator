"""A module that contains functions to create day objects which are printed to the plan."""

from datetime import datetime, timedelta

from dates.day import Day
from dates.holy_mass import HolyMass
from events.event_calendar import EventCalendar
from events.event_day import EventDay


def create_calendar(
    start_date: datetime.date, end_date: datetime.date, event_calendar: EventCalendar
) -> list:
    """Create a calendar (all the dates on the plan) which is a list of calendar days.

    :param start_date: The first day of the calendar.
    :param end_date: The last day of the calendar.
    :param event_calendar: The event calendar object containing all masses.
    :return: The list of day objects.
    """
    calendar = []
    date = start_date
    while date <= end_date:
        event_day = event_calendar.get_event_day_by_date(date)
        if event_day is not None:
            calendar.append(create_calendar_day(date, event_day))

        date += timedelta(days=1)
    return calendar


def clear_calendar(calendar: list) -> None:
    """Remove the assigned servers from the calendar.

    :param calendar: The calendar to clear.
    """
    for day in calendar:
        for mass in day.masses:
            mass.servers = []


def create_calendar_day(date: datetime.time, event_day: EventDay) -> Day:
    """Create a calendar day object for an event day object.

    :param date: The date of the day.
    :param event_day: The associated event day.
    :return: The calendar day object.
    """
    calendar_day = Day(date, event_day)
    calendar_day.name = event_day.name

    for event in event_day.events:
        calendar_day.add_mass(HolyMass(event))

    return calendar_day
