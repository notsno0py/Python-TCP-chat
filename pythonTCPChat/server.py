import threading
import socket
from cryptography.fernet import Fernet

HOST = '127.0.0.1'
PORT = 5051
KEY = b'u7R6X_0_8WpP-vB-7v9X8zV_5_J3j_k_L_m_N_o_P_q='
cipher = Fernet(KEY)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []


def broadcast(message, is_encrypted=True):
    if not is_encrypted:
        message = cipher.encrypt(message.encode('ascii'))

    for client in clients:
        try:
            client.send(message)
        except:
            pass


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if message:
                broadcast(message, is_encrypted=True)
            else:
                raise Exception("Connection closed")
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                nicknames.pop(index)
                broadcast(f'{nickname} left the chat!', is_encrypted=False)
            break


def receive():
    print("Server is running and listening...")
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of client is {nickname}")

        broadcast(f"{nickname} joined the chat!", is_encrypted=False)

        welcome_msg = cipher.encrypt('Connected to the server!'.encode('ascii'))
        client.send(welcome_msg)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


if __name__ == "__main__":
    receive()