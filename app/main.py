import asyncio
import logging

from aiohttp import web

logging.basicConfig(level=logging.INFO)


async def handle_request(request):
    logging.info("Received a request")
    return web.Response(text="Server is running, but no request processing")


async def main():
    app = web.Application()
    app.router.add_get('/', handle_request)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    logging.info("Server is running at http://localhost:8080")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
