async def credentials(conn):
    cursor = await conn.cursor()
    await cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            device_id TEXT NOT NULL,
            token TEXT NOT NULL,
            phone TEXT NOT NULL
        );
    ''')
    await conn.commit()
    await cursor.close()