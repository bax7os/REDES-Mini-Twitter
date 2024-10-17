import tkinter as tk
from tkinter import scrolledtext
import socket
import threading

class ChatClient:
    def __init__(self, master, server_ip, server_port, username):
        self.master = master
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = username

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, server_port))
        
        self.client_socket.send(f"OI|{username}".encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        if response != "OI":
            print("Falha na conexão.")
            self.client_socket.close()
            return
        
        self.build_gui()
        self.listen_for_messages()

    def build_gui(self):
        self.master.title("Chat")

        self.chat_display = scrolledtext.ScrolledText(self.master)
        self.chat_display.pack(padx=10, pady=10)

        self.message_entry = tk.Entry(self.master)
        self.message_entry.pack(padx=10, pady=5)
        self.message_entry.bind("<Return>", self.send_message)

        self.dest_entry = tk.Entry(self.master)
        self.dest_entry.pack(padx=10, pady=5)
        self.dest_entry.insert(0, 'todos')

        self.send_button = tk.Button(self.master, text="Enviar", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)

    def send_message(self, event=None):
        destination = self.dest_entry.get()
        message = self.message_entry.get()
        if message:
            self.client_socket.send(f"{self.username}|{destination}|{message}".encode('utf-8'))
            self.message_entry.delete(0, tk.END)

    def listen_for_messages(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.chat_display.insert(tk.END, message + "\n")
                self.chat_display.yview(tk.END)
            except:
                print("Conexão perdida.")
                self.client_socket.close()
                break

def main():
    root = tk.Tk()
    server_ip = input("Digite o IP do servidor: ")
    server_port = int(input("Digite a porta do servidor: "))
    username = input("Digite seu nome de usuário: ")

    client = ChatClient(root, server_ip, server_port, username)
    root.mainloop()

if __name__ == "__main__":
    main()
