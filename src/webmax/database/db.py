import aiosqlite
from . import models

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await models.credentials(db)

    async def get_credentials(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.cursor()
            await cursor.execute(
                'SELECT * FROM credentials'
            )
            await db.commit()
            row = await cursor.fetchone()
            if row is not None:
                return dict(row)
            return None

    async def update_credentials(self, device_id: str, token: str, phone: str):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            try:
                await db.execute(
                    'INSERT INTO credentials (device_id, token, phone) VALUES (?, ?, ?)',
                    (device_id, token, phone)
                )
                await db.commit()
            except aiosqlite.IntegrityError:
                await db.execute(
                    'UPDATE credentials SET device_id = ?, token = ?, phone = ?',
                    (device_id, token, phone)
                )
                await db.commit()