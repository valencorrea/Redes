import socket
import threading
import os

from ..constants import *
from ..protocols.selectAndRepeat import selective_repeat_receive
from ..protocols.stopAndWait import stop_and_wait_receive


def runServer(serverPort, serverName, terminalArgs):
    print(terminalArgs)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', serverPort))
        print("antes del while")
        while True:
            package, clientAddress = s.recvfrom(CHUNK_SIZE)
            res, clientMethod = getClientHeader(package)

            if clientMethod == UPLOAD:
                fileSize, fileName = getUploadClientFileMetadata(package)
                print("Uploading " + fileName + " ...")
                callClientMethod(res, fileSize, clientAddress, SERVER_FILE_PATH + fileName, terminalArgs)
            elif clientMethod == DOWNLOAD:
                fileName = getDownloadClientFileMetadata(package)
                print("Downloading " + fileName + " ...")
                fileSize = os.stat(SERVER_FILE_PATH + str(fileName)).st_size
                callClientMethod(res, fileSize, clientAddress, CLIENT_FILE_PATH + str(fileName),terminalArgs)
    s.close()


def getUploadClientFileMetadata(package):
    fileSize = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + FILE_SIZE], byteorder='big')
    fileName = package[HEADER_SIZE + FILE_SIZE:].decode('utf-8')
    fileName = fileName.rstrip('\0')
    return fileSize, fileName


def getDownloadClientFileMetadata(package):
    fileName = package[HEADER_SIZE:].decode('utf-8')
    fileName = fileName.rstrip('\0')
    return fileName


def callClientMethod(res, fileSize, clientAddress, path, terminalArgs):
    thread = threading.Thread(target=handleServerChunk, args=(res, clientAddress, path, fileSize, terminalArgs))
    thread.start()


def getClientHeader(package):
    packageId = int.from_bytes(package[:PACKAGE_SIZE], byteorder='big')
    clientMethod = int.from_bytes(package[PACKAGE_SIZE:PACKAGE_SIZE + CLIENT_METHOD_SIZE], byteorder='big')

    #        if fileSize > 5000000:  # Hacer las validaciones de verdad
    #            res = packageId.to_bytes(HEADER_SIZE) + FILE_TOO_BIG.to_bytes(STATUS_CODE_SIZE)
    #            print("File too big")
    #        else:
    # puerto server, puerto cliente, puerto server donde se hace la transferencia
    # levanto hilo con port
    #            print("Status OK")
    return packageId.to_bytes(PACKAGE_SIZE, byteorder='big') + STATUS_OK.to_bytes(STATUS_CODE_SIZE,
                                                                                  byteorder='big'), clientMethod


def handleServerChunk(res, clientAddress, fileName, fileSize, terminalArgs):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as transferSocket:
        transferSocket.bind(('localhost', 0))
        client_port = transferSocket.getsockname()[1]
        # Enviar el nuevo puerto al cliente para que este lo utilice
        paddingSize = CHUNK_SIZE - len(res) - 2
        transferSocket.sendto(res + client_port.to_bytes(2, byteorder='big') + b'\x00' * paddingSize, clientAddress)

        with open(fileName, WRITE_MODE) as f:
            if terminalArgs.selectiveRepeat:
                selective_repeat_receive(transferSocket, f, clientAddress, fileSize)
            else:
                stop_and_wait_receive(transferSocket, f, clientAddress, fileSize)

        f.close()
        print("Operation successfully done.")

    transferSocket.close()

