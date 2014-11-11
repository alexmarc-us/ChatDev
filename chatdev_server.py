from socket import *
from threading import Thread
import xml.etree.ElementTree as ET
import time
dictlock = False

### Add time since last seen to userDict
### Loop for presence checking
###	### If time since last check in > x time, remove from userDict 

class chatdevServer: 
    def __init__(self):
		# Get own IP with dummy socket
		s = socket(AF_INET, SOCK_DGRAM)
		s.connect(('google.com', 0))
		self.host = s.getsockname()[0]
		self.port = 3818
		self.address = (self.host, self.port)
		self.userListing = userDict()
		self.userListing.userDictSetup()
		presenceThread().start()
		self.socketLoop(self.address)

    def socketLoop(self, address):
        # Set up TCP socket for incoming XML string
		# Creating TCP socket for internet connections
		serverSock = socket(AF_INET, SOCK_STREAM)
		# Setting socket options to allow address reuse
		serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		# Binding socket to port
		print "Setting up Cha+dev server on host", self.host, "on port", self.port
		serverSock.bind(address)
		# Initiating socket listening
		serverSock.listen(4)
        
		print "Accepting incoming connections on socket..."
		while True:
			clientSock, clientAddress = serverSock.accept()
			NetworkThread(clientSock, clientAddress).start()
		serverSock.close()
		
class userDict:
	def __init__(self):
		pass

	def userDictSetup(self):
		"""Set up the dictionary used to store online users
		userDictLayout = {'username' : ['realName', 'ip', 'port', 'lastseen']}"""
        onlineUserDict = {}
    
	def userDictAdd (self, username, realName, ip, port):
		while dictlock == True:
			pass
		self.onlineUserDict[username] = [realName, ip, port, time.time()]
		
	def removeUser (self, user):
		global dictlock
		dictlock = True
		del self.onlineUserDict[user]
		dictlock = False
        
	def userDictGet (self):
		return self.onlineUserDict

class handleXML:
	def __init__(self):
		pass
    
	def unpackXML(self, stringOfXML):
		"""Takes in XML as a string, returns XML element"""
		parsedXML = ET.fromstring(stringOfXML)
		return parsedXML
        
	def packXML(self, elementXML):
		"""Takes in XML element, returns XML as string"""
		XMLstring = ET.tostring(elementXML)
		return XMLstring
	
	def addXML(self, element):
		userDictClass = userDict()
		userDictionary = userDictClass.userDictGet()
		username = element.findtext('username')
		realname = element.findtext('realname')
		ip = element.findtext('ip')
		port = element.findtext('port')
		if username in userDictionary:
			print username, " checked in,  presence noted"
		else:
			print "Adding ", username, " to onlineUser dictionary."

		userDictClass.userDictAdd(username, realname, ip, port)
        
	def generateOnlineUsers(self):
		userDictClass = userDict()
		onlineUsersDict = userDictClass.userDictGet()
		onlineUsersXML = ET.Element("onlineUsers")
		for onlineUser in onlineUsersDict:
			xmluser = ET.SubElement(onlineUsersXML, "user")
			xmlusername = ET.SubElement(xmluser, "username")
			xmlusername.text = onlineUser
			for i in range(3):
				if i == 0:
					xmlrealname = ET.SubElement(xmluser, "realName")
					xmlrealname.text = onlineUsersDict[onlineUser][i]
				if i == 1:
					xmlip = ET.SubElement(xmluser, "ip")
					xmlip.text = onlineUsersDict[onlineUser][i]
				if i == 2:
					xmlport = ET.SubElement(xmluser, 'port')
					xmlport.text = onlineUsersDict[onlineUser][i]
		return onlineUsersXML
		
		
class presenceThread(Thread):
	"""Class to check user presence and update userDict accordingly"""
	
	def run(self):
		userDictClass = userDict()
		while True:
			onlineusers = userDictClass.userDictGet()
			deluser = None
			for user in onlineusers:
				# Check if the user hasn't connected in more than 12 seconds
				if time.time() - onlineusers[user][3] > 3:
					deluser = user
					break
			if deluser != None:
				print "Removing ", user, " due to inactivity"
				userDictClass.removeUser(deluser)
			time.sleep(1)

class NetworkThread (Thread):
    """Class to connect to clients and begin threads"""
    
    # Thread's __init__ needs to be overridden to accept needed parameters
    def __init__ (self, clientSock, clientAddress):
        self.clientSock = clientSock
        self.clientAddress = clientAddress
        Thread.__init__(self)
        
    def run(self):
		print "Client connected from ", self.clientAddress
		# Get user data from incoming connection
		final_data = []
		temp_data = ""
		End = "</data>"
		while True:
			temp_data = self.clientSock.recv(1024)
			if End in temp_data:
				final_data.append(temp_data[:temp_data.find(End)])
				break
			final_data.append(temp_data)
			if len(final_data) > 1:
				# Check if End was split
				last_pair = final_data[-2] + final_data[-1]
				if End in last_pair:
					final_data[-2] = last_pair[:last_pair.find( End)]
					final_data.pop()
					break
		final_data = ''.join(final_data)
		print "Received data from ", self.clientAddress
		# Add user to online user database
		xmlClass = handleXML()
		userXML = xmlClass.unpackXML(final_data)
		xmlClass.addXML(userXML)
		
		# Send online user data back to user
		onlineUsersXML = xmlClass.generateOnlineUsers()
		onlineUsersString = xmlClass.packXML(onlineUsersXML)
		onlineUsersString += "</data>"
		self.clientSock.sendall(onlineUsersString)
                        
chatdevServer()
