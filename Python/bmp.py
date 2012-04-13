import socket, os, Image, binascii

"""Send a sample image to the machine, ASCII encoded in base 16"""
HOST = '169.254.1.1'
PORT = 2000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
img = Image.open('a.bmp')
img.resize((2,2)).convert('1').save('.temp', 'bmp')
with open('.temp', 'rb') as f:
  s.send(binascii.hexlify(f.read()))
os.remove('.temp')
s.close()