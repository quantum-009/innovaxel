from fastapi import APIRouter, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from models.eventModels import EventModels
from models.eventModels import Event as EventORM
from schemas.pydantic_schemas import EventSchema
from utils.sqlErrorMap import SQLITE_ERROR_MAP

router = APIRouter()

@router.post("/create-event")
async def create_event(event: EventSchema, response: Response):
    response.status_code = 201
    try:
        event_orm_obj = EventORM(
            event_name=event.event_name,
            total_seats=event.total_seats,
            event_date=str(event.event_date),
        )
        EventModels.create_event(event_orm_obj)
        return {"message": "Event created Successfully"}
    except IntegrityError as e:
        error = e.orig
        error_name = getattr(error, "sqlite_errorname", None)
        if error_name in SQLITE_ERROR_MAP:
            error_status = SQLITE_ERROR_MAP[error_name]
            raise HTTPException(status_code=error_status[0], detail=error_status[1])
        raise HTTPException(status_code=500, detail="DB ERROR")

@router.get("/view-events")
async def view_events(upcomming_only: bool = False, order_by_date: bool = False):
    events = EventModels.view_events(upcomming_only, order_by_date)
    return events

