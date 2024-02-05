import asyncio
import logging

from aiohttp import web

from app.routes.api import setup_routes
from aiohttp_swagger import setup_swagger

logging.basicConfig(level=logging.INFO)


async def handle_request(request):
    logging.info("Received a request")
    return web.Response(text="Server is running, but no request processing")


async def main():
    app = web.Application()
    setup_routes(app)  # Configure API routes
    setup_swagger(app, swagger_url="/api/doc", description="API documentation", title="API Documentation", api_version="1.0.0")  # Add Swagger documentation

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    logging.info("Server is running at http://localhost:8080")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
