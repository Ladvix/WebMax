import aiosqlite
from . import models

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as conn:
            await models.credentials(conn)

    async def get_credentials(self):
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row

            cursor = await conn.cursor()
            await cursor.execute(
                'SELECT * FROM credentials'
            )
            await conn.commit()
            row = await cursor.fetchone()
            if row is not None:
                return dict(row)
            return None

    async def update_credentials(self, device_id: str, token: str, phone: str):
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row

            try:
                await conn.execute(
                    'INSERT INTO credentials (device_id, token, phone) VALUES (?, ?, ?)',
                    (device_id, token, phone)
                )
                await conn.commit()
            except aiosqlite.IntegrityError:
                await conn.execute(
                    'UPDATE credentials SET device_id = ?, token = ?, phone = ?',
                    (device_id, token, phone)
                )
                await conn.commit()