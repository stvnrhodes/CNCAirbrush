import socket

"""Send a sample image to the machine, ASCII encoded in base 16"""
HOST = '169.254.1.1'
PORT = 2000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('Hello World')
s.close()