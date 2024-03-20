from enum import Enum
from asyncio.log import logger

from models.base_model import BaseModel
from services.database import create_db_connection


# It might be useful for the future of the project to encapsulate logic and make it more readable
class WasteCategory(Enum):
    RECYCLABLE = "RECYCLABLE"
    COMPOSTABLE = "COMPOSTABLE"
    NON_RECYCLABLE = "NON_RECYCLABLE"


class ReportModel:
    @staticmethod
    async def register_report() -> str:
        """
        Register a new report in the database and return the generated report UUID.

        Returns:
        str: The generated report UUID.

        Raises:
        Exception: If an error occurs during report registration.
        """
        try:
            conn = await create_db_connection()
            query = """
            INSERT INTO reports DEFAULT VALUES
            RETURNING report_uuid;  -- Return the generated 'report_uuid'
            """
            report_uuid = await conn.fetchval(
                query
            )  # Execute the query and get the report_uuid
            return report_uuid
        except Exception as e:
            logger.error(f"Failed to register report: {str(e)}")
            raise e  # Re-raise the exception to be caught by the calling handler
        finally:
            await conn.close()  # Ensure the connection is closed


class EnergyUsageModel(BaseModel):
    @staticmethod
    async def create_or_update_energy_usage(
        report_uuid: str,
        average_monthly_bill: float,
        average_natural_gas_bill: float,
        monthly_fuel_bill: float,
        city: str,
        company_name: str,
    ) -> int:
        """
        Create or update energy usage records for in the database.

        Args:
        report_uuid (str): The UUID of the report.
        average_monthly_bill (float): The average monthly energy bill.
        average_natural_gas_bill (float): The average monthly natural gas bill.
        monthly_fuel_bill (float): The monthly fuel bill.
        city (str): The city name
        company_name (str): Company name

        Returns:
        int: The ID of the inserted or updated record.

        Raises:
        Exception: If an error occurs during database operations.
        """
        query = """
                    INSERT INTO energy_usage (report_uuid, 
                                  average_monthly_bill, 
                                  average_natural_gas_bill, 
                                  monthly_fuel_bill, 
                                  city, 
                                  company_name)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (report_uuid) DO UPDATE 
                    SET average_monthly_bill = EXCLUDED.average_monthly_bill,
                        average_natural_gas_bill = EXCLUDED.average_natural_gas_bill,
                        monthly_fuel_bill = EXCLUDED.monthly_fuel_bill, 
                        company_name = EXCLUDED.company_name,
                        city = EXCLUDED.city
                    RETURNING id;
                """
        record_fields = {
            "company_name": "company_name",
            "city": "city",
            "report_uuid": "report_uuid",
            "average_monthly_bill": "average_monthly_bill",
            "average_natural_gas_bill": "average_natural_gas_bill",
            "monthly_fuel_bill": "monthly_fuel_bill",
        }
        return await BaseModel.create_or_update_record(
            query,
            report_uuid,
            average_monthly_bill,
            average_natural_gas_bill,
            monthly_fuel_bill,
            city,
            company_name,
            record_fields=record_fields,
        )

    @staticmethod
    async def get_energy_usage(company_name: str):
        """
        Retrieve energy usage data for a city from the database.

        Args:
        company_name (str): The name of the company.

        Returns:
        list: A list of dictionaries containing energy usage data for all reports related to the company, or an empty list if
        no data is found.

        Raises:
        Exception: If an error occurs during database operations.
        """
        query = """
                    SELECT company_name,
                           city, 
                           created_at,
                           report_uuid,
                           ROUND((average_monthly_bill * 12 * 0.0005) + 
                                 (average_natural_gas_bill * 12 * 0.053) + 
                                 (monthly_fuel_bill * 12 * 2.32), 1) AS carbon_footprint
                    FROM energy_usage 
                    WHERE company_name = $1;
                """
        record_fields = {
            "company_name": "company_name",
            "city": "city",
            "created_at": "created_at",
            "report_uuid": "report_uuid",
            "carbon_footprint": "carbon_footprint",
        }
        return await BaseModel.get_records(
            query, company_name, record_fields=record_fields
        )


