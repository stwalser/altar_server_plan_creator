"""A module that contains the calendar class and its convenience methods."""

from datetime import datetime

from dates.day import Day


class Calendar:
    """The calendar class that contains all days and their information."""

    def __init__(self: "Calendar") -> None:
        """Initialize the calendar class."""
        self.days = []

    def add_day(self: "Calendar", day: Day) -> None:
        self.days.append(day)

    def get_day_for(self: "Calendar", date: str) -> Day | None:
        for day in self.days:
            if day.date == datetime.strptime(date, "%Y-%m-%d").date():
                return day
        return None

    def clear(self: "Calendar") -> None:
        """Remove the assigned servers from the calendar."""
        for day in self.days:
            for mass in day.masses:
                mass.servers = []
