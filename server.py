import socket
import threading
import time

HOST = socket.gethostname()
PORT = 9000
MAX_CONNECTIONS = 2


class MyServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.active_connections = 0
        self.max_connections_reached = 0

    def handle_client_connection(self, client_sock: socket.socket):
        data = client_sock.recv(1024)
        print("Request:", repr(data))
        if data.startswith(b"GET"):
            client_sock.sendall(b"This is a server response")
        else:
            client_sock.sendall(b"Invalid request")
        client_sock.close()
        self.active_connections -= 1
        if self.active_connections < MAX_CONNECTIONS:
            self.max_connections_reached = False

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(MAX_CONNECTIONS)

            print(f"Listening on {socket.gethostname()}")

            while True:
                if self.active_connections < MAX_CONNECTIONS:
                    client_sock, address = s.accept()
                    print("Accepted connection to ", address)
                    self.active_connections += 1
                    client_handler = threading.Thread(
                        target=self.handle_client_connection, args=(client_sock,)
                    )
                    client_handler.start()
                else:
                    if not self.max_connections_reached:
                        print("Max connections reached. Refusuing new connections")
                        self.max_connections_reached = True
                    time.sleep(1)


if __name__ == "__main__":
    server = MyServer(HOST, PORT)
    server.start()
