import socket

HOST = socket.gethostname()
PORT = 9000

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    s.sendall(b"This is a client request")

    data = s.recv(1024)
    print("Response:", repr(data))
finally:
    s.close()
