from socket import *
import threading
import xml.etree.ElementTree as ET
import time
import sys
import random

# Various Variables
serverip = None
serverport = 3818
chatport = random.randrange(2000,4200)
quit = False

#############TODO##############
### Connect to other clients based on location

class chatdevClient:
	def __init__(self):
		global quit
		global serverip
		print "Welcome to Chatdev!"
		print "Please input your information."
		print "What is the IP of your ChatDev server?"
		chatserv = raw_input("IP: ")
		serverip = str.strip(chatserv)
		print "What is your username?"
		username = raw_input("Username: ")
		print "Thanks.  What is your real name?"
		realname = raw_input("Real name: ")
		print "Great!  Setting up now..."
		# Get own IP with dummy socket
		s = socket(AF_INET, SOCK_DGRAM)
		s.connect(('google.com', 0))
		ip = s.getsockname()[0]
		serverNetworkingClass = serverNetworking()
		handleXMLClass = handleXML()
		onlineUsersDictClass = onlineUsersDict()
		userXML = handleXMLClass.userXML(username, realname, ip, chatport)
		userXMLString = handleXMLClass.packXML(userXML)
		userXMLString += "</data>"
		serverConnection(userXMLString).start()
		chatConnection(chatport, ip).start()
		while quit != True:
			print "Please choose an action (input digit):"
			print "\t1: View online users"
			print "\t2: Send message to user"
			print "\t3: Quit Cha+dev"
			userChoice = str.strip(raw_input("\tAction: "))
			if userChoice == "1":
				onlineUsersDictClass.onlineUsersPrint()
			elif userChoice == "2":
				### Display online users, allow choice of chat
				onlineUsersDictClass.onlineUsersPrint()
				print "Choose a user to message (input digit)"
				chatwithuser = str.strip(raw_input("User: "))
				if str.isdigit(chatwithuser):
					if int(chatwithuser) <= len(onlineUsersDictClass.userDictGet()):
						test = 0
						usernum = int(chatwithuser)-1
						# Ugh, hack to use digit with dict
						for dictuser in onlineUsersDictClass.userDictGet():
							if test == usernum:
								chatmessage = raw_input("Message: ")
								serverNetworkingClass.sendChatXML(handleXMLClass.chatXML(chatmessage), dictuser)
								break
							else:
								test += 1
					else:
						print "You must input a user's digit.  Exiting to main menu"
				else:
					print "You must input a digit.  Exiting to main menu"
			elif userChoice == "3":
				quit = True
			else:
				print "Please input a correct digit"
		print "Thanks for using Cha+dev!"
		sys.exit()
		
class chatConnection (threading.Thread):
	"""Class to accept incoming chat messages on proper port"""
	def __init__(self, port, ip):
		self.port = port
		self.ip = ip
		self.chatSock = socket(AF_INET, SOCK_STREAM)
		self.chatSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		address = (self.ip, self.port)
		self.chatSock.bind(address)
		threading.Thread.__init__(self)
		
		
	def run(self):
		serverNetworkingClass = serverNetworking()
		handleXMLClass = handleXML()
		self.chatSock.listen(4)
		while quit != True:
			peerSock, peerAddress = self.chatSock.accept()
			chatData = serverNetworkingClass.getChatXML(peerSock)
			handleXMLClass.displayChatXML(handleXMLClass.unpackXML(chatData[0]))

		
class serverConnection (threading.Thread):
	"""Class to keep connection to server active, send/receive XML"""
    # Thread's __init__ needs to be overridden to accept needed parameters
	def __init__ (self, userXMLString):
		self.userXMLString = userXMLString
		print "Connecting to Cha+dev server"
		self.serverNetworkingClass = serverNetworking()
		threading.Thread.__init__(self)
	        
	def run(self):
		handleXMLClass = handleXML()
		onlineUsersDictClass = onlineUsersDict()
		# Connect to server every 10 seconds, deal with incoming/outgoing XML
		while(quit != True):
			self.serverSock = self.serverNetworkingClass.serverConnect()
			onlineUsers = self.serverNetworkingClass.sendUserXML(self.userXMLString, self.serverSock)
			onlineUsers = handleXMLClass.unpackXML(onlineUsers[0])
			onlineUsersDictClass.userDictSetup()
			for user in onlineUsers.findall('user'):
				handleXMLClass.addOnlineUser(user)
			self.serverSock.close()
			time.sleep(1)
		
