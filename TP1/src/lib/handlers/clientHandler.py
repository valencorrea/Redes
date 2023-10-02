import argparse
import socket
import os

from ..constants import *
from ..protocols.selectAndRepeat import selective_repeat_send


def parseArguments():
    parser = argparse.ArgumentParser(description="Upload a file to a server.")
    # parser.add_argument('-H', '--host', help="Server IP address", required=True)
    # parser.add_argument('-p', '--port', help="Server port", type=int, required=True)
    # parser.add_argument('-s', '--src', help="Source file path", required=True)
    parser.add_argument('-n', '--name', help="File name", required=True)
    protocol = parser.add_mutually_exclusive_group(required=True)
    protocol.add_argument('-saw', '--stopAndWait', help="use stop and wait protocol", action="store_true")
    protocol.add_argument('-sr', '--selectiveRepeat', help="use selective repeat protocol", action="store_true")
    # group = parser.add_mutually_exclusive_group()
    # group.add_argument('-v', '--verbose', help="Increase output verbosity", action="store_true")
    # group.add_argument('-q', '--quiet', help="Decrease output verbosity", action="store_true")

    args = parser.parse_args()
    return args  # , group


def runClient(path, host, port, args, method):
    with open(path, READ_MODE) as file:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as chunkSocket:
            package_id = 0
            clientHandshake(package_id, args.name, path, method, host, port, chunkSocket)
            package, serverAddress = chunkSocket.recvfrom(CHUNK_SIZE)  # serverAddress: ('123.0.8.0', 55555)
            ack, handshakeStatusCode, newPort = handleHandshake(package)
            serverAddress = (host, newPort)
            if args.selectiveRepeat:
                selective_repeat_send(serverAddress, chunkSocket, file)
            else:
                handleClientChunk(ack, package_id, serverAddress, chunkSocket, file)

        chunkSocket.close()

    file.close()


def clientHandshake(packageId, name, path, clientMethod, host, port, chunkSocket):
    packageIdBytes = packageId.to_bytes(PACKAGE_SIZE, byteorder='big')
    clientMethodBytes = clientMethod.to_bytes(CLIENT_METHOD_SIZE, byteorder='big')
    if clientMethod == UPLOAD:
        header = uploadClientHandshake(packageIdBytes, name, path, clientMethodBytes)
    else:
        header = downloadClientHandshake(packageIdBytes, name, clientMethodBytes)
    chunkSocket.sendto(header, (host, port))


def uploadClientHandshake(packageIdBytes, name, path, clientMethodBytes):
    fileSize = os.stat(path).st_size
    header = (packageIdBytes
              + clientMethodBytes
              + fileSize.to_bytes(FILE_SIZE, byteorder='big')
              + name.ljust(CHUNK_SIZE - PACKAGE_SIZE - FILE_SIZE, '\0').encode('utf-8'))
    return header


def downloadClientHandshake(packageIdBytes, name, clientMethodBytes):
    header = (packageIdBytes
              + clientMethodBytes
              + name.ljust(CHUNK_SIZE - PACKAGE_SIZE, '\0').encode('utf-8'))
    return header


def handleHandshake(package):
    ack = int.from_bytes(package[:ACK_SIZE], byteorder='big')
    handshakeStatusCode = int.from_bytes(package[ACK_SIZE:ACK_SIZE + STATUS_CODE_SIZE], byteorder='big')
    newPort = int.from_bytes(package[ACK_SIZE + STATUS_CODE_SIZE: ACK_SIZE + STATUS_CODE_SIZE + 2], byteorder='big')
    print(handshakeStatusCode)
    if handshakeStatusCode != STATUS_OK:
        print("El servidor respondió con error", handshakeStatusCode)
        exit(1)

    return ack, handshakeStatusCode, newPort


def handleClientChunk(ack, packageId, serverAddress, chunkSocket, file):
    chunkSocket.settimeout(5)
    timeouts = 0
    while True:
        print(f'ack: {ack} package_id:  {packageId}')
        try:
            if ack == packageId:
                packageId = 1 if packageId == 255 else packageId + 1
                data = file.read(CHUNK_SIZE - HEADER_SIZE)
                if not data:
                    break
            headerb = packageId.to_bytes(HEADER_SIZE, byteorder='big')
            chunk = headerb + data
            chunkSocket.sendto(chunk, serverAddress)

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
