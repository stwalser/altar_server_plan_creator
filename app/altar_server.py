import queue
import random
from datetime import datetime

from event_calendar import EventDay, Event


class AltarServer:
    def __init__(self, raw_altar_server):
        self.name = ""
        self.siblings = []
        self.avoid = []
        self.prefer = []
        self.always_high_mass = False
        self.already_chosen_this_round = False

        if type(raw_altar_server) is str:
            self.name = raw_altar_server
        elif type(raw_altar_server) is dict:
            self.name = list(raw_altar_server)[0]
            inner = raw_altar_server[self.name]
            if "siblings" in inner:
                self.siblings = inner["siblings"]
            if "avoid" in inner:
                for element in inner["avoid"]:
                    try:
                        time = datetime.strptime(element, "%H:%M").time()
                        self.avoid.append(time)
                    except ValueError:
                        self.avoid.append(element)
            if "always_high_mass" in inner:
                self.always_high_mass = True

    def has_siblings(self):
        return len(self.siblings) > 0

    def is_available(self, event_day: EventDay, event: Event):
        if event_day.id in self.avoid or event.time in self.avoid:
            return False

        return True

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.name)


class AltarServers:
    def __init__(self, raw_altar_servers):
        altar_servers = []
        for raw_altar_server in raw_altar_servers:
            altar_servers.append(AltarServer(raw_altar_server))

        for altar_server in altar_servers:
            object_list = []
            if altar_server.has_siblings():
                for sibling_name in altar_server.siblings:
                    object_list.append(list(filter(lambda x: x.name == sibling_name, altar_servers))[0])
                altar_server.siblings = object_list

        self.queue = queue.Queue()
        self.waiting = queue.Queue()

        random.shuffle(altar_servers)
        for altar_server in altar_servers:
            self.queue.put(altar_server)
