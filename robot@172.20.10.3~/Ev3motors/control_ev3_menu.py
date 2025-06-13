import socket
import time
import keyboard

def send_command(command):
    # Sends a command to the EV3 robot over a socket connection.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode())
            print(f"Sent command: {command}")
    except Exception as e:
        print(f"Error sending command: {e}")

HOST = '172.20.10.3'
PORT = 65432

def keyboard_mode():
    print("\n--- Keyboard Control Mode ---")
    print("W = Forward | S = Backward | A = Left | D = Right | Q = Stop | ESC = Quit")
    motor_ports = input("Enter motor ports (e.g., A+B): ").strip().upper().replace(' ', '')

    try:
        while True:
            if keyboard.is_pressed('w'):
                send_command(f'forward:{motor_ports}')
                time.sleep(0.3)
            elif keyboard.is_pressed('s'):
                send_command(f'backward:{motor_ports}')
                time.sleep(0.3)
            elif keyboard.is_pressed('a'):
                send_command(f'left:{motor_ports}')
                time.sleep(0.3)
            elif keyboard.is_pressed('d'):
                send_command(f'right:{motor_ports}')
                time.sleep(0.3)
            elif keyboard.is_pressed('q'):
                send_command(f'stop:{motor_ports}')
                time.sleep(0.3)
            elif keyboard.is_pressed('esc'):
                print("Exiting keyboard control.")
                break
    except KeyboardInterrupt:
        print("\nKeyboard control stopped.")

def menu():
    while True:
        print("\n--- EV3 Robot Control Menu ---")
        print("1. Move forward")
        print("2. Move backward")
        print("3. Turn left")
        print("4. Turn right")
        print("5. Stop")
        print("6. Keyboard WASD control")
        print("7. Quit")

        choice = input("Enter your choice: ").strip()

        if choice in {'1', '2', '3', '4', '5'}:
            motor_ports = input("Enter motor port(s) to use (e.g., A, B, C+D, A+B): ").strip().upper().replace(' ', '')
            command_map = {
                '1': 'forward',
                '2': 'backward',
                '3': 'left',
                '4': 'right',
                '5': 'stop'
            }
            command = f"{command_map[choice]}:{motor_ports}"
            send_command(command)

        elif choice == '6':
            keyboard_mode()

        elif choice == '7':
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Try again.")