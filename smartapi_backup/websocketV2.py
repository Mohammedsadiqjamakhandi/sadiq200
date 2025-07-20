import json
import threading
import websocket
import logging

class SmartWebSocketV2:
    def __init__(self, feed_token, client_code, task="mw", on_message=None, on_open=None, on_error=None, on_close=None):
        self.feed_token = feed_token
        self.client_code = client_code
        self.task = task
        self.ws = None
        self.on_message = on_message
        self.on_open = on_open
        self.on_error = on_error
        self.on_close = on_close
        self.url = "wss://wsfeeds.angelbroking.com/NestHtml5Mobile/socket/stream"

    def connect(self):
        headers = {
            "Authorization": f"Bearer {self.feed_token}"
        }
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            header=headers
        )
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def _on_open(self, ws):
        if self.on_open:
            self.on_open(ws)

    def _on_message(self, ws, message):
        if self.on_message:
            self.on_message(ws, message)

    def _on_error(self, ws, error):
        if self.on_error:
            self.on_error(ws, error)

    def _on_close(self, ws, close_status_code, close_msg):
        if self.on_close:
            self.on_close(ws, close_status_code, close_msg)

    def subscribe(self, tokens):
        payload = {
            "task": self.task,
            "mode": "compact",
            "token": tokens,
            "acctid": self.client_code
        }
        self.ws.send(json.dumps(payload))

    def close(self):
        if self.ws:
            self.ws.close()
