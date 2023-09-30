import argparse
from socket import *
from constants import *
import threading

from utils import *

serverPort = 12001
path = 'correa-tp-greedy.txt'
serverName = '127.0.0.1'


def main():
    args = parseArguments()
    #upload()
    download()

def download():
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind(('', serverPort))
        print("Socket open at:", serverPort)
        # llega conexion
        while True:
            package, clientAddress = s.recvfrom(CHUNK_SIZE)
            res, fileSize, fileName = serverHandshake(package)

            thread = threading.Thread(target=handleChunks, args=(res, clientAddress, "lib/client-files/" + fileName, fileSize))
            thread.start()

    s.close()

def upload():
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind(('', serverPort))
        print("Socket open at:", serverPort)
        # llega conexion
        while True:
            package, clientAddress = s.recvfrom(CHUNK_SIZE)
            res, fileSize, fileName = serverHandshake(package)
            thread = threading.Thread(target=handleChunks, args=(res, clientAddress, "lib/server-files/" + fileName, fileSize))
            thread.start()

    s.close()


def handleChunks(res, clientAddress, fileName, fileSize):
    with socket(AF_INET, SOCK_DGRAM) as transferSocket:
        transferSocket.bind(('localhost', 0))
        client_port = transferSocket.getsockname()[1]

        # Enviar el nuevo puerto al cliente para que este lo utilice
        paddingSize = CHUNK_SIZE - len(res) - 2
        transferSocket.sendto(res + client_port.to_bytes(2, byteorder='big') + b'\x00' * paddingSize, clientAddress)

        transferSocket.sendto(res, clientAddress)

        received = 0
        oldId = 0
        with open(fileName, "wb") as f:
            while received < fileSize:  # contemplar perdida de paquetes
                package, clientAddress = transferSocket.recvfrom(CHUNK_SIZE)
                package_id = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
                data = package[HEADER_SIZE:]
                if (oldId + 1) == package_id:  # Recibi paquete siguiente
                    received += len(data)
                    w = f.write(data)
                    oldId = package_id
                res = oldId.to_bytes(HEADER_SIZE, byteorder='big')
                transferSocket.sendto(res, clientAddress)

        f.close()

    transferSocket.close()


main()
