import socket
import time

HOST = '172.20.10.3'  # ← husk igen at opdatere, hvis IP ændres
PORT = 65432

def send_command(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode())
            print("Sent command: {}".format(command))
    except Exception as e:
        print("Error sending command: {}".format(e))

def manual_keyboard_mode():
    print("\n--- Simple Keyboard Control Mode ---")
    print("W = Forward | S = Backward | A = Left | D = Right | Q = Stop | X = Exit")
    motor_ports = input("Enter motor ports (e.g., A+B): ").strip().upper().replace(' ', '')
    speed = input("Enter speed (e.g., 75 for 75%): ").strip()

    while True:
        key = input("Enter command: ").strip().lower()

        if key == 'w':
            send_command("forward:{}:{}".format(motor_ports, speed))
        elif key == 's':
            send_command("backward:{}:{}".format(motor_ports, speed))
        elif key == 'a':
            send_command("left:{}:{}".format(motor_ports, speed))
        elif key == 'd':
            send_command("right:{}:{}".format(motor_ports, speed))
        elif key == 'q':
            send_command("stop:{}:{}".format(motor_ports, speed))
        elif key == 'x':
            print("Exiting keyboard mode.")
            break
        else:
            print("Unknown input. Use W/S/A/D/Q or X to exit.")
        time.sleep(0.3)

def menu():
    while True:
        print("\n--- EV3 Robot Control Menu ---")
        print("1. Move forward")
        print("2. Move backward")
        print("3. Turn left")
        print("4. Turn right")
        print("5. Stop")
        print("6. Simple keyboard input mode")
        print("7. Quit")

        choice = input("Enter your choice: ").strip()

        if choice in {'1', '2', '3', '4', '5'}:
            motor_ports = input("Enter motor ports (e.g., A+B): ").strip().upper().replace(' ', '')
            speed = input("Enter speed (e.g., 75 for 75%): ").strip()
            command_map = {
                '1': 'forward',
                '2': 'backward',
                '3': 'left',
                '4': 'right',
                '5': 'stop'
            }
            command = "{}:{}:{}".format(command_map[choice], motor_ports, speed)
            send_command(command)

        elif choice == '6':
            manual_keyboard_mode()

        elif choice == '7':
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Try again.")

# Run the program
if __name__ == "__main__":
    menu()