import socket
import threading
import sys
import time
import os
import atexit

from message import Message
from message import MessageType

## Disable error messages
sys.stderr = object

## Debug function
DEBUG = False
def debug(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", * args, **kwargs)

## Global variables
server_ip = '127.0.0.1'
server_port = 0
cur_client_id = 0
cur_client_name = ""
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
time_out = 1 # seconds
client_dest_ip = 0

def receive_messages():
    global client_socket
    msg = Message()
    while True:
        try:
            server_socket, server_addr = client_socket.recvfrom(1024)
            msg.decode(server_socket)
            
            print("", end="\r")
            
            if msg.type == MessageType.OI:
                ## Messsage from server
                print(f"Server{server_addr}: {msg.text} \n", end="")
                client_socket.settimeout(None)
                continue
            elif msg.type == MessageType.ERRO:
                ## Message from server
                debug(msg.textSize)
                print(f"Server{server_addr}: {msg.text} \nMe({cur_client_name}|{cur_client_id}): ", end="")
                return
            elif msg.type == MessageType.MSG and msg.client_origin_id == 0:
                ## Message from server
                print(f"Server{server_addr}: {msg.text} \nMe({cur_client_name}|{cur_client_id}): ", end="")
            elif msg.type == MessageType.MSG:
                ## Message from client
                print(f"Client({msg.name}|{msg.client_origin_id}): {msg.text} \nMe({cur_client_name}|{cur_client_id}): ", end="")
            elif msg.type == MessageType.TCHAU:
                ## Message from client
                print(f"Client({msg.name}|{msg.client_origin_id}): {msg.text} \nMe({cur_client_name}|{cur_client_id}): ", end="")
            else:
                # send error message to server
                msg.set_message(MessageType.ERRO, cur_client_id, 0, cur_client_name, "Mensagem inválida.")
                client_socket.send(msg.encode())
        except:
            print("Conexão Não estabelecida.")
            return

### Send message to server to start connection
def client_oi():
    global cur_client_id, cur_client_name, client_socket, red_line
    msg = Message()

    msg.set_message(MessageType.OI, cur_client_id, 0, cur_client_name, "OI")
    client_socket.send(msg.encode())
    print(f"Me({cur_client_name}|{cur_client_id}): {msg.text}")
        
def send_messages():
    global cur_client_id, cur_client_name, client_socket, client_dest_ip
    while True:
        try:
            text = input(f"Me({cur_client_name}|{cur_client_id}): ")
            if text == "":
                continue
            if text == "TCHAU":
                msg = Message()
                msg.set_message(MessageType.TCHAU, cur_client_id, client_dest_ip, cur_client_name, "TCHAU")
                client_socket.send(msg.encode())
                return
            else:
                msg = Message()
                msg.set_message(MessageType.MSG, cur_client_id, client_dest_ip, cur_client_name, text)
                client_socket.send(msg.encode())
        except:
            print("Conexão perdida.")

def main():
    global cur_client_id, cur_client_name, server_ip, server_port, client_socket, time_out, client_dest_ip
    # get args in format: python cliente_udp.py <client_id> <client_name> <server_ip> <server_port>
    if len(sys.argv) != 6:
        print("Uso correto: python cliente_udp.py <client_id> <client_name> <server_ip> <server_port> <client_dest_ip>")
        return
    
    cur_client_id = int(sys.argv[1]) # This is the client's ID
    cur_client_name = sys.argv[2] # This is the client's name
    server_ip = sys.argv[3] # This is the server's IP address
    server_port = int(sys.argv[4]) # This is the server's port
    client_dest_ip = int(sys.argv[5]) # This is the client's destination IP address
    
    # Connect to the server udp
    client_socket.connect((server_ip, server_port))
    client_socket.settimeout(time_out)
    
    # STABILISH CONNECTION
    client_oi()
    
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()
    
    time.sleep(time_out+1)
    if not receive_thread.is_alive():
        sys.exit()
    else:
        send_thread = threading.Thread(target=send_messages)
        send_thread.start()


##  servidor também deve manter um registro (log) indicando o horário e identificação
## dos clientes que entram e saem do sistema.

## Caso uma conexão seja interrompida inesperadamente, o servidor deve tratar o evento como
## se uma mensagem TCHAU daquele cliente tivesse sido recebida
def atexit_handler():
    debug("Exiting...")
    global client_socket, cur_client_id, cur_client_name, client_dest_ip
    msg = Message()
    msg.set_message(MessageType.TCHAU, cur_client_id, client_dest_ip, cur_client_name, "TCHAU")
                
    print("", end="\r")
    print(f"Me({cur_client_name}|{cur_client_id}): {msg.text}")
    client_socket.send(msg.encode())
    client_socket.close()
    
if __name__ == '__main__':
    main()
    # when program ends, close socket and send TCHAU message
    atexit.register(atexit_handler)