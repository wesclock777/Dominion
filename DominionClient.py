import socket
import sys

def main():
    #host = input("Host: ")
    #port = input("Port: ")

    host = "127.0.0.1"
    #10.147.171.24 UT
    #192.168.0.42 NETGEAR
    #172.16.16.158 BLOCK
    port = 5000

    s = socket.socket()
    s.connect((host, port))
    message = ""
    data = ""

    while "victory points in" not in data:
        data = s.recv(8192)
        data = data.decode('utf-8')
        if data.startswith("Asking: "):
            data = data.strip("Asking: ")
            print(str(data))
            message = input("-> ")
            if message == "":
                message = " "
            s.send(message.encode('utf-8'))
        else:
            print(str(data))
    s.close()

main()
