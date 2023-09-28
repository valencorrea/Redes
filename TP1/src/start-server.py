from socket import *
from constants import *

serverPort = 12001
path = 'correa-tp-greedy.txt'
serverName = '127.0.0.1'


with socket(AF_INET, SOCK_DGRAM) as s:

    s.bind(('', serverPort))
    print("Socket open at:", serverPort)
    package, clientAddress = s.recvfrom(CHUNK_SIZE)
    print("recv handshake")
    package_id = int.from_bytes(package[:HEADER_SIZE])
    fileSize = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + LENGTH_BYTES])
    fileName = package[HEADER_SIZE + LENGTH_BYTES:].decode('utf-8')
    fileName = fileName.rstrip('\0')
    print("File name received:", fileName, 'of size:', fileSize)

    if fileSize > 5000000:  # Hacer las validaciones de verdad
        res = package_id.to_bytes(HEADER_SIZE) + FILE_TOO_BIG.to_bytes(STATUS_CODE_SIZE)
        print("File too big")
    else:
        res = package_id.to_bytes(HEADER_SIZE) + STATUS_OK.to_bytes(STATUS_CODE_SIZE)
        print("Status OK")
    print("About to send response")
    s.sendto(res, clientAddress)
    print("response sent")

    received = 0
    oldId = package_id

    with open('lib/server-files/' + fileName, "wb") as f:
        while received < fileSize:
            if fileSize - received < CHUNK_SIZE - HEADER_SIZE:
                package, clientAddress = s.recvfrom(CHUNK_SIZE)
            else:
                package, clientAddress = s.recvfrom(fileSize - received + HEADER_SIZE)
            package_id = int.from_bytes(package[:HEADER_SIZE])
            data = package[HEADER_SIZE:]

            if (oldId + 1) == package_id:  # Recibi paquete siguiente
                received += len(data)
                f.write(data)
                oldId = package_id
            res = oldId.to_bytes(HEADER_SIZE)
            s.sendto(res, clientAddress)

s.close()
f.close()
