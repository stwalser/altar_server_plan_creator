import datetime
from pydantic import BaseModel

class WelcomeText(BaseModel):
    greeting: str
    body: list[str]
    dismissal: str

class PlanInfo(BaseModel):
    start_date: datetime.date
    end_date: datetime.date
    welcome_text: WelcomeText
