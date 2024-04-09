import datetime

from event_calendar import Event, EventDay


class HolyMass:
    def __init__(self, event: Event):
        self.servers = []
        self.event = event

    def add_server(self, server):
        self.servers.append(server)

    def __str__(self):
        return f"{self.event} - {self.servers}"

    def __repr__(self):
        return self.__str__()


class Day:
    def __init__(self, date: datetime.date, event_day: EventDay):
        self.date = date
        self.event_day = event_day
        self.masses = []

    def add_mass(self, mass):
        self.masses.append(mass)

    def __str__(self):
        return f"{self.date} - {self.event_day} - {self.masses}"

    def __repr__(self):
        return self.__str__()
