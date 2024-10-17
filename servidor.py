import socket
import threading

clients = []

def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            broadcast(message, client_socket)
        except:
            client_socket.close()
            clients.remove(client_socket)
            break

def main():
    server_ip = '0.0.0.0'
    server_port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen()

    print(f"Servidor ouvindo em {server_ip}:{server_port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Nova conexão de {client_address}")
        clients.append(client_socket)
        client_socket.send("OI".encode('utf-8'))

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    main()
