import socket
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank

tank = MoveTank(OUTPUT_A, OUTPUT_B)

HOST = '0.0.0.0' # ip of the ev3 brick
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print("Socket server listening on port", PORT)
    conn, addr = s.accept()
    with conn:
        print("Connected by", addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode().strip()
            print("Received:", command)
            if command == "forward":
                tank.on_for_seconds(SpeedPercent(50), SpeedPercent(50), 2)
            elif command == "backward":
                tank.on_for_seconds(SpeedPercent(-50), SpeedPercent(-50), 2)
            elif command == "left":
                tank.on_for_seconds(SpeedPercent(-30), SpeedPercent(30), 1)
            elif command == "right":
                tank.on_for_seconds(SpeedPercent(30), SpeedPercent(-30), 1)
            elif command == "stop":
                tank.off()

""" import asyncio
import websockets
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank

tank = MoveTank(OUTPUT_A, OUTPUT_B)

async def handler(websocket, path):
    async for message in websocket:
        print("Received: {}".format(message))
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
asyncio.get_event_loop().run_forever() """