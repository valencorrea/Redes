from socket import *

serverPort = 12001
path = 'test.txt'

# CONSTANTES
CHUNK_SIZE = 64

with open('lib/server-files/' + path, "wb") as f:
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind(('', serverPort))
        chunk, clientAddress = s.recvfrom(CHUNK_SIZE)
        f.write(chunk)

f.close()
