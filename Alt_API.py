# Adding altitude API from http://www.gpsvisualizer.com/geocoder/elevation.html
import urllib2
import json

def elev(lat,lon):
  api_key = 'AIzaSyCju46bbkBVwXyAyEkE6tCmOkUc4hN4PhI'
  url = 'https://maps.googleapis.com/maps/api/elevation/json?locations=' + str(lat) + ',' + str(lon) + '&key=' + api_key
  json_obj = urllib2.urlopen(url)
  data = json.load(json_obj)

  for item in data['results']
    return item['elevation']

elev(39.714764,-105.114946)

# https://dds.cr.usgs.gov/srtm/version2_1/SRTM1/
