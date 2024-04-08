from datetime import datetime, timedelta
from enum import Enum

from dateutil import easter

from holy_mass import HolyMass, Day

EASTER_SUNDAY = easter.easter(datetime.today().year)


class EventType(str, Enum):
    STD_SUNDAY = "STD_SUNDAY"
    STD_WEDNESDAY = "STD_WEDNESDAY"
    ASCENSION_DAY = "ASCENSION_DAY"
    WHIT_SUNDAY = "WHIT_SUNDAY"
    WHIT_MONDAY = "WHIT_MONDAY"
    CUSTOM = "CUSTOM"


def create_mass_list(start_date, end_date, spec, custom_masses):
    masses = []
    date = start_date
    while date <= end_date:
        event_type = get_event_type(date)
        if event_type is not None:
            masses.append(create_event_day(date, event_type, spec, custom_masses))
        elif date.date().strftime("%d.%m.%Y") in custom_masses.keys():
            masses.append(create_event_day(date, EventType.CUSTOM, spec, custom_masses))

        date += timedelta(days=1)
    return masses


def get_event_type(date: datetime) -> EventType | None:
    if date.date() == EASTER_SUNDAY + timedelta(days=39):
        return EventType.ASCENSION_DAY
    elif date.date() == EASTER_SUNDAY + timedelta(days=49):
        return EventType.WHIT_SUNDAY
    elif date.date() == EASTER_SUNDAY + timedelta(days=50):
        return EventType.WHIT_MONDAY
    elif date.weekday() == 2:
        return EventType.STD_WEDNESDAY
    elif date.weekday() == 6:
        return EventType.STD_SUNDAY


def create_event_day(date, event_type, spec, custom_masses):
    event_day = Day(date.date())

    if "name" in spec[event_type]:
        event_day.name = spec[event_type]["name"]

    for mass in spec[event_type]["masses"]:
        event_day.add_mass(create_mass(mass))

    date_string = date.date().strftime("%d.%m.%Y")
    if date_string in custom_masses.keys():
        if "name" in custom_masses[date_string]:
            event_day.name = custom_masses[date_string]["name"]
        for mass in custom_masses[date.date().strftime("%d.%m.%Y")]["masses"]:
            event_day.add_mass(create_mass(mass))

    return event_day


def create_mass(mass) -> HolyMass:
    time_string = list(mass)[0]
    time = datetime.strptime(time_string, "%H:%M")
    mass_obj = HolyMass(time.time(), mass[time_string]["n_minis"])
    if "comment" in mass[time_string]:
        mass_obj.comment = mass[time_string]["comment"]
    return mass_obj
