import socket
import os
from pathlib import Path

from .logLevelHandler import *
from ..constants import *
from ..protocols.selectiveRepeat import selective_repeat_send, selective_repeat_receive
from ..protocols.stopAndWait import stop_and_wait_send, stop_and_wait_receive


def run_client(args, method):
    host, port = args.host, args.port
    log_level = retrieve_level(args.verbose, )
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(HANDSHAKE_TIMEOUT)
        log(f'client sarted at {s.getsockname()}', LogLevel.HIGH, log_level)
        if method == UPLOAD:
            try:
                send_address = upload_handshake(s, host, port, args.name, args.src, log_level)
            except socket.timeout:
                log('Connection failed', LogLevel.LOW, log_level)
                log('HANDSHAKE FAILED', LogLevel.HIGH, log_level)
                exit(1)
            path = Path(args.src)
            if not path.exists():
                log('The file does not exist', LogLevel.LOW, log_level)
            with open(args.src, READ_MODE) as f:
                if args.selectiveRepeat:
                    selective_repeat_send(s, f, send_address, log_level)
                else:
                    stop_and_wait_send(s, f, send_address)
        elif method == DOWNLOAD:
            try:
                receive_address, file_size = download_handshake(s, host, port, args.name, log_level)
            except socket.timeout:
                log('Connection failed', LogLevel.LOW, log_level)
                log('HANDSHAKE FAILED', LogLevel.HIGH, log_level)
                exit(1)
            with open(args.dst, WRITE_MODE) as f:
                if args.selectiveRepeat:
                    selective_repeat_receive(s, f, receive_address, file_size)
                else:
                    stop_and_wait_receive(s, f, receive_address, file_size)


def upload_handshake(s, host, port, name, path, log_level):
    file_size = os.path.getsize(path)
    first_chunk = (int(0).to_bytes(ID_SIZE, byteorder='big')
              + UPLOAD.to_bytes(CLIENT_METHOD_SIZE, byteorder='big')
              + file_size.to_bytes(FILE_SIZE, byteorder='big')
              + name.ljust(CHUNK_SIZE - ID_SIZE - FILE_SIZE - CLIENT_METHOD_SIZE, '\0').encode('utf-8'))
    s.sendto(first_chunk, (host, port))
    package, upload_address = s.recvfrom(ID_SIZE + STATUS_CODE_SIZE)
    handshake_response_code = int.from_bytes(package[ID_SIZE:ID_SIZE + STATUS_CODE_SIZE], byteorder='big')
    if handshake_response_code != STATUS_OK:
        log(f'El servidor respondio con error: {handshake_response_code}', LogLevel.LOW, log_level)
        exit(1)
    return upload_address


def download_handshake(s, host, port, name, log_level):
    header = (int(0).to_bytes(ID_SIZE, byteorder='big')
              + DOWNLOAD.to_bytes(CLIENT_METHOD_SIZE, byteorder='big')
              + name.ljust(CHUNK_SIZE - ID_SIZE - CLIENT_METHOD_SIZE, '\0').encode('utf-8'))
    s.sendto(header, (host, port))
    package, download_address = s.recvfrom(ID_SIZE + STATUS_CODE_SIZE + FILE_SIZE)
    handshake_response_code = int.from_bytes(package[ID_SIZE:ID_SIZE + STATUS_CODE_SIZE], byteorder='big')
    if handshake_response_code != STATUS_OK:
        log(f'El servidor respondio con error: {handshake_response_code}', LogLevel.LOW, log_level)
        exit(1)
    file_size = int.from_bytes(package[ID_SIZE + STATUS_CODE_SIZE:ID_SIZE + STATUS_CODE_SIZE + FILE_SIZE],
                               byteorder='big')
    return download_address, file_size
