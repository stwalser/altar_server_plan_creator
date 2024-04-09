from datetime import datetime, timedelta

from event_calendar import EventCalendar
from holy_mass import Day, HolyMass


def create_mass_list(
    start_date: datetime.date, end_date: datetime.date, event_calendar: EventCalendar, custom_masses
    ):
    masses = []
    print()
    date = start_date
    while date <= end_date:
        event_day = event_calendar.get_event_day_by_date(date)
        if event_day is not None:
            masses.append(create_calendar_day(date, event_day, custom_masses))
        elif date.strftime("%d.%m.%Y") in custom_masses.keys():
            masses.append(create_calendar_day(date, None, custom_masses))

        date += timedelta(days=1)
    return masses


def create_calendar_day(date, event_day, custom_masses):
    calendar_day = Day(date)

    if event_day is not None:
        calendar_day.name = event_day.name

        for mass in event_day.masses:
            calendar_day.add_mass(create_mass(mass))
    else:
        date_string = date.strftime("%d.%m.%Y")
        if date_string in custom_masses.keys():
            if "name" in custom_masses[date_string]:
                calendar_day.name = custom_masses[date_string]["name"]
            for mass in custom_masses[date.strftime("%d.%m.%Y")]["masses"]:
                calendar_day.add_mass(create_mass(mass))

    return calendar_day


def create_mass(mass) -> HolyMass:
    time_string = list(mass)[0]
    time = datetime.strptime(time_string, "%H:%M")
    mass_obj = HolyMass(time.time(), mass[time_string]["n_minis"])
    if "comment" in mass[time_string]:
        mass_obj.comment = mass[time_string]["comment"]
    return mass_obj
