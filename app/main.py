import uuid
import logging
import traceback
from datetime import datetime

import aiohttp_swagger
from aiohttp import web
from decimal import Decimal
from aiohttp_swagger import swagger_path
from app.templates.constans import recommendation_files

from models.models import (
    BusinessTravelModel,
    EnergyUsageModel,
    UserModel,
    WasteSectorModel, WasteCategory,
)

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s:%(message)s",
)
# Create logger instance
logger = logging.getLogger(__name__)


@swagger_path("swagger/create-user-handler.yml")
async def create_user_handler(request):
    logger.info("Create a new user")
    try:
        user_uuid = await UserModel.register_user()  # Attempt to register a user
        # Convert UUID to string before returning in JSON response
        return web.json_response({"user_uuid": str(user_uuid)}, status=201)
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {str(e)}"
        )  # Log the error if registration fails
        # Return a 500 Internal Server Error response with the error message
        return web.Response(status=500, text=f"An unexpected error occurred: {str(e)}")


@swagger_path("swagger/create-energy-usage-handler.yml")
async def create_energy_usage_handler(request):
    logger.info("Handling a request to create or update energy usage")
    try:
        data = await request.json()
        record_id = await EnergyUsageModel.create_or_update_energy_usage(
            data["user_uuid"],
            data["average_monthly_bill"],
            data["average_natural_gas_bill"],
            data["monthly_fuel_bill"],
            data["city"],
            data["company_name"],
        )
        return web.json_response({"record_id": record_id})
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {str(e)}"
        )
        # Log the full stack trace to help with debugging
        traceback.print_exc()  # I've decided to left it after debugging some issue
        return web.Response(text=f"An error occurred: {str(e)}", status=500)


@swagger_path("./swagger/create-waste-sector.yml")
async def create_waste_sector_handler(request):
    logger.info("Handling a request to create waste sector data")
    try:
        data = await request.json()
        waste_category_value = data.get("waste_category_enum", None)
        if waste_category_value is None or waste_category_value.upper() not in WasteCategory.__members__:
            return web.Response(text="Invalid or missing waste category", status=400)
        # Validate and convert waste_category_value to WasteCategory Enum
        try:
            waste_category_enum = WasteCategory[waste_category_value.upper()]
        except KeyError:
            return web.Response(text=f"Invalid waste category: {waste_category_value}", status=400)

        record_id = await WasteSectorModel.create_or_update_waste_sector(
            data["user_uuid"],
            data["waste_kg"],
            data["recycled_or_composted_kg"],
            data["city"],
            data["company_name"],
            waste_category=waste_category_enum
        )
        return web.json_response({"record_id": record_id}, status=200)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        traceback.print_exc()
        return web.Response(text=f"An error occurred: {str(e)}", status=500)


@swagger_path("./swagger/create-business-travel.yml")
async def create_business_travel_handler(request):
    logger.info("Handling a request to create business travel data")
    try:
        data = await request.json()
        record_id = await BusinessTravelModel.create_business_travel(
            data["user_uuid"],
            data["kilometers_per_year"],
            data["average_efficiency_per_100km"],
            data["city"],
            data["company_name"],
        )
        return web.json_response({"BMW": record_id})
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {str(e)}"
        )
        traceback.print_exc()
        return web.Response(text=f"An error occurred: {str(e)}", status=500)


@swagger_path("./swagger/get-business-travel.yml")
async def get_business_travel_handler(request):
    logger.info("Get business travel info")
    try:
        user_uuid = request.query.get("user_uuid")
        record = await BusinessTravelModel.get_business_travel(user_uuid)
        data = {
            key: (str(value) if isinstance(value, (Decimal, uuid.UUID)) else value)
            for key, value in record.items()
        }
        return web.json_response({"data": data})
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {str(e)}"
        )
        traceback.print_exc()
        return web.Response(text=f"An error occurred: {str(e)}", status=500)


@swagger_path("swagger/get-energy-usage-handler.yml")
async def get_energy_usage_handler(request):
    logger.info("Get energy usage info")
    try:
        city = request.query.get("city")
        company_name = request.query.get("company_name")
        created_at = request.query.get("created_at")
        records = await EnergyUsageModel.get_energy_usage(city, company_name, created_at)
        # Convert Decimal and UUID to string for JSON serialization
        data = {
            key: (str(value) if isinstance(value, (Decimal, uuid.UUID)) else value)
            for record in records
            for key, value in record.items()
        }
        return web.json_response({"data": data})
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {str(e)}"
        )
        traceback.print_exc()
        return web.Response(text=f"An error occurred: {str(e)}", status=500)


@swagger_path("./swagger/get-waste-sector.yml")
async def get_waste_sector_handler(request):
    logger.info("Get waste sector data")
    try:
        user_uuid = request.query.get("user_uuid")
        record = await WasteSectorModel.get_waste_sector(user_uuid)
        if record:
            response_data = {
                key: (str(value) if isinstance(value, (Decimal, uuid.UUID)) else value)
                for key, value in record.items()
            }
            return web.json_response({"data": response_data})
        else:
            return web.json_response({"data": {}})
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {str(e)}"
        )
        traceback.print_exc()
        return web.Response(text=f"An error occurred: {str(e)}", status=500)


