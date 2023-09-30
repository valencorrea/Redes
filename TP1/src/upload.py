import argparse
import os
from constants import *
from socket import *
import sys

serverName = '127.0.0.1'
serverPort = 12001
fileName = 'correa-tp-greedy.txt'


def main():
    parser = argparse.ArgumentParser(description="Upload a file to a server.")

    #parser.add_argument('-H', '--host', help="Server IP address", required=True)
    #parser.add_argument('-p', '--port', help="Server port", type=int, required=True)
    #parser.add_argument('-s', '--src', help="Source file path", required=True)
    parser.add_argument('-n', '--name', help="File name", required=True)
    #group = parser.add_mutually_exclusive_group()
    #group.add_argument('-v', '--verbose', help="Increase output verbosity", action="store_true")
    #group.add_argument('-q', '--quiet', help="Decrease output verbosity", action="store_true")

    args = parser.parse_args()
    #upload(args.src, args.host, args.port, args.name)
    upload("lib/client-files/" + fileName, serverName, serverPort, args.name)


def upload(path, host, port, name):
    with (open(path, "rb") as f):
        with socket(AF_INET, SOCK_DGRAM) as s:
            print("Socket created")
#            s.settimeout(TIMEOUT)
            package_id = 1

            # PRIMER PAQUETE DE PETICION
            # [ ID (Paquete 0) ] 1 byte
            # [ LARGO DEL ARCHIVO en bytes ] 8 bytes
            # [ NOMBRE                     ] 8 bytes
            # ...
            # [ NOMBRE                     ] 8 bytes

            header = package_id.to_bytes(HEADER_SIZE, byteorder='big')
            fileSize = os.stat(path).st_size
            handshake = header + fileSize.to_bytes(LENGTH_BYTES, byteorder='big') + name.ljust(CHUNK_SIZE - HEADER_SIZE - LENGTH_BYTES,
                                                                              '\0').encode('utf-8')

            s.sendto(handshake, (host, port))

            package, serverAddress = s.recvfrom(CHUNK_SIZE)  # serverAddress: ('123.0.8.0', 55555)
            ack = int.from_bytes(package[:HEADER_SIZE], byteorder='big')
            status_code = int.from_bytes(package[HEADER_SIZE:HEADER_SIZE + STATUS_CODE_SIZE], byteorder='big')
            newPort = int.from_bytes(package[HEADER_SIZE + STATUS_CODE_SIZE: HEADER_SIZE + STATUS_CODE_SIZE + 2], byteorder='big')
            print(newPort)

            if status_code != STATUS_OK:
                print("El servidor respondió con error", status_code)
                exit(1)
            else:
                print("Status OK")

            serverAddress = (host, newPort)
            while data := f.read(CHUNK_SIZE - HEADER_SIZE):
                header_b = package_id.to_bytes(HEADER_SIZE, byteorder='big')
                chunk = header_b + data
                s.sendto(chunk, serverAddress)

                # Esperar la confirmación del servidor para este paquete
                package, _ = s.recvfrom(HEADER_SIZE)
                ack = int.from_bytes(package, byteorder='big')
                print(f'Confirmation received for packet {ack}')

                package_id += 1  # Incrementar el número de secuencia del paquete
        s.close()

    f.close()



main()
