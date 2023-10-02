import socket
import threading
import os

from ..constants import *
from ..protocols.selectAndRepeat import selective_repeat_receive, selective_repeat_send
from ..protocols.stopAndWait import stop_and_wait_receive, stop_and_wait_send


def runServer(serverPort, serverName, args):
    print(args)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', serverPort))
        print("Starting server at", serverName, ':', serverPort)
        threads = []
        try:
            while True:
                package, client_address = s.recvfrom(CHUNK_SIZE)
                new_thread = threading.Thread(
                    target=handle_connection,
                    args=(package, client_address, args.selectiveRepeat)
                )
                new_thread.start()
                threads.append(new_thread)

                #  remove dead threads
                threads = [thread for thread in threads if thread.is_alive()]

        except KeyboardInterrupt:
            try:
                for thread in threads:
                    thread.join()
            except KeyboardInterrupt:
                exit(1)


def handle_connection(package, client_address, algorithm):
    with (socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s):
        client_method = int.from_bytes(package[ID_SIZE:ID_SIZE + CLIENT_METHOD_SIZE], byteorder='big')
        if client_method == UPLOAD:
            file_size = int.from_bytes(package[ID_SIZE + CLIENT_METHOD_SIZE:ID_SIZE + CLIENT_METHOD_SIZE + FILE_SIZE],
                                       byteorder='big')
            file_name = package[ID_SIZE + CLIENT_METHOD_SIZE + FILE_SIZE:].decode('utf-8')
            file_name = file_name.rstrip('\0')
            with open(file_name, WRITE_MODE) as f:
                s.sendto(int(0).to_bytes(ID_SIZE, byteorder='big') +
                         STATUS_OK.to_bytes(STATUS_CODE_SIZE, byteorder='big'), client_address)
                if algorithm == STOP_AND_WAIT:
                    stop_and_wait_receive(s, f, client_address, file_size)
                else:
                    selective_repeat_receive(s, f, client_address, file_size)

        elif client_method == DOWNLOAD:
            file_name = package[ID_SIZE + CLIENT_METHOD_SIZE:].decode('utf-8')
            file_name = file_name.rstrip('\0')
            try:
                with open(file_name, READ_MODE) as f:
                    file_size = os.path.getsize(file_name)
                    s.sendto(int(0).to_bytes(ID_SIZE, byteorder='big') +
                             STATUS_OK.to_bytes(STATUS_CODE_SIZE, byteorder='big') +
                             file_size.to_bytes(FILE_SIZE, byteorder='big'),
                             client_address)
                    if algorithm == STOP_AND_WAIT:
                        stop_and_wait_send(s, f, client_address)
                    else:
                        selective_repeat_send(s, f, client_address)
            except OSError as err:
                print('Error al intentar descargar el archivo: ', err)
                s.sendto(int(0).to_bytes(ID_SIZE, byteorder='big') +
                         ERR_FILE_NOT_FOUND.to_bytes(STATUS_CODE_SIZE, byteorder='big'), client_address)
    print('finished')
