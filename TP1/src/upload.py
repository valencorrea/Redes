import os
from socket import *

serverName = '127.0.0.1'
serverPort = 12001
path = 'test.txt'

# CONSTANTES
CHUNK_SIZE = 64

with open('lib/client-files/' + path, "rb") as f:
    with socket(AF_INET, SOCK_DGRAM) as s:
        # PRIMER PAQUETE DE METADATA
        # [ LARGO DEL ARCHIVO en bytes ] 64 bits
        # [ NOMBRE                     ] 64 bits
        # ...
        # [ NOMBRE                     ] 64 bits

        fileSize = os.stat('lib/client-files/' + path).st_size.to_bytes(8, byteorder='big')
        metadata = fileSize + path.encode()
        s.sendto(metadata, (serverName, serverPort))

        while chunk := f.read(CHUNK_SIZE):
            s.sendto(chunk, (serverName, serverPort))

f.close()
