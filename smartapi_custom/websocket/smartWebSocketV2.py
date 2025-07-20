import asyncio
import json
import websockets


class SmartWebSocketV2:
    def __init__(self, auth_token, api_key, client_code, feed_token):
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token
        self.ws = None
        self.url = "wss://wsfeeds.angelone.in/"

    async def _connect(self):
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "x-api-key": self.api_key,
            "x-client-code": self.client_code,
            "x-feed-token": self.feed_token
        }

        async with websockets.connect(self.url, extra_headers=headers) as websocket:
            self.ws = websocket
            print("🌐 WebSocket connection established.")

            await self.on_open()
            async for message in websocket:
                await self.on_message(message)

    async def on_open(self):
        print("✅ WebSocket opened. You can now subscribe to tokens.")

    async def on_message(self, message):
        print("📨 Message received:", message)

    async def subscribe(self, tokens, action="subscribe"):
        if not self.ws:
            print("❌ WebSocket not connected.")
            return

        payload = {
            "action": action,
            "params": {
                "mode": "FULL",
                "tokenList": tokens  # Format: ["nse_cm|2885"]
            }
        }
        await self.ws.send(json.dumps(payload))
        print(f"📡 Sent subscription request: {payload}")

    def run(self):
        asyncio.run(self._connect())
