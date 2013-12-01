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
       "5: Send a.bmp\n" +
       "6: Send a.bmp in parts")
ans = raw_input("Which would you like? (1-6)")
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
  time.sleep(2)
  with open('a_backup.bmp', 'rb') as f:
    num = s.send(hexlify(f.read()))
    print "We sent this many bytes: " + repr(num)
  print repr(s.send('*'))
  ans = s.recv(1024)
  print "Answer Recieved: " +  repr(ans)
  s.close()
  print ("Bye bye!")
elif '6' in ans:
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  s.send('q')
  time.sleep(0.2)
  with open('b.bmp', 'rb') as f:
     data = hexlify(f.read())
     for i in range (0, len(data), 1024):
       print float(i)/len(data)
       num = s.send(data[i:i+1024])
       print "We sent this many bytes: " + repr(num)
       if num < 1024:
         print repr(s.send('*'))
       recieved = s.recv(1024)
       print "Answer Received: " + repr(recieved)
  s.close()
else:
  print "I\'m sorry I couldn\'t be useful.  Byebye!"
  exit()