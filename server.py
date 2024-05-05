import socket
import threading

HOST = socket.gethostname()
PORT = 9000


class MyServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def handle_client_connection(self, client_sock: socket.socket):
        data = client_sock.recv(1024)
        print("Request:", repr(data))
        client_sock.sendall(b"This is a server response")
        client_sock.close()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(1)

            print(f"Listening on {socket.gethostname()}")

            try:
                while True:
                    client_sock, address = s.accept()
                    print("Accepted connection to ", address)
                    client_handler = threading.Thread(
                        target=self.handle_client_connection, args=(client_sock,)
                    )
                    client_handler.start()
            finally:
                s.close()
                print("Server closed.")


if __name__ == "__main__":
    server = MyServer(HOST, PORT)
    server.start()
