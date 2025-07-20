import asyncio
import websockets
import json

class SmartWebSocketV2:
    def __init__(self, auth_token, api_key, client_code, feed_token):
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token

    async def _connect(self):
        url = "wss://wsfeeds.angelone.in/NestHtml5Mobile/socket/stream"
        async with websockets.connect(url) as websocket:
            print("✅ WebSocket connected")
            # Add your subscription logic here
            while True:
                message = await websocket.recv()
                print("📥", message)

    def connect(self):
        asyncio.run(self._connect())