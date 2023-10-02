from socket import *

from lib.constants import *
from lib.handlers.clientHandler import runClient, parseArguments

serverName = '127.0.0.1'
serverPort = 12001
fileName = 'a.txt'
fileNameIMG = 'huevos_revueltos.jpeg'


def main():
    args = parseArguments() #arg, group = parseArguments()
    runClient(CLIENT_FILE_PATH + fileName, serverName, serverPort, args, UPLOAD) #VALU


main()
