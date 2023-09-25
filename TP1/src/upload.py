import os
from socket import *

serverName = '127.0.0.1'
serverPort = 12001
path = 'test.txt'

# CONSTANTES
CHUNK_SIZE = 64
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
        responseTime = 0
        ack = 1

        while (chunk := f.read(CHUNK_SIZE)) and (ack == 1):
            chunkMetadata = id.to_bytes(8, byteorder='big') + ack.to_bytes(8, byteorder='big')
            data = chunkMetadata + chunk
            s.sendto(data, (serverName, serverPort))

            if ack == 1:
                id = id + 1

f.close()
