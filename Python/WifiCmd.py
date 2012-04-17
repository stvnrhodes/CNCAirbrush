import socket, time
from binascii import hexlify

"""Send a hello world to the machine"""
HOST = '169.254.1.1'
PORT = 2000
print ("Hey there!  I\'m a quick program Steven wrote to be able to quickly send\n" +
       "data to the machine via the command line.")
ip = socket.gethostbyname(socket.gethostname())
if '169.254.' not in ip:
  print ("My IP Address appears to be " + repr(ip) + ", which means I probably can\'t connect " +
         "to the wifly.")
  ans = raw_input("Are you sure you want to continue? (y/n)")
  if ans in "noNo":
    print "I\'m sorry I couldn\'t be useful.  Byebye!"
    exit()
print ("\nI have 5 modes which you can choose from.  To quit, type exit.\n" +
       "1: Open a socket at the beginning of each message and close it at the end, \n" +
       "   ignoring responses\n" +
       "2: Open a socket at the beginning of each message and close it at the end, \n" +
       "   printing responses\n" +
       "3: Open a socket once and reuse it for messages, ignoring responses\n" +
       "4: Open a socket once and reuse it for messages, printing responses\n" +
       "5: Send a.bmp")
ans = raw_input("Which would you like? (1-5)")
if '1' in ans:
  print ("Awesome!  I\'ll use a new socket for each message.  Just type whatever \n" +
         "you want to see and I'll send it out.")
  while 1:
    input = raw_input("What is your command?")
    if 'exit' in input:
      print "I hope I was useful!"
      exit()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(input)
    print "Message Sent!"
    s.close()
elif '2' in ans:
  print ("Awesome!  I\'ll use a new socket for each message.  Just type whatever \n" +
         "you want to see and I'll send it out and print the response.")
  while 1:
    input = raw_input("What is your command?")
    if 'exit' in input:
      print "I hope I was useful!"
      exit()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(input)
    s.recv(1024)
    time.sleep(.1)
    ans = s.recv(1024)
    print "Answer Recieved: " +  repr(ans)
    s.close()
elif '3' in ans:
  print ("Awesome!  I\'ll reuse the socket for each message.  Just type whatever \n" +
         "you want to see and I'll send it out.")
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  while 1:
    input = raw_input("What is your command?")
    if 'exit' in input:
      break
    s.sendall(input)
    print "Message sent!"
  s.close()
  print "I hope I was useful!"
  exit()
elif '4' in ans:
  print ("Awesome!  I\'ll reuse the socket for each message.  Just type whatever \n" +
         "you want to see and I'll send it out and print the response.")
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  while 1:
    input = raw_input("What is your command?")
    if 'exit' in input:
      print "I hope I was useful!"
      exit()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(input)
    ans = s.recv(1024)
    print "Answer Recieved: " +  repr(ans)
elif '5' in ans:
  print ("Sending image...")
  """Send the image to the machine, ASCII encoded in base 16"""
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  s.send("q")
  with open('a.bmp', 'rb') as f:
    num = s.send(hexlify(f.read()))
    print "We sent this many bytes: " + repr(num)
  ans = s.recv(1024)
  print "Answer Recieved: " +  repr(ans)
  s.close()
  print ("Bye bye!")
else:
  print "I\'m sorry I couldn\'t be useful.  Byebye!"
  exit()