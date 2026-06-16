from fastapi import FastAPI, Response, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime, timezone
import sqlite3

app = FastAPI()
# db connect
con = sqlite3.connect("event.db", isolation_level=None)
cur = con.cursor()
con.execute("PRAGMA foreign_keys = ON")
# TODO: Add future check here too
cur.execute("CREATE TABLE IF NOT EXISTS events(  id INTEGER PRIMARY KEY AUTOINCREMENT,  name TEXT NOT NULL UNIQUE, seats INTEGER NOT NULL, date TEXT NOT NULL )")
cur.execute("CREATE TABLE IF NOT EXISTS users(  id INTEGER PRIMARY KEY AUTOINCREMENT,  username TEXT NOT NULL, event_id INTEGER REFERENCES events(id), TIMESTAMP TEXT, UNIQUE(username, event_id))")

SQLITE_ERROR_MAP = {
    "SQLITE_CONSTRAINT_UNIQUE": (409, "Resource already exists"),
    "SQLITE_CONSTRAINT_FOREIGNKEY": (400, "Invalid reference"),
    "SQLITE_CONSTRAINT_NOTNULL": (400, "Missing required field"),
    "SQLITE_CONSTRAINT_PRIMARYKEY": (409, "Duplicate primary key"),
    "SQLITE_CONSTRAINT_CHECK": (400, "Validation failed"),
}

class Event(BaseModel):
    name: str
    total_seats: int = Field(..., gt=0, description="Seats must be greater than 0")
    event_date: date

    @field_validator("event_date")
    @classmethod
    def check_event_date_in_future(cls, value: date) -> date:
        if value <= date.today():
            raise ValueError("Event date must be in the future")
        return value

class User(BaseModel):
    name: str
    event_id: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Event name must be unique
# Event date must be in the future
@app.post("/create-event")
async def create_event(event: Event, response: Response):
    response.status_code = 201
    try:
        await create_event_model(event)
    except sqlite3.IntegrityError as e:
        status = SQLITE_ERROR_MAP[e.sqlite_errorname]
        raise HTTPException(status_code=status[0], detail=status[1])
    return {"message": "Event created Successfully"}



def get_remaining_seats(event_id:int) -> int:
    cur = con.cursor()
    cur.execute("Select seats from events where id = ?", (event_id,))
    row = cur.fetchone()
    if (not row):
        return -1
    cur.execute("Select Count(*) from users where event_id = ?", (event_id,))
    remaining_seats = None or cur.fetchone()[0]
    return row[0] - remaining_seats
def check_if_event_exists(event_id: int) -> bool:
    cur = con.cursor()
    cur.execute("Select 1 from events where id = ?", (event_id,))
    if cur.fetchone():
        return 1
    return 0



con.create_function("get_remaining_seats", 1, get_remaining_seats)
con.create_function("check_if_event_exists", 1, check_if_event_exists)

# Cannot register if event is full   
@app.post("/register-user")
async def register_user(item: User, response: Response):
    response.status_code = 201
    try:
        cur.execute("BEGIN IMMEDIATE")
        cur.execute("Select check_if_event_exists(?)", (item.event_id,))
        ans = cur.fetchone()[0]
        if not ans:
            con.rollback()
            raise HTTPException(status_code=404, detail="Event not found")
        cur.execute("Insert into users(username, event_id, TIMESTAMP) select ?,?,? Where get_remaining_seats(?) > 0 returning id", (item.name, item.event_id, item.timestamp, item.event_id))
        result=cur.fetchone()
        con.commit()
        if result:
            return {"message":"User Created Successfully"}
        raise HTTPException(status_code=409, detail="Event is Full")
    except sqlite3.IntegrityError as e:
        status=SQLITE_ERROR_MAP[e.sqlite_errorname]
        raise HTTPException(status_code=status[0], detail=status[1])


@app.delete("/cancel-registration")
async def cancel_event(item: User):
    await cancel_registration(item)
    return {"message": "Cancelled Successfully"}

@app.get("/view-events")
async def view_events():
    cur.row_factory=sqlite3.Row
    cur.execute("Select * from events")
    result=cur.fetchall()
    return result


async def create_event_model(event: Event):
    cur.execute("INSERT INTO events(name, seats, date) VALUES (?,?,?)", (event.name, event.total_seats, event.event_date))
    con.commit()
    return cur.lastrowid

async def cancel_registration(event: User):
    cur.execute("Delete from users where username = ? and event_id = ?", (event.name, event.event_id))
    con.commit()

