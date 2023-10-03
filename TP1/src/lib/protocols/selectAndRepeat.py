import datetime
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
        self.__retry_count = 0

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
        return self.__id.to_bytes(ID_SIZE, byteorder='big')

    def has_been_received(self):
        return self.__is_ack

    def retry_times_over(self, max_times):
        return self.__retry_count > max_times

    def has_expired(self):
        new_time = time.time()
        is_old = ((self.__created_at + TIMEOUT) < new_time)
        has_expired = (not self.__is_ack) and is_old
        return has_expired

    def __lt__(self, other):
        return self.__id < other.__id

    def update_retry(self):
        self.__retry_count += 1


def wait_for_ack(s):
    try:
        package, server_address = s.recvfrom(ID_SIZE)
        return int.from_bytes(package, byteorder='big')
    except socket.timeout:
        print('socket timeout for ACK')
        return None


def selective_repeat_send(s, f, send_address):
    sent_window = []
    all_file_read = False
    newest_package_id = 0
    s.settimeout(TIMEOUT)
    print('in selective_repeat_send')
    while not all_file_read or len(sent_window) > 0:
        # fill the window
        print('len(sent_window)', len(sent_window))

        while len(sent_window) < MAX_WINDOW_SIZE and not all_file_read:
            data = f.read(CHUNK_SIZE - ID_SIZE)
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
        if ack:
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

        # sent_window = [item for item in sent_window if not item.has_the_id(ack)]

        # resend all expired
        for package in sent_window:
            if package.retry_times_over(MAXIMUM_RETRIES): #Quit if no response for MAXIMUM_RETRIES times
                print("TIMEOUT")
                exit(1)
            if package.has_expired():
                s.sendto(package.serialize_id_and_data(), send_address)
                package.set_timestamp()
                package.update_retry()
                print('Resent: ', package.get_id())


def selective_repeat_receive(s, file, client_address, file_size):
    amount_received = 0
    expected_package_id = 1
    s.settimeout(TIMEOUT)
    receive_window = PriorityQueue(MAX_WINDOW_SIZE)
    timeout_count = 0
    print('in selective_repeat_receive')
    while amount_received < file_size:
        while not receive_window.full() and amount_received < file_size:
            try:
                package, address = s.recvfrom(CHUNK_SIZE)
                timeout_count = 0
            except socket.timeout:
                timeout_count += 1
                if timeout_count > MAX_RECV_TIMEOUTS:
                    print("TIMEOUT")
                    exit(1)
                break
            package_id = int.from_bytes(package[:ID_SIZE], byteorder='big')
            print('received: ', package_id)
            data = package[ID_SIZE:]
            s.sendto(package[:ID_SIZE], client_address)
            if package_id != expected_package_id:
                if package_id < expected_package_id:
                    print("discarded package" + str(package_id))
                    continue
                #  check if its already in buffer
                for item in receive_window.queue:
                    if item[0] == package_id:
                        continue
                #  add to buffer
                ooo_package = Package(package_id, data)
                receive_window.put((package_id, ooo_package))
                print("added package" + str(package_id) + "to queue")
            else:
                file.write(data)
                amount_received += len(data)
                expected_package_id += 1
                print('amount_received', amount_received, 'fileSize', file_size)

        #print("sali del primer while")
        while not receive_window.empty() and receive_window.queue[0][1].has_the_id(expected_package_id):
            package = receive_window.get()[1]
            file.write(package.get_data())
            amount_received += len(package.get_data())
            print('amount_received', amount_received, 'fileSize', file_size)
            expected_package_id += 1
