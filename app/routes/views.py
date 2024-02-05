import logging
from aiohttp import web


async def handle_request(request):
    logging.info("Received a request")
    return web.Response(text="Server is running, but no request processing")


async def api_handler(request):
    """
    ---
    description: This endpoint returns a JSON response.
    tags:
    - API
    produces:
    - application/json
    responses:
        "200":
            description: successful operation
    """
    logging.info("API request received")
    data = {"message": "This is the API response"}
    return web.json_response(data)
