import socket
import json
from multiprocessing import shared_memory, resource_tracker

import time

# TODO
# 1) Recive oper sum as integer and ip ex. [120, 192, 150, 0, 12] => 0 index is sum, rest is ip address
# 2) Create JSON body for the request
# 3) Open connection with AQSI
# 4) Send body to the terminal
# 5)

PORT = 4455


def send(sock, data):
    try:
        body = bytearray(data)
        body_len = len(body).to_bytes(4, byteorder="big")
        message = body_len + body

        sock.sendall(message)
        response_length = int.from_bytes(recvall(sock, 4), byteorder="big")
        response = recvall(sock, response_length).decode('utf-8')
        print(f'Received: {response}')
        data_json = json.loads(response)

        return data_json
    except Exception as e:
        print(f"Error wtf: {e}")


def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def send_transaction(sock, amount):
    data = f'{{\
                     "command": "transaction",\
                     "type": "purchase",\
                     "currency": 643,\
                     "amount": {amount}\
                 }}'

    return send(sock, data.encode('utf-8'))


def send_keep_alive(sock):
    data = b'{\
                "command": "keep-alive"\
            }'

    return send(sock, data)


def send_finish(sock):
    data = b'{\
                "keep-alive-status": "cancelled"\
            }'

    return send(sock, data)


# Check while
def verifying_transaction(data):
    if data.get("reply") != "transaction":
        return False
    else:
        return True


def convert_status(status):
    if status == 'ok':
        return 200
    elif status == 'failed':
        return 403
    elif status == 'cancelled':
        return 400
    elif status == 'timeout':
        return 408
    elif status == 'tryagain':
        return 503
    else:
        return 500


def read_sm_input():
    SHM_NAME = 'cds_input'
    shm = shared_memory.SharedMemory(name=SHM_NAME)
    buffer = shm.buf
    return [buffer[0], str(buffer[1]) + '.' + str(buffer[2]) + '.' + str(buffer[3]) + '.' + str(buffer[4])]


def create_sm_input():
    SHM_NAME = 'cds_input'
    shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=16)
    shm.buf[0] = 100
    shm.buf[1] = 192
    shm.buf[2] = 168
    shm.buf[3] = 53
    shm.buf[4] = 154
    resource_tracker.unregister(shm._name, 'shared_memory')
    print("Save data input")


def delete_old_output():
    SHM_NAME = 'cds_output'
    try:
        shm = shared_memory.SharedMemory(name=SHM_NAME, create=False)
        shm.close()
        shm.unlink()
        print("Delete old data output")
    except:
        print("No find old data output")


def create_sm_output(status):
    SHM_NAME = 'cds_output'
    shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=16)
    shm.buf[0] = int(status)
    resource_tracker.unregister(shm._name, 'shared_memory')
    print("Save data output")


def main():
    delete_old_output()
    create_sm_input()
    data_arr = read_sm_input()

    CONNECT = True
    HOST = data_arr[1]

    print(HOST)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    try:
        amount = '{:.2f}'.format(data_arr[0])
        print(f"Sending Transaction with amount {amount}...")
        data = send_transaction(sock, amount)

        # Wait for some time before sending keep-alive requests
        time.sleep(0.5)

        # Send keep-alive requests until a successful response is received
        while data.get("reply") != "transaction":
            print("Sending Keep-Alive...")
            data = send_keep_alive(sock)
            # print(data)
            # Wait for a short interval before sending the next keep-alive
            time.sleep(2)

            # Check if a successful response for the transaction has been received
            # For example, you may check the content of the response and break the loop if successful

        CONNECT = False
        status = convert_status(data.get("status"))
        print(status)
        create_sm_output(status)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print(f"Closing connection")
        if CONNECT:
            send_finish(sock)
        sock.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(f'Started')
    main()