@swagger_path("./swagger/give-recommendation.yml")
async def recommendation(request):
    logger.info("Get recommendation")
    try:
        user_uuid = request.query.get("user_uuid")
        # Fetch records from all three models
        business_travel_record = await BusinessTravelModel.get_business_travel(
            user_uuid
        )
        energy_usage_record = await EnergyUsageModel.get_energy_usage(user_uuid)
        waste_sector_record = await WasteSectorModel.get_waste_sector(user_uuid)
        # Initialize a dictionary to hold carbon footprint data
        carbon_footprints = {}
        # Process each record, converting values as needed and extracting carbon footprint
        for record_name, record in [
            ("business_travel", business_travel_record),
            ("energy_usage", energy_usage_record),
            ("waste_sector", waste_sector_record),
        ]:
            if record:
                # Convert Decimal and UUID to string for JSON serialization
                data = {
                    key: (
                        str(value) if isinstance(value, (Decimal, uuid.UUID)) else value
                    )
                    for key, value in record.items()
                }
                carbon_footprints[record_name] = float(data["carbon_footprint"])

        # Compare carbon footprints and determine the highest
        if carbon_footprints:

            highest_sector = max(carbon_footprints, key=carbon_footprints.get)
            highest_footprint = max(carbon_footprints.values())

            # Find all sectors with the highest carbon footprint
            highest_sectors = [
                sector
                for sector, footprint in carbon_footprints.items()
                if footprint == highest_footprint
            ]

            # Formatting the highest sectors for display
            highest_sectors_formatted = ", ".join(highest_sectors)
            combined_recommendation_text = ""

            # Read recommendation text for each highest sector and combine
            for sector in highest_sectors:
                file_path = recommendation_files.get(sector)
                try:
                    with open(file_path, "r") as file:
                        recommendation_text = file.read()
                        # Add the sector's recommendation text to the combined text
                        combined_recommendation_text += (
                            f"Recommendations for"
                            f" {sector.replace('_', ' ').title()}:\n{recommendation_text}\n\n"
                        )
                except FileNotFoundError:
                    logger.error(
                        f"An unexpected error occurred: {str(e)}"
                    )
                    combined_recommendation_text += (
                        f"Recommendation file not found for {sector}.\n\n"
                    )
                except Exception as e:
                    logger.error(
                        f"An unexpected error occurred: {str(e)}"
                    )
                    combined_recommendation_text += (
                        f"An error occurred while reading "
                        f"the file for {sector}: {str(e)}\n\n"
                    )

            response_data = {
                "highest_carbon_footprint_sector": highest_sector,
                "carbon_footprint": highest_sectors_formatted,
                "EU_law": "https://climate.ec.europa.eu/eu-action/international-action-climate-change"
                          "/emissions-monitoring-reporting_en",
                "recommendation": combined_recommendation_text,
            }
        else:
            response_data = {
                "message": "No carbon footprint data available for the given user_uuid"
            }

        return web.json_response({"data": response_data})
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {str(e)}"
        )
        traceback.print_exc()
        return web.Response(text=f"An error occurred: {str(e)}", status=500)


async def init_app():
    app = web.Application()

    # Define my routes
    app.router.add_post("/register", create_user_handler)
    app.router.add_post("/create-energy-usage", create_energy_usage_handler)
    app.router.add_post("/create-waste-sector", create_waste_sector_handler)
    app.router.add_post("/create-business-travel", create_business_travel_handler)

    app.router.add_post("/get-waste-sector", get_waste_sector_handler)
    app.router.add_post("/get-energy-usage", get_energy_usage_handler)
    app.router.add_post("/get-business-travel", get_business_travel_handler)

    app.router.add_post("/give-recommendation", recommendation)

    # Setup Swagger documentation
    aiohttp_swagger.setup_swagger(
        app,
        api_version="1.0.0",
        title="co2-reduction project",
        description="""
    This project is part of the M602A Computer Programming (WS0124) course, designed to offer a 
    practical experience in assessing the carbon footprint associated with energy consumption, 
    waste production, and business travel. Upon completion of all sections, participants will receive 
    tailored recommendations. These suggestions are grounded in the guidelines and data provided by The European 
    Environment Agency (EEA), which focuses on the environmental impacts of transportation.

    ***Some useful links:***
    - [The project repository](https://github.com/Pakhomovskii/gisma_computer_programming_project)
    - [EU law Emissions monitoring & reporting](https://climate.ec.europa.eu/eu-action/international
    -action-climate-change/emissions-monitoring-reporting_en)  
    
    ***License:*** [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/) 
    """,
    )
    return app


if __name__ == "__main__":
    web.run_app(init_app(), host="localhost", port=8080)
