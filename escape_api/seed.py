"""
Seed the database with initial escape rooms.
Run from the escape_api directory:
    python seed.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import asyncpg
from config import settings

ROOMS = [
    {
        "type": "cipher",
        "title": "Room 1 - The Cipher Chamber",
        "clue": "Gur cnffjbeq vf: bcraqbbe",  # ROT13 of "The password is: opendoor"
        "answer": "opendoor",
        "hint": "ROT13 shifts each letter by 13 positions. Try rot13.com",
        "room_order": 1,
        "active": True,
    },
    {
        "type": "header",
        "title": "Room 2 - The Encoded Key",
        "clue": (
            "The door accepts only encoded credentials. "
            "Encode the word 'letmein' in Base64 and deliver it "
            "in the request header: x-secret-base"
        ),
        "answer": "letmein",
        "hint": "In terminal: echo -n 'letmein' | base64",
        "room_order": 2,
        "active": True,
    },
    {
        "type": "method",
        "title": "Room 3 - The Method Door",
        "clue": (
            "This door does not respond to knocking (GET) or pushing (POST). "
            "You must DELETE your way through."
        ),
        "answer": "DELETE",
        "hint": "Change your HTTP request method to DELETE when submitting.",
        "room_order": 3,
        "active": True,
    },
    {
        "type": "useragent",
        "title": "Room 4 - Identity Check",
        "clue": (
            "A scanner blocks the entrance. It only admits agents it recognises. "
            "Identify yourself as: EscapeAgent/1.0"
        ),
        "answer": "EscapeAgent/1.0",
        "hint": "Set the User-Agent header to exactly: EscapeAgent/1.0",
        "room_order": 4,
        "active": True,
    },
    {
        "type": "query_param",
        "title": "Room 5 - The Query Gate",
        "clue": (
            "The lock has a keyhole in the URL itself. "
            "Append the right query parameter to unlock it. "
            "The key is 'opensesame'."
        ),
        "answer": "opensesame",
        "hint": "Add ?key=opensesame to your request URL.",
        "room_order": 5,
        "active": True,
    },
    {
        "type": "hidden_header",
        "title": "Room 6 - The Invisible Message",
        "clue": "The message is not in the body. Look between the lines of the response itself.",
        "answer": "shadowkey",
        "hint": "Inspect the HTTP response headers. The answer is hiding there.",
        "room_order": 6,
        "active": True,
    },
    {
        "type": "body_field",
        "title": "Room 7 - The Deep Vault",
        "clue": (
            "The vault accepts only structured secrets. "
            "Send a nested JSON payload: {\"secret\": {\"key\": \"<answer>\"}}. "
            "The answer is: freedomgate"
        ),
        "answer": "freedomgate",
        "hint": 'POST JSON body: {"secret": {"key": "freedomgate"}}',
        "room_order": 7,
        "active": True,
    },
]


async def seed():
    print(f"Connecting to {settings.DATABASE_URL.split('@')[-1]}...")
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        existing = await conn.fetchval("SELECT COUNT(*) FROM rooms")
        if existing > 0:
            print(f"Database already has {existing} room(s).")
            ans = input("Reseed? This will delete existing rooms. (y/N): ").strip().lower()
            if ans != "y":
                print("Cancelled.")
                return
            await conn.execute("DELETE FROM rooms")
            print("Existing rooms deleted.")

        for room in ROOMS:
            await conn.execute(
                """
                INSERT INTO rooms (type, title, clue, answer, hint, room_order, active)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                room["type"],
                room["title"],
                room["clue"],
                room["answer"],
                room.get("hint"),
                room["room_order"],
                room["active"],
            )
            print(f"  Created: Room {room['room_order']} — {room['title']}")

        print(f"\nSeeded {len(ROOMS)} rooms successfully!")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())
