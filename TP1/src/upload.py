from socket import *
from utils import *

serverName = '127.0.0.1'
serverPort = 12001
fileName = 'correa-tp-greedy.txt'


def main():
    args = parseArguments() #arg, group = parseArguments()
    upload("lib/client-files/" + fileName, serverName, serverPort, args.name) #upload(args.src, args.host, args.port, args.name)


def upload(path, host, port, name):
    with open(path, "rb") as f:
        with socket(AF_INET, SOCK_DGRAM) as chunkSocket:
            package_id = 0
            header = clientHandshake(package_id, name, path)
            chunkSocket.sendto(header, (host, port)) # mover adentro del handshake
            package, serverAddress = chunkSocket.recvfrom(CHUNK_SIZE)  # serverAddress: ('123.0.8.0', 55555)

            ack, handshakeStatusCode, newPort = handleHandshake(package)

            serverAddress = (host, newPort)

            while data := f.read(CHUNK_SIZE - HEADER_SIZE):
                handleChunk(data, package_id, serverAddress, chunkSocket)
        chunkSocket.close()

    f.close()



main()