class WasteSectorModel:
    @staticmethod
    async def create_or_update_waste_sector(
        report_uuid: str,
        waste_kg: float,
        recycled_or_composted_kg: float,
        city: str,
        company_name: str,
        waste_category: WasteCategory = WasteCategory.RECYCLABLE,  # Set a default value for waste_category
    ) -> int:
        """
        Create or update waste sector in the database.

        Args:
        report_uuid (str): The UUID of the report.
        waste_kg (float): The amount of waste in kilograms.
        recycled_or_composted_kg (float): The amount of waste recycled or composted in kilograms.
        waste_category (enum): RECYCLABLE
        city (str): The name of the city
        company_name (str): The name of the company

        Returns:
        int: The ID of the record created or updated in the database.

        Raises:
        Exception: If an error occurs during database operations.
        """
        query = """
                    INSERT INTO waste_sector (report_uuid, 
                                              waste_kg, 
                                              recycled_or_composted_kg, 
                                              waste_category,
                                              city,
                                              company_name)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (report_uuid) DO UPDATE 
                    SET waste_kg = EXCLUDED.waste_kg,
                        recycled_or_composted_kg = EXCLUDED.recycled_or_composted_kg,
                        waste_category = EXCLUDED.waste_category, 
                        city = EXCLUDED.city, 
                        company_name = EXCLUDED.company_name
                    RETURNING id;
                """
        record_fields = {
            "company_name": "company_name",
            "city": "city",
            "created_at": "created_at",
            "report_uuid": "report_uuid",
            "carbon_footprint": "carbon_footprint",
            "waste_category": "waste_category",
        }
        return await BaseModel.create_or_update_record(
            query,
            report_uuid,
            waste_kg,
            recycled_or_composted_kg,
            waste_category.name,
            city,
            company_name,
            record_fields=record_fields,
        )

    @staticmethod
    async def get_waste_sector(company_name: str) -> list:
        """
        Retrieve waste sector from the database and
        calculate the carbon footprint based on the waste data and category.

        Args:
            company_name (str): Name of the company

        Returns:
            dict: A dictionary containing waste sector data including the calculated carbon footprint, or
            None if no data is found.

        Raises:
            Exception: If an error occurs during database operations.

        """
        query = """
                    SELECT company_name, 
                           city, 
                           created_at,
                           report_uuid,
                           waste_category,
                           CASE 
                               WHEN waste_category = 'RECYCLABLE' THEN ROUND((waste_kg * 12 * 0.57) * ((100 - recycled_or_composted_kg) / 100), 1)
                               ELSE 0
                           END AS carbon_footprint
                    FROM waste_sector
                    WHERE company_name = $1;
                """
        record_fields = {
            "company_name": "company_name",
            "city": "city",
            "created_at": "created_at",
            "report_uuid": "report_uuid",
            "carbon_footprint": "carbon_footprint",
            "waste_category": "waste_category",
        }
        return await BaseModel.get_records(
            query, company_name, record_fields=record_fields
        )


class BusinessTravelModel:
    @staticmethod
    async def create_or_update_business_travel(
        report_uuid: str,
        kilometers_per_year: float,
        average_efficiency_per_100km: float,
        city: str,
        company_name: str,
    ) -> int:
        """
        Create or update business travel data for

        Args:
            report_uuid (str): The UUID of the report for which the business travel data is being created or updated.
            kilometers_per_year (float): The total kilometers traveled per year.
            average_efficiency_per_100km (float): The average efficiency of travel per 100 kilometers.
            city (str): The name of the city
            company_name (str): The name of the company

        Returns:
            int: The ID of the record created or updated in the database.

        Raises:
        Exception: If an error occurs during database operations.
        """
        query = """
                    INSERT INTO business_travel (report_uuid, 
                                  kilometers_per_year, 
                                  average_efficiency_per_100km, 
                                  city, 
                                  company_name)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (report_uuid) DO UPDATE 
                    SET kilometers_per_year = EXCLUDED.kilometers_per_year,
                        average_efficiency_per_100km = EXCLUDED.average_efficiency_per_100km, 
                        city = EXCLUDED.city, 
                        company_name = EXCLUDED.company_name
                    RETURNING id;
                """
        record_fields = {
            "company_name": "company_name",
            "city": "city",
            "report_uuid": "report_uuid",
            "kilometers_per_year": "kilometers_per_year",
            "average_efficiency_per_100km": "average_efficiency_per_100km",
        }
        return await BaseModel.create_or_update_record(
            query,
            report_uuid,
            kilometers_per_year,
            average_efficiency_per_100km,
            city,
            company_name,
            record_fields=record_fields,
        )

    @staticmethod
    async def get_business_travel(company_name: str):
        """
        Retrieve business travel data from the database and calculate
        the carbon footprint based on the travel data.

        Args:
        company_name (str): The name of the company.

        Returns:
        list: A list of dictionaries containing business travel data for the company, or an empty list if no data is found.

        Raises:
        Exception: If an error occurs during database operations.
        """
        query = """
                    SELECT company_name, 
                           city, 
                           created_at,
                           report_uuid,
                           ROUND((kilometers_per_year / average_efficiency_per_100km) * 2.31, 1) AS carbon_footprint
                    FROM business_travel 
                    WHERE company_name = $1;
                """
        record_fields = {
            "company_name": "company_name",
            "city": "city",
            "created_at": "created_at",
            "report_uuid": "report_uuid",
            "carbon_footprint": "carbon_footprint",
        }
        return await BaseModel.get_records(
            query, company_name, record_fields=record_fields
        )
