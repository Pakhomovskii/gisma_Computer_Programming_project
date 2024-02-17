import uuid
import inspect
import traceback
from asyncio.log import logger

from aiohttp import web
from decimal import Decimal


async def create_data_handler(request, model, create_method):
    try:
        data = await request.json()

        # Extract the required arguments dynamically based on the model
        args = {
            key: data[key]
            for key in inspect.signature(create_method).parameters
            if key in data and key != "waste_category"
        }

        # Call the create_method with the extracted arguments
        record_id = await create_method(**args)

        return web.json_response({"record_id": record_id}, status=200)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        traceback.print_exc()
        return web.Response(text=f"An error occurred: {str(e)}", status=500)


async def get_data_handler(request, model, method_name):
    logger.info(f"Get {model.__name__} info")
    try:
        company_name = request.query.get("company_name")
        records = await getattr(model, method_name)(company_name)

        if not records:
            return web.Response(text="Data not found", status=404)

        response_data = []

        for record in records:
            formatted_record = {
                key: (
                    str(value)
                    if isinstance(value, (Decimal, uuid.UUID))
                    else str(value)
                )
                for key, value in record.items()
            }
            response_data.append(formatted_record)

        return web.json_response({"data": response_data})

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        traceback.print_exc()
        return web.Response(text=f"An error occurred: {str(e)}", status=500)
