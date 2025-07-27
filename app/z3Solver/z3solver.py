import datetime

from z3.z3 import Int, Sum, Or, If, And, Solver, unsat, unknown

from altar_servers.altar_servers import AltarServers
from altar_servers.scheduling_unit import SchedulingUnit
from dates.calendar import Calendar

MAXIMUM_PER_PLAN = 6
MINIMUM_ID_CAP = 3


def get_day_stamp_from_date(day: datetime.datetime.date) -> int:
    return int(datetime.datetime.combine(day, datetime.time()).timestamp())


def get_past_x_mass_blocker_cond(date_x_su: list, i: int, min_masses_between_services: int) -> bool:
    if date_x_su:
        return Sum([j[i] for j in reversed(date_x_su[-min_masses_between_services:])]) == 0
    else:
        return True


def get_solver() -> Solver:
    solver = Solver()
    solver.set("timeout", 120000)
    return solver


def solve(calendar: Calendar, altar_servers: AltarServers, min_masses_between_services: int):
    solver = get_solver()

    while True:
        date_x_id = []
        date_x_su = []
        start_date = calendar.days[0].date
        for day in calendar.days:
            for mass in sorted(day.masses, key=lambda x: x.event.time):
                id_var = Int(f"{mass.day.date}_{mass.event.time}")
                solver.add(id_var == mass.event.id)
                date_x_id.append(id_var)

                new_mass_x_name = []
                for i, su in enumerate(altar_servers.scheduling_units):
                    name_var = Int(f"{mass.day.date}_{mass.event.time}_{su}")
                    new_mass_x_name.append(name_var)

                    if (
                            mass.event.id in su.avoid()
                            or mass.day.date in su.vacations()
                            or (mass.event.location and mass.event.location not in su.locations)
                    ):
                        solver.add(name_var == 0)
                    elif any([server in mass.servers for server in su.servers]):
                        solver.add(name_var == 1)
                    else:
                        result = get_past_x_mass_blocker_cond(
                            date_x_su, i, min_masses_between_services
                        )
                        solver.add(Or(name_var == 0, And(name_var == len(su), result)))

                solver.add(Sum(new_mass_x_name) == mass.event.n_servers)

                date_x_su.append(new_mass_x_name)

        weeks_in_plan = int((calendar.days[-1].date - start_date).days / 7)
        for event_id in range(1, 4):
            limit = max(
                MINIMUM_ID_CAP,
                int(
                    (weeks_in_plan * altar_servers.get_n_servers_available_at(event_id))
                    / len(altar_servers.altar_servers)
                ),
            )
            for i in range(len(date_x_su[0])):
                id_sum = Sum(
                    [
                        If(And(date_x_su[j][i] > 0, date_x_id[j] == event_id), 1, 0)
                        for j in range(len(date_x_su))
                    ]
                )
                solver.add(id_sum < limit)

        for i in range(len(date_x_su[0])):
            total_sum = Sum(
                [
                    j[i] / len(altar_servers.get_su_from(j[i].decl().name().split("_")[2]).servers)
                    for j in date_x_su
                ]
            )
            solver.add(total_sum < MAXIMUM_PER_PLAN)

        result = solver.check()
        if result == unsat or result == unknown:
            print(f"Tried with pause of {min_masses_between_services}. Decreasing and trying again")
            min_masses_between_services -= 1
            solver = get_solver()
            continue

        break

    model = solver.model()

    for mass in date_x_su:
        for name_var in mass:
            if model[name_var].as_long() != 0:
                var_split = name_var.decl().name().split("_")
                day = calendar.get_day_for(var_split[0])
                mass = day.get_mass_at(var_split[1])
                names = var_split[2]
                su: SchedulingUnit = altar_servers.get_su_from(names)
                mass.add_scheduling_unit(su)

    return altar_servers.get_copy(), calendar
