import socket
import json
import time

# TODO
# 1) Recive oper sum as integer and ip ex. [120, 192, 150, 0, 12] => 0 index is sum, rest is ip address
# 2) Create JSON body for the request
# 3) Open connection with AQSI
# 4) Send body to the terminal
# 5)
#
#


HOST = '192.168.53.154'
PORT = 4455


def send(sock, data):
    try:
        body = bytearray(data)
        body_len = len(body).to_bytes(4, byteorder="big")
        message = body_len + body

        sock.sendall(message)
        response = sock.recv(1024).decode('utf-8').replace('\x00', '').replace('\n', '').replace('\r', '').replace(' ', '')
        print(f'Received: {response}')
        data_json = json.loads(response)


        return data_json
    except Exception as e:
        print(f"Error wtf: {e}")


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


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    try:
        amount = 1.00  # Replace with the desired amount
        print(f"Sending Transaction with amount {amount}...")
        data = send_transaction(sock, amount)

        # Wait for some time before sending keep-alive requests
        time.sleep(0.5)

        # Send keep-alive requests until a successful response is received
        while True:
            print("Sending Keep-Alive...")
            data = send_keep_alive(sock)
            #print(data)
            # Wait for a short interval before sending the next keep-alive
            time.sleep(2)

            # Check if a successful response for the transaction has been received
            # For example, you may check the content of the response and break the loop if successful

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print(f"Closing connection")
        sock.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(f'Started')
    main()
