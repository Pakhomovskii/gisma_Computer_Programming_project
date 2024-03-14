import logging

import aiohttp_cors
import aiohttp_swagger
from aiohttp import web
from aiohttp_cors import CorsConfig, ResourceOptions

from app.handlers.handlers import (
    create_report_handler,
    create_waste_sector_handler,
    create_business_travel_handler,
    get_energy_usage_handler,
    get_waste_sector_handler,
    create_energy_usage_handler,
    get_business_travel_handler,
    recommendation,
)


# Configure logging (more context)
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def init_app():
    app = web.Application()

    # Configure CORS (allow requests from your frontend's origin)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET"],  # Allow GET requests specifically for this endpoint
        )
    })

    # Define all routes together
    cors.add(app.router.add_post("/register", create_report_handler))
    cors.add(app.router.add_post("/create-energy-usage", create_energy_usage_handler))
    cors.add(app.router.add_post("/create-waste-sector", create_waste_sector_handler))
    cors.add(app.router.add_post("/create-business-travel", create_business_travel_handler))
    cors.add(app.router.add_post("/get-waste-sector", get_waste_sector_handler))
    cors.add(app.router.add_post("/get-energy-usage", get_energy_usage_handler))  # Existing line
    cors.add(app.router.add_post("/get-business-travel", get_business_travel_handler))
    cors.add(app.router.add_post("/give-recommendation", recommendation))

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
                """,)

    return app


if __name__ == "__main__":
    web.run_app(init_app(), host="localhost", port=8080)
