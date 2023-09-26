import os
import sys
from socket import *

serverName = '127.0.0.1'
serverPort = 12001
path = 'correa-tp-greedy.txt'

# CONSTANTES
CHUNK_SIZE = 128
TIMEOUT = 5 # RANDOM, PERO PONER ALGUNA JUSTIFICACION EN EL INFORME

class header:
    def __init__(self, seqNumber, ack):
        self.seqNumber = seqNumber
        self.ack = ack


with open('lib/client-files/' + path, "rb") as f:
    with socket(AF_INET, SOCK_DGRAM) as s:
        # PRIMER PAQUETE DE METADATA
        # [ LARGO DEL ARCHIVO en bytes ] 64 bits
        # [ NOMBRE                     ] 64 bits
        # ...
        # [ NOMBRE                     ] 64 bits
        s.settimeout(TIMEOUT)
        fileSize = os.stat('lib/client-files/' + path).st_size.to_bytes(8, byteorder='big')
        fileMetadata = fileSize + path.encode()
        s.sendto(fileMetadata, (serverName, serverPort))

        id = 0
        ack = 0

        while chunk := f.read(CHUNK_SIZE-16):
            chunkMetadata = id.to_bytes(2, byteorder='big') + ack.to_bytes(8, byteorder='big')
            data = chunkMetadata + chunk
            s.sendto(data, (serverName, serverPort))

            content, clientAddress = s.recvfrom(CHUNK_SIZE)
            id, ack, chunk = int.from_bytes(content[:2], byteorder='big'), int.from_bytes(content[2:10], byteorder='big'), content[16:]

            if ack == id:
                id = id + 1

f.close()
