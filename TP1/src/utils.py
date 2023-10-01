import argparse
import time

from constants import *
import os
import socket



def parseArguments():
    parser = argparse.ArgumentParser(description="Upload a file to a server.")
    # parser.add_argument('-H', '--host', help="Server IP address", required=True)
    # parser.add_argument('-p', '--port', help="Server port", type=int, required=True)
    # parser.add_argument('-s', '--src', help="Source file path", required=True)
    parser.add_argument('-n', '--name', help="File name", required=True)
    # group = parser.add_mutually_exclusive_group()
    # group.add_argument('-v', '--verbose', help="Increase output verbosity", action="store_true")
    # group.add_argument('-q', '--quiet', help="Decrease output verbosity", action="store_true")

    args = parser.parse_args()
    return args  # , group


def getClientHeader(package):
    packageId = int.from_bytes(package[:PACKAGE_SIZE], byteorder='big')
    clientMethod = int.from_bytes(package[PACKAGE_SIZE:CLIENT_METHOD_SIZE], byteorder='big')
    #        if fileSize > 5000000:  # Hacer las validaciones de verdad
    #            res = packageId.to_bytes(HEADER_SIZE) + FILE_TOO_BIG.to_bytes(STATUS_CODE_SIZE)
    #            print("File too big")
    #        else:
    # puerto server, puerto cliente, puerto server donde se hace la transferencia
    # levanto hilo con port
    #            print("Status OK")
    return packageId.to_bytes(PACKAGE_SIZE, byteorder='big') + STATUS_OK.to_bytes(STATUS_CODE_SIZE, byteorder='big'), clientMethod


def getUploadClientFileMetadata(package):
    fileSize = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + LENGTH_BYTES], byteorder='big')
    fileName = package[HEADER_SIZE + LENGTH_BYTES:].decode('utf-8')
    fileName = fileName.rstrip('\0')
    return fileSize, fileName


def getDownloadClientFileMetadata(package):
    fileName = package[HEADER_SIZE:].decode('utf-8')
    fileName = fileName.rstrip('\0')
    return fileName


def clientHandshake(packageId, name, path, clientMethod):
    clientMethodBytes = clientMethod.to_bytes(CLIENT_METHOD_SIZE, byteorder='big')
    if clientMethod == UPLOAD:
        return uploadClientHandshake(packageId, name, path, clientMethodBytes)
    else:
        return downloadClientHandshake(packageId, name, clientMethodBytes)


def uploadClientHandshake(packageId, name, path, clientMethodBytes):
    packageIdBytes = packageId.to_bytes(PACKAGE_SIZE, byteorder='big')
    fileSize = os.stat(path).st_size
    header = packageIdBytes + clientMethodBytes + fileSize.to_bytes(LENGTH_BYTES, byteorder='big') + name.ljust(
        CHUNK_SIZE - HEADER_SIZE - LENGTH_BYTES, '\0').encode('utf-8')
    return header


def downloadClientHandshake(packageId, name, clientMethodBytes):
    packageIdBytes = packageId.to_bytes(PACKAGE_SIZE, byteorder='big')
    header = packageIdBytes + clientMethodBytes + name.ljust(CHUNK_SIZE - HEADER_SIZE - LENGTH_BYTES, '\0').encode('utf-8')
    return header


def handleHandshake(package, clientMethod):
    ack = int.from_bytes(package[:ACK_SIZE], byteorder='big')
    handshakeStatusCode = int.from_bytes(package[ACK_SIZE:ACK_SIZE + STATUS_CODE_SIZE], byteorder='big')
    newPort = int.from_bytes(package[ACK_SIZE + STATUS_CODE_SIZE: ACK_SIZE + STATUS_CODE_SIZE + 2], byteorder='big')

    if handshakeStatusCode != STATUS_OK.to_bytes(LENGTH_BYTES, byteorder='big'):
        print("El servidor respondió con error", handshakeStatusCode)
        exit(1)

    return ack, handshakeStatusCode, newPort


def handleChunk(ack, packageId, serverAddress, chunkSocket, file):
    chunkSocket.settimeout(5)
    timeouts = 0
    while True:
        time.sleep(5)
        print(f'ack: {ack} package_id:  {packageId}')
        try:
            if ack == packageId:
                packageId = 1 if packageId == 255 else packageId + 1
                data = file.read(CHUNK_SIZE - HEADER_SIZE)
                if not data:
                    break
                print("Data readed:", len(data))
            headerb = packageId.to_bytes(HEADER_SIZE, byteorder='big')
            chunk = headerb + data
            chunkSocket.sendto(chunk, serverAddress)
            print("Sended:", len(data))

            # Esperar la confirmación del servidor para este paquete
            package, _ = chunkSocket.recvfrom(HEADER_SIZE)
            ack = int.from_bytes(package, byteorder='big')
            print(f'Confirmation received for pacakge {ack}')
            timeouts = 0
        except socket.timeout:
            print("hubo timeout")
            timeouts += 1
            if timeouts == MAX_TIMEOUTS:
                print("Too many timeouts, connection abort")
                break
