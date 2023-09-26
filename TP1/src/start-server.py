from socket import *

serverPort = 12001
path = 'correa-tp-greedy.txt'
serverName = '127.0.0.1'


# CONSTANTES
CHUNK_SIZE = 128

with socket(AF_INET, SOCK_DGRAM) as s:
    s.bind(('', serverPort))
    content, clientAddress = s.recvfrom(CHUNK_SIZE)

    fileSize = int.from_bytes(content[:8], byteorder='big')
    fileName = content[8:].decode()

    received = 0
    oldId = -1

    with open('lib/server-files/' + fileName, "wb") as f:
        while received < fileSize:
            content, clientAddress = s.recvfrom(CHUNK_SIZE)

            id, ack, chunk = int.from_bytes(content[:2], byteorder='big'), int.from_bytes(content[2:10], byteorder='big'), content[16:]

            if oldId == id:
                responseAck = id
                chunkMetadata = oldId.to_bytes(2, byteorder='big') + responseAck.to_bytes(8, byteorder='big')
                data = chunkMetadata + chunk
                s.sendto(data, (clientAddress[0], clientAddress[1]))
                continue

            received += len(chunk)
            f.write(chunk)
            oldId = id

            responseAck = id
            chunkMetadata = oldId.to_bytes(2, byteorder='big') + responseAck.to_bytes(8, byteorder='big')
            data = chunkMetadata + chunk
            s.sendto(data, (clientAddress[0], clientAddress[1]))


s.close()
f.close()
