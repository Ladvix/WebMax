import aiosqlite

async def read(db):
    try:
        response = await db.get_credentials()
        if response is not None:
            return response
        return {}
    except (aiosqlite.Error):
        return {}

async def save(db, device_id: str, token: str, phone: str):
    await db.update_credentials(device_id, token, phone)