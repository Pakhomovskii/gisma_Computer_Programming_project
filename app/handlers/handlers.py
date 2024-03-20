import traceback
from asyncio.log import logger
import streamlit as st
from aiohttp import web
from aiohttp_swagger import swagger_path

from app.handlers.config_handlers import get_data_handler, create_data_handler
from app.handlers.recommendation import (
    fetch_records,
    generate_recommendations,
    process_records,
)
from app.models.models import (
    BusinessTravelModel,
    EnergyUsageModel,
    WasteSectorModel,
    ReportModel,
)


@swagger_path("swagger/create-report-handler.yml")
async def create_report_handler(request: web.Request) -> web.Response:
    logger.info("Creating a new report")
    try:
        report_uuid = (
            await ReportModel.register_report()
        )  # Attempt to register a report
        # Convert UUID to string before returning in JSON response
        return web.json_response({"report_uuid": str(report_uuid)}, status=201)
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {str(e)}"
        )  # Log the error if registration fails
        # Return a 500 Internal Server Error response with the error message
        return web.Response(status=500, text=f"An unexpected error occurred: {str(e)}")


@swagger_path("swagger/create-energy-usage-handler.yml")
async def create_energy_usage_handler(request) -> web.Response:
    logger.info("Creating energy sector data")
    return await create_data_handler(
        request, EnergyUsageModel, EnergyUsageModel.create_or_update_energy_usage
    )


@swagger_path("./swagger/create-waste-sector.yml")
async def create_waste_sector_handler(request):
    logger.info("Creating waste sector data")
    return await create_data_handler(
        request, WasteSectorModel, WasteSectorModel.create_or_update_waste_sector
    )


@swagger_path("./swagger/create-business-travel.yml")
async def create_business_travel_handler(request):
    logger.info("Creating business travel data")
    return await create_data_handler(
        request,
        BusinessTravelModel,
        BusinessTravelModel.create_or_update_business_travel,
    )


@swagger_path("./swagger/get-business-travel.yml")
async def get_business_travel_handler(request):
    logger.info("Getting business travel data")
    return await get_data_handler(request, BusinessTravelModel, "get_business_travel")


@swagger_path("swagger/get-energy-usage-handler.yml")
async def get_energy_usage_handler(request):
    logger.info("Getting energy usage data")
    return await get_data_handler(request, EnergyUsageModel, "get_energy_usage")


@swagger_path("./swagger/get-waste-sector.yml")
async def get_waste_sector_handler(request):
    logger.info("Getting waste sector data")
    return await get_data_handler(request, WasteSectorModel, "get_waste_sector")


# Main recommendation function@swagger_path("./swagger/give-recommendation.yml")
async def recommendation(request):
    logger.info("Getting recommendation")
    try:
        company_name = request.query.get("company_name")
        records = await fetch_records(company_name)
        carbon_footprints = process_records(records)
        response_data = generate_recommendations(carbon_footprints)
        return web.json_response({"data": response_data})
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        traceback.print_exc()
        return web.Response(text=f"An error occurred: {str(e)}", status=500)
