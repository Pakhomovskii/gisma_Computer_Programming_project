# import aiohttp
#
#
# class CustomHTTPClient:
#     async def post_json(self, url, json_data):
#         async with aiohttp.ClientSession() as session:
#             try:
#                 async with session.post(url, json=json_data) as response:
#                     if response.content_type == 'application/json':
#                         return await response.json()
#                     else:
#                         raise ValueError(f"Unexpected content type: {response.content_type}")
#             except aiohttp.ClientError as e:
#                 raise ValueError(f"HTTP request failed: {e}")
#
#     async def get(self, url):
#         async with aiohttp.ClientSession() as session:
#             try:
#                 async with session.get(url) as response:
#                     if response.content_type == 'application/json':
#                         return await response.json()
#                     else:
#                         raise ValueError(f"Unexpected content type: {response.content_type}")
#             except aiohttp.ClientError as e:
#                 raise ValueError(f"HTTP request failed: {e}")
