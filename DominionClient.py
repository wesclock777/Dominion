import socket
import sys

def main():
    host = '127.0.0.1'
    port = 5000

    s = socket.socket()
    s.connect((host,port))
    message = ""
    data = ""
    while "won the game with" not in data:
        data = s.recv(4096)
        data = data.decode('utf-8')
        if data.startswith("Asking :"):
            data = data.strip("Asking :")
            print (str(data))
            message = input("-> ")
            s.send(message.encode('utf-8'))
        else:
            print (str(data))
    s.close()

main()
