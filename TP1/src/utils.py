import argparse
import time

from constants import *
import os
import socket
import time
from queue import PriorityQueue

def parseArguments():
    parser = argparse.ArgumentParser(description="Upload a file to a server.")
    # parser.add_argument('-H', '--host', help="Server IP address", required=True)
    # parser.add_argument('-p', '--port', help="Server port", type=int, required=True)
    # parser.add_argument('-s', '--src', help="Source file path", required=True)
    parser.add_argument('-n', '--name', help="File name", required=True)
    # group = parser.add_mutually_exclusive_group()
    # group.add_argument('-v', '--verbose', help="Increase output verbosity", action="store_true")
    # group.add_argument('-q', '--quiet', help="Decrease output verbosity", action="store_true")

    args = parser.parse_args()
    return args  # , group


def serverHandshake(package):
    package_id = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
    fileSize = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + LENGTH_BYTES], byteorder='big')
    fileName = package[HEADER_SIZE + LENGTH_BYTES:].decode('utf-8')
    fileName = fileName.rstrip('\0')
    #        if fileSize > 5000000:  # Hacer las validaciones de verdad
    #            res = package_id.to_bytes(HEADER_SIZE) + FILE_TOO_BIG.to_bytes(STATUS_CODE_SIZE)
    #            print("File too big")
    #        else:
    # puerto server, puerto cliente, puerto server donde se hace la transferencia
    # levanto hilo con port
    #            print("Status OK")
    res = package_id.to_bytes(HEADER_SIZE, byteorder='big') + STATUS_OK.to_bytes(STATUS_CODE_SIZE, byteorder='big')

    return res, fileSize, fileName


def clientHandshake(package_id, name, path):
    package_id_bytes = package_id.to_bytes(HEADER_SIZE, byteorder='big')
    fileSize = os.stat(path).st_size
    header = package_id_bytes + fileSize.to_bytes(LENGTH_BYTES, byteorder='big') + name.ljust(
        CHUNK_SIZE - HEADER_SIZE - LENGTH_BYTES, '\0').encode('utf-8')

    return header


def handleHandshake(package):
    ack = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
    handshakeStatusCode = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + STATUS_CODE_SIZE], byteorder='big')
    newPort = int.from_bytes(package[HEADER_SIZE + STATUS_CODE_SIZE: HEADER_SIZE + STATUS_CODE_SIZE + 2],
                             byteorder='big')

    if handshakeStatusCode != STATUS_OK:
        print("El servidor respondió con error", handshakeStatusCode)
        exit(1)

    return ack, handshakeStatusCode, newPort


def handleChunk(ack, packageId, serverAddress, chunkSocket, file):
    chunkSocket.settimeout(5)
    timeouts = 0
    while True:
        time.sleep(5)
        print(f'ack: {ack} package_id:  {packageId}')
        try:
            if ack == packageId:
                packageId += 1  # Incrementar el número de secuencia del paquete
                data = file.read(CHUNK_SIZE - HEADER_SIZE)
                if not data:
                    break
                print("Data readed:", len(data))
            headerb = packageId.to_bytes(HEADER_SIZE, byteorder='big')
            chunk = headerb + data
            chunkSocket.sendto(chunk, serverAddress)
            print("Sended:", len(data))

            # Esperar la confirmación del servidor para este paquete
            package, _ = chunkSocket.recvfrom(HEADER_SIZE)
            ack = int.from_bytes(package, byteorder='big')
            print(f'Confirmation received for pacakge {ack}')
            timeouts = 0
        except socket.timeout:
            print("hubo timeout")
            timeouts += 1
            if timeouts == MAX_TIMEOUTS:
                print("Too many timeouts, connection abort")
                break


class Package:
    def __init__(self, package_id, data):
        self.__id = package_id
        self.__data = data
        self.__is_ack = False
        self.__created_at = 0

    def get_id(self):
        return self.__id

    def get_data(self):
        return self.__data

    def has_the_id(self, package_id):
        return self.__id == package_id

    def mark_as_received(self):
        self.__is_ack = True

    def set_timestamp(self):
        self.__created_at = time.time()

    def serialize_id_and_data(self):
        return self.serialize_id() + self.__data

    def serialize_id(self):
        return self.__id.to_bytes(HEADER_SIZE, byteorder='big')

    def has_been_received(self):
        return self.__is_ack

    def has_expired(self):
        return not self.__is_ack and self.__created_at > time.time() + TIMEOUT

    def __lt__(self, other):
        return self.__id < other.__id


MAX_WINDOW_SIZE = 5
TIMEOUT = 5


def wait_for_ack(s):
    try:
        package, server_address = s.recvfrom(HEADER_SIZE)
        return int.from_bytes(package, byteorder='big')
    except socket.timeout:
        print('socket timeout')


def selective_repeat_send(server_address, s, file):
    sent_window = []
    all_file_read = False
    newest_package_id = 0
    print('in selective_repeat_send')
    while not all_file_read or len(sent_window) > 0:
        # fill the window
        print('len(sent_window)', len(sent_window))
        while len(sent_window) < MAX_WINDOW_SIZE and not all_file_read:
            data = file.read(CHUNK_SIZE - HEADER_SIZE)
            if not data:
                all_file_read = True
                break
            newest_package_id += 1
            package = Package(newest_package_id, data)
            s.sendto(package.serialize_id_and_data(), server_address)
            print('sent package', newest_package_id)
            package.set_timestamp()
            sent_window.append(package)

        print('waiting for some ack')
        ack = wait_for_ack(s)
        print('received ack: ', ack)
        # mark the acknowledged packages as received
        for package in sent_window:
            print('package:', package.get_id(), 'ack', package.has_been_received())
            if package.has_the_id(ack):
                package.mark_as_received()
                print('Found package with ack: ', ack)
                break

        # remove packages until first unacknowledged (slide window)
        while len(sent_window) > 0 and sent_window[0].has_been_received():
            print('Poped acked package: ', sent_window[0].get_id())
            sent_window.pop(0)

        # resend all expired
        for package in sent_window:
            if package.has_expired():
                s.sendto(package.serialize_id_and_data(), server_address)
                package.set_timestamp()
                print('Resent: ', package.get_id())


def selective_repeat_receive(s, file, client_address, fileSize):
    amount_received = 0
    expected_package_id = 1
    # s.timeout(TIMEOUT)
    receive_window = PriorityQueue(MAX_WINDOW_SIZE)
    print('in selective_repeat_receive')
    while amount_received < fileSize:
        while not receive_window.full() and amount_received < fileSize:
            print('amount_received', amount_received, 'fileSize', fileSize)
            print('while 1')
            try:
                package, address = s.recvfrom(CHUNK_SIZE)
            except socket.timeout:
                break
            package_id = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
            print('received: ', package_id)
            data = package[HEADER_SIZE:]
            if package_id != expected_package_id:
                #  check if its already in buffer
                for item in receive_window.queue:
                    if item[0] == package_id:
                        continue
                #  add to buffer
                ooo_package = Package(package_id, data)
                receive_window.put((package_id, ooo_package))
            else:
                file.write(data)
                amount_received += len(data)
                s.sendto(package[:HEADER_SIZE], client_address)
                expected_package_id += 1
                print('acknowledged de una: ', package_id)
                print('amount_received', amount_received, 'fileSize', fileSize)

        while not receive_window.empty() and receive_window.queue[0][1].has_the_id(expected_package_id):
            print('while 2')
            package = receive_window.get()
            file.write(package.get_data())
            amount_received += len(package.get_data())
            print("Hice un write de la receive_window")
            s.sendto(package.serialize_id(), client_address)
            expected_package_id += 1
