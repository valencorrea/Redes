from lib.handlers.clientHandler import *
from lib.constants import *

serverName = '127.0.0.1'
serverPort = 12001
fileName = 'test.txt'

CHUNK_SIZE = 64

def main():
    args = parseArguments()  # arg, group = parseArguments()
    runClient(SERVER_FILE_PATH + fileName, serverName, serverPort, args.name,
              DOWNLOAD)  # upload(args.src, args.host, args.port, args.name)

main()


