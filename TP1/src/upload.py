from socket import *

serverName = '127.0.0.1'
serverPort = 12001
path = 'test.txt'

# CONSTANTES
CHUNK_SIZE = 64

with open('lib/client-files/' + path, "rb") as f:
    with socket(AF_INET, SOCK_DGRAM) as s:
        while chunk := f.read(CHUNK_SIZE):
            s.sendto(chunk, (serverName, serverPort))

f.close()
