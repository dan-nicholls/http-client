import socket
import time
from threading import Event, Thread
from typing import Tuple, List
import os.path
import argparse
import signal

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
        self.client_threads: List[Thread] = []
        self.max_connections_reached = False
        self.directory = directory

        # Set Event for closing the server
        self.shutdown_flag = Event()
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)

    def shutdown_handler(self, signum, frame):
        print("Shutting down server")
        self.shutdown_flag.set()

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

    def get_resource(self, resource: str) -> bytes:
        filepath = self.directory + resource
        print(filepath)
        if os.path.isdir(filepath):
            filepath = filepath + "/index.html"
        if not os.path.exists(filepath):
            raise RequestError("Resource not found")

        with open(filepath, "rb") as file:
            return file.read()

    def handle_client_connection(self, client_sock: socket.socket):
        try:
            data = client_sock.recv(1024).decode(ENCODING_FORMAT)
            print(f"Request: {data}")

            method, resource = MyServer.parse_request(data)
            MyServer.validate_request(method, resource)
            message = self.get_resource(resource)
            client_sock.sendall(message)
        except Exception as e:
            print(f"Bad Request: {e}")
            error_message = str(e).encode(ENCODING_FORMAT)
            client_sock.sendall(error_message)
        finally:
            client_sock.close()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(MAX_CONNECTIONS)
            s.settimeout(1.0)

            print(f"Listening on {self.host}:{self.port}")

            while not self.shutdown_flag.is_set():
                try:
                    client_sock, address = s.accept()
                    print("Accepted connection to ", address)
                    client_handler = Thread(
                        target=self.handle_client_connection, args=(client_sock,)
                    )
                    self.client_threads.append(client_handler)
                    client_handler.start()
                except socket.timeout:
                    continue
                except socket.error as e:
                    print(f"Error: {e}")

            s.close()

            for thread in self.client_threads:
                thread.join()

            print("Server has shutdown")


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
