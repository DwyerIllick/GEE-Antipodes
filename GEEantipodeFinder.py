'''
Dwyer's Dev's Digest March 2024 Submission; 1st Issue
This program retrieves images from the Google Earth Engine Api, stitches them together, 
and slowly zooms in on the portion of the map exactly on the other side of the world from us. 

To run this program on your own computer:
Download these pythonlibraries: 
earthengine-api [Not the 'ee' library, thats different]
requests
matplotlib
geocoder

To download these, you can type 'pip install [name of library]' into terminal 

I ran this file by typing 'python3 Geeantipodes.py' into terminal. 

Note that to run this yourself you will need to manually authenticate your computer with Google Earth Engine.
Tutorial with how to Authenticate: 'https://www.youtube.com/watch?v=Fd1eYs49dUI'
'''

import ee 
import requests
import matplotlib.pyplot as mtp
import matplotlib.image as mti
from io import BytesIO
import geocoder

ee.Authenticate()

print('passed')

ee.Initialize()   #starts the communication session with the Google Earth Engine API (GEE)

mtp.axis('off')
bufferSize = 400000  #Sets how wide the initial view is from the satelites in meters
reps = 7  #Number of times the program re-finds the image to zoom in 

#Find coords of antipode 
location = geocoder.ip('me').latlng         
print('coords: ', location[0], location[1])
oppLat = location[0] -location[0]
if location[1]< 0:
    oppLong = location[1] + 180 
else:
    oppLong = location[1] - 180

def getPic(i):
    roi = ee.Geometry.Point(oppLat, oppLong)
    buffed = roi.buffer(bufferSize*2)
    #-122.262, 37.8719
    #oppLat, oppLong
    startDate = '2016-04-01'
    endDate = '2018-05-01'

    #Take a collection of images from GEE and manipulate it to suit my needs
    group = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filterDate(startDate, endDate)\
    .select(['B2', 'B3', 'B4'])\
    .mosaic()

    #.filterBounds(ee.Algorithms.GeometryConstructors.BBox(oppLong - 10, oppLat -10, oppLong +10, oppLat+10))\

    try:
       print('*************', group.size())
    except:
       print('&&&&&&&&&&&&&&&&&&&&&&&&& alllllll goooooooddd, plenty of images')
    nGroup = group  #.mosaic() 
    #.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15))

    print(group.getInfo())

    reg = roi.buffer(bufferSize - i*bufferSize/reps + 7000).getInfo()['coordinates'] 
    print('alert', nGroup.getInfo()['bands'])  #info to help me debug
    
    visParms = {
        'min': 0,
        #'max': 1500,
        'max': 20000,
        #'min': 4,
        #'max': 1500,
    }
    #Min and Max values under visParms determines the brightness scaling of the images
    vissed = nGroup.visualize(**visParms)  

    #Retrieve the url of the manipulated image
    link = vissed.getThumbUrl({'region': reg, 'scale': (bufferSize - i*bufferSize/reps + 10000)/60, 'format': 'png'}) 

    print(link)
    
    #Scrape the Image from the Url to display later
    scraped = requests.get(link)
    imgData = BytesIO(scraped.content)
    image = mti.imread(imgData)
    return image



def upPic(a):               #Actually display the image retrieved
    mtp.axis('off')
    mtp.imshow(getPic(a))
    mtp.draw()
    mtp.pause(1)
    
    
for b in range(reps):           #Loop through displaying the image, zooms in each time
    upPic(b)
    mtp.clf()
    print('cleared', b, ' / ', reps-1)

upPic(reps+1)
mtp.pause(100) #Display the furthest zoomed in image for a few seconds



