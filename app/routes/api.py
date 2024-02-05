from aiohttp import web
from .views import handle_request, api_handler

def setup_routes(app):
    app.router.add_get('/', handle_request)
    app.router.add_get('/api', api_handler)
    # Add more API endpoints here as needed