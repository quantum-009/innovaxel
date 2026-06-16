from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime, timezone

class EventSchema(BaseModel):
    event_name: str
    total_seats: int = Field(..., gt=0, description="Seats must be greater than 0")
    event_date: date

    @field_validator("event_date")
    @classmethod
    def check_event_date_in_future(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError("Event date must be in the future")
        return value

class UserSchema(BaseModel):
    username: str
    event_id: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserEssentialSchema(BaseModel):
    username: str
    event_id: int

