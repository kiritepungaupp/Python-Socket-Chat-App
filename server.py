import threading
import socket
import datetime

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_lock = threading.Lock()


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} Connected")
    client_id = str(addr)
    clients[client_id] = conn

    try:
        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                break

            if msg.startswith('/discover'):
                with clients_lock:
                    print(clients)
                    client_list = "\n".join([f"{i + 1}. {cid}" for i, cid in enumerate(clients.keys()) if cid != client_id])
                conn.sendall(f"Connected clients:\n{client_list}".encode(FORMAT))

            elif msg.startswith('/connect'):
                try:

                    _,target_id = msg.split(" ",1)

                    
                    target_conn = clients.get(str(target_id))
                    if target_conn:
                        conn.sendall(f"Connected".encode(FORMAT))
                        while True:
                            direct_msg = conn.recv(1024).decode(FORMAT)
                            if direct_msg == DISCONNECT_MESSAGE:
                                break
                            target_conn.sendall(f"PRIVATE: [{client_id}]: {direct_msg}".encode(FORMAT))
                    else:
                        conn.sendall(f"CLIENT: {target_id} not found.".encode(FORMAT))
                except Exception as e:
                    conn.sendall("Usage: /connect <client_id>".encode(FORMAT))

            else:
                with clients_lock:
                    for cid, c in clients.items():
                        if cid != client_id:
                            c.sendall(f"PUBLIC | [{client_id}] {msg}".encode(FORMAT))

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        with clients_lock:
            clients.pop(client_id, None)

        conn.close()

def listen_commands():
    while True:
        command = input()
        if command.startswith('/bc'):
            try:
                with clients_lock:
                    for cid, conn in clients.items():
                        conn.sendall(f"[Broadcast]: {command.split(' ', 1)[1]}".encode(FORMAT))
                print("Broadcast Successful")
            except Exception as e:
                print(f'Broadcast Failed: {e}')

    

def start():
    print('[SERVER STARTED]!')
    thread = threading.Thread(target=listen_commands)
    thread.start()
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start()
