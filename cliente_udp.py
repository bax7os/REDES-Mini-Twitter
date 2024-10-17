import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Conexão perdida.")
            client_socket.close()
            break

def send_messages(client_socket, username):
    while True:
        destination = input("Digite o destinatário (ou 'todos' para mensagem pública): ")
        message = input("Digite a mensagem: ")
        full_message = f"{username}|{destination}|{message}"
        client_socket.send(full_message.encode('utf-8'))

def main():
    ip = input("Digite o IP do servidor: ")
    port = int(input("Digite a porta do servidor: "))
    username = input("Digite seu nome de usuário: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))

    # Envia mensagem de OI e espera pela resposta
    client_socket.send(f"OI|{username}".encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    if response != "OI":
        print("Falha na conexão.")
        client_socket.close()
        return

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    send_messages(client_socket, username)

if __name__ == "__main__":
    main()
