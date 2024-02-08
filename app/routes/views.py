import logging
from aiohttp import web


from flask import Flask, request, jsonify
import asyncio
from CustomHTTPClient import CustomHTTPClient  # Assuming CustomHTTPClient is in a separate file

app = Flask(__name__)

# Create an instance of CustomHTTPClient
http_client = CustomHTTPClient()

# Define API endpoints
@app.route('/create-energy-usage', methods=['POST'])
def create_energy_usage():
    data = request.json
    created_energy_usage = asyncio.run(http_client.post_json("http://localhost:5000/energy-usage", data))
    return jsonify(created_energy_usage)

@app.route('/get-energy-usage', methods=['GET'])
def get_energy_usage():
    retrieved_energy_usage = asyncio.run(http_client.get("http://localhost:5000/energy-usage"))
    return jsonify(retrieved_energy_usage)

# Add more API endpoints for waste sector and business travel using similar patterns
