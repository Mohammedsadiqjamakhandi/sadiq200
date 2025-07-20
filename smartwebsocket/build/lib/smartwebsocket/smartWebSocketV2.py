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
        self.subscribed_tokens = []
        self.retry_attempts = 3

    async def _on_message(self, message):
        try:
            data = json.loads(message)
            print(f"📨 Message received: {data}")
        except Exception as e:
            print(f"❌ Error decoding message: {e}")

    async def _on_connect(self):
        print("🌐 WebSocket connected. Subscribing to tokens...")
        await self.subscribe(self.subscribed_tokens)

    async def _on_close(self):
        print("🔌 WebSocket closed.")

    async def _on_error(self, error):
        print(f"❌ WebSocket error: {error}")

    async def subscribe(self, tokens):
        if not self.ws or self.ws.closed:
            print("⚠️ Cannot subscribe, WebSocket not connected.")
            return
        try:
            self.subscribed_tokens = tokens
            payload = {
                "action": 1,
                "params": {
                    "mode": "FULL",
                    "tokenList": [{"exchangeType": "1", "tokens": tokens}]
                }
            }
            await self.ws.send(json.dumps(payload))
            print(f"✅ Subscribed to tokens: {tokens}")
        except Exception as e:
            print(f"❌ Subscription failed: {e}")

    async def _connect(self):
        url = f"wss://ws.angelone.in/NorenWSTP/"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "x-api-key": self.api_key,
            "x-client-code": self.client_code,
            "x-feed-token": self.feed_token
        }

        retry = 0
        while retry < self.retry_attempts:
            try:
                async with websockets.connect(url, extra_headers=headers) as websocket:
                    self.ws = websocket
                    await self._on_connect()

                    async for message in websocket:
                        await self._on_message(message)

            except websockets.exceptions.ConnectionClosed as e:
                await self._on_error(f"Connection closed: {e}")
                retry += 1
                print(f"🔁 Retrying... Attempt {retry}")
                await asyncio.sleep(2)
            except Exception as e:
                await self._on_error(str(e))
                break

        await self._on_close()

    def start(self, tokens):
        self.subscribed_tokens = tokens
        asyncio.run(self._connect())
