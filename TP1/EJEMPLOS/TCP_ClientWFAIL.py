from socket import *
serverName = '10.71.103.223'
serverPort = 12000
sentence = ' '
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
while sentence != 'FIN' :
  sentence = input('Input lowercase sentence:')
  clientSocket.send(sentence.encode())
  modifiedSentence = clientSocket.recv(1024)
  print('From Server: ', modifiedSentence.decode())
  clientSocket.close()
