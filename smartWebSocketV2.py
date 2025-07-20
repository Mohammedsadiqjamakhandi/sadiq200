import asyncio
import json
import threading
import websockets

class SmartWebSocketV2:
    def __init__(self, auth_token, api_key, client_code, feed_token):
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token
        self.websocket_url = "wss://wsfeeds.angelbroking.com/NestHtml5Mobile/socket/stream"
        self.subscribed_tokens = []
        self.ws = None
        self.loop = None

    def _get_subscribe_message(self, token):
        return {
            "task": "cn",
            "channel": token,
            "token": self.feed_token,
            "user": self.client_code,
            "acctid": self.client_code
        }

    async def _connect(self):
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                self.ws = websocket
                print("🌐 WebSocket connected.")

                # Send subscription messages
                for token in self.subscribed_tokens:
                    msg = self._get_subscribe_message(token)
                    await websocket.send(json.dumps(msg))
                    print(f"✅ Subscribed to token: {token}")

                while True:
                    response = await websocket.recv()
                    self.on_message(response)

        except Exception as e:
            self.on_error(e)

    def on_message(self, message):
        print(f"📩 Message: {message}")

    def on_error(self, error):
        print(f"❌ WebSocket error: {error}")

    def on_close(self):
        print("🔌 WebSocket closed.")

    def subscribe(self, token_list):
        self.subscribed_tokens = token_list

    def start(self):
        def run():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(self._connect())
            except KeyboardInterrupt:
                self.on_close()
            except Exception as e:
                self.on_error(e)

        t = threading.Thread(target=run)
        t.start()
