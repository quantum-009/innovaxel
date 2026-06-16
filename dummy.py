from db import engine, Event, User
from sqlalchemy.orm import Session

# 1. Dummy data for the 'events' table
# Schema: event_name, total_seats, event_date (remaining_seats auto-set to total_seats)
events_data = [
    {"event_name": 'Tech Conference 2026', "total_seats": 500, "event_date": '2026-08-15'},
    {"event_name": 'Summer Music Festival', "total_seats": 2000, "event_date": '2026-07-10'},
    {"event_name": 'AI Workshop', "total_seats": 50, "event_date": '2026-09-05'},
    {"event_name": 'Local Hackathon', "total_seats": 150, "event_date": '2026-10-22'},
    {"event_name": 'Art & Design Expo', "total_seats": 300, "event_date": '2026-11-12'}
]

# 2. Dummy data for the 'users' table
# Schema: username, event_id, timestamp
users_data = [
    {"username": 'Alice Johnson', "event_id": 1, "timestamp": '2026-06-10T09:30:00+00:00'},
    {"username": 'Bob Smith', "event_id": 1, "timestamp": '2026-06-10T10:15:00+00:00'},
    {"username": 'Charlie Brown', "event_id": 2, "timestamp": '2026-06-11T08:00:00+00:00'},
    {"username": 'Diana Prince', "event_id": 3, "timestamp": '2026-06-11T14:45:00+00:00'},
    {"username": 'Evan Wright', "event_id": 4, "timestamp": '2026-06-12T11:20:00+00:00'},
    {"username": 'Fiona Gallagher', "event_id": 2, "timestamp": '2026-06-12T16:00:00+00:00'},
    {"username": 'George Miller', "event_id": 5, "timestamp": '2026-06-13T09:00:00+00:00'},
    {"username": 'Hannah Abbott', "event_id": 1, "timestamp": '2026-06-13T13:30:00+00:00'}
]

with Session(engine) as session:
    try:
        # Insert all events
        for e_data in events_data:
            session.add(Event(**e_data))
            
        # Commit events so they get their database IDs (1, 2, 3...) generated
        session.commit()

        # Insert all users
        for u_data in users_data:
            session.add(User(**u_data))
            
            # Since this is a dummy script, we also manually decrement the remaining_seats for realism
            event = session.query(Event).filter(Event.event_id == u_data["event_id"]).first()
            if event:
                event.remaining_seats -= 1

        # Commit all users and seat updates
        session.commit()
        print("Dummy data inserted successfully using SQLAlchemy!")

    except Exception as e:
        session.rollback()
        print(f"Error inserting dummy data: {e}")
