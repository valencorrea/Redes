from ..constants import *
import socket


def stop_and_wait_receive(transferSocket, f, clientAddress, fileSize):
    received = 0
    ack = 0
    while received < fileSize:  #contemplar perdida de paquetes
        package, clientAddress = transferSocket.recvfrom(CHUNK_SIZE)
        package_id = int.from_bytes(package[:ID_SIZE], byteorder='big')
        data = package[HEADER_SIZE:]
        if (ack + 1) == package_id:  # Recibi paquete siguiente
            received += len(data)
            f.write(data)
            ack = package_id
        res = package_id.to_bytes(ID_SIZE, byteorder='big') + ack.to_bytes(ACK_SIZE, byteorder='big')
        transferSocket.sendto(res, clientAddress)
        ack = 0 if package_id == 65535 else package_id


def stop_and_wait_send(s, f, send_address):
    s.settimeout(5)
    timeouts = 0
    packageId = 0
    ack = 0
    data = ''
    while True:
        print(f'ack: {ack} package_id:  {packageId}')
        try:
            if ack == packageId:
                packageId = 1 if packageId == 65535 else packageId + 1
                data = f.read(CHUNK_SIZE - HEADER_SIZE)
                if not data:
                    break
            else:
                print("\n\nhubo perdida de paquete\n\n")
            headerb = packageId.to_bytes(ID_SIZE, byteorder='big') + ack.to_bytes(ACK_SIZE, byteorder='big')
            chunk = headerb + data
            s.sendto(chunk, send_address)

            # Esperar la confirmación del servidor para este paquete
            package, _ = s.recvfrom(HEADER_SIZE)
            ack = int.from_bytes(package[ID_SIZE: ID_SIZE + ACK_SIZE], byteorder='big')
            print(f'Confirmation received for pacakge {ack}')
            timeouts = 0
        except socket.timeout:
            print("hubo timeout")
            timeouts += 1
            if timeouts == MAX_TIMEOUTS:
                print("Too many timeouts, connection abort")
                break
