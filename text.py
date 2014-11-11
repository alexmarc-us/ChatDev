import xml.etree.ElementTree as ET  # ElementTree module for easy XML manipulation
from pickle import *

username = "optimarcusprime"
realname = "Marcus"
ip = "localhost"
progLanguages = ["Python", "Java", "PHP", "HTML", "CSS"]

# Generate handshake XML
xmluser = ET.Element("user")
xmlusername = ET.SubElement(xmluser, "username")
xmlusername.text = username
xmlrealname = ET.SubElement(xmluser, "realname")
xmlrealname.text = realname
xmlip = ET.SubElement(xmluser, "ip")
xmlip.text = ip
xmlprog_languages = ET.SubElement(xmluser, "prog_languages")
for lang in progLanguages:
    xmllanguage = ET.SubElement(xmlprog_languages, "language")
    xmllanguage.text = lang
userXML = ET.ElementTree(xmluser)
#ET.dump(XMLstring, userXML)
XMLstring = ET.tostring(xmluser)
print XMLstring
