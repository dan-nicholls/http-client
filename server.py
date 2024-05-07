import socket
import threading
import time
from typing import Tuple
import os.path
import argparse

HOST = socket.gethostname()
PORT = 9000
MAX_CONNECTIONS = 2
ENCODING_FORMAT = "utf-8"


class RequestError(Exception):
    def __init__(self, message="Invalid request"):
        super().__init__(message)


class MyServer:
    def __init__(self, host: str, port: int, directory: str = "."):
        self.host = host
        self.port = port
        self.active_connections = 0
        self.max_connections_reached = 0
        self.directory = directory

    @staticmethod
    def parse_request(data: str) -> Tuple[str, str]:
        parts = data.split()
        if len(parts) != 2:
            raise RequestError()

        method = parts[0]
        resource = parts[1]

        return method, resource

    @staticmethod
    def validate_request(method: str, resource: str) -> None:
        if method != "GET":
            raise RequestError("Invalid request type")

        if not resource.startswith("/"):
            raise RequestError("Invalid resource")

    def get_resource(self, resource: str) -> str:
        filepath = self.directory + resource
        print(filepath)
        if os.path.isdir(filepath):
            filepath = filepath + "/index.html"
        if not os.path.exists(filepath):
            raise RequestError("Resource not found")

        with open(filepath, "r", encoding=ENCODING_FORMAT) as file:
            return file.read()

    def handle_client_connection(self, client_sock: socket.socket):
        data = client_sock.recv(1024).decode(ENCODING_FORMAT)
        print(f"Request: {data}")

        try:
            method, resource = MyServer.parse_request(data)
            MyServer.validate_request(method, resource)
            message = self.get_resource(resource)
            # client_sock.sendall("This is a server response".encode(ENCODING_FORMAT))
            client_sock.sendall(message.encode(ENCODING_FORMAT))
        except Exception as e:
            print(f"Bad Request: {e}")
            error_message = str(e).encode(ENCODING_FORMAT)
            client_sock.sendall(error_message)

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


def parse_args():
    parser = argparse.ArgumentParser(
        prog="server", description="A simple HTTP server", usage="%(prog)s [options]"
    )

    server_config = parser.add_argument_group("Server Configuration")
    server_config.add_argument(
        "-H",
        "--host",
        type=str,
        default=socket.gethostname(),
        help="Set the host on which to listen (default: current hostname)",
    )
    server_config.add_argument(
        "-p",
        "--port",
        type=int,
        default=9000,
        choices=range(1, 65536),
        metavar="[1-65535]",
        help="Set the port on which the server listens (default: 9000)",
    )
    server_config.add_argument(
        "--max_conn",
        type=int,
        default=2,
        help="Set the maximum number of concurrent connections (default: 2)",
    )
    server_config.add_argument(
        "-d",
        "--directory",
        type=str,
        default=".",
        help="Set the directory on which to server files (default: current directory)",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.9",
        help="Show the HTTP server version number",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    server = MyServer(args.host, args.port, args.directory)
    server.start()
