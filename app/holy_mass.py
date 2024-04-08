import datetime


class Day:
    def __init__(self, date: datetime.date):
        self.date = date
        self.name = ""
        self.masses = []

    def add_mass(self, mass):
        self.masses.append(mass)

    def __str__(self):
        return f"{self.date} {self.name} - {self.masses}"

    def __repr__(self):
        return f"{self.date} {self.name} - {self.masses}"


class HolyMass:
    def __init__(self, time: datetime.time, n_servers: int):
        self.time = time
        self.servers = []
        self.n_servers = n_servers
        self.comment = ""

    def add_server(self, server):
        self.servers.append(server)

    def __str__(self):
        return f"{self.time} - {self.servers} {self.comment}"

    def __repr__(self):
        return f"{self.time} - {self.servers} {self.comment}"
