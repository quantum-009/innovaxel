from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime, timezone
from models import UserModels, EventModels
from sqlalchemy.exc import IntegrityError
from db import init_db
from db import Event as EventORM
from db import User as UserORM

app = FastAPI()
init_db()

SQLITE_ERROR_MAP = {
    "SQLITE_CONSTRAINT_UNIQUE": (409, "Resource already exists"),
    "SQLITE_CONSTRAINT_FOREIGNKEY": (400, "Invalid reference"),
    "SQLITE_CONSTRAINT_NOTNULL": (400, "Missing required field"),
    "SQLITE_CONSTRAINT_PRIMARYKEY": (409, "Duplicate primary key"),
    "SQLITE_CONSTRAINT_CHECK": (400, "Validation failed"),
}

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

@app.post("/create-event")
async def create_event(event: EventSchema, response: Response):
    response.status_code = 201
    try:
        orm_event = EventORM(
            event_name=event.event_name,
            total_seats=event.total_seats,
            event_date=str(event.event_date),
        )
        EventModels.create_event(orm_event)
        return {"message": "Event created Successfully"}
    except IntegrityError as e:
        error = e.orig
        error_name = getattr(error, "sqlite_errorname", None)
        if error_name in SQLITE_ERROR_MAP:
            error_status = SQLITE_ERROR_MAP[error_name]
            raise HTTPException(status_code=error_status[0], detail=error_status[1])
        raise HTTPException(status_code=500, detail="DB ERROR")

@app.post("/register-user")
async def register_user(item: UserSchema, response: Response):
    response.status_code = 201
    try:
        orm_user = UserORM(
            username=item.username,
            event_id=item.event_id,
            timestamp=str(item.timestamp),
        )
        registered = UserModels.register(orm_user)
        if not registered:
            raise HTTPException(status_code=409, detail="Event is full or does not exist")
        return {"message": "User Registered Successfully"}
    except IntegrityError as e:
        error = e.orig
        error_name = getattr(error, "sqlite_errorname", None)
        if error_name in SQLITE_ERROR_MAP:
            error_status = SQLITE_ERROR_MAP[error_name]
            raise HTTPException(status_code=error_status[0], detail=error_status[1])
        raise HTTPException(status_code=500, detail="DB ERROR")

@app.get("/view-events")
async def view_events(upcomming_only: bool = False, order_by_date: bool = False):
    events = EventModels.view_events(upcomming_only, order_by_date)
    return events

@app.delete("/cancel-user-registration")
async def cancel_user_reg(item: UserEssentialSchema):
    try:
        orm_user = UserORM(
            username=item.username,
            event_id=item.event_id,
            timestamp="",  
        )
        is_deleted = UserModels.delete_registration(orm_user)
        if not is_deleted:
            raise HTTPException(status_code=404, detail="User registration does not exist")
        return {"message": "Cancelled Successfully"}
    except IntegrityError:
        raise HTTPException(status_code=500, detail="DB ERROR")
