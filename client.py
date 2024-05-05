import socket

HOST = socket.gethostname()
PORT = 9000


class MyClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def send_request(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(b"This is a client request")
                data = s.recv(1024)
                print("Response:", repr(data))
        finally:
            s.close()


if __name__ == "__main__":
    client = MyClient(HOST, PORT)
    client.send_request()
