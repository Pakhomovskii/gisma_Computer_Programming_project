from asyncio.log import logger
from enum import Enum
from app.services.database import create_db_connection


# It might be useful for the future of the project to encapsulate logic and make it more readable
class WasteCategory(Enum):
    RECYCLABLE = "RECYCLABLE"
    COMPOSTABLE = "COMPOSTABLE"
    NON_RECYCLABLE = "NON_RECYCLABLE"


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
            monthly_fuel_bill: float,
            city: str,
            company_name: str
    ) -> int:
        """
        Create or update energy usage records for a user in the database.

        Args:
        user_uuid (str): The UUID of the user.
        average_monthly_bill (float): The average monthly energy bill.
        average_natural_gas_bill (float): The average monthly natural gas bill.
        monthly_fuel_bill (float): The monthly fuel bill.
        city (str): The city
        company_name (str): The company name

        Returns:
        int: The ID of the inserted or updated record.

        Raises:
        Exception: If an error occurs during database operations.
        """
        try:
            conn = await create_db_connection()
            query = """
            INSERT INTO energy_usage (user_uuid, city, company_name, average_monthly_bill, average_natural_gas_bill, monthly_fuel_bill)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id;
;
            """
            record_id = await conn.fetchval(
                query,
                user_uuid,
                average_monthly_bill,
                average_natural_gas_bill,
                monthly_fuel_bill,
                city,
                company_name
            )
            await conn.close()
            return record_id
        except Exception as e:
            logger.error(f"Failed to create energy sector: {str(e)}")
            raise e
        finally:
            await conn.close()

    @staticmethod
    async def get_energy_usage(user_uuid: str, city: str,
            company_name: str) -> dict:
        """
        Retrieve energy usage data for a user from the database.

        Args:
        user_uuid (str): The UUID of the user.
        city (str): The city
        company_name (str): The company name

        Returns:
        dict: A dictionary containing the user's energy usage data. or
            None if no data is found.

        Raises:
        Exception: If an error occurs during database operations.
        """
        try:
            conn = await create_db_connection()
            query = """
                SELECT user_uuid, 
                   ROUND((average_monthly_bill * 12 * 0.0005) + 
                         (average_natural_gas_bill * 12 * 0.053) + 
                         (monthly_fuel_bill * 12 * 2.32), 1) AS carbon_footprint,
                   city,
                   company_name
            FROM energy_usage 
            WHERE user_uuid = $1
            AND city = $2
            AND company_name = $3;
            """
            record = await conn.fetchrow(query, user_uuid)
            await conn.close()
            if record:
                return dict(record)
            return None
        except Exception as e:
            logger.error(f"Failed to get energy date: {str(e)}")
            raise e
        finally:
            await conn.close()


