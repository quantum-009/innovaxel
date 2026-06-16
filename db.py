from sqlalchemy import create_engine, ForeignKey, UniqueConstraint, CheckConstraint, text, event
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import DeclarativeBase


engine = create_engine("sqlite+pysqlite:///event.db", echo=True)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()

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

def init_db():
    Base.metadata.create_all(engine)
