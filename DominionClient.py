import socket

def main():
    host = '127.0.0.1'
    port = 5000

    s = socket.socket()
    s.connect((host,port))
    message=""
    while message != 'q':
        data = s.recv(1024)
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
