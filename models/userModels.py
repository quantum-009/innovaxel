from db import engine
from models.schemas import Event, User
from sqlalchemy import select, update
from sqlalchemy.orm import Session

class UserModels:
    def register(user: User):
        with Session(engine) as session:
            reserve_seat = session.execute(
                update(Event)
                .values(remaining_seats=Event.remaining_seats - 1)
                .where(Event.event_id == user.event_id, Event.remaining_seats > 0)
                .returning(Event.event_id)
            ).scalar()

            if reserve_seat:
                session.add(user)
                session.commit()
                return True

            return False

    def delete_registration(user: User):
        with Session(engine) as session:
            existing = session.execute(
                select(User).where(
                    User.username == user.username,
                    User.event_id == user.event_id
                )
            ).scalar()

            if not existing:
                return None

            session.delete(existing)

            session.execute(
                update(Event)
                .values(remaining_seats=Event.remaining_seats + 1)
                .where(Event.event_id == user.event_id)
            )

            session.commit()
            return existing
