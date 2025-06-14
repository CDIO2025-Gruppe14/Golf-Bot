import socket
from ev3dev2.motor import LargeMotor, MoveTank, SpeedPercent, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D

# Map port names to ev3dev constants
PORT_MAP = {
    'A': OUTPUT_A,
    'B': OUTPUT_B,
    'C': OUTPUT_C,
    'D': OUTPUT_D
}

def get_motor_controller(motor_str):
    motors = motor_str.split('+')
    if len(motors) == 1:
        return LargeMotor(PORT_MAP[motors[0]])
    elif len(motors) == 2:
        return MoveTank(PORT_MAP[motors[0]], PORT_MAP[motors[1]])
    else:
        raise ValueError("Invalid motor selection")

HOST = '0.0.0.0'  # Your EV3's IP
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
                print("Received command:", command)

                parts = command.split(':')
                if len(parts) not in [2, 3]:
                    print("Invalid command format. Expected action:motor[:speed]")
                    continue

                action = parts[0]
                motor_str = parts[1]
                speed = int(parts[2]) if len(parts) == 3 else 50  # Default speed = 50%

                try:
                    controller = get_motor_controller(motor_str)
                    if isinstance(controller, MoveTank):
                        if action == "forward":
                            controller.on_for_seconds(SpeedPercent(speed), SpeedPercent(speed), 2)
                        elif action == "backward":
                            controller.on_for_seconds(SpeedPercent(-speed), SpeedPercent(-speed), 2)
                        elif action == "left":
                            controller.on_for_seconds(SpeedPercent(-speed), SpeedPercent(speed), 1)
                        elif action == "right":
                            controller.on_for_seconds(SpeedPercent(speed), SpeedPercent(-speed), 1)
                        elif action == "stop":
                            controller.off()
                        else:
                            print("Unknown action:", action)

                    elif isinstance(controller, LargeMotor):
                        if action == "forward":
                            controller.on_for_seconds(SpeedPercent(speed), 2)
                        elif action == "backward":
                            controller.on_for_seconds(SpeedPercent(-speed), 2)
                        elif action == "stop":
                            controller.off()
                        else:
                            print("Only forward/backward/stop supported for single motor.")
                except Exception as e:
                    print("Error handling command:", e)

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