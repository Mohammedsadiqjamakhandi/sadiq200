import asyncio
import websockets
import json
import random
import datetime

connected_clients = set()

async def send_fake_stock_data():
    while True:
        price = round(random.uniform(950, 1050), 2)
        data = {
            "symbol": "RELIANCE",
            "price": price,
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        }
        message = json.dumps(data)
        for client in connected_clients:
            await client.send(message)
        await asyncio.sleep(1)

async def handler(websocket):
    connected_clients.add(websocket)
    print("Client connected")
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print("Client disconnected")

async def main():
    print("Starting WebSocket server at ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await send_fake_stock_data()

asyncio.run(main())
