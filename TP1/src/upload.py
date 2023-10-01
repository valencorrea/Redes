import socket
from utils import *

serverName = '127.0.0.1'
serverPort = 12001
fileName = 'test.txt'


def main():
    args = parseArguments() #arg, group = parseArguments()
    upload("lib/client-files/" + fileName, serverName, serverPort, args.name) #upload(args.src, args.host, args.port, args.name)


def upload(path, host, port, name):
    with open(path, "rb") as file:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as chunkSocket:
            package_id = 0
            header = clientHandshake(package_id, name, path, UPLOAD)
            chunkSocket.sendto(header, (host, port))  # mover adentro del handshake
            package, serverAddress = chunkSocket.recvfrom(CHUNK_SIZE)  # serverAddress: ('123.0.8.0', 55555)
            print("ANTES DE HANDLE HANDSHAKE")
            ack, handshakeStatusCode, newPort = handleHandshake(package, UPLOAD)

            serverAddress = (host, newPort)
            print("ANTES DE HANDLE chunck")

            handleChunk(ack, package_id, serverAddress, chunkSocket, file)
        chunkSocket.close()

    file.close()



main()
