import argparse
import socket
from constants import *
import threading

from utils import *

serverPort = 12001
serverName = '127.0.0.1'


def main():
    #args = parseArguments()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', serverPort))
        while True:
            package, clientAddress = s.recvfrom(CHUNK_SIZE)
            res, clientMethod = getClientHeader(package)

            if clientMethod == UPLOAD:
                fileSize, fileName = getUploadClientFileMetadata(package)
                callClientMethod(res, fileSize, clientAddress, "lib/server-files/" + fileName)
#            elif clientMethod == DOWNLOAD:
#                fileName = getDownloadClientFileMetadata(package)
#                fileSize = os.stat("lib/server-files/" + fileName).st_size #CHEKEAR QUE LO TENGO POSTA
#                print(fileSize)
#                callClientMethod(res, fileSize, clientAddress, "lib/client-files/" + fileName)
    s.close()


def callClientMethod(res, fileSize, clientAddress, path):
    thread = threading.Thread(target=handleChunks, args=(res, clientAddress, path, fileSize))
    thread.start()


def handleChunks(res, clientAddress, fileName, fileSize):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as transferSocket:
        transferSocket.bind(('localhost', 0))
        client_port = transferSocket.getsockname()[1]
        # Enviar el nuevo puerto al cliente para que este lo utilice
        paddingSize = CHUNK_SIZE - len(res) - 2
        transferSocket.sendto(res + client_port.to_bytes(2, byteorder='big') + b'\x00' * paddingSize, clientAddress)

        received = 0
        oldId = 0
        with open(fileName, "wb") as f:
            while received < fileSize:  # contemplar perdida de paquetes
                package, clientAddress = transferSocket.recvfrom(CHUNK_SIZE)
                package_id = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
                data = package[HEADER_SIZE:]
                if (oldId + 1) == package_id:  # Recibi paquete siguiente
                    received += len(data)
                    f.write(data)
                    oldId = package_id
                res = oldId.to_bytes(HEADER_SIZE, byteorder='big')
                transferSocket.sendto(res, clientAddress)

        f.close()

    transferSocket.close()


main()
