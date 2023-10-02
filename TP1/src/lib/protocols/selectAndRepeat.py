import socket
import time
from queue import PriorityQueue

from ..constants import *


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


def selective_repeat_send(s, f, send_address):
    sent_window = []
    all_file_read = False
    newest_package_id = 0
    print('in selective_repeat_send')
    while not all_file_read or len(sent_window) > 0:
        # fill the window
        print('len(sent_window)', len(sent_window))
        while len(sent_window) < MAX_WINDOW_SIZE and not all_file_read:
            data = f.read(CHUNK_SIZE - HEADER_SIZE)
            if not data:
                all_file_read = True
                break
            newest_package_id += 1
            package = Package(newest_package_id, data)
            s.sendto(package.serialize_id_and_data(), send_address)
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
                s.sendto(package.serialize_id_and_data(), send_address)
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
