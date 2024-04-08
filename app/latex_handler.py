from datetime import datetime

from pylatex import Document, Command, NoEscape, Tabular, NewPage, MultiColumn
from pylatex.utils import bold
from babel.dates import format_date, format_time


class Plan(Document):
    def __init__(self, start_date, end_date):
        super().__init__(indent=False, geometry_options=["a4paper", "margin=1in", "landscape",
                                                         "twocolumn"])

        self.preamble.append(Command("usepackage", "supertabular"))
        self.preamble.append(Command("usepackage", "float"))

        self.preamble.append(Command('title', 'Miniplan'))
        self.preamble.append(Command('date', start_date.strftime('%d.%m.') + " - " +
                                     end_date.strftime('%d.%m.%Y')))
        self.append(NoEscape(r'\maketitle'))

    def add_welcome_text(self, welcome_text) -> None:
        self.append(f"{welcome_text["greeting"]}\n\n")
        for body in welcome_text["body"]:
            self.append(f"{body}\n\n")
        self.append(welcome_text["dismissal"])


def generate_pdf(days: list, start_date: datetime, end_date: datetime, welcome_text: dict) -> None:
    doc = Plan(start_date, end_date)
    doc.add_welcome_text(welcome_text)

    doc.append(NewPage())

    patched_tabular = Tabular("llll", row_height=1.4)
    patched_tabular._latex_name = "supertabular"
    with doc.create(patched_tabular) as table:
        fill_document(table, days)

    doc.generate_pdf("output/plan", clean_tex=False)


def fill_document(table: Tabular, days: list) -> None:
    for day in days:
        conditional_hline(day, table)
        table_row = (format_date(day.date, "EEE dd.LL.", locale="de"), )
        for i, mass in enumerate(day.masses):
            mass.servers = sorted(mass.servers)

            if i == 0:
                table_row += (format_time(mass.time, "H.mm", locale="de") + " Uhr", )
            else:
                table_row = ("", format_time(mass.time, "H.mm", locale="de") + " Uhr", )

            if mass.comment != "":
                table_row += (MultiColumn(2, align="l", data=bold(f"({mass.comment})")), )
                table.add_row(table_row)
                table_row = ("", "", )

            for altar_server in mass.servers:
                table_row += (altar_server,)
                table_row = conditional_write(table, table_row)
        conditional_hline(day, table, True)
        table.add_empty_row()


def conditional_hline(day, table, end=False):
    if day.name != "":
        table.add_hline()
        if not end:
            table.add_row((MultiColumn(4, align="c", data=bold(day.name)), ))


def conditional_write(table, table_row):
    if len(table_row) == 4:
        table.add_row(table_row)
        table_row = ("", "",)
    return table_row
