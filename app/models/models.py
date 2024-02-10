from asyncio.log import logger
from decimal import Decimal
from app.services.database import create_db_connection


def serialize_decimal(value) -> str:
    """
    Serialize a decimal value to a string representation.

    Args:
    value (Decimal): The value to be serialized.

    Returns:
    str: The string representation of the decimal value.

    Raises:
    TypeError: If the input value is not a Decimal.
    """
    if not isinstance(value, Decimal):
        raise TypeError("Input value must be a Decimal")
    return str(value)


class UserModel:
    @staticmethod
    async def register_user() -> str:
        """
        Register a new user in the database and return the generated user UUID.

        Returns:
        str: The generated user UUID.

        Raises:
        Exception: If an error occurs during user registration.
        """
        try:
            conn = await create_db_connection()
            query = """
            INSERT INTO users DEFAULT VALUES
            RETURNING user_uuid;  -- Return the generated 'user_uuid'
            """
            user_uuid = await conn.fetchval(
                query
            )  # Execute the query and get the user_uuid
            return user_uuid
        except Exception as e:
            logger.error(f"Failed to register user: {str(e)}")
            raise e  # Re-raise the exception to be caught by the calling handler
        finally:
            await conn.close()  # Ensure the connection is closed


class EnergyUsageModel:
    @staticmethod
    async def create_or_update_energy_usage(
        user_uuid: str,
        average_monthly_bill: float,
        average_natural_gas_bill: float,
        monthly_fuel_bill: float
    ) -> int:
        """
        Create or update energy usage records for a user in the database.

        Args:
        user_uuid (str): The UUID of the user.
        average_monthly_bill (float): The average monthly energy bill.
        average_natural_gas_bill (float): The average monthly natural gas bill.
        monthly_fuel_bill (float): The monthly fuel bill.

        Returns:
        int: The ID of the inserted or updated record.

        Raises:
        Exception: If an error occurs during database operations.
        """
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
        record_id = await conn.fetchval(
            query,
            user_uuid,
            average_monthly_bill,
            average_natural_gas_bill,
            monthly_fuel_bill,
        )
        await conn.close()
        return record_id

    @staticmethod
    async def get_energy_usage(user_uuid: str) -> dict:
        """
        Retrieve energy usage data for a user from the database.

        Args:
        user_uuid (str): The UUID of the user.

        Returns:
        dict: A dictionary containing the user's energy usage data.

        Raises:
        Exception: If an error occurs during database operations.
        """
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
    async def create_or_update_waste_sector(
        user_uuid, waste_kg, recycled_or_composted_kg
    ):
        """
        Create or update waste sector data for a user in the database.

        Args:
        user_uuid (str): The UUID of the user for whom the waste sector data is being created or updated.
        waste_kg (float): The amount of waste in kilograms.
        recycled_or_composted_kg (float): The amount of waste recycled or composted in kilograms.

        Returns:
        int: The ID of the record created or updated in the database.
                """
        conn = await create_db_connection()
        # In this query I use postgres functionality to make an update if values are already in DB
        query = """
        INSERT INTO waste_sector (user_uuid, waste_kg, recycled_or_composted_kg)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_uuid) DO UPDATE 
        SET waste_kg = EXCLUDED.waste_kg,
            recycled_or_composted_kg = EXCLUDED.recycled_or_composted_kg
        RETURNING id;
        """
        record_id = await conn.fetchval(
            query, user_uuid, waste_kg, recycled_or_composted_kg
        )
        await conn.close()
        return record_id

    @staticmethod
    async def get_waste_sector(user_uuid: str) -> dict:
        """
        Retrieve waste sector data for a user from the database and
        calculate the carbon footprint based on the waste data.

        Args:
            user_uuid (str): The UUID of the user for whom the waste sector data is being retrieved.

        Returns:
            dict: A dictionary containing waste sector data including the calculated carbon footprint.
        """
        conn = await create_db_connection()
        query = """
SELECT user_uuid, 
       ROUND((waste_kg * 12 * 0.57) * ((100 - recycled_or_composted_kg) / 100), 1) AS carbon_footprint
FROM waste_sector 
WHERE user_uuid = $1;

        """
        record = await conn.fetchrow(
            query, user_uuid
        )  # Use 'record' since it's a single row
        await conn.close()
        return dict(record)


class BusinessTravelModel:
    @staticmethod
    async def create_or_update_business_travel(
        user_uuid: str, kilometers_per_year: float, average_efficiency_per_100km: float
    ) -> int:
        """
        Create or update business travel data for a user in
        the database using PostgreSQL's upsert (ON CONFLICT) functionality.

        Args:
            user_uuid (str): The UUID of the user for whom the business travel data is being created or updated.
            kilometers_per_year (float): The total kilometers traveled per year.
            average_efficiency_per_100km (float): The average efficiency of travel per 100 kilometers.

        Returns:
            int: The ID of the record created or updated in the database.
        """
        conn = await create_db_connection()
        # In this query I use postgres functionality to make an update if values are already in DB
        query = """
        INSERT INTO business_travel (user_uuid, kilometers_per_year, average_efficiency_per_100km)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_uuid) DO UPDATE 
        SET kilometers_per_year = EXCLUDED.kilometers_per_year,
            average_efficiency_per_100km = EXCLUDED.average_efficiency_per_100km
        RETURNING id;
        """
        record_id = await conn.fetchval(
            query, user_uuid, kilometers_per_year, average_efficiency_per_100km
        )
        await conn.close()
        return record_id

    @staticmethod
    async def get_business_travel(user_uuid: str) -> dict:
        """
        Retrieve business travel data for a user from the database and calculate the carbon footprint based on the travel data.

        Args:
            user_uuid (str): The UUID of the user for whom the business travel data is being retrieved.

        Returns:
            dict or None: A dictionary containing business travel data including the calculated carbon footprint, or None if no data is found.
                """
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
            return None  # Or return an empty dictionary {}
