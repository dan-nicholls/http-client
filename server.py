import socket
import threading

HOST = socket.gethostname()
PORT = 9000


def handle_client_connection(client_sock):
    data = client_sock.recv(1024)
    print("Request:", repr(data))
    client_sock.sendall(b"This is a server response")
    client_sock.close()


# 4. Accept connections in a loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)

    print(f"Listening on {socket.gethostname()}")

    try:
        while True:
            client_sock, addr = s.accept()
            print("Accpeted connection to ", addr)
            client_handler = threading.Thread(
                target=handle_client_connection, args=(client_sock,)
            )
            client_handler.start()
    finally:
        s.close()
        print("Server closed")
