#!/usr/bin/env python

##################################
# CIT Python Socket Assignment 1
# Cloud Computing with Python CPP Application
# By Robert Knaap
# student ID R00091539
# email: robert.knaap@emc.com
# phone: 086-6050603
# October 31st 2012
#
# Check README.TXT for suggested parameter values
# Logfile YYYYMMDD_CCP1.log in working Directory
##################################

import socket	#for sockets
import sys	#for exit function
import os       #for operating system functions
import argparse #for command line options
import json     #for parsing of JSON file
import urllib   #for second part of the assignment
import shutil   #to create zip file and delete directory
import logging  #for debug and error logging
import time  #for creating a datetime logfile

#Function to remove illegal file and directory name characters
def funRemoveChars(value, deletechars):
    for c in deletechars:
        value = value.replace(c,'')
    return value;

# create logger for the 'CCP1 CIT application'
errorlog = logging.getLogger('CCP1_application')
errorlog.setLevel(logging.DEBUG)
# create file handler which logs info messages to YYYYMMDD_CCP1.log
filehandler = logging.FileHandler(time.strftime("%Y%m%d_CCP1.log"))
filehandler.setLevel(logging.DEBUG)
# create console handler with a higher log level of INFO
consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.INFO)
# define format and assign it to  handlers
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
consolehandler.setFormatter(formatter)
filehandler.setFormatter(formatter)
# add the handlers to the logger
errorlog.addHandler(filehandler)
errorlog.addHandler(consolehandler)

# Process Command Line Parameters
parser = argparse.ArgumentParser()
parser.add_argument('-a','-A',action='store',help='Name of the Artist')
parser.add_argument('-f','-F',action='store',help='Export Folder Location')
parser.add_argument('-d','-D',action='store_true', default=False,dest='delete_switch',help='Delete files when present')

args=parser.parse_args()

#Assign arguments to attributes
strSearchArg = args.a      # Artist Search Key
#Make all lower Case
if strSearchArg:
   strSearchArg = strSearchArg.lower()
   #if artist argument contains spaces ... replace spaces with +
   strSearchArgsFixed = strSearchArg.replace(' ', '+')

strFolderArg = args.f      # Folder Location within working Folder

boDelete = args.delete_switch # Check the Delete Existing Files yes/no switch
    
#parameters are mandatory
if not strSearchArg :
    #print 'ERROR: Missing Search Parameter (-a)'
    errorlog.error('Missing Search Parameter (-a), Exiting') 
    sys.exit()
if not strFolderArg :
    #print 'ERROR: Missing Export Folder (-f)'
    errorlog.error('Missing Export Folder (-f), Exiting')
    sys.exit()

errorlog.info('CIT iTUNES PARSE APP - Parameter(s) : Artist =' + str(strSearchArg) + ' Directory = ' + strFolderArg)
if boDelete :
   errorlog.info('Parameter(s) : Deleting existing files in target directory')
else:
   errorlog.info('Parameter(s) : Keep existing files in target directory')
    
# Check if Export Folder provided in command line argument exists
try:
   if not os.path.exists(strFolderArg):
      os.mkdir (strFolderArg)
   else:
      #delete folder with its contents and recreate when boDelete = true
      if boDelete:
        shutil.rmtree(strFolderArg)
	os.mkdir (strFolderArg)
except OSError:
    errorlog.error('Unable to create/delete Export Folder (-f), Exiting')
    sys.exit()

#create an INET, STREAMing socket to itunes service
try:
	sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
	errorlog.error('Unable to create socket')
	sys.exit()
errorlog.info('CIT iTUNES PARSE APP - Successfully Created Socket')


#itunes service details
strHostName = 'itunes.apple.com';
iPortNumber = 80;

#get ip address from hostname
try:
        host_ip = socket.gethostbyname( strHostName )
except socket.gaierror:
	#could not resolve hostname
	errorlog.error('Hostname ' + strHostName + ' could not be resolved. Exiting')
	sys.exit()

#Try to Connect to remote server
sSocket.connect((host_ip , iPortNumber))
errorlog.info('CIT iTUNES PARSE APP - Socket Connected to ' + strHostName + ' on ip ' + host_ip)

#I tried the syntax, as per aislings recording
#GET = '/search?term=U2&media=music&entity=musicArtist&attribute=artistTerm&country=ie&limit=200'
#HOST = 'http://itunes.apple.com'
#HTTPRequest = "GET %s HTTP/1.1\r\n Host: %s\r\n\r\n" % (GET, HOST)
#and other variations, but they kept resulting in a HTTP/1.0 400 Bad Request ERROR
#this API requires to be called using the full PATH: e.g. GET http://itunes.apple.com/search?term=
#in order for it to work

HTTPRequest = """GET http://itunes.apple.com/search?term=""" + strSearchArgsFixed + """&media=music&entity=musicArtist&attribute=artistTerm&country=ie&limit=200 HTTP/1.0\r\n
Host: itunes.apple.com\r\n
From: robert.knaap@mycit.ie\r\n
User-Agent: Python\r\n
Content-type: application/json\r\n
Charset: utf-8\r\n
Accept:	application/json\r\n"""

try :
	#Send the request
	sSocket.send(HTTPRequest)
except socket.error:
	#Request failed
	errorlog.error('Search API Request failed')
	sys.exit()
errorlog.info('CIT iTUNES PARSE APP - Search API Request send successfully')

