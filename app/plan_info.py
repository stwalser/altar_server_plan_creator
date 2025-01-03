"""The plan info module."""

import datetime

from pydantic import BaseModel


class WelcomeText(BaseModel):
    """The welcom text of the plan."""

    greeting: str
    body: list[str]
    dismissal: str


class PlanInfo(BaseModel):
    """The plan info."""

    start_date: datetime.date
    end_date: datetime.date
    welcome_text: WelcomeText
