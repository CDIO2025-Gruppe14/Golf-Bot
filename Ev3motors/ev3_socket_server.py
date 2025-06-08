import socket
from ev3dev2.motor import MoveTank, OUTPUT_A, OUTPUT_B, SpeedPercent

tank = MoveTank(OUTPUT_A, OUTPUT_B)

HOST = '0.0.0.0'  # enter EV3 IP address
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("EV3 socket server running on {}:{}".format(HOST, PORT))

    while True:
        print("Waiting for a new client connection...")
        conn, addr = server_socket.accept()
        with conn:
            print("Connected by {}".format(addr))
            while True:
                data = conn.recv(1024)
                if not data:
                    print("Client disconnected.")
                    break
                command = data.decode().strip()
                print("Received command: " + command)

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
                else:
                    print("Unknown command: " + command)

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