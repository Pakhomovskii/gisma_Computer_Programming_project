from asyncio.log import logger
from decimal import Decimal

from aiohttp import web

from app.services.database import create_db_connection

def serialize_decimal(value):
    if isinstance(value, Decimal):
        return str(value)
    return value

class UserModel:
    @staticmethod
    async def register_user():
        try:
            # Assuming create_db_connection is a function that establishes a DB connection
            conn = await create_db_connection()
            query = """
            INSERT INTO users DEFAULT VALUES
            RETURNING user_uuid;  -- Return the generated 'user_uuid'
            """
            user_uuid = await conn.fetchval(query)  # Execute the query and get the user_uuid
            return user_uuid
        except Exception as e:
            logger.error(f"Failed to register user: {str(e)}")
            raise e  # Re-raise the exception to be caught by the calling handler
        finally:
            await conn.close()  # Ensure the connection is closed


class EnergyUsageModel:
    @staticmethod
    async def create_or_update_energy_usage(user_uuid, average_monthly_bill, average_natural_gas_bill,
                                            monthly_fuel_bill):
        conn = await create_db_connection()
        query = """
        INSERT INTO energy_usage (user_uuid, average_monthly_bill, average_natural_gas_bill, monthly_fuel_bill)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (user_uuid) DO UPDATE 
        SET average_monthly_bill = EXCLUDED.average_monthly_bill,
            average_natural_gas_bill = EXCLUDED.average_natural_gas_bill,
            monthly_fuel_bill = EXCLUDED.monthly_fuel_bill
        RETURNING id;
        """
        record_id = await conn.fetchval(query, user_uuid, average_monthly_bill, average_natural_gas_bill,
                                        monthly_fuel_bill)
        await conn.close()
        return record_id

    @staticmethod
    async def get_energy_usage(user_uuid):
        conn = await create_db_connection()
        query = """
SELECT user_uuid, 
       ROUND((average_monthly_bill * 12 * 0.0005) + 
             (average_natural_gas_bill * 12 * 0.053) + 
             (monthly_fuel_bill * 12 * 2.32), 1) AS carbon_footprint
FROM energy_usage 
WHERE user_uuid = $1;
        """
        record = await conn.fetchrow(query, user_uuid)
        await conn.close()
        return dict(record)


class WasteSectorModel:
    @staticmethod
    async def create_or_update_waste_sector(user_uuid, waste_kg, recycled_or_composted_kg):
        conn = await create_db_connection()
        query = """
        INSERT INTO waste_sector (user_uuid, waste_kg, recycled_or_composted_kg)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_uuid) DO UPDATE 
        SET waste_kg = EXCLUDED.waste_kg,
            recycled_or_composted_kg = EXCLUDED.recycled_or_composted_kg
        RETURNING id;
        """
        record_id = await conn.fetchval(query, user_uuid, waste_kg, recycled_or_composted_kg)
        await conn.close()
        return record_id

    @staticmethod
    async def get_waste_sector(user_uuid):
        conn = await create_db_connection()
        query = """
SELECT user_uuid, 
       ROUND((waste_kg * 12 * 0.57) * ((100 - recycled_or_composted_kg) / 100), 1) AS carbon_footprint
FROM waste_sector 
WHERE user_uuid = $1;

        """
        record = await conn.fetchrow(query, user_uuid)  # Use 'record' since it's a single row
        await conn.close()
        return dict(record)


class BusinessTravelModel:
    @staticmethod
    async def create_or_update_business_travel(user_uuid, kilometers_per_year, average_efficiency_per_100km):
        conn = await create_db_connection()
        query = """
        INSERT INTO business_travel (user_uuid, kilometers_per_year, average_efficiency_per_100km)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_uuid) DO UPDATE 
        SET kilometers_per_year = EXCLUDED.kilometers_per_year,
            average_efficiency_per_100km = EXCLUDED.average_efficiency_per_100km
        RETURNING id;
        """
        record_id = await conn.fetchval(query, user_uuid, kilometers_per_year, average_efficiency_per_100km)
        await conn.close()
        return record_id

    @staticmethod
    async def get_business_travel(user_uuid):
        conn = await create_db_connection()
        query = """
SELECT user_uuid, 
       ROUND((kilometers_per_year / average_efficiency_per_100km) * 2.31, 1) AS carbon_footprint
FROM business_travel 
WHERE user_uuid = $1;

        """
        record = await conn.fetchrow(query, user_uuid)
        await conn.close()
        if record:
            return dict(record)
        else:
            return None  # Or return an empty dictionary {}, depending on how you want to handle this case
