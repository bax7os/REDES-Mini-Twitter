import socket
import threading
import sys
import time

from message import Message
from message import MessageType

## Disable error messages
sys.stderr = object

DEBUG = False
def debug(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", * args, **kwargs)

## Global variables
server_ip = '127.0.0.1'
server_port = 12345
clients_limit = 15
geral_info_time = 100
waked_up = time.time()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   
# client map with id and socket
clients = {}

def geral_info():
    message = Message()
    while True:
        time.sleep(geral_info_time)
        for client in clients:
            client_socket = clients[client]
            message.set_message(MessageType.MSG, 0, client, "Servidor", f"Servidor ativo com {len(clients)} clientes aberto há {int(time.time() - waked_up)} segundos.")
            server_socket.sendto(message.encode(), client_socket)

def handle_client():
    global clients
    message = Message()
    while True:
        try:
            # Receive message from client
            client_socket, client_address = server_socket.recvfrom(2048)
            message.decode(client_socket)
            print(f"[{time.strftime('%X %x')}] Client({message.name}|{message.client_origin_id}): {message.text}")
        except:
            client_socket.close()
            clients.remove(client_socket)
            break


def save_client(id, client_socket):
    global clients
    clients[id] = client_socket

def handle_oi(message:Message, client_address):
    global clients, clients_limit
    
    #check if server is full
    if len(clients) >= clients_limit:
        debug("Servidor cheio.")
        message.set_message(MessageType.ERRO, 0, message.client_origin_id, "Server", "Servidor cheio.")
        server_socket.sendto(message.encode(), client_address)
        return
    
    # check if id is already in use    
    if message.client_origin_id in clients:
        debug("ID já está em uso.")
        message.set_message(MessageType.ERRO, 0, message.client_origin_id, "Server", "ID já está em uso.")
        server_socket.sendto(message.encode(), client_address)
        return
    else:
        debug("ID disponível.")
        server_socket.sendto(message.encode(), client_address) # Send same message to client
        # save cliente in list
        save_client(message.client_origin_id, client_address)
        # create a thread to handle client

def handle_error(message:Message, client_address):
    debug("Erro recebido.")
    print(f"[{time.strftime('%X %x')}] Client({message.name}|{message.client_origin_id}): {message.text}")

def handle_msg(message:Message, client_address):
    cur_message = Message()
    if (message.client_dest_id == 0):
        # broadcast message to all client except the sender
        for client in clients:
            if client != message.client_origin_id:
                cur_message.set_message(MessageType.MSG, message.client_origin_id, client, message.name, message.text)
                server_socket.sendto(cur_message.encode(), clients[client])
    else:
        if message.client_dest_id not in clients:
            debug("Cliente não encontrado.")
            cur_message.set_message(MessageType.ERRO, 0, message.client_origin_id, "Server", "Cliente não encontrado.")
            server_socket.sendto(cur_message.encode(), client_address)
        else:
            cur_message.set_message(MessageType.MSG, message.client_origin_id, message.client_dest_id, message.name, message.text)
            server_socket.sendto(cur_message.encode(), clients[message.client_dest_id])

def handle_tchau(message:Message, client_address):
    clients.pop(message.client_origin_id)
    if message.client_dest_id == 0:
        for client in clients:
            # send same message to all clients
            server_socket.sendto(message.encode(), clients[client])
    else:
        # only send the dest
        server_socket.sendto(message.encode(), clients[message.client_dest_id])             
    
    
def main():
    global server_socket, server_ip, server_port
    server_socket.bind((server_ip, server_port))

    print(f"Servidor ouvindo em {server_ip}:{server_port}")

    receive_thread = threading.Thread(target=geral_info)
    receive_thread.start()
    
    message = Message()
    while True:
        # Receive message from client
        client_socket, client_address = server_socket.recvfrom(2048)
        message.decode(client_socket)
        print(f"[{time.strftime('%X %x')}] Client({message.name}|{message.client_origin_id}): {message.text}")
        
        if(message.type == MessageType.OI):
            handle_oi(message, client_address)
        elif(message.type == MessageType.ERRO):
            handle_error(message, client_address)
        elif(message.type == MessageType.MSG):
            handle_msg(message, client_address)
        elif(message.type == MessageType.TCHAU):
            handle_tchau(message, client_address)
        else:
            print("Mensagem inválida.")
            message.set_message(MessageType.ERRO, 0, message.client_origin_id, "Servidor", "Mensagem inválida.")
            server_socket.sendto(message.encode(), client_address)
            continue
if __name__ == "__main__":
    main()
