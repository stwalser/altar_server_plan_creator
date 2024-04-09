from datetime import datetime, timedelta

from dateutil import easter

EASTER_SUNDAY = easter.easter(datetime.today().year)


class Event:
    def __init__(self, raw_mass):
        time_string = list(raw_mass)[0]

        self.time = datetime.strptime(time_string, "%H:%M").time()
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

    def __str__(self):
        return f"{self.time}: {self.comment}"

    def __repr__(self):
        return self.__str__()


class EventDay:
    def __init__(self, raw_event: dict):
        self.id = list(raw_event)[0]
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
            self.date = datetime.strptime(inner["date"], "%d.%m.%Y").date()

        for raw_mass in inner["masses"]:
            self.events.append(Event(raw_mass))

    def __str__(self):
        return f"{self.date} - {self.weekday} - {self.id}"

    def __repr__(self):
        return self.__str__()


class EventCalendar:
    def __init__(self, raw_event_calendar: list, raw_custom_masses: list):
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

    def get_event_day_by_date(self, date: datetime.date) -> EventDay | None:
        if date in self.irregular_events:
            return self.irregular_events[date]
        elif date.weekday() in self.weekday_events:
            return self.weekday_events[date.weekday()]
