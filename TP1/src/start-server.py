import argparse
from socket import *
from constants import *
import threading

serverPort = 12001
path = 'correa-tp-greedy.txt'
serverName = '127.0.0.1'


def main():
    # parser = argparse.ArgumentParser(description="Start a server.")

    # parser.add_argument('-H', '--host', help="Service IP address", required=True)
    # parser.add_argument('-p', '--port', help="Service port", type=int, required=True)
    # parser.add_argument('-s', '--storage', help="Storage directory path", required=True)

    # group = parser.add_mutually_exclusive_group()
    # group.add_argument('-v', '--verbose', help="Increase output verbosity", action="store_true")
    # group.add_argument('-q', '--quiet', help="Decrease output verbosity", action="store_true")

    # args = parser.parse_args()
    upload()


def upload():
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.bind(('', serverPort))
        print("Socket open at:", serverPort)
        # llega conexion
        while True:
            package, clientAddress = s.recvfrom(CHUNK_SIZE)

            # hago validaciones
            print("recv handshake")
            package_id = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
            fileSize = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + LENGTH_BYTES], byteorder='big')
            fileName = package[HEADER_SIZE + LENGTH_BYTES:].decode('utf-8')
            fileName = fileName.rstrip('\0')
            print("File name received:", fileName, 'of size:', fileSize)

            #        if fileSize > 5000000:  # Hacer las validaciones de verdad
            #            res = package_id.to_bytes(HEADER_SIZE) + FILE_TOO_BIG.to_bytes(STATUS_CODE_SIZE)
            #            print("File too big")
            #        else:
            # puerto server, puerto cliente, puerto server donde se hace la transferencia
            # levanto hilo con port
            res = package_id.to_bytes(HEADER_SIZE, byteorder='big') + STATUS_OK.to_bytes(STATUS_CODE_SIZE,
                                                                                         byteorder='big')
            #            print("Status OK")

            print("About to send response")
            thread = threading.Thread(target=handleChunks, args=(res, clientAddress, fileName, fileSize))
            thread.start()

    s.close()


def handleChunks(res, clientAddress, fileName, fileSize):
    with socket(AF_INET, SOCK_DGRAM) as transferSocket:
        transferSocket.bind(('localhost', 0))
        client_port = transferSocket.getsockname()[1]
        print(client_port)
        # Enviar el nuevo puerto al cliente para que este lo utilice
        paddingSize = CHUNK_SIZE - len(res) - 2
        transferSocket.sendto(res + client_port.to_bytes(2, byteorder='big') + b'\x00' * paddingSize, clientAddress)

        transferSocket.sendto(res, clientAddress)
        print("response sent")

        received = 0
        oldId = 0
        with open('lib/server-files/' + fileName, "wb") as f:
            while received < fileSize:  # contemplar perdida de paquetes
                package, clientAddress = transferSocket.recvfrom(CHUNK_SIZE)
                package_id = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
                data = package[HEADER_SIZE:]
                print(f'{oldId} != {package_id}')
                if (oldId + 1) == package_id:  # Recibi paquete siguiente
                    print("recibi id" + str(package_id))
                    received += len(data)
                    w = f.write(data)
                    print(w)
                    oldId = package_id
                res = oldId.to_bytes(HEADER_SIZE, byteorder='big')
                transferSocket.sendto(res, clientAddress)

        f.close()

    transferSocket.close()


main()