#Store results in results.json file in the current working directory
strOutputFile = open("results.json", "w")

jsonData = sSocket.recv(1024)
strData = ""

while len(jsonData):
    strData = strData + jsonData
    jsonData = sSocket.recv(1024)
sSocket.close()
strOutputFile.write(strData)
strOutputFile.close()

errorlog.debug(strData)

#remove HTTP header from results.json file
#the standard output contains the following header
#HTTP/1.0 200 OK
#x-apple-orig-url-path: /search?term=kiss&media=music&entity=musicArtist&country=ie&limit=200
#x-apple-translated-wo-url: /WebObjects/MZStoreServices.woa/ws/wsSearch?term=kiss&media=music&entity=musicArtist&country=ie&limit=200
#x-apple-application-site: NWK
#apple-timing-app: 3002 ms
#Content-Type: text/javascript; charset=utf-8
#x-apple-application-instance: 1021017
#x-webobjects-loadaverage: 0
#Cache-Control: no-transform, max-age=57
#Date: Wed, 17 Oct 2012 19:29:25 GMT
#Connection: close
#X-Apple-Partner: origin.0

#remove first 15 lines of the result.json file
print "rename json"
jsonArtistdata="".join(open("results.json").readlines()[15:-1])
#save cleaned file to results2.json
open("results2.json","wb").write(jsonArtistdata)

origWD = os.getcwd() # remember our original working directory
errorlog.debug('Current Working Directory:' + os.getcwd())

#Process Json Data
errorlog.info('CIT iTUNES PARSE APP - Processing results.json file')   
results=json.load(open('results2.json'))

# Change Directory from working directory to the export folder provided in the command line argument
os.chdir(os.path.join(origWD, strFolderArg))
strSearchDir =  os.getcwd()

# Create Folder that corresponds with the Search Argument
try:
   if not os.path.exists(strSearchArg):
      os.mkdir(strSearchArg)
except OSError:
    errorlog.error('Unable to create directory /' + strSearchArg + ' in working directory')   
    pass

os.chdir(os.path.join(strSearchDir, strSearchArg))
strProcessDir =  os.getcwd()

#Processing Json Results
errorlog.info("Processing " + str(results["resultCount"]) + " potential artists")
           
for artist in results["results"]:
    
    #filter out non-artist references returned by iTunes
    #by checking if the artistAmgId key is in the JSON results - if not skip
    #amg =  All Music Guide 
    
    if  artist.has_key('amgArtistId'):
       #get artistname and encode in utf-8 due to chinese and other weird characters
       strArtistName =  artist["artistName"].encode('utf-8')
       #remove illegal file characters from name
       strArtistName =  funRemoveChars(strArtistName, '\/:*?"<>|')
       errorlog.debug(strSearchArg + ";" + strArtistName)
    
       if strSearchArg in strArtistName.lower():
        
           #reset WorkingFolder
           os.chdir(strProcessDir)
           strArtistID =str( artist["artistId"])
           strArtistAmgId =  str(artist["amgArtistId"])
           errorlog.debug('strAMGid = ' + strArtistAmgId)
           #strArtistName =  str(artist["artistName"])
           #strArtistName =  funRemoveChars(strArtistName, '\/:*?"<>|')
           #errorlog.debug('strArtistNAME = ' + strArtistName)
           #Change directory to existing or new artist directory 
           if not os.path.exists(strArtistName):
              os.mkdir (strArtistName)
           errorlog.debug('chdir ' + strProcessDir + '/' + strArtistName)
           os.chdir(os.path.join(strProcessDir, strArtistName))
          
           #For each artist, execute an API request to retrieve all the albums using the AMG Artist Id
           #Use URLLIB to retieve JSON data
           HTTPRequest = 'http://itunes.apple.com/lookup?amgArtistId=' + strArtistAmgId + '&entity=album'
           
           errorlog.info(HTTPRequest)
           jsonAlbumData =  urllib.urlopen(HTTPRequest).read()
           AlbumResults = json.loads(jsonAlbumData)
           errorlog.debug(AlbumResults)
           errorlog.info("Processing " + str(AlbumResults["resultCount"]) + " potential albums for artist " + strArtistName)
           
           #Loop through JSON results (using URLLIB no http header is received, so no need to filter)
           for collection in AlbumResults["results"]:
            # filter out the album data and ignore the artist data returned by the query
              if collection["wrapperType"] == "collection":
                #only filter out albums that have an URL value
                if  collection.has_key('collectionViewUrl'):
                   errorlog.info("id: %s \t name: %s" % (collection["collectionId"],collection["collectionName"]))
                   #retrieve albumname and remove illegal file characters and encode in utf-8
                   strAlbumName = (collection["collectionName"].encode('utf-8'))             
                   strAlbumName =  funRemoveChars(strAlbumName, '\/:*?"<>|')
                   #Create Internet ShortCut
                   strCollectionUrl = strAlbumName + ".url"
                   path = os.path.join(os.getcwd(), strCollectionUrl)
                   target = (collection["collectionViewUrl"])
                   shortcut = file(path, 'w')
                   shortcut.write('[InternetShortcut]\n')
                   shortcut.write('URL=%s\n' % target )
                   shortcut.write('IconIndex=0')
                   shortcut.close()
errorlog.info('JSON parsing Completed')

# Zip the contents of the ProcessDir and Store it in the processdir
shutil.make_archive(strProcessDir, 'zip', strProcessDir)


