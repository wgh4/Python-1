***************************
* README.TXT
***************************
CIT iTunes Search Application
Name: itunes_search.py
Version: 1.RELEASE
Author: Robert Knaap
StudentId: R00091539
email: robert.knaap@emc.com
phone: 086-6050603
Date: Wed Oct 31, 2012
***************************
* API
***************************
This application uses the itunes search API hosted on http://itunes.apple.com to execute searches on the itunes application store. See http://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html for more details. 

This The Search API allows to search for content within the iTunes Store, App Store, iBookstore and Mac App Store. You can search for a variety of content; including apps, ebooks, movies, podcasts, music, music videos, audiobooks, and TV shows. You can also call an ID-based lookup request to create mappings between your content library and the digital catalog.
***************************
* CIT iTunes Search Application
***************************
The CIT iTunes Search Application can search the iTunes Store for all albums of a given artist. The results will be stored in a file in the working directory in JSON format. This file will be parsed and for each album the application will create a Internet Shortcut within a folder of the artist. This shortcut will point to the location on the iTunes webstore.

The application will create the following directory structure within the working directory:

\SearchParameter\ArtistName\Albumname.url

e.g

\eminem\Eminem\The Slim Shady LP.url
\eminem\Eminem\The Marshall Mathers LP.url
\eminem\eminem.zip	

The application flow will be as follows:
1) The application accepts 2 command line arguments -a ArtistName -fFolderLocation and 1 -d(delete files) option
   If the -d option is provided, the application will delete all existing files within the given -f Folderlocation
2) The application uses a socket to connect to the itunes.apple.com server and to execute a search request 
3) The first search request will be similar like "Select all artists with artist name like %-a command line argument%"
4) The itunes.apple.com search api will return a json resultset
5) The json resultset will be stored in a file in the working directory called result.json
6) The HTTP header will be removed from the file and the file will be renamed to results2.json 
7) A Directory will be created with the same name as the -a search parameter in the working directory
8) The json resultset will be processed and for each artist found in the result set it should execute the following steps
a) check if the returned artist contains the %app artist command line argument% string 
b) check if the returned artist has an artist id (e.g some of the returned data is from ringtones and videos) and only registered artist have an id in the allmusic guide (amg)
c) create a directory with the same name as the artist in the directory created in step 7
d) execute another api search using urllib to execute a search for each artist albums
e) parse the resulting json data for each album and create an internet shortcut in the artist directory linking to the itunes album
f) Create a zip file that contains all the artists and albums returned by the search. The zip file will be stored in the search parameter folder
9) The application creates a logfile in a file within the working directory named YYYYMMDD_CCP1.log
***************************
* Parameters
***************************
Examples:

python itunes_search.py -aU2 -fSEARCH
python itunes_search.py -a"Maroon 5" -fSEARCH
python itunes_search.py -aMadonna -fSEARCH -d
python itunes_search.py -a"Rolling Stones" -fSEARCH -d
python itunes_search.py -a"Beyonce" -fSEARCH -d

-a defines the Artist to look for
-f defines the folder name where to store the search results
-d will delete the existing contents in the destination folder
***************************
* Notes
***************************

This program has been tested on an Apple MAC 
SourceCode can be found on GitHub: https://github.com/wgh4/Python-1.git







