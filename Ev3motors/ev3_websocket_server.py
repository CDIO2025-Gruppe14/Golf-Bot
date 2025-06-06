import asyncio
import websockets
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank

tank = MoveTank(OUTPUT_A, OUTPUT_B)

async def handler(websocket, path):
    async for message in websocket:
        print(f"Received: {message}")
        if message == "forward":
            tank.on_for_seconds(SpeedPercent(50), SpeedPercent(50), 2)
        elif message == "backward":
            tank.on_for_seconds(SpeedPercent(-50), SpeedPercent(-50), 2)
        elif message == "left":
            tank.on_for_seconds(SpeedPercent(-30), SpeedPercent(30), 1)
        elif message == "right":
            tank.on_for_seconds(SpeedPercent(30), SpeedPercent(-30), 1)
        elif message == "stop":
            tank.off()
        else:
            print("Unknown command")

start_server = websockets.serve(handler, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started on port 8765...")
asyncio.get_event_loop().run_forever()