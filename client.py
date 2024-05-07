import socket
import threading
import time
import argparse

HOST = socket.gethostname()
PORT = 9000


class MyClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def send_request(self, resource: str = "/"):
        # socket is implicitly closed by socket.socket.__exit__
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
                # time.sleep(5)
                request = "GET " + resource
                s.sendall(request.encode("utf-8"))
                data = s.recv(1024)
                print("Response:", repr(data))
            except socket.error as e:
                print(f"Connection error: {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="client",
        description="A simple HTTP client",
        usage="%(prog)s [options] [resource]",
    )

    parser.add_argument(
        "resource",
        nargs="?",
        type=str,
        default="/",
        help="The resource to fetch (default: /)",
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        default=socket.gethostname(),
        help="Host to connect to (default: current hostname)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=9000,
        choices=range(1, 65536),
        metavar="[1-65535]",
        help="The port to connect on (default: 9000)",
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=1,
        help="Number of request threads to instantiate",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    def create_client_and_send_request():
        client = MyClient(args.host, PORT)
        client.send_request(args.resource)

    threads = []

    for _ in range(args.num):
        thread = threading.Thread(target=create_client_and_send_request)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
