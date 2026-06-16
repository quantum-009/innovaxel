from db import engine
from models.schemas import Event
from sqlalchemy import select, func
from sqlalchemy.orm import Session


class EventModels:
    def create_event(event: Event):
        with Session(engine) as session:
            session.add(event)
            session.commit()

    def view_events(upcomming_only=False, order_by_date=False):
        with Session(engine) as session:
            query = select(Event)
            if upcomming_only:
                query = query.filter(Event.event_date > func.date('now'))
            if order_by_date:
                query = query.order_by(Event.event_date)
            events = session.execute(query).scalars().all()
            return [
                {
                    "event_id": e.event_id,
                    "event_name": e.event_name,
                    "total_seats": e.total_seats,
                    "remaining_seats": e.remaining_seats,
                    "total_registrations": e.total_seats - e.remaining_seats,
                    "event_date": e.event_date,
                }
                for e in events
            ]

