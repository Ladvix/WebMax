import aiosqlite
from webmax.database.db import Database

async def read(db: Database):
    try:
        response = await db.get_credentials()
        if response is not None:
            return response
        return {}
    except (aiosqlite.Error):
        return {}

async def save(db: Database, device_id: str, token: str, phone: str):
    await db.update_credentials(device_id, token, phone)