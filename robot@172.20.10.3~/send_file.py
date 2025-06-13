"""import socket

HOST = '172.20.10.2'  # IP'en til EV3
PORT = 65432          # Den port din EV3 socket-server lytter på
FILENAME = 'ev3_socket_server.py'

with open(FILENAME, 'rb') as f:
    data = f.read()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'FILE:' + FILENAME.encode() + b'\n')
    s.sendall(data)

print(f"Sent {FILENAME} to EV3")
"""