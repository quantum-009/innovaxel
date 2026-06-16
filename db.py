from sqlalchemy import create_engine,event
from models.schemas import Base
from config import DB_URL

engine = create_engine(DB_URL, echo=True)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def init_db():
    Base.metadata.create_all(engine)
