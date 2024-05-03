import socket

HOST = socket.gethostname()
PORT = 9000

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    data = s.recv(1024)
    print("Recieved", repr(data))

    s.sendall(b"This is a message from the client")
finally:
    s.close()
