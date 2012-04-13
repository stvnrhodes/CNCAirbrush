import socket

"""Send a hello world to the machine"""
HOST = '169.254.1.1'
PORT = 2000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall('Hello World')
data = s.recv(1024)
s.close()
print ('Recieved', repr(data))