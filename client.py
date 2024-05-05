import socket
import threading
import time

HOST = socket.gethostname()
PORT = 9000


class MyClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def send_request(self):
        # socket is implicitly closed by socket.socket.__exit__
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((HOST, PORT))
                # time.sleep(5)
                s.sendall(b"GET This is a client request")
                data = s.recv(1024)
                print("Response:", repr(data))
            except socket.error as e:
                print(f"Connection error: {e}")


if __name__ == "__main__":

    def create_client_and_send_request():
        client = MyClient(HOST, PORT)
        client.send_request()

    threads = []

    for _ in range(1):
        thread = threading.Thread(target=create_client_and_send_request)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