class WasteSectorModel:
    @staticmethod
    async def create_or_update_waste_sector(user_uuid: str,
                                            waste_kg: float,
                                            recycled_or_composted_kg: float,
                                            waste_category: WasteCategory,
                                            city: str,
                                            company_name: str
                                            ) -> int:
        """
        Create or update waste sector data for a user in the database.

        Args:
        user_uuid (str): The UUID of the user for whom the waste sector data is being created or updated.
        waste_kg (float): The amount of waste in kilograms.
        recycled_or_composted_kg (float): The amount of waste recycled or composted in kilograms.
        waste_category (enum): RECYCLABLE
        city (str): The city
        company_name (str): The company name
        city (str): The city
        company_name (str): The company name

        Returns:
        int: The ID of the record created or updated in the database.

        Raises:
        Exception: If an error occurs during database operations.
        """
        try:
            conn = await create_db_connection()
            query = """
                    INSERT INTO waste_sector (user_uuid, city, company_name, waste_kg, recycled_or_composted_kg, waste_category)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (user_uuid) DO UPDATE 
                    SET waste_kg = EXCLUDED.waste_kg,
                        recycled_or_composted_kg = EXCLUDED.recycled_or_composted_kg,
                        waste_category = EXCLUDED.waste_category
                    RETURNING id;
                    """
            record_id = await conn.fetchval(
                query, user_uuid, waste_kg, recycled_or_composted_kg, waste_category.name, city, company_name)
            await conn.close()
            return record_id
        except Exception as e:
            logger.error(f"Failed to create waste sector: {str(e)}")
            raise e
        finally:
            if conn:
                await conn.close()

    @staticmethod
    async def get_waste_sector(user_uuid: str, city: str,
            company_name: str) -> dict:
        """
        Retrieve waste sector data for a user from the database and
        calculate the carbon footprint based on the waste data and category.

        Args:
            user_uuid (str): The UUID of the user for whom the waste sector data is being retrieved.
            city (str): The city
            company_name (str): The company name

        Returns:
            dict: A dictionary containing waste sector data including the calculated carbon footprint, or
            None if no data is found.

        Raises:
            Exception: If an error occurs during database operations.
        """
        try:
            conn = await create_db_connection()
            query = """
               SELECT user_uuid, city, company_name, waste_kg, recycled_or_composted_kg, waste_category,
                      CASE 
                          WHEN waste_category = 'RECYCLABLE' THEN ROUND((waste_kg * 12 * 0.57) * ((100 - recycled_or_composted_kg) / 100), 1)
                          --WHEN waste_category = 'COMPOSTABLE' THEN ROUND((waste_kg * 12 * 0.45) * ((100 - recycled_or_composted_kg) / 100), 1) -- It would be another logic
                          --WHEN waste_category = 'NON_RECYCLABLE' THEN ROUND((waste_kg * 12 * 0.75) * ((100 - recycled_or_composted_kg) / 100), 1) -- It would be another logic
                          ELSE 0
                      END AS carbon_footprint
               FROM waste_sector
               WHERE user_uuid = $1;
               """
            row = await conn.fetchrow(query, user_uuid)
            await conn.close()

            if row:
                return {
                    "user_uuid": row["user_uuid"],
                    "city": row["city"],
                    "company_name": row["company_name"],
                    "waste_kg": row["waste_kg"],
                    "recycled_or_composted_kg": row["recycled_or_composted_kg"],
                    "waste_category": row["waste_category"],
                    "carbon_footprint": row["carbon_footprint"],
                }
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve waste sector data: {str(e)}")
            raise e
        finally:
            if conn:
                await conn.close()


class BusinessTravelModel:
    @staticmethod
    async def create_or_update_business_travel(
            user_uuid: str,
            kilometers_per_year: float,
            average_efficiency_per_100km: float,
            city: str,
            company_name: str
    ) -> int:
        """
        Create or update business travel data for a user

        Args:
            user_uuid (str): The UUID of the user for whom the business travel data is being created or updated.
            kilometers_per_year (float): The total kilometers traveled per year.
            average_efficiency_per_100km (float): The average efficiency of travel per 100 kilometers.
            city (str): The city
            company_name (str): The company name

        Returns:
            int: The ID of the record created or updated in the database.

        Raises:
        Exception: If an error occurs during database operations.
        """
        try:
            conn = await create_db_connection()
            # In this query I use postgres functionality to make an update if values are already in DB
            query = """
            INSERT INTO business_travel (user_uuid, city, company_name, kilometers_per_year, average_efficiency_per_100km)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_uuid) DO UPDATE 
            SET kilometers_per_year = EXCLUDED.kilometers_per_year,
                average_efficiency_per_100km = EXCLUDED.average_efficiency_per_100km
            RETURNING id;
            """
            record_id = await conn.fetchval(
                query, user_uuid, kilometers_per_year, average_efficiency_per_100km, city, company_name)
            await conn.close()
            return record_id
        except Exception as e:
            logger.error(f"Failed to create business travel sector: {str(e)}")
            raise e
        finally:
            await conn.close()

    @staticmethod
    async def get_business_travel(user_uuid: str, city: str,
            company_name: str) -> dict:
        """
        Retrieve business travel data for a user from the database and calculate
        the carbon footprint based on the travel data.

        Args:
            user_uuid (str): The UUID of the user for whom the business travel data is being retrieved.
            city (str): The city
            company_name (str): The company name
        Returns:
            dict or None: A dictionary containing business travel data including the calculated carbon footprint, or
            None if no data is found.\


        Raises:
        Exception: If an error occurs during database operations.
        """
        try:

            conn = await create_db_connection()
            query = """
    SELECT user_uuid, city, company_name,
           ROUND((kilometers_per_year / average_efficiency_per_100km) * 2.31, 1) AS carbon_footprint
    FROM business_travel 
    WHERE user_uuid = $1;
    
            """
            record = await conn.fetchrow(query, user_uuid, city, company_name)
            await conn.close()
            if record:
                return dict(record)
            else:
                return None  # Or return an empty dictionary {}
        except Exception as e:
            logger.error(f"Failed to get business travel sector: {str(e)}")
            raise e
        finally:
            await conn.close()
