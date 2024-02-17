from asyncio.log import logger
from app.services.database import create_db_connection


class BaseModel:
    @staticmethod
    async def create_or_update_record(query: str, *args, record_fields: dict) -> int:
        try:
            conn = await create_db_connection()
            record_id = await conn.fetchval(query, *args)
            await conn.close()
            return record_id
        except Exception as e:
            logger.error(f"Failed to create or update record: {str(e)}")
            raise e
        finally:
            if conn:
                await conn.close()

    @staticmethod
    async def get_records(query: str, *args, record_fields: dict) -> list:
        try:
            conn = await create_db_connection()
            rows = await conn.fetch(query, *args)
            await conn.close()

            if rows:
                result = []
                for row in rows:
                    record = {field: row.get(field) for field in record_fields}
                    result.append(record)
                return result
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to get records: {str(e)}")
            raise e
        finally:
            if conn:
                await conn.close()
