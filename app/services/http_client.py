import aiohttp


class CustomHTTPClient:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def post_json(self, url, json_data):
        try:
            async with self.session.post(url, json=json_data) as response:
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    # Handle unexpected content type
                    raise ValueError(f"Unexpected content type: {response.content_type}")
        except aiohttp.ClientError as e:
            # Handle client errors
            raise ValueError(f"HTTP request failed: {e}")
        finally:
            await self.close()

    async def get(self, url):
        try:
            async with self.session.get(url) as response:
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    # Handle unexpected content type
                    raise ValueError(f"Unexpected content type: {response.content_type}")
        except aiohttp.ClientError as e:
            # Handle client errors
            raise ValueError(f"HTTP request failed: {e}")
        finally:
            await self.close()

    async def close(self):
        if not self.session.closed:
            await self.session.close()
