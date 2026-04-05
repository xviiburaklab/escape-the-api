import json as _json
import asyncpg
from config import settings


async def _setup_codecs(conn):
    await conn.set_type_codec(
        "jsonb", encoder=_json.dumps, decoder=_json.loads, schema="pg_catalog"
    )
    await conn.set_type_codec(
        "json", encoder=_json.dumps, decoder=_json.loads, schema="pg_catalog"
    )


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            # hoping the db is actually up when this runs
            self.pool = await asyncpg.create_pool(
                settings.DATABASE_URL, init=_setup_codecs
            )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

# global singleton db instance because why not
db = Database()
