from socket import *
from threading import *

# Handler for creating multiple threads/connections
class Threader(Thread):
       def __init__ (self, clientsock, addr):
              self.clientsock = clientsock
              self.addr = addr
              Thread.__init__(self)

       def goThread(self):
              while 1:
                     print 'Received connection: ', self.addr
                     data = clientsock.recv(1024)
                     if not data:
                            break
                     clientsock.send('Message received: ' + data)
                     
              self.clientsock.close()

if __name__=='__main__':
       HOST = 'localhost'
       PORT = 8080
       ADDR = (HOST, PORT)
       serversock = socket(AF_INET, SOCK_STREAM)
       serversock.bind(ADDR)
       serversock.listen(2)
       
       while 1:
              print "Waiting for connection..."
              clientsock, addr = serversock.accept()
              print'Connected from: ', addr
              
              Threader(clientsock, addr).goThread()         

       serversock.close()
