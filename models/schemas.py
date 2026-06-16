from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint, text

class Base(DeclarativeBase):
    pass

class Event(Base):
    __tablename__ = "events"
    event_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_name: Mapped[str] = mapped_column()
    total_seats: Mapped[int] = mapped_column()
    remaining_seats: Mapped[int] = mapped_column(default=lambda kwargs: kwargs.get_current_parameters()['total_seats'])
    event_date: Mapped[str] = mapped_column()
    __table_args__ = (
        UniqueConstraint("event_name"),
        CheckConstraint(text("total_seats > 0")),
    )

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column()
    event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id"))
    timestamp: Mapped[str] = mapped_column()
    __table_args__ = (
        UniqueConstraint("username", "event_id"),
    )
