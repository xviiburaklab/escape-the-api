from fastapi import APIRouter, Header, HTTPException, Depends
from database import db
from models import RoomCreate, RoomResponse, SessionResponse
from config import settings
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

def verify_admin(x_admin_key: str = Header(None)):
    if x_admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True

@router.get("/rooms")
async def get_rooms(admin: bool = Depends(verify_admin)):
    rooms = await db.fetch("SELECT * FROM rooms ORDER BY room_order")
    return [dict(r) for r in rooms]

@router.post("/rooms")
async def create_room(room: RoomCreate, admin: bool = Depends(verify_admin)):
    query = """
    INSERT INTO rooms (type, title, clue, answer, hint, room_order, active)
    VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
    """
    row = await db.fetchrow(query, room.type, room.title, room.clue, room.answer, room.hint, room.room_order, room.active)
    return {"message": "Room created", "id": row["id"]}

@router.put("/rooms/{room_id}")
async def update_room(room_id: int, room: RoomCreate, admin: bool = Depends(verify_admin)):
    query = """
    UPDATE rooms 
    SET type=$1, title=$2, clue=$3, answer=$4, hint=$5, room_order=$6, active=$7
    WHERE id=$8
    """
    await db.execute(query, room.type, room.title, room.clue, room.answer, room.hint, room.room_order, room.active, room_id)
    return {"message": "Room updated"}

@router.delete("/rooms/{room_id}")
async def delete_room(room_id: int, admin: bool = Depends(verify_admin)):
    await db.execute("DELETE FROM rooms WHERE id=$1", room_id)
    return {"message": "Room deleted"}

@router.get("/sessions")
async def get_sessions(admin: bool = Depends(verify_admin)):
    sessions = await db.fetch("SELECT * FROM sessions ORDER BY started_at DESC")
    return [dict(s) for s in sessions]
