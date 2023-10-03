import socket
import os

from .logLevelHandler import retrieveLevel
from ..constants import *
from ..protocols.selectAndRepeat import selective_repeat_send, selective_repeat_receive
from ..protocols.stopAndWait import stop_and_wait_send, stop_and_wait_receive

def runClient(args, method):
    host, port = args.host, args.port
    logLevel = retrieveLevel(args.verbose,)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(HANDSHAKE_TIMEOUT)
        if method == UPLOAD:
            try:
                send_address = upload_handshake(s, host, port, args.name, args.src)
            except socket.timeout:
                print('HANDSHAKE FAILED')
                exit(1)
            with open(args.src, READ_MODE) as f:
                if args.selectiveRepeat:
                    selective_repeat_send(s, f, send_address)
                else:
                    stop_and_wait_send(s, f, send_address)
        elif method == DOWNLOAD:
            try:
                receive_address, file_size = download_handshake(s, host, port, args.name)
            except socket.timeout:
                print('HANDSHAKE FAILED')
                exit(1)
            with open(args.dst, WRITE_MODE) as f:
                if args.selectiveRepeat:
                    selective_repeat_receive(s, f, receive_address, file_size)
                else:
                    stop_and_wait_receive(s, f, receive_address, file_size)


def upload_handshake(s, host, port, name, path):
    file_size = os.path.getsize(path)
    header = (int(0).to_bytes(ID_SIZE, byteorder='big')
              + UPLOAD.to_bytes(CLIENT_METHOD_SIZE, byteorder='big')
              + file_size.to_bytes(FILE_SIZE, byteorder='big')
              + name.ljust(CHUNK_SIZE - ID_SIZE - FILE_SIZE - CLIENT_METHOD_SIZE, '\0').encode('utf-8'))
    s.sendto(header, (host, port))
    package, upload_address = s.recvfrom(ID_SIZE + STATUS_CODE_SIZE)
    handshake_response_code = int.from_bytes(package[ID_SIZE:ID_SIZE + STATUS_CODE_SIZE], byteorder='big')
    if handshake_response_code != STATUS_OK:
        print('El servidor respondio con error: ', handshake_response_code)
        exit(1)
    return upload_address


def download_handshake(s, host, port, name):
    header = (int(0).to_bytes(ID_SIZE, byteorder='big')
              + DOWNLOAD.to_bytes(CLIENT_METHOD_SIZE, byteorder='big')
              + name.ljust(CHUNK_SIZE - ID_SIZE - CLIENT_METHOD_SIZE, '\0').encode('utf-8'))
    s.sendto(header, (host, port))
    package, download_address = s.recvfrom(ID_SIZE + STATUS_CODE_SIZE + FILE_SIZE)
    handshake_response_code = int.from_bytes(package[ID_SIZE:ID_SIZE + STATUS_CODE_SIZE], byteorder='big')
    if handshake_response_code != STATUS_OK:
        print('El servidor respondio con error: ', handshake_response_code)
        exit(1)
    file_size = int.from_bytes(package[ID_SIZE + STATUS_CODE_SIZE:ID_SIZE + STATUS_CODE_SIZE + FILE_SIZE], byteorder='big')
    return download_address, file_size


# def uploadClientHandshake(packageIdBytes, name, path, method_b):
#     file_size = os.path.getsize(path)
#     header = (packageIdBytes
#               + method_b
#               + file_size.to_bytes(FILE_SIZE, byteorder='big')
#               + name.ljust(CHUNK_SIZE - ID_SIZE - FILE_SIZE, '\0').encode('utf-8'))
#
#     # return header
#
#
# def downloadClientHandshake(packageIdBytes, name, clientMethodBytes):
#     header = (packageIdBytes
#               + clientMethodBytes
#               + name.ljust(CHUNK_SIZE - ID_SIZE, '\0').encode('utf-8'))
#     return header
#
#
# def handleHandshake(package):
#     ack = int.from_bytes(package[:ACK_SIZE], byteorder='big')
#     handshakeStatusCode = int.from_bytes(package[ACK_SIZE:ACK_SIZE + STATUS_CODE_SIZE], byteorder='big')
#     newPort = int.from_bytes(package[ACK_SIZE + STATUS_CODE_SIZE: ACK_SIZE + STATUS_CODE_SIZE + 2], byteorder='big')
#     print(handshakeStatusCode)
#     if handshakeStatusCode != STATUS_OK:
#         print("El servidor respondió con error", handshakeStatusCode)
#         exit(1)
#
#     return ack, handshakeStatusCode, newPort


