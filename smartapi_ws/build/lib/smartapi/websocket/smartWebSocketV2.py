import asyncio, websockets, json

class SmartWebSocketV2:
    def __init__(self, auth_token, api_key, client_code, feed_token):
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token
        self.ws = None

    async def _connect(self):
        url = "wss://wsfeeds.angelone.in/NestHtml5Mobile/socket/stream"
        async with websockets.connect(url) as ws:
            self.ws = ws
            print("🌐 WebSocket connected")
            while True:
                msg = await ws.recv()
                try:
                    data = json.loads(msg)
                except:
                    data = msg
                print("📩", data)

    def connect(self):
        asyncio.run(self._connect())
