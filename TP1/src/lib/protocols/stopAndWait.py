from ..constants import *
import socket


def stop_and_wait_receive(s, f, address, file_size):
    received = 0
    ack = 0
    s.settimeout(HANDSHAKE_TIMEOUT)
    while received < file_size:
        try:
            package, address = s.recvfrom(CHUNK_SIZE)
        except:
            print("TIMEOUT")
            exit(1)
        package_id = int.from_bytes(package[:ID_SIZE], byteorder='big')
        data = package[HEADER_SIZE:]
        if (ack + 1) == package_id:  # Recibi paquete siguiente
            received += len(data)
            f.write(data)
            ack = package_id
        res = package_id.to_bytes(ID_SIZE, byteorder='big')
        s.sendto(res, address)


def stop_and_wait_send(s, f, address):
    s.settimeout(TIMEOUT)
    timeouts = 0
    package_id = 0
    ack = 0
    data = ''
    while True:
        print(f'ack: {ack} package_id:  {package_id}')
        try:
            if ack == package_id:
                package_id = 1 if package_id == 65535 else package_id + 1
                data = f.read(CHUNK_SIZE - HEADER_SIZE)
                if not data:
                    break
            else:
                print(f'packet {package_id} will be repeated')
            header_b = package_id.to_bytes(ID_SIZE, byteorder='big')
            chunk = header_b + data
            s.sendto(chunk, address)

            # Esperar la confirmación del servidor para este paquete
            package, _ = s.recvfrom(HEADER_SIZE)
            ack = int.from_bytes(package[: ID_SIZE], byteorder='big')
            print(f'Confirmation received for pacakge {ack}')
            timeouts = 0
        except socket.timeout:
            print("hubo timeout")
            timeouts += 1
            if timeouts == MAX_TIMEOUTS:
                print("Too many timeouts, connection abort")
                break
