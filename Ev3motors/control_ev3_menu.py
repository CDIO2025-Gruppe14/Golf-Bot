import socket

HOST = '0.0.0.0'  # enter EV3 IP address
PORT = 65432

def send_command(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall((command + '\n').encode())
            print("Sent command: " + command)
    except Exception as e:
        print("Error sending command '{}': {}".format(command, e))

def menu():
    while True:
        print("\n--- EV3 Robot Control Menu ---")
        print("1. Move forward")
        print("2. Move backward")
        print("3. Turn left")
        print("4. Turn right")
        print("5. Stop")
        print("6. Quit")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            send_command("forward")
        elif choice == '2':
            send_command("backward")
        elif choice == '3':
            send_command("left")
        elif choice == '4':
            send_command("right")
        elif choice == '5':
            send_command("stop")
        elif choice == '6':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    menu()