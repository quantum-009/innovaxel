import sqlite3

con = sqlite3.connect("event.db")
cur = con.cursor()
con.execute("PRAGMA foreign_keys = ON")
# TODO: Add future check here too
cur.execute("CREATE TABLE IF NOT EXISTS events(  id INTEGER PRIMARY KEY AUTOINCREMENT,  name TEXT NOT NULL UNIQUE, seats INTEGER NOT NULL, date TEXT NOT NULL )")
cur.execute("CREATE TABLE IF NOT EXISTS users(  id INTEGER PRIMARY KEY AUTOINCREMENT,  name TEXT NOT NULL, event_id INTEGER REFERENCES events(id), timestamp TEXT NOT NULL )")
# 1. Dummy data for the 'events' table
# Schema: (name, seats, date) -> id is AUTOINCREMENT
events_data = [
    ('Tech Conference 2026', 500, '2026-08-15'),
    ('Summer Music Festival', 2000, '2026-07-10'),
    ('AI Workshop', 50, '2026-09-05'),
    ('Local Hackathon', 150, '2026-10-22'),
    ('Art & Design Expo', 300, '2026-11-12')
]

# Insert into events
cur.executemany("""
    INSERT INTO events (name, seats, date) 
    VALUES (?, ?, ?)
""", events_data)
con.commit()

# 2. Dummy data for the 'users' table
# Schema: (name, event_id, timestamp) -> id is AUTOINCREMENT
# Note: event_id corresponds to the auto-incremented IDs from the events table (1 to 5)
users_data = [
    ('Alice Johnson', 1, '2026-06-10T09:30:00+00:00'),  # Going to Tech Conference
    ('Bob Smith', 1, '2026-06-10T10:15:00+00:00'),      # Going to Tech Conference
    ('Charlie Brown', 2, '2026-06-11T08:00:00+00:00'),  # Going to Summer Music Festival
    ('Diana Prince', 3, '2026-06-11T14:45:00+00:00'),   # Going to AI Workshop
    ('Evan Wright', 4, '2026-06-12T11:20:00+00:00'),    # Going to Local Hackathon
    ('Fiona Gallagher', 2, '2026-06-12T16:00:00+00:00'),  # Going to Summer Music Festival
    ('George Miller', 5, '2026-06-13T09:00:00+00:00'),  # Going to Art & Design Expo
    ('Hannah Abbott', 1, '2026-06-13T13:30:00+00:00')   # Going to Tech Conference
]

# Insert into users
cur.executemany("""
    INSERT INTO users (name, event_id, timestamp) 
    VALUES (?, ?, ?)
""", users_data)
con.commit()

# Don't forget to commit the changes to your database connection!
# conn.commit()
