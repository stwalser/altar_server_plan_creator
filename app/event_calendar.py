from datetime import datetime, timedelta
from dateutil import easter

EASTER_SUNDAY = easter.easter(datetime.today().year)


class EventDay:
    def __init__(self, raw_event: dict):
        inner = raw_event[list(raw_event)[0]]

        self.weekday = None
        self.date = None
        self.name = ""

        if "name" in inner:
            self.name = inner['name']

        if "weekday" in inner["date"]:
            self.weekday = inner["date"]["weekday"]
        elif "easter" in inner["date"]:
            self.date = EASTER_SUNDAY + timedelta(days=int(inner["date"]["easter"]))
        else:
            self.date = datetime.strptime(inner["date"], "%d.%m.%Y").date()

        self.masses = inner['masses']

    def __str__(self):
        return f"{self.date} - {self.weekday} - {self.name} - {self.masses}"

    def __repr__(self):
        return self.__str__()


class EventCalendar:
    def __init__(self, raw_event_calendar: list):
        self.weekday_events = {}
        self.irregular_events = {}
        for raw_event_day in raw_event_calendar:
            event_day = EventDay(raw_event_day)
            if event_day.weekday is not None:
                self.weekday_events[event_day.weekday] = event_day
            else:
                self.irregular_events[event_day.date] = event_day

    def get_event_day_by_date(self, date: datetime.date) -> EventDay | None:
        if date in self.irregular_events:
            return self.irregular_events[date]
        elif date.weekday() in self.weekday_events:
            return self.weekday_events[date.weekday()]
