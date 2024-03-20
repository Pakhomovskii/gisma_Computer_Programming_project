import uuid
from asyncio.log import logger
from decimal import Decimal

from models.models import BusinessTravelModel, EnergyUsageModel, WasteSectorModel


# Function to fetch records from all three models
async def fetch_records(company_name):
    business_travel_record = await BusinessTravelModel.get_business_travel(company_name)
    energy_usage_record = await EnergyUsageModel.get_energy_usage(company_name)
    waste_sector_record = await WasteSectorModel.get_waste_sector(company_name)

    # Return records as a list of tuples
    return [
        ("business_travel", business_travel_record),
        ("energy_usage", energy_usage_record),
        ("waste_sector", waste_sector_record)
    ]


# Function to process each record and extract carbon footprint
def process_records(records):
    carbon_footprints = {}
    for record_name, record in records:
        if record:
            for item in record:
                data = {
                    key: (
                        str(value) if isinstance(value, (Decimal, uuid.UUID)) else value
                    )
                    for key, value in item.items()
                }
                carbon_footprints[record_name] = float(data["carbon_footprint"])
    return carbon_footprints



# Function to read recommendation text for a given sector
def read_recommendation_text(sector):
    recommendation_files = {
        "business_travel": "./templates/recommendation_business.txt",
        "energy_usage": "./templates/recommendation_energy_usage.txt",
        "waste_sector": "./templates/recommendation_waste.txt",
    }
    file_path = recommendation_files.get(sector)
    try:
        with open(file_path, "r") as file:
            recommendation_text = file.read()
            return recommendation_text
    except FileNotFoundError as e:
        logger.error(f"Recommendation file not found for {sector}: {str(e)}")
        return f"Recommendation file not found for {sector}.\n\n"
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while reading the file for {sector}: {str(e)}"
        )
        return f"An error occurred while reading the file for {sector}: {str(e)}\n\n"


# Function to calculate the highest carbon footprint and generate recommendations
def generate_recommendations(carbon_footprints):
    if carbon_footprints:
        total_carbon_footprint = sum(carbon_footprints.values())
        highest_sector = max(carbon_footprints, key=carbon_footprints.get)
        highest_footprint = max(carbon_footprints.values())
        highest_sectors = [
            sector
            for sector, footprint in carbon_footprints.items()
            if footprint == highest_footprint
        ]
        highest_sectors_formatted = ", ".join(highest_sectors)
        combined_recommendation_text = (
            f"Total carbon footprint: {round(total_carbon_footprint,2)} kg \n"
        )
        for sector in highest_sectors:
            recommendation_text = read_recommendation_text(sector)
            combined_recommendation_text += f"Recommendations for the max footprint sector - {sector.replace('_', ' ').title()}:\n{recommendation_text}\n\n"

        response_data = {
            "highest_carbon_footprint_sector": highest_sector,
            "carbon_footprint": highest_sectors_formatted,
            "EU_law": "https://climate.ec.europa.eu/eu-action/international-action-climate-change/emissions-monitoring-reporting_en",
            "recommendation": combined_recommendation_text,
            "business_travel": carbon_footprints.get("business_travel"),
            "energy_usage": carbon_footprints.get("energy_usage"),
            "waste_sector": carbon_footprints.get("waste_sector"),
        }
    else:
        response_data = {
            "message": "No carbon footprint data available for the given report_uuid"
        }
    return response_data
