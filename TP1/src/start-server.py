from socket import *

serverPort = 12001
path = 'test.txt'

# CONSTANTES
CHUNK_SIZE = 64


with socket(AF_INET, SOCK_DGRAM) as s:
    s.bind(('', serverPort))
    content, clientAddress = s.recvfrom(CHUNK_SIZE)

    fileSize = int.from_bytes(content[:8], byteorder='big')
    fileName = content[8:].decode()

    print("FILE SIZE:", fileSize)
    print("FILE NAME:", fileName)

    received = 0
    with open('lib/server-files/' + fileName, "wb") as f:
        while received < fileSize:
            content, clientAddress = s.recvfrom(CHUNK_SIZE)
            received += len(content)
            print(content)
            f.write(content)

s.close()
f.close()
