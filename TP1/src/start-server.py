from lib.handlers.serverHandler import runServer

serverPort = 12001
serverName = '127.0.0.1'


def main():
    #args = parseArguments()
    runServer(serverPort, serverName)


main()
