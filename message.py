import enum

class Message:
    def set_message(self, type, client_origin_id, client_dest_id, name='', text=''):
        self.type = type
        self.client_origin_id = client_origin_id
        self.client_dest_id = client_dest_id
        self.textSize = len(text)

        if len(name) > 20:
            raise Exception("Nome do cliente deve ter no máximo 20 caracteres.")
        self.name = name

        if len(text) > 140:
            raise Exception("Texto da mensagem deve ter no máximo 100 caracteres.")
        self.text = text
    def encode(self):
        msg = str(format(self.type.value,'19d')).encode('utf-8') + str(format(self.client_origin_id, '19d')).encode('utf-8') + str(format(self.client_dest_id, '19d')).encode('utf-8') + str(format(self.textSize, '19d')).encode('utf-8') + self.name.encode('utf-8') + self.text.encode('utf-8') + b'\0'
        return msg

    def decode(self, message):
        message = message.decode('utf-8').split('\0')[0]
        # get first int
        self.type = MessageType(int(message[:19]))
        # get second int
        self.client_origin_id = int(message[19:38])
        # get third int
        self.client_dest_id = int(message[38:57])
        # get fourth int
        self.textSize = int(message[57:76])

        self.text = ""
        self.name = ""
        if self.textSize > 0:
            self.name = message[76:len(message)-self.textSize]
            self.text = message[len(message)-self.textSize:]  
# type enum 
class MessageType(enum.Enum):
    OI = 0
    TCHAU = 1
    MSG = 2
    ERRO = 3