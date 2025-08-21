
import asyncpg
from conf import PASSWORD

db_pool = None

async def get_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            user='postgres',
            password=PASSWORD,
            database='PCClub',
            host='localhost',
            port=5432
        )
    return db_pool
