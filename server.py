import socket

HOST = socket.gethostname()
PORT = 9000

# 4. Accept connections in a loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)

    print(f"Listening on {socket.gethostname()}")

    try:
        while True:
            conn, addr = s.accept()

            with conn:
                print("Connected by", addr)
                data = conn.recv(1024)
                print(f"Request ({addr}):", repr(data))
                conn.sendall(b"This is a server response")
                conn.close()
    finally:
        s.close()
        print("Server closed")
