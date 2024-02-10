import asyncpg


async def create_db_connection():
    return await asyncpg.connect(
        user="postgres",
        password="postgres",
        database="save_energy_project",
        host="",
    )
