import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello from Python client!")
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.run(test_websocket())
