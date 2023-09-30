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


def serverHandshake(package):
    package_id = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
    fileSize = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + LENGTH_BYTES], byteorder='big')
    fileName = package[HEADER_SIZE + LENGTH_BYTES:].decode('utf-8')
    fileName = fileName.rstrip('\0')
    #        if fileSize > 5000000:  # Hacer las validaciones de verdad
    #            res = package_id.to_bytes(HEADER_SIZE) + FILE_TOO_BIG.to_bytes(STATUS_CODE_SIZE)
    #            print("File too big")
    #        else:
    # puerto server, puerto cliente, puerto server donde se hace la transferencia
    # levanto hilo con port
    #            print("Status OK")
    res = package_id.to_bytes(HEADER_SIZE, byteorder='big') + STATUS_OK.to_bytes(STATUS_CODE_SIZE, byteorder='big')

    return res, fileSize, fileName


def clientHandshake(package_id, name, path):
    package_id_bytes = package_id.to_bytes(HEADER_SIZE, byteorder='big')
    fileSize = os.stat(path).st_size
    header = package_id_bytes + fileSize.to_bytes(LENGTH_BYTES, byteorder='big') + name.ljust(
        CHUNK_SIZE - HEADER_SIZE - LENGTH_BYTES, '\0').encode('utf-8')

    return header


def handleHandshake(package):
    ack = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
    handshakeStatusCode = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + STATUS_CODE_SIZE], byteorder='big')
    newPort = int.from_bytes(package[HEADER_SIZE + STATUS_CODE_SIZE: HEADER_SIZE + STATUS_CODE_SIZE + 2], byteorder='big')

    if handshakeStatusCode != STATUS_OK:
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
                packageId += 1  # Incrementar el número de secuencia del paquete
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
