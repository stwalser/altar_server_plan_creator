"""A that module contains logic to convert the list of masses into a PDF file via PyLaTeX."""

from datetime import datetime

from babel.dates import format_date, format_time
from dates.day import Day
from plan_info.plan_info import WelcomeText
from pylatex import Command, Document, MultiColumn, NewPage, NoEscape, Tabular
from pylatex.utils import bold

TABLE_WIDTH = 4


class Plan(Document):
    """Represents a plan that is converted to PDF file via PyLaTeX."""

    def __init__(self: "Plan", start_date: datetime.date, end_date: datetime.date) -> None:
        """Create a plan object.

        :param start_date: Start date of the plan.
        :param end_date: End date of the plan.
        """
        super().__init__(
            indent=False,
            geometry_options=["a4paper", "margin=1in", "landscape", "twocolumn"],
            font_size="large",
        )

        self.preamble.append(Command("usepackage", "supertabular"))
        self.preamble.append(Command("usepackage", "float"))

        self.preamble.append(Command("title", "Miniplan"))
        if start_date.year != end_date.year:
            self.preamble.append(
                Command(
                    "date", start_date.strftime("%d.%m.%Y") + " - " + end_date.strftime("%d.%m.%Y")
                )
            )
        else:
            self.preamble.append(
                Command(
                    "date", start_date.strftime("%d.%m") + " - " + end_date.strftime("%d.%m.%Y")
                )
            )
        self.append(NoEscape(r"\maketitle"))

    def add_welcome_text(self: "Plan", welcome_text: WelcomeText) -> None:
        """Add the welcome text to the plan.

        :param welcome_text: The welcome text.
        """
        self.append(f"{welcome_text.greeting}\n\n")
        for body in welcome_text.body:
            self.append(f"{body}\n\n")
        self.append(welcome_text.dismissal)


def generate_pdf(
    days: list, start_date: datetime.date, end_date: datetime.date, welcome_text: WelcomeText
) -> None:
    """Generate a PDF of the plan.

    First the welcome text is added. Then the table with all masses and servers is added. The
    tabular object is changed to a supertabular, which allows to span over multiple pages.
    :param days: The calendar days.
    :param start_date: The start date of the plan.
    :param end_date: The end date of the plan.
    :param welcome_text: The welcome text.
    """
    doc = Plan(start_date, end_date)
    doc.add_welcome_text(welcome_text)

    doc.append(NewPage())

    patched_tabular = Tabular("llll", row_height=1.4)
    patched_tabular._latex_name = "supertabular"  # noqa: SLF001
    with doc.create(patched_tabular) as table:
        fill_document(table, days)

    doc.generate_pdf("output/plan", clean_tex=False)


def fill_document(table: Tabular, days: list) -> None:
    """Add the masses to the document.

    :param table: The table containing the masses and servers.
    :param days: The calendar days.
    """
    for day in days:
        conditional_hline_start(day, table)
        table_row = (format_date(day.date, "EEE dd.LL.", locale="de"),)
        for i, mass in enumerate(sorted(day.masses, key=lambda x: x.event.time)):
            if i != 0:
                table.add_empty_row()

            mass.servers = sorted(mass.servers, key=lambda x: x.name)

            if i == 0:
                table_row += (format_time(mass.event.time, "H.mm", locale="de") + " Uhr",)
            else:
                table_row = ("", format_time(mass.event.time, "H.mm", locale="de") + " Uhr")

            if mass.event.comment is not None:
                table_row += (MultiColumn(2, align="l", data=bold(f"({mass.event.comment})")),)
                table.add_row(table_row)
                table_row = ("", "")

            for altar_server in mass.servers:
                table_row += (altar_server,)
                table_row = conditional_write(table, table_row)

        conditional_hline_end(day, table)
        table.add_empty_row()


def conditional_hline_start(day: Day, table: Tabular) -> None:
    """Add a horizontal line and the name of the day to the table if it is a day with a name.

    :param day: The calendar day.
    :param table: The tabular object.
    """
    if day.event_day.name is not None:
        table.add_hline()
        table.add_row((MultiColumn(TABLE_WIDTH, align="c", data=bold(day.event_day.name)),))


def conditional_hline_end(day: Day, table: Tabular) -> None:
    """Add a horizontal line to the table if it is a special day with a name.

    :param day: The calendar day.
    :param table: The tabular object
    """
    if day.event_day.name is not None:
        table.add_hline()


def conditional_write(table: Tabular, table_row: tuple) -> tuple:
    """Write a complete row to the tabular object.

    :param table: The tabular object.
    :param table_row: The row to write.
    :return: A new row, if the row was written or, otherwise, the same row.
    """
    if len(table_row) == TABLE_WIDTH:
        table.add_row(table_row)
        table_row = ("", "")
    return table_row
