import socket
from ev3dev2.motor import LargeMotor, MoveTank, SpeedPercent, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D

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

HOST = '0.0.0.0'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("EV3 socket server running on {}:{}".format(HOST, PORT))

    while True:
        print("Waiting for a new client connection...")
        conn, addr = server_socket.accept()
        with conn:
            print("Connected by", addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    print("Client disconnected.")
                    break

                command = data.decode().strip()
                print("Received command:", command)

                parts = command.split(':')
                if len(parts) not in [3, 4]:
                    print("Invalid command format. Expected action:motor:speed[:duration]")
                    continue

                action = parts[0]
                motor_str = parts[1]
                speed = int(parts[2])
                duration = float(parts[3]) if len(parts) == 4 else 2.0

                try:
                    controller = get_motor_controller(motor_str)

                    if isinstance(controller, MoveTank):
                        if action == "forward":
                            controller.on_for_seconds(SpeedPercent(speed), SpeedPercent(speed), duration)
                        elif action == "backward":
                            controller.on_for_seconds(SpeedPercent(-speed), SpeedPercent(-speed), duration)
                        elif action == "left":
                            controller.on_for_seconds(SpeedPercent(-speed), SpeedPercent(speed), duration)
                        elif action == "right":
                            controller.on_for_seconds(SpeedPercent(speed), SpeedPercent(-speed), duration)
                        elif action == "stop":
                            controller.off()
                        else:
                            print("Unknown action:", action)

                    elif isinstance(controller, LargeMotor):
                        if action == "forward":
                            controller.on_for_seconds(SpeedPercent(speed), duration)
                        elif action == "backward":
                            controller.on_for_seconds(SpeedPercent(-speed), duration)
                        elif action == "stop":
                            controller.off()
                        else:
                            print("Only forward/backward/stop supported for single motor.")

                except Exception as e:
                    print("Error handling command:", e)
