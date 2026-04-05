import json
from fastapi import APIRouter, Header, HTTPException, Request, Depends, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from uuid import uuid4, UUID as PyUUID
from datetime import datetime, timezone
from database import db
from engine.room_solver import RoomSolver
from config import settings

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


async def get_session(x_session_id: str = Header(None)):
    # tbh I don't know why we use headers instead of cookies here, but it works
    if not x_session_id:
        raise HTTPException(status_code=401, detail="Session ID missing.")
    try:
        sid = PyUUID(x_session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format.")
    
    session = await db.fetchrow("SELECT * FROM sessions WHERE id = $1", sid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Use /start to begin.")
    return dict(session)


@router.get("/")
async def get_rules():
    return {
        "message": "Welcome to the Escape Terminal.",
        "rules": [
            "1. GET /start to begin your session.",
            "2. Read the clues carefully.",
            "3. The system monitors your requests. Some doors require unconventional keys.",
            "4. Submit answers via POST /room/{room_id} with JSON body.",
            "5. GET /status to check your progress.",
            "Good luck.",
        ],
    }


@router.get("/start")
async def start_session(difficulty: str = "easy"):
    if difficulty not in ("easy", "hard"):
        raise HTTPException(status_code=400, detail="difficulty must be 'easy' or 'hard'.")
    # TODO: maybe check if user already has an active session? whatever.
    session_id = uuid4()
    now = datetime.now(timezone.utc)
    await db.execute(
        "INSERT INTO sessions (id, started_at, current_room, config) VALUES ($1, $2, 1, $3)",
        session_id,
        now,
        {"difficulty": difficulty},
    )
    return {
        "message": "Session started.",
        "session_id": str(session_id),
        "difficulty": difficulty,
        "instruction": "GET /status for progress. GET /room/1 for your first clue.",
    }


@router.get("/status")
async def get_status(session: dict = Depends(get_session)):
    config = session.get("config") or {}
    return {
        "id": str(session["id"]),
        "started_at": session["started_at"].isoformat(),
        "completed_at": session["completed_at"].isoformat() if session["completed_at"] else None,
        "current_room": session["current_room"],
        "request_count": session["request_count"],
        "request_limit": settings.SESSION_REQUEST_LIMIT,
        "difficulty": config.get("difficulty", "easy"),
    }


@router.delete("/session")
async def reset_session(session: dict = Depends(get_session)):
    await db.execute("DELETE FROM sessions WHERE id = $1", session["id"])
    return {"message": "Session deleted. GET /start to begin a new session."}


@router.get("/room/{room_id}")
async def get_room_clue(room_id: int, session: dict = Depends(get_session)):
    new_count = session["request_count"] + 1
    await db.execute(
        "UPDATE sessions SET request_count = request_count + 1 WHERE id = $1", session["id"]
    )

    if new_count > settings.SESSION_REQUEST_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Terminal overloaded. Request limit ({settings.SESSION_REQUEST_LIMIT}) reached. Start a new session.",
        )

    if room_id != session["current_room"]:
        raise HTTPException(status_code=403, detail="You are not in this room.")

    room = await db.fetchrow(
        "SELECT * FROM rooms WHERE room_order = $1 AND active = TRUE", room_id
    )
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    config = session.get("config") or {}
    is_hard = config.get("difficulty", "easy") == "hard"
    response_content = {"title": room["title"]}

    if room["type"] == "hidden_header":
        response_content["clue"] = (
            "The clue is not here. Look inside the communication layer. (Check response headers)"
        )
        # lol hiding the clue in the headers
        return Response(
            content=json.dumps(response_content),
            media_type="application/json",
            headers={"x-hidden-clue": room["clue"]},
        )

    if room["clue"]:
        response_content["clue"] = room["clue"]
    if room["hint"] and not is_hard:
        response_content["hint"] = room["hint"]

    return response_content


@router.api_route("/room/{room_id}", methods=["POST", "PUT", "DELETE", "PATCH"])
@limiter.limit("15/minute")
async def submit_room_answer(
    room_id: int, request: Request, session: dict = Depends(get_session)
):
    new_count = session["request_count"] + 1
    await db.execute(
        "UPDATE sessions SET request_count = request_count + 1 WHERE id = $1", session["id"]
    )

    if new_count > settings.SESSION_REQUEST_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Terminal overloaded. Request limit ({settings.SESSION_REQUEST_LIMIT}) reached. Start a new session.",
        )

    if session.get("completed_at"):
        return {"message": "You have already escaped all rooms! Congratulations!"}

    if room_id != session["current_room"]:
        raise HTTPException(status_code=403, detail="You are not in this room.")

    room = await db.fetchrow(
        "SELECT * FROM rooms WHERE room_order = $1 AND active = TRUE", room_id
    )
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    body = {}
    try:
        body = await request.json()
    except Exception:
        pass # whatever, if it fails it's their problem

    request_info = {
        "headers": dict(request.headers),
        "method": request.method,
        "query_params": dict(request.query_params),
        "body": body,
        "expected": room["answer"],
        "clue": room["clue"],
    }

    verifier = RoomSolver.get_verifier(room["type"])
    is_correct, msg = verifier(request_info, room["answer"])

    if is_correct:
        next_room_exists = await db.fetchrow(
            "SELECT 1 FROM rooms WHERE room_order = $1 AND active = TRUE", room_id + 1
        )
        if next_room_exists:
            next_room = room_id + 1
            await db.execute(
                "UPDATE sessions SET current_room = $1 WHERE id = $2", next_room, session["id"]
            )
            return {"message": f"{msg} You may proceed to room {next_room}."}
        else:
            now = datetime.now(timezone.utc)
            await db.execute(
                "UPDATE sessions SET completed_at = $1 WHERE id = $2", now, session["id"]
            )
            return {"message": f"{msg} Congratulations! You have escaped all rooms!"}
    else:
        config = session.get("config") or {}
        is_hard = config.get("difficulty", "easy") == "hard"
        hint = {"hint": room["hint"]} if room.get("hint") and not is_hard else {}
        return {"message": msg, **hint}
