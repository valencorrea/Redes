import os
from constants import *
from socket import *

serverName = '127.0.0.1'
serverPort = 12001
fileName = 'correa-tp-greedy.txt'


with (open('lib/client-files/' + fileName, "rb") as f):
    with socket(AF_INET, SOCK_DGRAM) as s:
        print("Socket created")
        s.settimeout(TIMEOUT)
        package_id = 0

        # PRIMER PAQUETE DE PETICION
        # [ ID (Paquete 0) ] 1 byte
        # [ LARGO DEL ARCHIVO en bytes ] 8 bytes
        # [ NOMBRE                     ] 8 bytes
        # ...
        # [ NOMBRE                     ] 8 bytes

        header = package_id.to_bytes(HEADER_SIZE)
        fileSize = os.stat('lib/client-files/' + fileName).st_size
        handshake = header + fileSize.to_bytes(LENGTH_BYTES) + fileName.ljust(CHUNK_SIZE - HEADER_SIZE - LENGTH_BYTES, '\0').encode('utf-8')
        print(len(handshake))

        print("To send file:", fileName, ' of size:', fileSize)
        s.sendto(handshake, (serverName, serverPort))
        print("Sent file:", fileName, ' of size:', fileSize)
        # ACCEPT/REJECT
        package, serverAddress = s.recvfrom(HEADER_SIZE + STATUS_CODE_SIZE)  # serverAddress: ('123.0.8.0', 55555)
        ack = int.from_bytes(package[:HEADER_SIZE])
        status_code = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + STATUS_CODE_SIZE])

        if status_code is not STATUS_OK:
            print("El servidor respondió con error", status_code)
            exit(1)
        else:
            print("Status OK")
        package_id += 1

        # ENVIO PAQUETES DE DATOS
        # [ ID (numero del paquete)    ] 1 byte
        # [           DATA             ] 255 bytes

        while data := f.read(CHUNK_SIZE - HEADER_SIZE):
            header_b = package_id.to_bytes(HEADER_SIZE)
            chunk = header_b + data
            s.sendto(chunk, serverAddress)

            package, serverAddress = s.recvfrom(HEADER_SIZE)
            ack = int.from_bytes(package)
            print(ack)
            if ack == package_id:
                package_id += 1

f.close()
s.close()
