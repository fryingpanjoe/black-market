import socket
import sys


def send(host, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print('response: {}'.format(response))
    finally:
        sock.close()


def main():
    send(sys.argv[1], int(sys.argv[2]), sys.argv[3])


if __name__ == '__main__':
    main()
