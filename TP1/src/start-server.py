from lib.handlers.clientHandler import parseArguments
from lib.handlers.serverHandler import runServer

serverPort = 12002
serverName = '127.0.0.1'


def main():
    args = parseArguments()
    try:
        runServer(serverPort, serverName, args)
    except KeyboardInterrupt:
        print(" pressed. Exiting gracefully.")


main()