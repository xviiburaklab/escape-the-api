from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from database import db
from routers import game, admin
from routers.game import limiter
from config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # init db on startup, hope we don't crash
    await db.connect()

    await db.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
      id SERIAL PRIMARY KEY,
      type TEXT NOT NULL,
      title TEXT,
      clue TEXT,
      answer TEXT NOT NULL,
      hint TEXT,
      room_order INT UNIQUE NOT NULL,
      active BOOLEAN DEFAULT TRUE
    );
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
      id UUID PRIMARY KEY,
      started_at TIMESTAMPTZ NOT NULL,
      completed_at TIMESTAMPTZ,
      current_room INT DEFAULT 1,
      request_count INT DEFAULT 0,
      config JSONB
    );
    """)
    yield
    await db.disconnect()


# turn off openapi docs because hackers gonna hack (or maybe I'm too lazy)
app = FastAPI(openapi_url=None, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router)
app.include_router(admin.router)