class onlineUsersDict:
	def __init__(self):
		pass

	def userDictSetup(self):
		"""Set up the dictionary used to store online users
		userDictLayout = {'username' : ['realName', 'ip', port]}"""
        onlineUserDict = {}
    
	def userDictAdd (self, username, realName, ip, port):
		self.onlineUserDict[username] = [realName, ip, port]
		
	def onlineUsersPrint(self):
		print self.onlineUserDict
		print "Online users:"
		tempcount = 1
		for user in self.onlineUserDict:
			print tempcount, ": ", user
			print "\tReal name: ", self.onlineUserDict[user][0]
			tempcount += 1
        
	def userDictGet (self):
		return self.onlineUserDict
		
class serverNetworking:
	def __init__(self):
		self.address = (serverip, serverport)
	
	def serverConnect(self):
		self.serverSock = socket(AF_INET,SOCK_STREAM)
		self.serverSock.connect(self.address)
		return self.serverSock
		
	def sendUserXML(self, userXMLString, serverSocket):
		# Send user XML to server
	    serverSocket.sendall(userXMLString)
	    
	    # Receive online user data back
	    final_data = []
	    temp_data=""
	    End = "</data>"
	    while True:
	        temp_data = serverSocket.recv(1024)
	        if End in temp_data:
	            final_data.append(temp_data[:temp_data.find(End)])
	            return final_data
	        final_data.append(temp_data)
	        if len(final_data) > 1:
	            # Check if End was split
	            last_pair = final_data[-2] + final_data[-1]
	            if End in last_pair:
	                final_data[-2] = last_pair[:last_pair.find( End)]
	                final_data.pop()
	                return final_data
	           
	def getChatXML(self, chatSocket):
		final_data = []
		temp_data=""
		End = "</data>"
		while True:
			temp_data = chatSocket.recv(1024)
			if End in temp_data:
				final_data.append(temp_data[:temp_data.find(End)])
				return final_data
			final_data.append(temp_data)
			if len(final_data) > 1:
				# Check if End was split
				last_pair = final_data[-2] + final_data[-1]
				if End in last_pair:
					final_data[-2] = last_pair[:last_pair.find( End)]
					final_data.pop()
					return final_data
					
	def sendChatXML(self, chatXML, chatuser):
		handleXMLClass = handleXML()
		userDictClass = onlineUsersDict()
		chatXMLString = handleXMLClass.packXML(chatXML)
		chatXMLString += "</data>"
		userdict2 = userDictClass.userDictGet()
		address = (userdict2[chatuser][1], int(userdict2[chatuser][2]))
		chatSock = socket(AF_INET,SOCK_STREAM)
		chatSock.connect(address)
		chatSock.sendall(chatXMLString)
		print "Message sent"
		chatSock.close()
	                
class handleXML:
	def __init__(self):
		pass
		
	def displayChatXML(self, chatXML):
		username = chatXML.findtext('username')
		message = chatXML.findtext('message')
		print username, "says: ", message, "\n"
				
	def userXML(self, username, realname, ip, port):
		self.username = username
		"""Generate client XML object"""
		xmluser = ET.Element("user")
		xmlusername = ET.SubElement(xmluser, "username")
		xmlusername.text = username
		xmlrealname = ET.SubElement(xmluser, "realname")
		xmlrealname.text = realname
		xmlip = ET.SubElement(xmluser, "ip")
		xmlip.text = ip
		xmlport = ET.SubElement(xmluser, "port")
		xmlport.text = str(port)
		return xmluser
		
	def chatXML(self, chatmessage):
		# Form message into proper XML for sending w/ format:
		# # <chat><username>username</username><message>message text</message></chat>
		xmlchat = ET.Element("chat")
		xmlusername = ET.SubElement(xmlchat, "username")
		xmlusername.text = self.username
		xmlmessage = ET.SubElement(xmlchat, "message")
		xmlmessage.text = chatmessage
		return xmlchat

		
	def addOnlineUser(self, element):
		username = element.findtext('username')
		realname = element.findtext('realName')
		ip = element.findtext('ip')
		port = element.findtext('port')
		userListing = onlineUsersDict()
		userListing.userDictAdd(username, realname, ip, port)

	def unpackXML(self, stringOfXML):
		"""Takes in XML as a string, returns XML element"""
		parsedXML = ET.fromstring(stringOfXML)
		return parsedXML
        
	def packXML(self, elementXML):
		"""Takes in XML element, returns XML as string"""
		XMLstring = ET.tostring(elementXML)
		return XMLstring

chatdevClient()
