from socket import *

# http://www.devshed.com/c/a/Python/Sockets-in-Python-Into-the-World-of-Python-Network-Programming/
testsocket = socket(AF_INET,SOCK_STREAM)

testsocket.connect(('127.0.0.1',8080))
