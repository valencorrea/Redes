from src.lib.handlers.clientHandler import *

serverName = '127.0.0.1'
serverPort = 12001
fileName = 'test.txt'


def main():
    args = parseArguments() #arg, group = parseArguments()
    runClient(CLIENT_FILE_PATH + fileName, serverName, serverPort, args.name, UPLOAD) #upload(args.src, args.host, args.port, args.name)

main()
